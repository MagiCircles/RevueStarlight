# -*- coding: utf-8 -*-
from __future__ import print_function
import cStringIO, csv, datetime, html2text, requests, time, urllib
from collections import OrderedDict
from django.conf import settings as django_settings
from django.utils import timezone
from wand.image import Image
from wand.exceptions import BlobError
from magi.import_data import (
    import_data as magi_import_data,
    import_generic_item,
    save_item,
)
from magi import models as magi_models
from magi.tools import (
    create_user,
)
from magi import urls # loads context
from magi.utils import (
    getAstrologicalSign,
    saveImageURLToModel,
    join_data,
    localImageToImageFile,
    saveLocalImageToModel,
    split_data,
)
from starlight import models
from starlight.utils import (
    calculateMemoirStatistics,
)

############################################################
# API Import
############################################################

TO_STATISTICS = {
    'hp': 'hp',
    'atk': 'act_power',
    'pdef': 'normal_defense',
    'mdef': 'special_defense',
    'agi': 'agility',
}

TO_CHARACTER = {
    401: u'Akira Yukishiro',
    402: u'Michiru Otori',
    403: u'Liu Mei Fan',
    404: u'Shiori Yumeoji',
    405: u'Yachiyo Tsuruhime',
    801: u'Giraffe',
    802: u'Elle',
    803: u'Andrew',
    301: u'Aruru Otsuki',
    302: u'Misora Kano',
    303: u'Lalafin Nonomiya',
    304: u'Tsukasa Ebisu',
    305: u'Shizuha Kocho',
    201: u'Tamao Tomoe',
    202: u'Ichie Otonashi',
    203: u'Fumi Yumeoji',
    204: u'Rui Akikaze',
    205: u'Yuyuko Tanaka',
    101: u'Karen Aijo',
    102: u'Hikari Kagura',
    103: u'Mahiru Tsuyuzaki',
    104: u'Claudine Saijo',
    105: u'Maya Tendo',
    106: u'Junna Hoshimi',
    107: u'Nana Daiba',
    108: u'Futaba Isurugi',
    109: u'Kaoruko Hanayagi',
}

TO_CHARACTER_NAME_SWAPPED = {
    _id: u' '.join(reversed(_name.split(' ')))
    for _id, _name in TO_CHARACTER.items()
}
TO_CHARACTER_NAME_SWAPPED[403] = u'Liu Mei Fan'

TO_ATTRIBUTES = {
    1: 'flower',
    2: 'wind',
    3: 'snow',
    4: 'moon',
    5: 'space',
    6: 'cloud',
    7: 'dream',
}

TO_DAMAGE = {
    1: 'normal',
    2: 'special',
}

TO_POSITION = {
    1: 'rear',
    2: 'center',
    3: 'front',
}

TO_SKILL_TYPE = {
    'command_1': 'basic',
    'command_2': 'basic',
    'command_3': 'basic',
    'unique': 'climax',
    'confusion': None, # couldn't find what it was in the game?
    # Missing from json files atm:
    'auto': 'auto',
    'finishing': 'finishing',
}

MEMOIR_TYPE_TO_UPGRADE = {
    1: False,
    2: True,
}

TO_VOICE_ACTRESS = {
    'Ayasa Ito': 'Ayasa Itou',
    'Emiri Kato': 'Emiri Katou',
    'Hotaru Nomoto': 'Nomoto Hotaru', # swapped for some reason?
    'Hinata Sato': 'Hinata Satou',
}

def mapStatistics(prefix):
    def _f(v):
        return {
            u'{}{}'.format(prefix, field_name): v.get(api_field_name, None) or None
            for api_field_name, field_name in TO_STATISTICS.items()
        }
    return _f

def mapTranslatedValues(field_name, external_japanese_field=False):
    def _f(v):
        d = {
            field_name: v.get('en', None),
            u'd_{}s'.format(field_name): {},
        }
        if v.get('ko', None):
            d[u'd_{}s'.format(field_name)]['kr'] = unicode(v['ko'])
        if v.get('zh_hant', None):
            d[u'd_{}s'.format(field_name)]['zh-hant'] = unicode(v['zh_hant'])
        if v.get('ja', None):
            if external_japanese_field:
                d[u'japanese_{}'.format(field_name)] = unicode(v['ja'])
            else:
                d[u'd_{}s'.format(field_name)]['ja'] = unicode(v['ja'])
        return d
    return _f

def updateOrCreateFk(model, new_field_name, default_name=None, transform_name=None):
    def _f(v):
        name = v.get('en', None)
        if not name:
            if default_name:
                name = default_name
            else:
                return (new_field_name, None)
        if transform_name:
            name = transform_name(name)
        item, created = model.objects.get_or_create(name=name, defaults={ 'owner_id': 1 })
        if v.get('ja', None):
            item.add_d('names', 'ja', v['ja'])
        if v.get('kr', None):
            item.add_d('names', 'kr', v['kr'])
        if v.get('zh_hant', None):
            item.add_d('names', 'zh-hant', v['zh_hant'])
        item.save()
        return (new_field_name, item)
    return _f

