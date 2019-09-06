# -*- coding: utf-8 -*-
from __future__ import print_function
import cStringIO, csv, datetime, html2text, requests, time, urllib, os
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
    FilterByMode,
    filterByTranslatedValue,
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

API_BASE_URL = u'http://beta.karen.makoo.eu/api/json/'
ASSET_BASE_URL = u'http://beta.karen.makoo.eu/assets/'

REQUEST_OPTIONS = {
    'headers': {
        'X-Karen-API-Header': getattr(django_settings, 'KAREN_API_TOKEN', None),
    },
}

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

def findAct(model, unique_data, data, manytomany, dictionaries):
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
    global global_verbose
    added_acts = []
    for skill_name, item in skills.items():
        item['i_type'] = TO_SKILL_TYPE[skill_name]
        if item['i_type']:
            act_unique_data, act_data, not_in_fields = import_generic_item(ACT_IMPORT_CONFIGURATION, item)
            if global_verbose:
                print('- Ignored:', not_in_fields)
            item = save_item(
                ACT_IMPORT_CONFIGURATION, act_unique_data, act_data,
                print, json_item=item, verbose=global_verbose,
            )
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

def baseCardAfterSave(details, item, json_item):
    # Check if it's available in English version based on presence of all translations
    available_in_ww = True
    for term in ['name', 'description', 'profile', 'get_message']:
        for language in ['en', 'ko', 'zh_hant']:
            if not json_item.get(term, {}).get(language, None):
                available_in_ww = False
                break
    if available_in_ww and not item.ww_release_date:
        item.ww_release_date = timezone.now()
        item.save()
    # Add Japanese release date as today if no release date has been saved
    if not item.jp_release_date:
        item.jp_release_date = timezone.now()
        item.save()

def memoirCallbackEnd():
    # Auto calculate min_level and max_level from base and delta
    for memoir in models.Memoir.objects.all():
        calculateMemoirStatistics(memoir)
        memoir.save()

