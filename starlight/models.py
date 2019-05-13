# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _
from magi.abstract_models import BaseAccount
from magi.item_model import MagiModel, i_choices
from magi.utils import (
    ColorField,
    getAge,
    ordinalNumber,
    staticImageURL,
    uploadItem,
    uploadTiny,
    upload2x,
    uploadTthumb,
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
# Elements

ELEMENTS = OrderedDict([
    ('flower', {
        'translation': _('Flower'),
        'japanese': u'花',
        'color': '#F0484D',
        'light_color': '#FFD7CE',
    }),
    ('wind', {
        'translation': _('Wind'),
        'japanese': u'風',
        'color': '#30AB49',
        'light_color': '#AEFFBD',
    }),
    ('snow', {
        'translation': _('Snow'),
        'japanese': u'雪',
        'color': '#0072A6',
        'light_color': '#99EFFF',
    }),
    ('cloud', {
        'translation': _('Cloud'),
        'japanese': u'雲',
        'color': '#F3608A',
        'light_color': '#FFCED7',
    }),
    ('moon', {
        'translation': _('Moon'),
        'japanese': u'月',
        'color': '#F9AA12',
        'light_color': '#FBFEC8',
    }),
    ('cosmos', {
        'translation': _('Cosmos'),
        'japanese': u'宙',
        'color': '#794A92',
        'light_color': '#E5D4FF',
    }),
    ('dream', {
        'translation': _('Dream'),
        'japanese': u'夢',
        'color': '#38495A',
        'light_color': '#BDD5DE',
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

    name = models.CharField(_('Name'), max_length=100, unique=True)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)
    japanese_name = property(lambda _s: _s.names.get('ja', _s.name))

    _original_image = models.ImageField(null=True, upload_to=uploadTiny('voiceactress'))
    image = models.ImageField(_('Image'), upload_to=uploadItem('voiceactress'), null=True)

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

    reverse_related = [
        ('stagegirls', 'stagegirls', _('Stage girl')),
    ]

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

    _original_image = models.ImageField(null=True, upload_to=uploadTiny('school'))
    image = models.ImageField(_('Image'), upload_to=uploadItem('school'), null=True)

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

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

    _original_image = models.ImageField(null=True, upload_to=uploadTiny('stagegirl'))
    image = models.ImageField(_('Image'), upload_to=uploadItem('stagegirl'), null=True)

    voice_actress = models.ForeignKey(
        VoiceActress, verbose_name=_('Voice actress'), related_name='stagegirls',
        null=True, on_delete=models.SET_NULL,
    )

    birthday = models.DateField(_('Birthday'), null=True, help_text='The year will be ignored.')
    display_birthday = property(lambda _s: date_format(_s.birthday, format='MONTH_DAY_FORMAT', use_l10n=True))

    ASTROLOGICAL_SIGN_CHOICES = ASTROLOGICAL_SIGN_CHOICES
    i_astrological_sign = models.PositiveIntegerField(
        _('Astrological sign'), choices=i_choices(ASTROLOGICAL_SIGN_CHOICES), null=True)
    astrological_sign_image_url = property(
        lambda _s: staticImageURL(_s.i_astrological_sign, folder='i_astrological_sign', extension='png'))

    color = ColorField(_('Color'), null=True, blank=True)

    school = models.ForeignKey(
        School, verbose_name=_('School'), related_name='students',
    )

    YEAR_CHOICES = _to_year_choices()
    i_year = models.PositiveIntegerField(_('School year'), choices=i_choices(YEAR_CHOICES), null=True)
    to_year_choices = classmethod(lambda _s: _to_year_choices())
    to_t_year = classmethod(lambda _s, _i: dict(i_choices(_to_year_choices())).get(_i, None))

    # todo: department, class?

    weapon = models.CharField(_('Weapon'), max_length=100, null=True)
    WEAPONS_CHOICES = ALL_ALT_LANGUAGES
    d_weapons = models.TextField(_('Weapon'), null=True)

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

    def __unicode__(self):
        return self.t_name

############################################################
############################################################
# Relive models
############################################################
############################################################

############################################################
# Card

class Card(MagiModel):
    collection_name = 'card'
    owner = models.ForeignKey(User, related_name='added_cards')

    ############################################################
    # Basic details: Rarity, elements, ...

    number = models.PositiveIntegerField(_('ID'), unique=True, primary_key=True)
    stage_girl = models.ForeignKey(StageGirl, verbose_name=_('Stage girl'), related_name='cards')

    name = models.CharField(_('Title'), max_length=100, null=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Title'), null=True)

    RARITY_CHOICES = (
        (1, u'★'),
        (2, u'★★'),
        (3, u'★★★'),
        (4, u'★★★★'),
    )
    RARITY_WITHOUT_I_CHOICES = True
    i_rarity = models.PositiveIntegerField(_('Rarity'), choices=RARITY_CHOICES, db_index=True)

    ELEMENTS_CHOICES = ELEMENT_CHOICES
    c_elements = models.TextField(_('Elements'), blank=True, null=True)

    DAMAGE_CHOICES = (
        ('normal', _('Normal')),
        ('special', _('Special')),
    )
    i_damage = models.PositiveIntegerField(_('Damage'), choices=i_choices(DAMAGE_CHOICES), default=0)

    POSITION_CHOICES = (
        ('front', _('Front')),
        ('center', _('Center')),
        ('rear', _('Rear')),
    )
    i_position = models.PositiveIntegerField(_('Position'), choices=i_choices(POSITION_CHOICES), default=0)

    ############################################################
    # Images

    _2x_image = models.ImageField(null=True, upload_to=upload2x('card'))
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('card'))
    image = models.ImageField(_('Image'), upload_to=uploadItem('card'), null=True)

    _original_icon = models.ImageField(null=True, upload_to=uploadTiny('card/icon'))
    icon = models.ImageField(_('Icon'), upload_to=uploadItem('card/icon'), null=True)

    _2x_art = models.ImageField(null=True, upload_to=upload2x('card/art'))
    _original_art = models.ImageField(null=True, upload_to=uploadTiny('card/art'))
    _tthumbnail_art = models.ImageField(null=True, upload_to=uploadTthumb('card/art'))
    art = models.ImageField(_('Art'), upload_to=uploadItem('card/art'), null=True)

    _2x_transparent = models.ImageField(null=True, upload_to=upload2x('card/transparent'))
    _original_transparent = models.ImageField(null=True, upload_to=uploadTiny('card/transparent'))
    _tthumbnail_transparent = models.ImageField(null=True, upload_to=uploadTthumb('card/transparent'))
    transparent = models.ImageField(_('Transparent'), upload_to=uploadItem('card/transparent'), null=True)

    live2d_model_package = models.FileField(upload_to=uploadItem('card/live2d'), null=True)

    tinypng_settings = {
        'art': {
            'resize': 'scale',
            'height': 402,
        },
    }

    ############################################################
    # Statistics fields

    ############################################################
    # Statistics utils

    # todo: so many things

    ############################################################
    # Cache stage girl

    _cached_stage_girl_collection_name = 'stagegirl'
    _cache_j_stage_girl = models.TextField(null=True)

    def to_cache_stage_girl(self):
        if not self.stage_girl_id:
            return None
        return {
            'id': self.stage_girl_id,
            'name': self.stage_girl.name,
            'names': self.stage_girl.d_names or {},
            'image': unicode(self.stage_girl.image),
        }

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