def findAct(model, unique_data, data):
    # First try to get it from the internal id
    try:
        return model.objects.filter(internal_id=unique_data['internal_id'])[0]
    except IndexError:
        pass
    # Then from Japanese name + details
    if data['japanese_name']:
        filters = { k: v for k, v in data.items() if k in ['japanese_name', 'japanese_description'] }
    # Finally from English name + details (shouldn't happen)
    else:
        filters = { k: v for k, v in data.items() if k in ['name', 'description'] }
    try:
        return model.objects.filter(**filters)[0]
    except IndexError:
        pass
    return None

ACT_IMPORT_CONFIGURATION = {
    'model': models.Act,
    'find_existing_item': findAct,
    'unique_fields': [
        'internal_id',
    ],
    'fields': [
        'i_type',
        'cost',
    ],
    'mapping': {
        'id': 'internal_id',
        'name': mapTranslatedValues('name', external_japanese_field=True),
        'description': mapTranslatedValues('description', external_japanese_field=True),
    },
    'mapped_fields': [
        'internal_id', 'name', 'japanese_name', 'description', 'japanese_description',
    ],
    'dont_erase_existing_value_fields': [
        'name',
        'japanese_name',
        'description',
        'japanese_description',
    ],
    'ignored_fields': [
        'attribute_id', # same as card
        'icon_id',
        'sequence_id',
    ],
}

def mapSkills(skills):
    added_acts = []
    for skill_name, item in skills.items():
        item['i_type'] = TO_SKILL_TYPE[skill_name]
        if item['i_type']:
            act_unique_data, act_data, not_in_fields = import_generic_item(ACT_IMPORT_CONFIGURATION, item)
            print('- Ignored:', not_in_fields)
            item = save_item(ACT_IMPORT_CONFIGURATION, act_unique_data, act_data, print, json_item=item)
            if item:
                added_acts.append(item)
    return ('acts', added_acts)

def stageGirlCallback(details, item, unique_data, data):
    # Swap name
    unique_data['name'] = TO_CHARACTER_NAME_SWAPPED[item['id']]

    # Birthday
    try:
        data['birthday'] = datetime.date(2017, item['birth_month'], item['birth_day'])
        data['i_astrological_sign'] = models.StageGirl.get_i(
            'astrological_sign',
            getAstrologicalSign(data['birthday'].month, data['birthday'].day),
        )
    except ValueError:
        pass

def memoirCallbackEnd():
    # Auto calculate min_level and max_level from base and delta
    for memoir in models.Memoir.objects.all():
        calculateMemoirStatistics(memoir)
        memoir.save()

TO_SONG_CREDIT = {
    'en': {
        'Written by': ['lyricist'],
        'Composed and arranged by': ['composer', 'lyricist'],
        'Composed by': ['composer'],
        'Arranged by': ['arranger'],
        'Orchestral arrangement': ['orchestral_arrangement'],
    },
    'ko': {
        u'작사': ['lyricist'],
        u'작곡/편곡': ['composer', 'lyricist'],
        u'작곡': ['composer'],
        u'편곡': ['arranger'],
        u'오케스트라 편곡': ['orchestral_arrangement'],
    },
    'zh_hant': {
        u'作詞': ['lyricist'],
        u'作曲/編曲': ['composer', 'lyricist'],
        u'作詞/編曲': ['arranger', 'lyricist'],
        u'作曲': ['composer'],
        u'編曲': ['arranger'],
        u'管弦樂版本': ['orchestral_arrangement'],
    },
    'ja': {
        u'作詞': ['lyricist'],
        u'作曲/編曲': ['composer', 'lyricist'],
        u'作曲': ['composer'],
        u'編曲': ['arranger'],
        u'オーケストラアレンジ': ['orchestral_arrangement'],
    },
}

TO_LANGUAGE_FIELD = {
    'ko': 'kr',
    'zh_hant': 'zh-hant',
    'ja': 'ja',
}