TO_SONG_CREDIT = {
    'en': {
        'Lyrics': ['lyricist'],
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
    if not item.image:
        url = u'{}jp/res/item_root/music_coverart/27_{}.png'.format(ASSET_BASE_URL, json_item['id'])
        saveImageURLToModel(item, 'image', url, request_options=REQUEST_OPTIONS)
        item.save()

IMPORT_CONFIGURATION = OrderedDict()

IMPORT_CONFIGURATION['stagegirls'] = {
    'model': models.StageGirl,
    'endpoint': 'chara',
    'results_location': ['entries'],
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
    'endpoint': 'dress',
    'results_location': ['entries'],
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
    'callback_after_save': baseCardAfterSave,
}

IMPORT_CONFIGURATION['memoirs'] = {
    'model': models.Memoir,
    'endpoint': 'equip',
    'results_location': ['entries'],
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
    'callback_after_save': baseCardAfterSave,
}

def findSong(model, unique_data, data, manytomany, dictionaries):
    # Find from Japanese name
    japanese_name = dictionaries.get('d_names', {}).get('ja', None)
    if japanese_name:
        try:
            return filterByTranslatedValue(
                model.objects.all(), 'name',
                language='ja',
                value=japanese_name,
                mode=FilterByMode.Exact,
            )[0]
        except IndexError:
            pass
    # Fallback to English name
    if unique_data.get('name', None):
        return model.objects.filter(**unique_data)[0]
    return None

IMPORT_CONFIGURATION['songs'] = {
    'model': models.Song,
    'results_location': ['entries'],
    'find_existing_item': findSong,
    'endpoint': 'music',
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

global_verbose = True

def import_data(local=False, to_import=None, log_function=print, verbose=False):
    global global_verbose
    global_verbose = verbose
    if to_import and 'images' in to_import:
        import_images([arg for arg in to_import if arg != 'images'])
    else:
        magi_import_data(
            API_BASE_URL, IMPORT_CONFIGURATION, results_location=None,
            local=local, to_import=to_import, log_function=log_function,
            request_options=REQUEST_OPTIONS, verbose=verbose,
        )

############################################################
# Images import
############################################################

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) + u'/'

# This is a temporary feature which in the future will be
# replaced by images downloaded directly from the API.
def import_images(to_import=None):
    global global_verbose
    if not to_import or 'cards' in to_import:
        for card in models.Card.objects.all():
            needs_save = []
            errors = []
            # Art
            art_data = None
            if not card.art or 'reload' in to_import:
                url = u'{}dlc/res/dress/cg/{}/image.png'.format(ASSET_BASE_URL, card.number)
                art_data, art = saveImageURLToModel(
                    card, 'art', url, return_data=True, request_options=REQUEST_OPTIONS)
                if art is None:
                    errors.append('  Art file not found:' + url)
                else:
                    needs_save.append('art')
            # Image
            if not card.image or 'art' in needs_save:
                art_data, image, new_errors = generate_card(card, art_data=art_data)
                errors += new_errors
                if image is not None:
                    needs_save.append('image')
            # Base icon
            base_icon_data = None
            if not card.base_icon or 'reload' in to_import:
                url = u'{}jp/res/item_root/large/1_{}.png'.format(ASSET_BASE_URL, card.number)
                base_icon_data, icon = saveImageURLToModel(
                    card, 'base_icon', url, return_data=True, request_options=REQUEST_OPTIONS)
                if icon is None:
                    errors.append('  Icon file not found:' + url)
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
                        base_icon_data, icon, new_errors = generate_card_icon(
                            card, field_name, rank, rarity, base_icon_data=base_icon_data)
                        errors += new_errors
                        if icon is not None:
                            needs_save.append(field_name)
            # Transparent
            if not card.transparent or 'reload' in to_import:
                url = u'{url}dlc/res/battle/model/{n}/cutin/cutin_special_{n}.png'.format(
                    url=ASSET_BASE_URL, n=card.number)
                transparent = saveImageURLToModel(card, 'transparent', url, request_options=REQUEST_OPTIONS)
                if transparent is None:
                    errors.append('  Transparent file not found:' + url)
                else:
                    needs_save.append('transparent')

            if global_verbose and not needs_save and not errors:
                print('Nothing to import for for card #{} {}'.format(card.number, card))
            if errors:
                print('Error(s) while importing images for card #{} {}'.format(card.number, card))
                for error in errors:
                    print(error)
            if needs_save:
                print('Importing images for card #{} {}'.format(card.number, card))
                card.save()
                print('  Saved:', needs_save)

    if not to_import or 'memoirs' in to_import:
        for memoir in models.Memoir.objects.all():
            errors = []
            needs_save = []
            # Art
            art_data = None
            if not memoir.art or 'reload' in to_import:
                url = u'{}dlc/res/equip/cg/{}/image.png'.format(ASSET_BASE_URL, memoir.number)
                art_data, art = saveImageURLToModel(
                    memoir, 'art', url, return_data=True, request_options=REQUEST_OPTIONS)
                if art is None:
                    errors.append('  Art file not found:' + url)
                else:
                    needs_save.append('art')
            # Image
            if not memoir.image or 'art' in needs_save:
                art_data, image, new_errors = generate_memoir(memoir, art_data=art_data)
                errors += new_errors
                if image is not None:
                    needs_save.append('image')
            # Base icon
            base_icon_data = None
            if not memoir.base_icon or 'reload' in to_import:
                url = u'{}jp/res/item_root/large/2_{}.png'.format(ASSET_BASE_URL, memoir.number)
                base_icon_data, icon = saveImageURLToModel(
                    memoir, 'base_icon', url, return_data=True, request_options=REQUEST_OPTIONS)
                if icon is None:
                    errors.append('  Icon file not found:' + url)
                else:
                    needs_save.append('base_icon')
            # Generated icons
            for rank in [1, 2, 3, 4, 5]:
                if rank == 5:
                    field_name = 'icon'
                else:
                    field_name = 'rank{rank}_icon'.format(rank=rank)
                if not getattr(memoir, field_name) or 'reload' in to_import:
                    base_icon_data, icon, new_errors = generate_memoir_icon(
                        memoir, field_name, rank, base_icon_data=base_icon_data)
                    errors += new_errors
                    if icon is not None:
                        needs_save.append(field_name)

            if global_verbose and not needs_save and not errors:
                print('Nothing to import for for memoir #{} {}'.format(memoir.number, memoir))
            if errors:
                print('Error(s) while importing images for memoir #{} {}'.format(memoir.number, memoir))
                for error in errors:
                    print(error)
            if needs_save:
                print('Importing images for memoir #{} {}'.format(memoir.number, memoir))
                memoir.save()
                print('  Saved:', needs_save)

def generate_card(card, art_data=None):
    errors = []
    try:
        if not art_data:
            art_field = getattr(card, 'art')
            art_data = art_field.read()
        art_image = Image(file=cStringIO.StringIO(art_data))
    except (BlobError, ValueError):
        errors.append('  Art not saved in card.')
        return art_data, None, errors

    try:
        border_image = Image(filename=BASE_DIR + 'starlight/static/extracts/cards_elements/card_border.png')
        element_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(card.element))
        rarity_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(card.rarity))
        position_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(card.position))
    except BlobError:
        errors.append('  Cards layer image(s) not found.')
        return art_data, None, errors

    art_image.resize(width=border_image.width, height=border_image.height)
    art_image.composite(border_image, left=0, top=0)
    art_image.composite(element_image, left=(art_image.width - element_image.width), top=0)
    art_image.composite(position_image, top=element_image.height, left=(art_image.width - position_image.width - 18))
    art_image.composite(rarity_image, top=(art_image.height - rarity_image.height - 22), left=22)

    art_image.save(filename=BASE_DIR + 'tmp.png')

    return art_data, saveLocalImageToModel(card, 'image', 'tmp.png'), errors

