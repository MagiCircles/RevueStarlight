# -*- coding: utf-8 -*-
from __future__ import division
from collections import OrderedDict
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _, string_concat
from magi.abstract_models import BaseAccount
from magi.item_model import MagiModel, i_choices, getInfoFromChoices
from magi.utils import (
    ColorField,
    getAge,
    getStaffConfiguration,
    ordinalNumber,
    staticImageURL,
    uploadItem,
    uploadTiny,
    upload2x,
    uploadTthumb,
    YouTubeVideoField,
)
from starlight.django_translated import t
from starlight.utils import (
    displayNameHTML,
    getMaxStatistic,
)

############################################################
############################################################
# Models utils and variables
############################################################
############################################################

############################################################
# Languages

NON_LATIN_LANGUAGES = [
    l for l in django_settings.LANGUAGES
    if l[0] in ['ja', 'ru', 'zh-hans', 'zh-hant', 'kr']
]
LANGUAGES_CANT_SPEAK_ENGLISH = [
    l for l in django_settings.LANGUAGES
    if l[0] in ['ja', 'zh-hans', 'zh-hant', 'kr']
]
ALL_ALT_LANGUAGES = [
    l for l in django_settings.LANGUAGES
    if l[0] != 'en'
]

############################################################
# Versions

VERSIONS = OrderedDict((
    ('JP', {
        'translation': _('Japanese version'),
        'image': 'ja',
        'prefix': 'jp_',
        'timezone': 'Asia/Tokyo',
    }),
    ('WW', {
        'translation': _('Worldwide version'),
        'image': 'world',
        'prefix': 'ww_',
        'timezone': 'UTC',
    }),
))

VERSION_CHOICES = [(_name, _info['translation']) for _name, _info in VERSIONS.items()]

LANGUAGES_TO_VERSIONS = {
    'ja': 'JP',
}
DEFAULT_VERSION = 'WW'

############################################################
# Elements

ELEMENTS = OrderedDict([
    ('flower', {
        'translation': _('Flower'),
        'japanese': u'花',
        'color': '#F0484D',
        'light_color': '#FFD7CE',
        'resists_against': 'wind',
        'weak_against': 'snow',
    }),
    ('wind', {
        'translation': _('Wind'),
        'japanese': u'風',
        'color': '#30AB49',
        'light_color': '#AEFFBD',
        'resists_against': 'snow',
        'weak_against': 'flower',
    }),
    ('snow', {
        'translation': _('Snow'),
        'japanese': u'雪',
        'color': '#0072A6',
        'light_color': '#99EFFF',
        'resists_against': 'flower',
        'weak_against': 'wind',
    }),
    ('cloud', {
        'translation': _('Cloud'),
        'japanese': u'雲',
        'color': '#F3608A',
        'light_color': '#FFCED7',
        'resists_against': 'moon',
        'weak_against': 'cosmos',
    }),
    ('moon', {
        'translation': _('Moon'),
        'japanese': u'月',
        'color': '#F9AA12',
        'light_color': '#FBFEC8',
        'resists_against': 'cosmos',
        'weak_against': 'cloud',
    }),
    ('cosmos', {
        'translation': _('Cosmos'),
        'japanese': u'宙',
        'color': '#794A92',
        'light_color': '#E5D4FF',
        'resists_against': 'cloud',
        'weak_against': 'moon',
    }),
    ('dream', {
        'translation': _('Dream'),
        'japanese': u'夢',
        'color': '#38495A',
        'light_color': '#BDD5DE',
        'resists_against': None,
        'weak_against': None,
    }),
])

ELEMENT_CHOICES = [(_name, _info['translation']) for _name, _info in ELEMENTS.items()]

############################################################
# Astrological signs