def songCredits(value):
    data = {
        u'd_{}s'.format(field_name): {}
        for field_name in models.Song.CREDITS_FIELDS
    }
    data['singers'] = []

    for language, description in value.items():
        if not description.strip():
            continue
        singers, credits = description.split('\n\n')

        if language == 'en':
            for singer in singers.split('\n')[1:]:
                voice_actress_name = singer.split('(')[1].split(')')[0].strip()
                voice_actress_name = TO_VOICE_ACTRESS.get(voice_actress_name, voice_actress_name)
                voice_actress_name_reversed = u' '.join(reversed(voice_actress_name.split(' ')))
                try:
                    voice_actress = models.VoiceActress.objects.filter(name=voice_actress_name_reversed)[0]
                except IndexError:
                    voice_actress = models.VoiceActress.objects.filter(name=voice_actress_name)[0]
                if voice_actress:
                    if 'singers' not in data:
                        data['singers'] = []
                    data['singers'].append(voice_actress)

        if language == 'ja' and not value.get('en', '').strip():
            for singer in singers.split('\n')[1:]:
                voice_actress_name = singer.split(u'（')[1].split(u'）')[0].strip()
                voice_actress_name_reversed = u' '.join(reversed(voice_actress_name.split(' ')))
                for va_pk, va in django_settings.VOICE_ACTRESSES.items():
                    if va['names'].get('ja', None) in [voice_actress_name, voice_actress_name_reversed]:
                        voice_actress = models.VoiceActress.objects.filter(pk=va_pk)[0]
                if voice_actress:
                    if 'singers' not in data:
                        data['singers'] = []
                    data['singers'].append(voice_actress)

        credits = credits.replace(u'：', ':')

        for title in TO_SONG_CREDIT[language].keys():
            credits = credits.replace(u'{}{}:'.format(
                u'　' if language in ['zh_hant', 'ja'] else ' ',
                title,
            ), u'\n{}:'.format(title))
        credits = credits.replace(u'오케스트라\n편곡', u'오케스트라 편곡')

        for credit in credits.split('\n'):
            title, name = credit.split(':')
            title = title.strip()
            name = name.strip().replace(' and ', ', ')
            if name.endswith('.'):
                name = name[:-1]
            for field_name in TO_SONG_CREDIT[language][title]:
                if language == 'en':
                    data[field_name] = name
                else:
                    data[u'd_{}s'.format(field_name)][TO_LANGUAGE_FIELD[language]] = name
    return data

def songCallbackAfterSave(details, item, json_item):
    path = u'starlight/static/extracts/revue3/27_{}.png'.format(json_item['id'])
    saveLocalImageToModel(item, 'image', path)
    item.save()

IMPORT_CONFIGURATION = OrderedDict()

IMPORT_CONFIGURATION['stagegirls'] = {
    'model': models.StageGirl,
    'unique_fields': [
        'name',
    ],
    'mapping': {
        'name': mapTranslatedValues('name'),
        'department_1': updateOrCreateFk(models.School, 'school', default_name='Other'),
        'likes': mapTranslatedValues('likes'),
        'dislikes': mapTranslatedValues('dislikes'),
        'like_food': mapTranslatedValues('favorite_food'),
        'dislike_food': mapTranslatedValues('least_favorite_food'),
        'introduction': mapTranslatedValues('introduction'),
        'department_2': mapTranslatedValues('school_department'),
        'cv': updateOrCreateFk(
            models.VoiceActress, 'voice_actress',
            transform_name=lambda _name: u' '.join(reversed(TO_VOICE_ACTRESS.get(
                _name, _name).split(' ')))),
    },
    'mapped_fields': [
        'name', 'school', 'likes', 'dislikes', 'favorite_food', 'least_favorite_food',
        'introduction', 'school_department', 'voice_actress',
    ],
    'ignored_fields': [
        'id',
        'first_name', 'last_name', 'cv_fist', 'cv_last', 'name_ruby', # Already in name
        'birth_day', 'birth_month', # Handled in stageGirlCallback
        'school_id', # Handled in department_1
    ],
    'callback': stageGirlCallback,
}

IMPORT_CONFIGURATION['cards'] = {
    'model': models.Card,
    'unique_fields': [
        'number',
   ],
    'mapping': {
        'id': 'number',
        'character_id': lambda v: ('stage_girl', models.StageGirl.objects.get_or_create(
            name=TO_CHARACTER_NAME_SWAPPED[v], defaults={ 'owner_id': 1, 'school_id': 1 })[0]),
        'base_rarity': lambda v: ('i_rarity', v),
        'attribute': lambda v: ('i_element', TO_ATTRIBUTES[v]),
        'damage_type': lambda v: ('i_damage', TO_DAMAGE[v]),
        'position': lambda v: ('i_position', TO_POSITION[v]),
        'base': mapStatistics('base_'),
        'delta': mapStatistics('delta_'),
        'skills': mapSkills,
        'name': mapTranslatedValues('name'),
        'description': mapTranslatedValues('description'),
        'profile': mapTranslatedValues('profile'),
        'get_message': mapTranslatedValues('message'),
    },
    'mapped_fields': [
        'number', 'stage_girl', 'i_rarity', 'i_element', 'i_damage', 'i_position',
    ] + [
        u'{}{}'.format(_prefix, _statistic)
        for _statistic in models.BaseCard.STATISTICS_FIELDS
        for _prefix in ['base_', 'delta_']
    ] + [
        'acts', 'name', 'description', 'profile', 'message',
    ],
    'dont_erase_existing_value_fields': [
        'name',
        'description',
        'profile',
        'message',
    ],
    'ignored_fields': [
        'cost', # value can be determined by rarity

        # I don't think we will store these
        'model_id',
        'win_sequence_id',
        'friendship_pattern_id',
        'friendship_level_up_adventures',

        # Maybe later?
        'growth_boards',

        # Todo: what is this?
        'stats', # cri: 50, dex: 5, eva: 0, hit: 0
        'personality_id', # personality.lua has sentences + final_attack_id?
        'role_index', # I couldn't find any list of index -> role
    ],
}

