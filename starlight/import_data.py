from __future__ import print_function
from collections import OrderedDict
from magi.import_data import (
    import_generic_item,
    save_item,
    import_data as magi_import_data,
)
from starlight import models

TO_STATISTICS = {
    'hp': 'hp',
    'atk': 'act_power',
    'pdef': 'special_defense',
    'mdef': 'normal_defense',
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

def mapStatistics(prefix):
    def _f(v):
        return {
            u'{}{}'.format(prefix, field_name): v.get(api_field_name, None) or None
            for api_field_name, field_name in TO_STATISTICS.items()
        }
    return _f

def mapTranslatedValues(field_name):
    def _f(v):
        return {
            field_name: v.get('en', None) or v.get('ja', None) or None,
            u'd_{}s'.format(field_name): {
                _l: _t for _l, _t in {
                    'ja': v.get('ja', None) or None,
                    'kr': v.get('ko', None) or None,
                    'zh-hant': v.get('zh_hant', None) or None,
                }.items() if _t } or None,
        }
    return _f

def mapSkills(skills):
    added_acts = []
    for skill_name, details in skills.items():
        details['i_type'] = TO_SKILL_TYPE[skill_name]
        if details['i_type']:
            act_unique_data, act_data, not_in_fields = import_generic_item({
                'model': models.Act,
                'unique_fields': [
                    'name',
                    'description',
                ],
                'fields': [
                    'i_type',
                    'cost',
                ],
                'mapping': {
                    'name': mapTranslatedValues('name'),
                    'description': mapTranslatedValues('description'),
                    'details': 'j_details',
                },
                'ignored_fields': [
                    'id',
                    'attribute_id', # same as card
                    'icon_id',
                    'sequence_id',
                ],
            }, details)
            print('- Ignored:', not_in_fields)
            item = save_item(models.Act, act_unique_data, act_data, print, unique_together=True)
            if item:
                added_acts.append(item)
    return ('acts', added_acts)

IMPORT_CONFIGURATION = OrderedDict()

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
    'ignored_fields': [
        'cost', # value can be determined by rarity

        # Todo: what is this?
        'material_exp',
    ],
}

def import_data(local=False, to_import=None, log_function=print):
    magi_import_data(
        None, IMPORT_CONFIGURATION, results_location=None,
        local=local, to_import=to_import, log_function=log_function,
    )