ASTROLOGICAL_SIGN_CHOICES = (
    ('leo', _('Leo')),
    ('aries', _('Aries')),
    ('libra', _('Libra')),
    ('virgo', _('Virgo')),
    ('scorpio', _('Scorpio')),
    ('capricorn', _('Capricorn')),
    ('pisces', _('Pisces')),
    ('gemini', _('Gemini')),
    ('cancer', _('Cancer')),
    ('sagittarius', _('Sagittarius')),
    ('aquarius', _('Aquarius')),
    ('taurus', _('Taurus')),
)

############################################################
############################################################
# MagiCircles' required models
############################################################
############################################################

############################################################
# Account

class Account(BaseAccount):
    class Meta:
        pass

############################################################
############################################################
# Revue Starlight models
############################################################
############################################################

############################################################
# Voice Actress

class VoiceActress(MagiModel):
    collection_name = 'voiceactress'

    owner = models.ForeignKey(User, related_name='added_voiceactresses')

    name = models.CharField(_('Name'), max_length=100, unique=True, db_index=True)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)
    japanese_name = property(lambda _s: _s.names.get('ja', _s.name))

    image = models.ImageField(_('Image'), upload_to=uploadItem('voiceactress'), null=True)
    _tthumbnail_image = models.ImageField(null=True, upload_to=uploadTthumb('voiceactress'))
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('voiceactress'))

    birthday = models.DateField(_('Birthday'), null=True)
    display_birthday = property(lambda _s: date_format(_s.birthday, format='DATE_FORMAT', use_l10n=True))
    age = property(lambda _s: getAge(_s.birthday))
    display_age = property(lambda _s: getAge(_s.birthday, formatted=True))

    ASTROLOGICAL_SIGN_CHOICES = ASTROLOGICAL_SIGN_CHOICES
    i_astrological_sign = models.PositiveIntegerField(
        _('Astrological sign'), choices=i_choices(ASTROLOGICAL_SIGN_CHOICES), null=True)
    astrological_sign_image_url = property(
        lambda _s: staticImageURL(_s.i_astrological_sign, folder='i_astrological_sign', extension='png'))

    BLOOD_CHOICES = (
        'O',
        'A',
        'B',
        'AB',
    )
    i_blood = models.PositiveIntegerField(_('Blood type'), choices=i_choices(BLOOD_CHOICES), null=True)

    height = models.PositiveIntegerField(_('Height'), null=True, default=None)
    display_height = property(lambda _s: u'{} cm'.format(_s.height))

    specialty = models.CharField(_('Specialty'), max_length=100, null=True)
    SPECIALTYS_CHOICES = ALL_ALT_LANGUAGES
    d_specialtys = models.TextField(_('Specialty'), null=True)

    hobbies = models.CharField(_('Hobbies'), max_length=100, null=True)
    HOBBIESS_CHOICES = ALL_ALT_LANGUAGES
    d_hobbiess = models.TextField(_('Hobbies'), null=True)

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

    video = YouTubeVideoField(_('Video'), null=True)

    ############################################################
    # Reverse relations

    reverse_related = [
        { 'field_name': 'stagegirls', 'verbose_name': _('Stage girl') },
        { 'field_name': 'links', 'verbose_name': _('Social media'), 'max_per_line': None },
    ]

    ############################################################
    # Views utils

    display_name = property(displayNameHTML)

    top_image_list = property(lambda _s: _s.image_thumbnail_url)
    image_for_prefetched = property(lambda _s: _s.image_thumbnail_url)

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
# Voice Actress link

class VoiceActressLink(MagiModel):
    collection_name = 'voiceactresslink'

    owner = models.ForeignKey(User, related_name='added_voiceactresslinks')

    voice_actress = models.ForeignKey(
        VoiceActress, verbose_name=_('Voice actress'), related_name='links',
        on_delete=models.CASCADE, db_index=True,
    )

    name = models.CharField(_('Platform'), max_length=100)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Platform'), null=True)

    url = models.CharField(_('URL'), max_length=100)

    ############################################################
    # Views utils

    display_item_url = property(lambda _s: _s.url)

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
# School