IMPORT_CONFIGURATION['memoirs'] = {
    'model': models.Memoir,
    'unique_fields': [
        'number',
    ],
    'fields': [
        'sell_price',
    ],
    'mapping': {
        'id': 'number',
        'type': lambda v: ('is_upgrade', MEMOIR_TYPE_TO_UPGRADE[v]),
        'rarity': 'i_rarity',
        'base': mapStatistics('base_'),
        'delta': mapStatistics('delta_'),
        'name': mapTranslatedValues('name'),
        'profile': mapTranslatedValues('explanation'),
        'skills': mapSkills, # todo: not in JSON atm
    },
    'mapped_fields': [
        'number', 'i_rarity', 'is_upgrade',
    ] + [
        u'{}{}'.format(_prefix, _statistic)
        for _statistic in models.BaseCard.STATISTICS_FIELDS
        for _prefix in ['base_', 'delta_']
    ] + [
        'name', 'explanation',
    ],
    'dont_erase_existing_value_fields': [
        'name',
        'explanation',
    ],
    'ignored_fields': [
        'cost', # value can be determined by rarity

        # Todo: what is this?
        'material_exp',
    ],
    'callback_end': memoirCallbackEnd,
}

IMPORT_CONFIGURATION['songs'] = {
    'model': models.Song,
    'unique_fields': [
        'name',
    ],
    'mapping': {
        'name': mapTranslatedValues('name'),
        'description': songCredits,
    },
    'mapped_fields': [
        'name', 'singers',
    ] + models.Song.CREDITS_FIELDS,
    'callback_after_save': songCallbackAfterSave,
}

def import_data(local=False, to_import=None, log_function=print):
    magi_import_data(
        None, IMPORT_CONFIGURATION, results_location=None,
        local=local, to_import=to_import, log_function=log_function,
    )

############################################################
# Local images import
############################################################

# This is a temporary feature which in the future will be
# replaced by images downloaded directly from the API.
def import_images(to_import=None):
    if not to_import or 'cards' in to_import:
        for card in models.Card.objects.all():
            print('Importing images for card #{} {}'.format(card.number, card))
            needs_save = []
            # Art
            art_data = None
            if not card.art or 'reload' in to_import:
                path = u'starlight/static/extracts/dress/cg/{}/image.png'.format(card.number)
                art_data, art = saveLocalImageToModel(card, 'art', path, return_data=True)
                if art is None:
                    print('  Art file not found:', path)
                else:
                    needs_save.append('art')
            # Base icon
            base_icon_data = None
            if not card.base_icon or 'reload' in to_import:
                path = u'starlight/static/extracts/large/1_{}.png'.format(card.number)
                base_icon_data, icon = saveLocalImageToModel(card, 'base_icon', path, return_data=True)
                if icon is None:
                    print('  Icon file not found:', path)
                else:
                    needs_save.append('base_icon')
            # Generated icons
            for rank in [1, 2, 3, 5, 7]:
                for rarity in [1, 2, 3, 4, 5, 6]:
                    if rarity < card.rarity:
                        continue
                    elif rarity == card.rarity and rank == 7:
                        field_name = 'icon'
                    else:
                        field_name = 'rank{rank}_rarity{rarity}_icon'.format(rank=rank, rarity=rarity)
                    if not getattr(card, field_name) or 'reload' in to_import:
                        base_icon_data, icon = generate_card_icon(
                            card, field_name, rank, rarity, base_icon_data=base_icon_data)
                        if icon is not None:
                            needs_save.append(field_name)
            # Transparent
            if not card.transparent or 'reload' in to_import:
                path = u'starlight/static/extracts/battle/model/{n}/cutin/cutin_special_{n}.png'.format(
                    n=card.number)
                transparent = saveLocalImageToModel(card, 'transparent', path)
                if transparent is None:
                    print('  Transparent file not found:', path)
                else:
                    needs_save.append('transparent')
            # Image
            if not card.image or 'art' in needs_save:
                art_data, image = generate_card(card, art_data=art_data)
                if image is not None:
                    needs_save.append('image')

            if needs_save:
                card.save()
                print('  Saved:', needs_save)
    if not to_import or 'memoirs' in to_import:
        for memoir in models.Memoir.objects.all():
            print('Importing images for memoir #{} {}'.format(memoir.number, memoir))
            needs_save = []
            # Art
            art_data = None
            if not memoir.art or 'reload' in to_import:
                path = u'starlight/static/extracts/equip/cg/{}/image.png'.format(memoir.number)
                art_data, art = saveLocalImageToModel(memoir, 'art', path, return_data=True)
                if art is None:
                    print('  Art file not found:', path)
                else:
                    needs_save.append('art')
            # Base icon
            base_icon_data = None
            if not memoir.base_icon or 'reload' in to_import:
                path = u'starlight/static/extracts/large/2_{}.png'.format(memoir.number)
                base_icon_data, icon = saveLocalImageToModel(memoir, 'base_icon', path, return_data=True)
                if icon is None:
                    print('  Icon file not found:', path)
                else:
                    needs_save.append('base_icon')
            # Generated icons
            for rank in [1, 2, 3, 4, 5]:
                if rank == 5:
                    field_name = 'icon'
                else:
                    field_name = 'rank{rank}_icon'.format(rank=rank)
                if not getattr(memoir, field_name) or 'reload' in to_import:
                    base_icon_data, icon = generate_memoir_icon(
                        memoir, field_name, rank, base_icon_data=base_icon_data)
                    if icon is not None:
                        needs_save.append(field_name)
            # Image
            if not memoir.image or 'art' in needs_save:
                art_data, image = generate_memoir(memoir, art_data=art_data)
                if image is not None:
                    needs_save.append('image')

            if needs_save:
                memoir.save()
                print('  Saved:', needs_save)