def generate_card_icon(card, field_name, rank, rarity, base_icon_data=None):
    errors = []
    try:
        if not base_icon_data:
            base_icon_field = getattr(card, 'base_icon')
            base_icon_data = base_icon_field.read()
        base_icon_image = Image(file=cStringIO.StringIO(base_icon_data))
    except (BlobError, ValueError):
        errors.append('  Base icon not saved in card.')
        return base_icon_data, None, errors

    try:
        border_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/card_icon_rank{}.png'.format(rank))
        position_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(card.position))
        element_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(card.element))
        rarity_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/icon_rarity{}.png'.format(rarity))
    except BlobError:
        errors.append('  Icon layer image(s) not found.')
        return base_icon_data, None, errors
    base_icon_image.composite(border_image, left=0, top=0)
    position_image.transform(resize='x20')
    base_icon_image.composite(position_image, top=34, left=4)
    element_image.resize(width=37, height=37)
    base_icon_image.composite(element_image, top=1, left=1)
    base_icon_image.composite(
        rarity_image, top=(base_icon_image.height - rarity_image.height) - 2,
        left=(base_icon_image.width / 2) - (rarity_image.width / 2),
    )

    base_icon_image.save(filename=BASE_DIR + 'tmp.png')

    return base_icon_data, saveLocalImageToModel(card, field_name, 'tmp.png'), errors

def generate_memoir(memoir, art_data=None):
    errors = []
    try:
        if not art_data:
            art_field = getattr(memoir, 'art')
            art_data = art_field.read()
        art_image = Image(file=cStringIO.StringIO(art_data))
    except (BlobError, ValueError):
        errors.append('  Art not saved in memoir.')
        return art_data, None, errors

    try:
        border_image = Image(filename=BASE_DIR + 'starlight/static/extracts/cards_elements/memoir_border.png')
        rarity_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/{}.png'.format(memoir.rarity))
    except BlobError:
        errors.append('  Memoir layer image(s) not found.')
        return art_data, None, errors

    art_image.resize(width=border_image.width, height=border_image.height)
    art_image.composite(border_image, left=0, top=0)
    rarity_image.transform(resize='x73')
    art_image.composite(rarity_image, top=(art_image.height - rarity_image.height - 19), left=20)

    art_image.save(filename=BASE_DIR + 'tmp.png')

    return art_data, saveLocalImageToModel(memoir, 'image', 'tmp.png'), errors

def generate_memoir_icon(memoir, field_name, rank, base_icon_data=None):
    errors = []
    try:
        if not base_icon_data:
            base_icon_field = getattr(memoir, 'base_icon')
            base_icon_data = base_icon_field.read()
        base_icon_image = Image(file=cStringIO.StringIO(base_icon_data))
    except (BlobError, ValueError):
        errors.append('  Base icon not saved in memoir.')
        return base_icon_data, None, errors

    try:
        border_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/memoir_icon_rank{}.png'.format(
            rank))
        rarity_image = Image(filename=BASE_DIR + u'starlight/static/extracts/cards_elements/icon_rarity{}.png'.format(
        memoir.rarity))
    except BlobError:
        errors.append('  Icon layer image(s) not found.')
        return base_icon_data, None, errors

    base_icon_image.composite(border_image, left=0, top=0)
    base_icon_image.composite(
        rarity_image, top=(base_icon_image.height - rarity_image.height) - 2,
        left=(base_icon_image.width / 2) - (rarity_image.width / 2),
    )

    base_icon_image.save(filename=BASE_DIR + 'tmp.png')

    return base_icon_data, saveLocalImageToModel(memoir, field_name, 'tmp.png'), errors