class School(MagiModel):
    collection_name = 'school'

    owner = models.ForeignKey(User, related_name='added_schools')

    name = models.CharField(_('Name'), max_length=100, unique=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)

    image = models.ImageField(_('Image'), upload_to=uploadItem('school'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('school'))

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

    ############################################################
    # Reverse relations

    reverse_related = [
        {
            'field_name': 'students',
            'url': 'stagegirls',
            'verbose_name': _('Students'),
            'max_per_line': None,
        },
    ]

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
# Stage girl

def _to_year_choices():
    return [
        ('first', _(u'{nth} year').format(nth=_(ordinalNumber(1)))),
        ('second', _(u'{nth} year').format(nth=_(ordinalNumber(2)))),
        ('third', _(u'{nth} year').format(nth=_(ordinalNumber(3)))),
    ]

class StageGirl(MagiModel):
    collection_name = 'stagegirl'

    owner = models.ForeignKey(User, related_name='added_stagegirls')

    name = models.CharField(_('Name'), max_length=100, unique=True)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)
    japanese_name = property(lambda _s: _s.names.get('ja', _s.name))
    first_name = property(lambda _s: _s.name.split(' ')[-1])

    image = models.ImageField(_('Image'), upload_to=uploadItem('stagegirl'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('stagegirl'))

    small_image = models.ImageField(
        upload_to=uploadItem('stagegirl/s'), null=True,
        help_text='Map pins, favorite characters on profile and character selectors.')

    voice_actress = models.ForeignKey(
        VoiceActress, verbose_name=_('Voice actress'), related_name='stagegirls',
        null=True, on_delete=models.SET_NULL,
        db_index=True,
    )

    school = models.ForeignKey(
        School, verbose_name=_('School'), related_name='students',
        db_index=True,
    )

    YEAR_CHOICES = _to_year_choices()
    i_year = models.PositiveIntegerField(_('School year'), choices=i_choices(YEAR_CHOICES), null=True)
    to_year_choices = classmethod(lambda _s: _to_year_choices())
    to_t_year = classmethod(lambda _s, _i: dict(i_choices(_to_year_choices())).get(_i, None))

    birthday = models.DateField(_('Birthday'), null=True, help_text='The year will be ignored.')
    display_birthday = property(lambda _s: date_format(_s.birthday, format='MONTH_DAY_FORMAT', use_l10n=True))

    ASTROLOGICAL_SIGN_CHOICES = ASTROLOGICAL_SIGN_CHOICES
    i_astrological_sign = models.PositiveIntegerField(
        _('Astrological sign'), choices=i_choices(ASTROLOGICAL_SIGN_CHOICES), null=True)
    astrological_sign_image_url = property(
        lambda _s: staticImageURL(_s.i_astrological_sign, folder='i_astrological_sign', extension='png'))

    color = ColorField(_('Color'), null=True)

    # todo: department, class?

    weapon = models.CharField(
        _('Weapon'), max_length=100, null=True,
        help_text='Example: Possibility of Puberty',
    )
    WEAPONS_CHOICES = ALL_ALT_LANGUAGES
    d_weapons = models.TextField(_('Weapon'), null=True)

    weapon_type = models.CharField(
        _('Weapon'), max_length=100, null=True,
        help_text='Example: Saber',
    )
    WEAPON_TYPES_CHOICES = ALL_ALT_LANGUAGES
    d_weapon_types = models.TextField(_('Weapon'), null=True)

    favorite_food = models.CharField(_('Liked food'), max_length=100, null=True)
    FAVORITE_FOODS_CHOICES = ALL_ALT_LANGUAGES
    d_favorite_foods = models.TextField(_('Liked food'), null=True)

    least_favorite_food = models.CharField(_('Disliked food'), max_length=100, null=True)
    LEAST_FAVORITE_FOODS_CHOICES = ALL_ALT_LANGUAGES
    d_least_favorite_foods = models.TextField(_('Disliked food'), null=True)

    likes = models.CharField(_('Likes'), max_length=100, null=True)
    LIKESS_CHOICES = ALL_ALT_LANGUAGES
    d_likess = models.TextField(_('Likes'), null=True)

    dislikes = models.CharField(_('Dislikes'), max_length=100, null=True)
    DISLIKESS_CHOICES = ALL_ALT_LANGUAGES
    d_dislikess = models.TextField(_('Dislikes'), null=True)

    hobbies = models.CharField(_('Hobbies'), max_length=100, null=True)
    HOBBIESS_CHOICES = ALL_ALT_LANGUAGES
    d_hobbiess = models.TextField(_('Hobbies'), null=True)

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

    video = YouTubeVideoField(_('Video'), null=True)

    ############################################################
    # Images settings

    tinypng_settings = {
        'small_image': {
            'resize': 'fit',
            'width': 80,
            'height': 80,
        }
    }

    ############################################################
    # Reverse relations

    reverse_related = [
        { 'field_name': 'cards', 'verbose_name': _('Cards') },
    ]

    ############################################################
    # Views utils

    display_name = property(displayNameHTML)

    image_for_prefetched = property(lambda _s: _s.small_image_url)

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
# Staff

class Staff(MagiModel):
    collection_name = 'staff'

    owner = models.ForeignKey(User, related_name='added_staff')

    name = models.CharField(_('Name'), max_length=100)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)
    japanese_name = property(lambda _s: _s.names.get('ja', _s.name))

    role = models.CharField(_('Role'), max_length=100, db_index=True)
    ROLES_CHOICES = ALL_ALT_LANGUAGES
    d_roles = models.TextField(_('Role'), null=True)

    social_media_url = models.CharField(_('Social media'), max_length=100, null=True)

    importance = models.IntegerField(
        'Importance', default=0, db_index=True,
        help_text='Allows to re-order how the staff appear. Highest number shows first.',
    )

    ############################################################
    # Views utils

    display_name = property(displayNameHTML)

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
############################################################
# Relive models
############################################################
############################################################