def generate_card(card, art_data=None):
    try:
        if not art_data:
            art_field = getattr(card, 'art')
            art_data = art_field.read()
        art_image = Image(file=cStringIO.StringIO(art_data))
    except (BlobError, ValueError):
        print('  Art not saved in card.')
        return art_data, None

    try:
        border_image = Image(filename='starlight/static/extracts/cards_elements/card_border.png')
        element_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(card.element))
        rarity_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(card.rarity))
        position_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(card.position))
    except BlobError:
        print('  Cards layer image(s) not found.')
        return art_data, None

    art_image.resize(width=border_image.width, height=border_image.height)
    art_image.composite(border_image, left=0, top=0)
    art_image.composite(element_image, left=(art_image.width - element_image.width), top=0)
    art_image.composite(position_image, top=element_image.height, left=(art_image.width - position_image.width - 18))
    art_image.composite(rarity_image, top=(art_image.height - rarity_image.height - 22), left=22)

    art_image.save(filename='tmp.png')

    return art_data, saveLocalImageToModel(card, 'image', 'tmp.png')

def generate_card_icon(card, field_name, rank, rarity, base_icon_data=None):
    try:
        if not base_icon_data:
            base_icon_field = getattr(card, 'base_icon')
            base_icon_data = base_icon_field.read()
        base_icon_image = Image(file=cStringIO.StringIO(base_icon_data))
    except (BlobError, ValueError):
        print('  Base icon not saved in card.')
        return base_icon_data, None

    try:
        border_image = Image(filename=u'starlight/static/extracts/cards_elements/card_icon_rank{}.png'.format(rank))
        position_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(card.position))
        element_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(card.element))
        rarity_image = Image(filename=u'starlight/static/extracts/cards_elements/icon_rarity{}.png'.format(rarity))
    except BlobError:
        print('  Icon layer image(s) not found.')
        return base_icon_data, None
    base_icon_image.composite(border_image, left=0, top=0)
    position_image.transform(resize='x20')
    base_icon_image.composite(position_image, top=34, left=4)
    element_image.resize(width=37, height=37)
    base_icon_image.composite(element_image, top=1, left=1)
    base_icon_image.composite(
        rarity_image, top=(base_icon_image.height - rarity_image.height) - 2,
        left=(base_icon_image.width / 2) - (rarity_image.width / 2),
    )

    base_icon_image.save(filename='tmp.png')

    return base_icon_data, saveLocalImageToModel(card, field_name, 'tmp.png')

def generate_memoir(memoir, art_data=None):
    try:
        if not art_data:
            art_field = getattr(memoir, 'art')
            art_data = art_field.read()
        art_image = Image(file=cStringIO.StringIO(art_data))
    except (BlobError, ValueError):
        print('  Art not saved in memoir.')
        return art_data, None

    try:
        border_image = Image(filename='starlight/static/extracts/cards_elements/memoir_border.png')
        rarity_image = Image(filename=u'starlight/static/extracts/cards_elements/{}.png'.format(memoir.rarity))
    except BlobError:
        print('  Memoir layer image(s) not found.')
        return art_data, None

    art_image.resize(width=border_image.width, height=border_image.height)
    art_image.composite(border_image, left=0, top=0)
    rarity_image.transform(resize='x73')
    art_image.composite(rarity_image, top=(art_image.height - rarity_image.height - 19), left=20)

    art_image.save(filename='tmp.png')

    return art_data, saveLocalImageToModel(memoir, 'image', 'tmp.png')

