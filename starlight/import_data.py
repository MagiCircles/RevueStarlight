from __future__ import print_function
import cStringIO, datetime
from collections import OrderedDict
from wand.image import Image
from wand.exceptions import BlobError
from magi import urls # loads context
from magi.import_data import (
    import_generic_item,
    save_item,
    import_data as magi_import_data,
)
from magi.utils import (
    saveLocalImageToModel,
    localImageToImageFile,
    getAstrologicalSign,
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
    4: 'cloud',
    5: 'moon',
    6: 'space',
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
            item = save_item(ACT_IMPORT_CONFIGURATION, act_unique_data, act_data, print)
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
    'dont_erase_existing_value_fields': [
        'name',
        'profile',
    ],
    'ignored_fields': [
        'cost', # value can be determined by rarity

        # Todo: what is this?
        'material_exp',
    ],
    'callback_end': memoirCallbackEnd,
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