############################################################
# Act

class Act(MagiModel):
    collection_name = 'act'
    owner = models.ForeignKey(User, related_name='added_acts')

    TYPES = OrderedDict([
        ('basic', {
            'translation': _('Basic'),
        }),
        ('climax', {
            'translation': _('Climax'),
        }),
        ('auto', {
            'translation': _('Auto'),
        }),
        ('finishing', {
            'translation': _('Finishing'),
        }),
        ('auto', {
            'translation': _('Auto'),
        }),
        ('auto', {
            'translation': _('Auto'),
        }),
    ])
    TYPE_CHOICES = [(_name, _info['translation']) for _name, _info in TYPES.items()]
    i_type = models.PositiveIntegerField(_('Type'), choices=i_choices(TYPE_CHOICES))

    name = models.CharField(_('Title'), max_length=100, db_index=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Title'), null=True)

    template = models.CharField(_('Template'), max_length=100, db_index=True)
    TEMPLATES_CHOICES = ALL_ALT_LANGUAGES
    d_templates = models.TextField(_('Template'), null=True)

    image = models.ImageField(_('Image'), upload_to=uploadItem('card'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('card'))

    cost = models.PositiveIntegerField('AP', default=1)

    #affected_attribute =

############################################################
# Abstract: Base card

class BaseCard(MagiModel):
    collection_name = 'card'
    owner = models.ForeignKey(User, related_name='added_%(class)ss')

    ############################################################
    # Basic details: Rarity, elements, ...

    number = models.PositiveIntegerField(_('ID'), unique=True, primary_key=True)
    stage_girl = models.ForeignKey(StageGirl, verbose_name=_('Stage girl'), related_name='%(class)ss')

    name = models.CharField(_('Title'), max_length=100, null=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Title'), null=True)

    RARITIES = OrderedDict([
        (1, {
            'translation': u'★',
            'cost': getStaffConfiguration('rarity_1_cost', 2),
        }),
        (2, {
            'translation': u'★★',
            'cost': getStaffConfiguration('rarity_2_cost', 6),
        }),
        (3, {
            'translation': u'★★★',
            'cost': getStaffConfiguration('rarity_3_cost', 9),
        }),
        (4, {
            'translation': u'★★★★',
            'cost': getStaffConfiguration('rarity_4_cost', 12),
        }),
        (5, {
            'translation': u'★★★★★',
            'cost': getStaffConfiguration('rarity_5_cost', 12),
        }),
        (6, {
            'translation': u'★★★★★★',
            'cost': getStaffConfiguration('rarity_6_cost', 12),
        }),
    ])
    RARITY_CHOICES = [(_name, _info['translation']) for _name, _info in RARITIES.items()]
    RARITY_WITHOUT_I_CHOICES = True
    i_rarity = models.PositiveIntegerField(_('Rarity'), choices=RARITY_CHOICES, db_index=True)
    rarity_image = property(lambda _s: staticImageURL(_s.i_rarity, folder='i_rarity', extension='png'))
    cost = property(getInfoFromChoices('rarity', RARITIES, 'cost'))

    ELEMENT_CHOICES = ELEMENT_CHOICES
    i_element = models.PositiveIntegerField(_('Element'), choices=i_choices(ELEMENT_CHOICES), db_index=True)
    element_image = property(lambda _s: staticImageURL(_s.element, folder='color', extension='png'))
    element_color = property(getInfoFromChoices('element', ELEMENTS, 'color'))
    element_resists_against = property(getInfoFromChoices('element', ELEMENTS, 'resists_against'))
    element_resists_against_image = property(lambda _s: staticImageURL(
        _s.element_resists_against, folder='color', extension='png'))
    element_weak_against = property(getInfoFromChoices('element', ELEMENTS, 'weak_against'))
    element_weak_against_image = property(lambda _s: staticImageURL(
        _s.element_weak_against, folder='color', extension='png'))

    DAMAGE_CHOICES = (
        ('normal', _('Normal')),
        ('special', _('Special')),
    )
    i_damage = models.PositiveIntegerField(_('Damage'), choices=i_choices(DAMAGE_CHOICES), default=0)
    damage_icon_image = property(lambda _s: staticImageURL(_s.damage, folder='i_damage', extension='png'))
    damage_image = property(lambda _s: staticImageURL(_s.i_damage, folder='i_damage', extension='png'))

    POSITION_CHOICES = (
        ('rear', _('Rear')),
        ('center', _('Center')),
        ('front', _('Front')),
    )
    i_position = models.PositiveIntegerField(_('Position'), choices=i_choices(POSITION_CHOICES), default=1)
    position_image = property(lambda _s: staticImageURL(_s.i_position, folder='i_position', extension='png'))

    ROLES_CHOICES = (
        ('anti-tank', _('Anti-tank')),
        ('assassin', _('Assassin')),
        ('attacker', _('Attacker')),
        ('burn', _('Burn')),
        ('debuffer', _('Debuffer')),
        ('defender', _('Defender')),
        ('disabler', _('Disabler')),
        ('healer', _('Healer')),
        ('nuker', _('Nuker')),
        ('poison', _('Poison')),
        ('special-defender', _('Special defender')),
        ('special-defense-tank', _('Special defense tank')),
        ('support', _('Support')),
        ('tank', _('Tank')),
    )
    c_roles = models.TextField(_('Roles'), null=True)

    limited = models.BooleanField(_('Limited'), default=False)

    ############################################################
    # Images

    image = models.ImageField(_('Image'), upload_to=uploadItem('card'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('card'))
    _2x_image = models.ImageField(null=True, upload_to=upload2x('card'))

    icon = models.ImageField(_('Icon'), upload_to=uploadItem('card/icon'), null=True)
    _original_icon = models.ImageField(null=True, upload_to=uploadTiny('card/icon'))

    art = models.ImageField(_('Art'), upload_to=uploadItem('card/art'), null=True)
    _original_art = models.ImageField(null=True, upload_to=uploadTiny('card/art'))
    _tthumbnail_art = models.ImageField(null=True, upload_to=uploadTthumb('card/art'))
    _2x_art = models.ImageField(null=True, upload_to=upload2x('card/art'))

    transparent = models.ImageField(_('Transparent'), upload_to=uploadItem('card/transparent'), null=True)
    _original_transparent = models.ImageField(null=True, upload_to=uploadTiny('card/transparent'))
    _tthumbnail_transparent = models.ImageField(null=True, upload_to=uploadTthumb('card/transparent'))
    _2x_transparent = models.ImageField(null=True, upload_to=upload2x('card/transparent'))

    live2d_model_package = models.FileField(upload_to=uploadItem('card/live2d'), null=True)

    tinypng_settings = {
        'art': {
            'resize': 'scale',
            'height': 402,
        },
    }

    ############################################################
    # Statistics fields

    base_hp = models.PositiveIntegerField(_('HP'), null=True)
    base_act_power = models.PositiveIntegerField(_('ACT Power'), null=True)
    base_normal_defense = models.PositiveIntegerField(_('Normal defense'), null=True)
    base_special_defense = models.PositiveIntegerField(_('Special defense'), null=True)
    base_agility = models.PositiveIntegerField(_('Agility'), null=True)

    delta_hp = models.PositiveIntegerField(string_concat(u'Δ ', _('HP')), null=True)
    delta_act_power = models.PositiveIntegerField(string_concat(u'Δ ', _('ACT Power')), null=True)
    delta_normal_defense = models.PositiveIntegerField(string_concat(u'Δ ', _('Normal defense')), null=True)
    delta_special_defense = models.PositiveIntegerField(string_concat(u'Δ ', _('Special defense')), null=True)
    delta_agility = models.PositiveIntegerField(string_concat(u'Δ ', _('Agility')), null=True)

    ############################################################
    # Statistics utils

    STATISTICS_FIELDS = ['hp', 'act_power', 'normal_defense', 'special_defense', 'agility']
    STATISTICS_PREFIXES = OrderedDict([
        ('base_', _('Base')),
        ('delta_', u'Δ'),
    ])
    ALL_STATISTICS_FIELDS = [
        u'{}{}'.format(_prefix, _statistic)
        for _statistic in STATISTICS_FIELDS
        for _prefix in STATISTICS_PREFIXES.keys()
    ]

    def get_statistic(self, statistic, prefix):
        return getattr(self, u'{}{}'.format(prefix, statistic)) or 0

    def statistic_percent(self, statistic, prefix):
        return (
            self.get_statistic(statistic, prefix) / getMaxStatistic(statistic)
        ) * 100

    def display_statistic(self, statistic, prefix):
        field_name = u'{}{}'.format(prefix, statistic)
        return u"""
	<div class="row">
	  <div class="col-xs-4 text-left"><span class="stat-label-{statistic}">{verbose_name}</span></div>
	  <div class="col-xs-2 text-right">{value}</div>
	  <div class="col-xs-6">
	    <div class="progress">
	      <div class="progress-bar progress-bar-{element} progress-bar-striped"
		   role="progressbar"
		   style="width: {percent}%;">
	      </div>
	    </div>
	  </div>
        </div>
        """.format(
            statistic=statistic,
            element=self.element,
            verbose_name=self._meta.get_field(field_name).verbose_name,
            value=self.get_statistic(statistic, prefix),
            percent=self.statistic_percent(statistic, prefix),
        )

    @property
    def display_statistics(self):
        return u"""
  <div class="card-statistics">
    <div class="btn-group" data-toggle="buttons" data-control-tabs="card-{card_number}">
        {labels}
    </div>
    <br><br>
    <div class="tab-content" data-tabs="card-{card_number}">
        {tabs}
    </div>
  </div>
        """.format(
            card_number=self.number,
            labels=u''.join([u"""
                <label class="btn btn-{element} {active}" style="width: {width}%"
                       data-open-tab="card-{card_number}-{prefix}">
	        <input type="radio" {checked}> {verbose_name}
                </label>
            """.format(
                element=self.element,
                active='active' if i == 0 else '',
                checked='checked' if i == 0 else '',
                width=100 / len(self.STATISTICS_PREFIXES),
                card_number=self.number,
                prefix=prefix[:-1],
                verbose_name=verbose_name,
            ) for i, (prefix, verbose_name) in enumerate(self.STATISTICS_PREFIXES.items())]),
            tabs=u''.join([u"""
            <div class="tab-pane {active}" data-tab="card-{card_number}-{prefix}">
            {statistics}
      </div>
            """.format(
                active='active' if i == 0 else '',
                card_number=self.number,
                prefix=prefix[:-1],
                statistics=u''.join([
                    self.display_statistic(statistic, prefix)
                    for statistic in self.STATISTICS_FIELDS
                ]),
            ) for i, (prefix, verbose_name) in enumerate(self.STATISTICS_PREFIXES.items())]),
        )

    ############################################################
    # Descriptions

    description = models.TextField(_('Description'), null=True)
    DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_descriptions = models.TextField(_('Description'), null=True)

    profile = models.TextField(_('Profile'), null=True)
    PROFILES_CHOICES = ALL_ALT_LANGUAGES
    d_profiles = models.TextField(_('Profile'), null=True)

    message = models.TextField(_('Message'), null=True)
    MESSAGES_CHOICES = ALL_ALT_LANGUAGES
    d_messages = models.TextField(_('Message'), null=True)

    ############################################################
    # Cache stage girl

    _cache_stage_girl_update_on_none = True
    _cached_stage_girl_collection_name = 'stagegirl'
    _cache_j_stage_girl = models.TextField(null=True)

    def to_cache_stage_girl(self):
        if not self.stage_girl_id:
            return None
        return {
            'id': self.stage_girl_id,
            'name': self.stage_girl.name,
            'names': self.stage_girl.names or {},
            'image_url': unicode(self.stage_girl.small_image_url),
        }

    ############################################################
    # Type

    TYPES = OrderedDict([
        ('permanent', {
            'icon': 'chest',
            'translation': _('Permanent'),
            'filter': lambda _q: _q.filter(limited=False),
            'is': lambda _s: not _s.limited,
        }),
        ('limited', {
            'icon': 'hourglass',
            'translation': _('Limited'),
            'filter': lambda _q: _q.filter(limited=True),
            'is': lambda _s: _s.limited,
        }),
        # ('event', {
        #     'icon': 'event',
        #     'translation': _('Event'),
        #     'filter': lambda _q: _q.filter(event__isnull=False),
        #     'is': lambda _s: bool(_s.event_id),
        # }),
    ])
    TYPE_CHOICES = [(_name, _info['translation']) for _name, _info in TYPES.items()]

    @property
    def types(self):
        return [
            _type
            for _type, _details in reversed(self.TYPES.items())
            if _details['is'](self)
        ]

    @property
    def type(self):
        return self.types[0]

    type_icon = property(getInfoFromChoices('type', TYPES, 'icon'))

    ############################################################
    # Unicode

    def __unicode__(self):
        if self.pk:
            return u'{rarity} {stage_girl_name} {name}'.format(
                rarity=self.t_rarity,
                stage_girl_name=self.cached_stage_girl.t_name if self.stage_girl_id else '',
                name=self.t_name or '',
            )
        return u''

    class Meta(MagiModel.Meta):
        abstract = True

############################################################
# Card

class Card(BaseCard):
    pass

############################################################
# Card

class Memoir(BaseCard):
    pass