def generate_memoir_icon(memoir, field_name, rank, base_icon_data=None):
    try:
        if not base_icon_data:
            base_icon_field = getattr(memoir, 'base_icon')
            base_icon_data = base_icon_field.read()
        base_icon_image = Image(file=cStringIO.StringIO(base_icon_data))
    except (BlobError, ValueError):
        print('  Base icon not saved in memoir.')
        return base_icon_data, None

    try:
        border_image = Image(filename=u'starlight/static/extracts/cards_elements/memoir_icon_rank{}.png'.format(
            rank))
        rarity_image = Image(filename=u'starlight/static/extracts/cards_elements/icon_rarity{}.png'.format(
        memoir.rarity))
    except BlobError:
        print('  Icon layer image(s) not found.')
        return base_icon_data, None

    base_icon_image.composite(border_image, left=0, top=0)
    base_icon_image.composite(
        rarity_image, top=(base_icon_image.height - rarity_image.height) - 2,
        left=(base_icon_image.width / 2) - (rarity_image.width / 2),
    )

    base_icon_image.save(filename='tmp.png')

    return base_icon_data, saveLocalImageToModel(memoir, field_name, 'tmp.png')

############################################################
# Local news import
############################################################

AUTHORS_MAP = {
    'Revue Starlight EN': 'satsunyan',
    'raide': 'Raide',
    'satsunyan': 'satsunyan',
}

_voice_actresses = list(models.VoiceActress.objects.all().values_list('name', flat=True))

ALL_CHARACTERS_NAMES = (
    TO_CHARACTER_NAME_SWAPPED.values()
) + (
    TO_CHARACTER.values()
) + [
    'Saijou Claudine',
    'Kochou Shizuha',
    'Kanou Misora',
    'Ootsuki Aruru',
    'Ootori Michiru',
    'Liu Meifan',
    'Aijou Karen',
    'Tendou Maya',
]

ALL_VOICE_ACTRESSES_NAMES = (
    _voice_actresses
) + [
    u' '.join(reversed(_name.split(' ')))
    for _name in _voice_actresses
] + (
    TO_VOICE_ACTRESS.keys()
) + (
    TO_VOICE_ACTRESS.values()
) + [
    u' '.join(reversed(_name.split(' ')))
    for _name in TO_VOICE_ACTRESS.keys()
] + [
    u' '.join(reversed(_name.split(' ')))
    for _name in TO_VOICE_ACTRESS.values()
]

MANUAL_IMPORT = [
    'Privacy Policy',
    'Cast / Staff',
    'About RSI',
    'Looking for Volunteers! We need Translators, Contributors and Social Media handlers!',
    'What is Revue Starlight?',
    'Test',
    '',
    'Sample Page',
] + (
    ALL_CHARACTERS_NAMES
) + (
    ALL_VOICE_ACTRESSES_NAMES
)

TAGS_MAPPER = {
    'site-news': 'community',
    'jp_trailers': 'JP',
    'en_trailers': 'WW',
    'revue-starlight-tv-anime': 'anime',
    'event-reports': 'irlevent',
    'starlight-theater': 'irlevent',
    'weiss-schwarz': 'merch',
    'interviews': 'voiceactress',
    'mobage': 'relive',
    'revue-starlight-relive': 'relive',
    'starira': 'relive',
    'latest': 'staff',
    'news': 'staff',
    'starlight-relive': 'relive',
    'my-theater': 'mytheater',
    'event-masterpost': 'event',
    'new-theater-items': 'mytheater',
    'gacha': 'gacha',
    'starira-announcement-stream': 'irlevent',
    'stickers': 'relive',
    'patch-notes': 'relive',
    'theater-items': 'mytheater',
    'my-theater-items': 'mytheater',
    'english-server': 'WW',
    'taiwan-event': 'irlevent',
}

TAGS_VERBOSE_MAPPER = {
    _va: 'voiceactresses'
    for _va in ALL_VOICE_ACTRESSES_NAMES
}
TAGS_VERBOSE_MAPPER.update({
    _va: 'stagegirls'
    for _va in ALL_CHARACTERS_NAMES
})

def importSongs(details, h):
    title = details['wp_post_title'][len('Lyrics - '):]
    romaji_title = None

    if '(' in title:
        romaji_title = title.split('(')[0].strip()
        title = title.split('(')[1].split(')')[0].strip()

    html = details['wp_post_content']
    html = u'<p>{}</p>'.format(html).replace(
        '\n\n', '</p><br><p>'
    ).replace(
        '\n', '</p><p>'
    )
    markdown = h.handle(html)
    markdown = markdown.strip()

    if not markdown:
        return

    # Author
    author_username = details['wp_post_author']
    author_username = AUTHORS_MAP.get(author_username, author_username)
    try:
        author = models.User.objects.filter(username=author_username)[0]
    except IndexError:
        author = create_user(author_username)

    try:
        song = models.Song.objects.filter(name=title)[0]
    except IndexError:
        song = None

    data = {
        'owner_id': author.id,
        'name': title,
    }
    if romaji_title:
        data['romaji_name'] = romaji_title

    # Image

    image_url = None
    if not song or not song.image:
        image_url = markdown.split('![')[1].split('](')[1].split(')')[0].strip()

    # Singers

    singers = []
    try:
        sung_by_parts = markdown.split('Sung by:')[1].split('\n')[0].split(', ')
    except IndexError:
        sung_by_parts = None
    if sung_by_parts:
        for part in sung_by_parts:
            voice_actress_name = part.split('CV: ')[-1].split(')')[0].strip()
            voice_actress_name = TO_VOICE_ACTRESS.get(voice_actress_name, voice_actress_name)
            voice_actress_name_reversed = u' '.join(reversed(voice_actress_name.split(' ')))
            try:
                voice_actress = models.VoiceActress.objects.filter(name=voice_actress_name_reversed)[0]
            except IndexError:
                voice_actress = models.VoiceActress.objects.filter(name=voice_actress_name)[0]
            image = part.split('![](')[1].split(')')[0]
            markdown = markdown.replace(
                u'_![]({})_'.format(image),
                u'![]({}) '.format(voice_actress.stagegirls.all()[0].http_small_image_url),
            )
            singers.append(voice_actress)

    # Credits

    try:
        data['lyricist'] = markdown.split('Lyrics: ')[1].split('\n')[0].strip()
    except IndexError:
        try:
            data['lyricist'] = markdown.split('Lyricist: ')[1].split('\n')[0].strip()
        except IndexError:
            pass

    try:
        data['composer'] = markdown.split('Composer: ')[1].split('\n')[0].strip()
    except IndexError:
        pass

    try:
        data['arranger'] = markdown.split('Lyrics: ')[1].split('\n')[0].strip()
    except IndexError:
        pass

    # Lyrics

    data['m_lyrics'] = markdown.split('[tabby title="Translation"]')[1].split('[tabby')[0].strip()
    data['m_japanese_lyrics'] = markdown.split('[tabby title="Kanji"]')[1].split('[tabby')[0].strip()
    data['m_romaji_lyrics'] = markdown.split('[tabby title="Romaji"]')[1].split('[tabby')[0].strip()

    # Upload images to imgur

    for field_name, value in data.items():
        if field_name.startswith('m_'):
            # Avoid reuploading
            if song and 'https://i.imgur.com/' in getattr(song, field_name):
                data[field_name] = getattr(song, field_name)
            else:
                data[field_name] = _replace_images(data[field_name])
                data[field_name] = data[field_name].replace('\n\n  \n\n', '\n\n<br>\n')

    # Add credit of who translated the lyrics
    data['m_lyrics'] += u'\n\n[Translation by {}]({})'.format(author.username, author.http_item_url)

    # Add or edit song

    if song:
        models.Song.objects.filter(pk=song.pk).update(**data)
        song = models.Song.objects.filter(pk=song.pk)[0]
    else:
        song = models.Song.objects.create(**data)

    # Add singers many to many

    song.singers.add(*singers)

    # Upload image

    try:
        saveImageURLToModel(song, 'image', image_url)
    except:
        pass

    song.save()
    print(details['wp_ID'], song)

TAGS_EXCEPTION = {
    'lyrics': importSongs,
}

def _parse_date(string):
    return timezone.make_aware(
        datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S'),
        timezone.get_default_timezone()
    )

def _upload_to_imgur(url, title=''):
    r = requests.post(
        u'https://api.imgur.com/3/upload.json',
        headers={
	    'Authorization': 'Client-ID {}'.format(django_settings.IMGUR_API_KEY),
	    'Accept': 'application/json',
	},
        data={
            'type': 'URL',
	    'image': urllib.quote(url.encode('utf8'), safe=':/'),
	    'title': title,
	},
    )
    r.raise_for_status()
    return r.json()['data']['link']

def _replace_images(markdown):
    if not getattr(django_settings, 'IMGUR_API_KEY', None):
        return markdown
    for i, part in enumerate(markdown.split('![')):
        if i != 0 and len(part) > 3:
            title = part.split('](')[0]
            url = part.split('](')[1].split(')')[0]
            if not url.startswith('https://i.starlight.academy/'):
                print('    Imgur upload', url)
                imgur_url = _upload_to_imgur(url, title)
                print('      ->', imgur_url)
                markdown = markdown.replace(url, imgur_url)
                time.sleep(5)
    return markdown

def import_news(args):
    author_username = 'Revue_EN'
    try:
        author = models.User.objects.filter(username=author_username)[0]
    except IndexError:
        author = create_user(author_username)

    h = html2text.HTML2Text(bodywidth=0)

    for main_hashtag, csv_file in [
            ('revuestarlight', 'starlight/static/extracts/revuestarlightnews.csv'),
            ('relive', 'starlight/static/extracts/relivenews.csv'),
    ]:
        csv_file = open(csv_file)
        csv_reader = csv.reader(csv_file)

        keys_i = {}
        for i, row in enumerate(csv_reader):

            if i == 0:

                for j, item in enumerate(row):
                    keys_i[item] = j

            else:

                details = {
                    key: row[i].decode("utf-8")
                    for key, i in keys_i.items()
                }

                title = details['wp_post_title']
                type = details['wp_post_type']
                if type in ['attachment', 'revision']:
                    continue
                if title in MANUAL_IMPORT:
                    continue

                # Tags from tags + category
                tags = {
                    'staff': True,
                    main_hashtag: True,
                }
                if title.startswith('[Event]'):
                    tags['event'] = True
                elif title.startswith('[Gacha]'):
                    tags['gacha'] = True
                elif title.startswith('[Event&Gacha]'):
                    tags['event'] = True
                    tags['gacha'] = True

                other_tags = {}
                dont_import_as_activity = False
                for tag in (
                        split_data(details['tx_post_tag'])
                        + split_data(details['tx_category'])
                ):
                    tag_code = tag.split(':')[0]
                    tag_verbose = tag.split(':')[1]
                    if tag_code in TAGS_EXCEPTION:
                        TAGS_EXCEPTION[tag_code](details, h)
                        dont_import_as_activity = True
                        break
                    if tag_code in TAGS_MAPPER:
                        tags[TAGS_MAPPER[tag_code]] = True
                    elif tag_verbose in TAGS_VERBOSE_MAPPER:
                        tags[TAGS_VERBOSE_MAPPER[tag_verbose]] = True
                    else:
                        other_tags[tag_code] = tag_verbose
                if dont_import_as_activity:
                    continue
                tags = join_data(*tags.keys())

                # Prepare invisible tag used to avoid duplicates
                unique_tag = u'[](importid#{id})'.format(id=details['wp_ID'])

                # Check if the activity exists
                try:
                    activity = magi_models.Activity.objects.filter(m_message__endswith=unique_tag)[0]
                except IndexError:
                    activity = None

                # Dates
                date = _parse_date(details['wp_post_date'])
                modification_date = _parse_date(details['wp_post_modified'])

                # Message
                html = details['wp_post_content']
                html = u'<p>{}</p>'.format(html).replace(
                    '\n\n', '</p><br><p>'
                ).replace(
                    '\n', '</p><p>'
                )
                markdown = h.handle(html)
                markdown = markdown.strip()

                if not markdown:
                    continue

                markdown_title = u'### {}\n\n'.format(title)

                # Don't reupload to imgur
                if activity and 'https://i.imgur.com/' in activity.m_message:
                    message = activity.m_message
                else:
                    markdown = _replace_images(markdown)
                    markdown = markdown.replace('\n\n  \n\n', '\n\n<br>\n')

                    message = u'{title}{content}\n\n{unique_tag}'.format(
                        title=markdown_title,
                        content=markdown,
                        unique_tag=unique_tag,
                    )

                # Check if an existing activity doesn't exist with exactly the same title
                try:
                    copy_activity = None
                    copy_activities = list(magi_models.Activity.objects.filter(m_message__startswith=markdown_title))
                    if len(copy_activities) == 1:
                        copy_activity = copy_activities[0]
                    elif len(copy_activities) > 1:
                        print('Multiple activities match!!')
                        print(u','.join([unicode(a.id) for a in copy_activities]))

                except IndexError:
                    copy_activity = None
                if copy_activity:
                    activity = copy_activity

                data = {
                    'owner_id': author.id,
                    'm_message': message,
                    '_cache_message': None,
                    'creation': date,
                    'last_bump': modification_date or date,
                    'i_language': 'en',
                    'c_tags': tags,
                    'archived_by_owner': True,
                }

                if activity:
                    magi_models.Activity.objects.filter(pk=activity.pk).update(**data)
                    activity = magi_models.Activity.objects.filter(pk=activity.pk)[0]
                else:
                    activity = magi_models.Activity.objects.create(**data)
                    activity.creation = data['creation']
                    activity.save()
                print(details['wp_ID'], activity.id, unicode(activity).replace('\n', ''))
                if other_tags:
                    print('     ', other_tags)

        csv_file.close()
