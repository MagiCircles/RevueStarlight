# -*- coding: utf-8 -*-
from __future__ import division
from collections import OrderedDict
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import Q
from django.utils.formats import date_format
from django.utils.html import mark_safe
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, string_concat
from magi.abstract_models import (
    BaseAccount,
    AccountAsOwnerModel,
)
from magi.item_model import MagiModel, i_choices, getInfoFromChoices
from magi.utils import (
    AttrDict,
    ColorField,
    getAge,
    getStaffConfiguration,
    ordinalNumber,
    staticImageURL,
    summarize,
    uploadItem,
    uploadTiny,
    upload2x,
    uploadThumb,
    uploadTthumb,
    YouTubeVideoField,
)
from starlight.django_translated import t
from starlight.utils import (
    displayNameHTML,
    getMaxStatistic,
    getSchoolImageFromPk,
    getSchoolNameFromPk,
    getSchoolURLFromPk,
    getStageGirlImageFromPk,
    getStageGirlNamesFromPk,
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
        'resists_against': ['wind'],
        'weak_against': ['snow', 'dream'],
    }),
    ('wind', {
        'translation': _('Wind'),
        'japanese': u'風',
        'color': '#30AB49',
        'light_color': '#AEFFBD',
        'resists_against': ['snow'],
        'weak_against': ['flower', 'dream'],
    }),
    ('snow', {
        'translation': _('Snow'),
        'japanese': u'雪',
        'color': '#0072A6',
        'light_color': '#99EFFF',
        'resists_against': ['flower'],
        'weak_against': ['wind', 'dream'],
    }),
    ('cloud', {
        'translation': _('Cloud'),
        'japanese': u'雲',
        'color': '#F3608A',
        'light_color': '#FFCED7',
        'resists_against': ['moon'],
        'weak_against': ['space', 'dream'],
    }),
    ('moon', {
        'translation': _('Moon'),
        'japanese': u'月',
        'color': '#F9AA12',
        'light_color': '#FBFEC8',
        'resists_against': ['space'],
        'weak_against': ['cloud', 'dream'],
    }),
    ('space', {
        'translation': _('Space'),
        'japanese': u'宙',
        'color': '#794A92',
        'light_color': '#E5D4FF',
        'resists_against': ['cloud'],
        'weak_against': ['moon', 'dream'],
    }),
    ('dream', {
        'translation': _('Dream'),
        'japanese': u'夢',
        'color': '#38495A',
        'light_color': '#BDD5DE',
        'resists_against': [],
        'weak_against': ['flower', 'wind', 'snow', 'cloud', 'moon', 'space'],
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
# Get voice actresses fans

def getVoiceActressFans(id, queryset=None):
    return (queryset or User.objects).filter(
        Q(preferences__d_extra__contains=u'"favorite_voiceactress1": "{}"'.format(id))
        | Q(preferences__d_extra__contains=u'"favorite_voiceactress2": "{}"'.format(id))
        | Q(preferences__d_extra__contains=u'"favorite_voiceactress3": "{}"'.format(id))
    )

############################################################
############################################################
# MagiCircles' required models
############################################################
############################################################

############################################################
# Account

class Account(BaseAccount):

    ############################################################
    # Version

    VERSION_CHOICES = VERSION_CHOICES
    i_version = models.PositiveIntegerField(_('Version'), choices=i_choices(VERSION_CHOICES))
    version_image = property(lambda _s: staticImageURL(
        VERSIONS[_s.version]['image'], folder='language', extension='png'))

    ############################################################
    # Generic

    friend_id = models.CharField(_('ID'), null=True, max_length=100, validators=[
        RegexValidator(r'^[0-9]+$', t['Enter a number.']),
    ])
    show_friend_id = models.BooleanField(_('Should your friend ID be visible to other players?'), default=True)
    center = models.ForeignKey(
        'CollectedCard', verbose_name=_('Center'), related_name='center_of_account',
        null=True, on_delete=models.SET_NULL)

    ############################################################
    # Self service verifications
    # See: https://github.com/MagiCircles/MagiCircles/wiki/BaseAccount-model#self-service-verifications

    _thumbnail_screenshot = models.ImageField(null=True, upload_to=uploadThumb('account_screenshot'))
    screenshot = models.ImageField(
        _('Screenshot'), help_text=_('In-game profile screenshot'),
        upload_to=uploadItem('account_screenshot'), null=True)
    level_on_screenshot_upload = models.PositiveIntegerField(null=True)
    is_hidden_from_leaderboard = models.BooleanField('Hide from leaderboard', default=False, db_index=True)

    ############################################################
    # Specific to Relive

    PLAY_STYLES = OrderedDict([
        ('casual', {
            'translation': _('Casual'),
            'icon': 'chibi',
        }),
        ('hardcore', {
            'translation': _('Hardcore'),
            'icon': 'fire',
        }),
    ])
    PLAY_STYLE_CHOICES = [(_name, _info['translation']) for _name, _info in PLAY_STYLES.items()]
    i_play_style = models.PositiveIntegerField(
        _('Play style'), choices=i_choices(PLAY_STYLE_CHOICES), null=True)
    play_style_icon = property(getInfoFromChoices('play_style', PLAY_STYLES, 'icon'))

    stage_of_dreams_level = models.PositiveIntegerField(_('Stage of dreams level'), null=True)

    VS_REVUE_RANK_CHOICES = (
        ('bronze1', string_concat(u'✦ ', _('Bronze'))),
        ('bronze2', string_concat(u'✦✦ ', _('Bronze'))),
        ('bronze3', string_concat(u'✦✦✦ ', _('Bronze'))),
        ('silver1', string_concat(u'✦ ', _('Silver'))),
        ('silver2', string_concat(u'✦✦ ', _('Silver'))),
        ('silver3', string_concat(u'✦✦✦ ', _('Silver'))),
        ('gold1', string_concat(u'✦ ', _('Gold'))),
        ('gold2', string_concat(u'✦✦ ', _('Gold'))),
        ('gold3', string_concat(u'✦✦✦ ', _('Gold'))),
        ('platinum1', string_concat(u'✦ ', _('Platinum'))),
        ('platinum2', string_concat(u'✦✦ ', _('Platinum'))),
        ('platinum3', string_concat(u'✦✦✦ ', _('Platinum'))),
        ('legend', _('Legend')),
    )

    i_vs_revue_rank = models.PositiveIntegerField(
        _('Vs. Revue rank'), choices=i_choices(VS_REVUE_RANK_CHOICES), null=True)
    vs_revue_rank_image = property(lambda _s: staticImageURL(
        _s.i_vs_revue_rank, folder='i_vs_revue_rank', extension='png'))

    ############################################################
    # Extra

    OS_CHOICES = (
        'Android',
        'iOs',
    )
    i_os = models.PositiveIntegerField(_('Operating System'), choices=i_choices(OS_CHOICES), null=True)
    os_icon = property(lambda _s: _s.os.lower() if _s.os else None)

    device = models.CharField(
        _('Device'), max_length=150, null=True,
        help_text=_('The model of your device. Example: Nexus 5, iPhone 4, iPad 2, ...'),
    )

    bought_stars = models.PositiveIntegerField(_('Total stars bought'), null=True)

    is_playground = models.BooleanField(
        _('Playground'), default=False, db_index=True,
        help_text=_('Check this box if this account doesn\'t exist in the game.'),
    )

    ############################################################
    # Leaderboard per version

    def update_cache_leaderboards(self):
        self._cache_leaderboards_last_update = timezone.now()
        if self.is_hidden_from_leaderboard or self.is_playground:
            self._cache_leaderboard = None
        else:
            self._cache_leaderboard = type(self).objects.filter(
                level__gt=self.level, i_version=self.i_version).exclude(
                    Q(is_hidden_from_leaderboard=True) | Q(is_playground=True)).values(
                        'level').distinct().count() + 1

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

    specialty = models.CharField(_('Specialty'), max_length=191, null=True)
    SPECIALTYS_CHOICES = ALL_ALT_LANGUAGES
    d_specialtys = models.TextField(_('Specialty'), null=True)

    hobbies = models.CharField(_('Hobbies'), max_length=191, null=True)
    HOBBIESS_CHOICES = ALL_ALT_LANGUAGES
    d_hobbiess = models.TextField(_('Hobbies'), null=True)

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

    m_staff_description = models.TextField(_('Message'), null=True, help_text='Only visible in staff list.')
    M_STAFF_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_staff_descriptions = models.TextField(_('Message'), null=True, help_text='Only visible in staff list.')

    video = YouTubeVideoField(_('Video'), null=True)

    birthday_banner = models.ImageField(upload_to=uploadItem('voiceactress/birthday'), null=True)
    _original_birthday_banner = models.ImageField(null=True, upload_to=uploadTiny('voiceactress/birthday'))

    ############################################################
    # Reverse relations

    reverse_related = [
        { 'field_name': 'stagegirls', 'verbose_name': _('Stage girl') },
        { 'field_name': 'links', 'verbose_name': _('Social media'), 'max_per_line': None },
        {
            'field_name': 'fans',
            'url': 'users',
            'verbose_name': _('Fans'),
            'filter_field_name': 'favorite_voice_actress',
            'max_per_line': 8,
            'allow_ajax_per_item': False,
        },
    ]

    @property
    def fans(self):
        return getVoiceActressFans(self.id).select_related('preferences').order_by('-id')

    ############################################################
    # Views utils

    display_name = property(displayNameHTML)

    top_image_list = property(lambda _s: _s.image_thumbnail_url or staticImageURL('default/default.png'))
    image_for_prefetched = top_image_list

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

    url = models.CharField(_('URL'), max_length=191)

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

    monochrome_image = models.ImageField(upload_to=uploadItem('school'), null=True)
    white_image = models.ImageField(upload_to=uploadItem('school'), null=True)

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
    # Views utils

    top_image = property(lambda _s: _s.image_url or staticImageURL('default/default_school.png'))

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

    uniform_image = models.ImageField('Uniform image', upload_to=uploadItem('stagegirl'), null=True)
    _original_uniform_image = models.ImageField(null=True, upload_to=uploadTiny('stagegirl'))

    small_image = models.ImageField(
        upload_to=uploadItem('stagegirl/s'), null=True,
        help_text='Map pins, favorite characters on profile and character selectors.')

    square_image = models.ImageField(
        upload_to=uploadItem('stagegirl/s'), null=True,
        help_text='On list page.')

    voice_actress = models.ForeignKey(
        VoiceActress, verbose_name=_('Voice actress'), related_name='stagegirls',
        null=True, on_delete=models.SET_NULL,
        db_index=True,
    )

    school = models.ForeignKey(
        School, verbose_name=_('School'), related_name='students',
        db_index=True,
    )

    school_department = models.CharField(
        _('Department'), max_length=100, null=True,
    )
    SCHOOL_DEPARTMENTS_CHOICES = ALL_ALT_LANGUAGES
    d_school_departments = models.TextField(_('Department'), null=True)

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

    weapon = models.CharField(
        _('Weapon'), max_length=200, null=True,
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

    likes = models.CharField(_('Likes'), max_length=150, null=True)
    LIKESS_CHOICES = ALL_ALT_LANGUAGES
    d_likess = models.TextField(_('Likes'), null=True)

    dislikes = models.CharField(_('Dislikes'), max_length=150, null=True)
    DISLIKESS_CHOICES = ALL_ALT_LANGUAGES
    d_dislikess = models.TextField(_('Dislikes'), null=True)

    hobbies = models.CharField(_('Hobbies'), max_length=200, null=True)
    HOBBIESS_CHOICES = ALL_ALT_LANGUAGES
    d_hobbiess = models.TextField(_('Hobbies'), null=True)

    introduction = models.TextField(_('Introduction'), help_text='In-game introduction', null=True)
    INTRODUCTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_introductions = models.TextField(_('Introduction'), help_text='In-game introduction', null=True)

    m_description = models.TextField(_('Description'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Description'), null=True)

    video = YouTubeVideoField(_('Video'), null=True)

    birthday_banner = models.ImageField(upload_to=uploadItem('stagegirl/birthday'), null=True)
    _original_birthday_banner = models.ImageField(null=True, upload_to=uploadTiny('stagegirl/birthday'))

    ############################################################
    # Images settings

    tinypng_settings = {
        'small_image': {
            'resize': 'fit',
            'width': 80,
            'height': 80,
        },
        'square_image': {
            'resize': 'fit',
            'width': 200,
            'height': 200,
        },
    }

    ############################################################
    # Reverse relations

    reverse_related = [
        { 'field_name': 'cards', 'verbose_name': _('Cards'), 'filter_field_name': 'stage_girl' },
        { 'field_name': 'memoirs', 'verbose_name': _('Memoirs'), 'filter_field_name': 'stage_girl' },
        {
            'field_name': 'fans',
            'url': 'users',
            'verbose_name': _('Fans'),
            'filter_field_name': 'favorite_character',
            'max_per_line': 8,
            'allow_ajax_per_item': False,
        },
    ]

    @property
    def fans(self):
        return User.objects.filter(
            Q(preferences__favorite_character1=self.id)
            | Q(preferences__favorite_character2=self.id)
            | Q(preferences__favorite_character3=self.id)
        ).select_related('preferences').order_by('-id')

    ############################################################
    # Views utils

    display_name = property(displayNameHTML)

    image_for_prefetched = property(lambda _s: _s.small_image_url or staticImageURL('default/default_stagegirl.png'))

    @property
    def display_section_header(self):
        return mark_safe(u'<a href="{url}" data-ajax-url="{ajax_url}" data-ajax-title="{title}"><img src="{image}" alt="{title}" height="50"> {title}'.format(
            image=getSchoolImageFromPk(self.school_id),
            title=getSchoolNameFromPk(self.school_id),
            url=getSchoolURLFromPk(self.school_id),
            ajax_url=getSchoolURLFromPk(self.school_id, ajax=True),
        ))

    @property
    def top_image_list(self):
        return self.square_image_url or staticImageURL('default/default.png')

    @property
    def top_html_item(self):
        return u''.join([
            u'<img src="{}" alt="{}" class="stage-girl-image {}">'.format(
                image,
                unicode(self),
                css_classes,
            ) for (image, css_classes) in [
                (_i, _c) for _i, _c in [
                    (getattr(self, 'uniform_image_url'), 'uniform'),
                    (getattr(self, 'image_url'), 'revue'),
                ] if _i
            ] or [
                (staticImageURL('default/default.png'), '')
            ]
        ])

    ############################################################
    # Unicode

    def __unicode__(self):
        return self.t_name

############################################################
# Staff

class Staff(MagiModel):
    collection_name = 'staff'

    owner = models.ForeignKey(User, related_name='added_staff')

    CATEGORY_CHOICES = (
        ('anime', string_concat(_('Anime'), ' - ', _('Cast'))),
        ('animestaff', string_concat(_('Anime'), ' - ', _('Staff'))),
        ('general', _('General')),
        ('stageplay', _('Stage play')),
        ('additional', _('Additional')),
    )
    i_category = models.PositiveIntegerField(_('Category'), choices=i_choices(CATEGORY_CHOICES))
    display_section_header = property(lambda _s: _s.t_category if _s.category != 'anime' else None)

    name = models.CharField(_('Name'), max_length=100)
    NAMES_CHOICES = NON_LATIN_LANGUAGES
    d_names = models.TextField(_('Name'), null=True)
    japanese_name = property(lambda _s: _s.names.get('ja', _s.name))

    role = models.CharField(_('Role'), max_length=150, db_index=True)
    ROLES_CHOICES = ALL_ALT_LANGUAGES
    d_roles = models.TextField(_('Role'), null=True)

    social_media_url = models.CharField(_('Social media'), max_length=191, null=True)

    importance = models.IntegerField(
        'Importance', default=0, db_index=True,
        help_text='Allows to re-order how the staff appear. Highest number shows first.',
    )

    m_description = models.TextField(_('Message'), null=True)
    M_DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_m_descriptions = models.TextField(_('Message'), null=True)

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
            'show_cost': True,
            'show_title': True,
        }),
        ('climax', {
            'translation': _('Climax'),
            'show_cost': True,
            'show_title': True,
        }),
        ('auto', {
            'translation': _('Auto'),
            'show_cost': False,
            'show_title': False,
        }),
        ('finishing', {
            'translation': _('Finishing'),
            'show_cost': False,
            'show_title': True,
        }),
        ('event', {
            'translation': _('Event'),
            'show_cost': False,
            'show_title': False,
        }),
    ])
    TYPE_CHOICES = [(_name, _info['translation']) for _name, _info in TYPES.items()]
    i_type = models.PositiveIntegerField(_('Type'), choices=i_choices(TYPE_CHOICES))

    name = models.CharField(_('Title'), max_length=100, db_index=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Title'), null=True)

    description = models.CharField(_('Description'), max_length=191)
    DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_descriptions = models.TextField(_('Description'), null=True)

    m_tips = models.TextField(
        _('Tips'), null=True,
        help_text='Extra details not present in the game that can be good to know for players.',
    )
    M_TIPSS_CHOICES = ALL_ALT_LANGUAGES
    d_m_tipss = models.TextField(_('Tips'), null=True)

    image = models.ImageField(_('Image'), upload_to=uploadItem('act'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('act'))

    small_image = models.ImageField('Small image', upload_to=uploadItem('act'), null=True)
    _original_small_image = models.ImageField(null=True, upload_to=uploadTiny('act'))

    cost = models.PositiveIntegerField('AP', default=1)

    unlock_at_rank = models.PositiveIntegerField(null=True)
    display_unlock_at_rank = property(lambda _s: _('Unlock at rank {rank}').format(rank=_s.unlock_at_rank))

    hits = models.PositiveIntegerField('How many hits?', default=1)
    display_hits = property(lambda _s: _('Hits {number_of_times} times').format(number_of_times=_s.hits))

    TARGET_CHOICES = (
        ('single', _('Front enemy')),
        ('group', _('Front group of enemies')),
        ('all', _('All enemies')),
    )
    i_target = models.PositiveIntegerField(_('Target'), choices=i_choices(TARGET_CHOICES), null=True)
    other_target = models.CharField(_('Target'), max_length=100, null=True)
    OTHER_TARGETS_CHOICES = ALL_ALT_LANGUAGES
    d_other_targets = models.TextField(_('Target'), null=True)
    display_target = property(lambda _s: u'{}: {}'.format(
        _('Target'), _s.t_other_target if _s.other_target else _s.t_target))
    has_target = property(lambda _s: _s.i_target is not None or _s.other_target)

    bound_break_value = models.FloatField(null=True)
    display_bound_break_value = property(lambda _s: u'{}: {}%'.format(
        _('After full bound break'), _s.bound_break_value))

    j_details = models.TextField(null=True)

    ############################################################
    # Views utils

    show_cost = property(getInfoFromChoices('type', TYPES, 'show_cost'))
    show_title = property(getInfoFromChoices('type', TYPES, 'show_title'))

    template_for_prefetched = 'items/acts.html'

    @property
    def show_top_details(self):
        return self.show_cost

    @property
    def top_details(self):
        return [
            d for d in [
                {
                    'verbose_name': _('AP'),
                    'value': self.cost,
                } if self.show_cost else None,
            ] if d
        ]

    ############################################################
    # Unicode

    def __unicode__(self):
        return u'{}]{} {} - {}'.format(
            unicode(self.t_type)[0],
            u'🔒{}'.format(self.unlock_at_rank) if self.unlock_at_rank else '',
            self.t_name,
            summarize(self.t_description, max_length=(80 - len(unicode(self.t_name)))),
        )

    class Meta(MagiModel.Meta):
        unique_together = (('name', 'description', 'unlock_at_rank'), )

############################################################
# Abstract: Base card

class BaseCard(MagiModel):
    owner = models.ForeignKey(User, related_name='added_%(class)ss')

    ############################################################
    # Basic details: Rarity, ...

    number = models.PositiveIntegerField(_('ID'), unique=True, primary_key=True)

    jp_release_date = models.DateField(
        string_concat(_('Release date'), ' - ', _('Japanese version')),
        null=True, db_index=True,
    )

    ww_release_date = models.DateField(
        string_concat(_('Release date'), ' - ', _('Worldwide version')),
        null=True,
    )

    name = models.CharField(_('Title'), max_length=100, null=True)
    NAMES_CHOICES = ALL_ALT_LANGUAGES
    d_names = models.TextField(_('Title'), null=True)

    RARITIES = OrderedDict([
        (1, {
            'translation': u'★',
            'cost': getStaffConfiguration('rarity_1_cost', 2),
            'min_level': 30,
            'max_level': 50,
        }),
        (2, {
            'translation': u'★★',
            'cost': getStaffConfiguration('rarity_2_cost', 6),
            'min_level': 40,
            'max_level': 60,
        }),
        (3, {
            'translation': u'★★★',
            'cost': getStaffConfiguration('rarity_3_cost', 9),
            'min_level': 50,
            'max_level': 70,
        }),
        (4, {
            'translation': u'★★★★',
            'cost': getStaffConfiguration('rarity_4_cost', 12),
            'min_level': 60,
            'max_level': 80,
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
    small_rarity_image = property(lambda _s: staticImageURL(_s.i_rarity, folder='small_rarity', extension='png'))

    cost = property(getInfoFromChoices('rarity', RARITIES, 'cost'))
    max_level = property(getInfoFromChoices('rarity', RARITIES, 'max_level'))
    min_level = property(getInfoFromChoices('rarity', RARITIES, 'min_level'))

    is_limited = models.BooleanField(_('Limited'), default=False)
    is_event = models.BooleanField(_('Event'), default=False)
    is_seasonal = models.BooleanField(_('Seasonal'), default=False)

    ############################################################
    # Fan made details

    m_tips = models.TextField(
        _('Tips'), null=True,
        help_text='Extra details not present in the game that can be good to know for players.',
    )
    M_TIPSS_CHOICES = ALL_ALT_LANGUAGES
    d_m_tipss = models.TextField(_('Tips'), null=True)

    ############################################################
    # Images

    image = models.ImageField(_('Image'), upload_to=uploadItem('card'), null=True)
    _original_image = models.ImageField(null=True, upload_to=uploadTiny('card'))
    _2x_image = models.ImageField(null=True, upload_to=upload2x('card'))

    base_icon = models.ImageField(
        'Base icon',
        help_text='Icon without border, as originally extracted from the game',
        upload_to=uploadItem('card/icon'), null=True,
    )
    icon = models.ImageField(_('Icon'), upload_to=uploadItem('card/icon'), null=True)
    _original_icon = models.ImageField(null=True, upload_to=uploadTiny('card/icon'))

    @property
    def ALL_ALT_ICONS_FIELDS(self):
        raise NotImplementedError('Collected cards require ALL_ALT_ICONS_FIELDS.')

    art = models.ImageField(_('Art'), upload_to=uploadItem('card/art'), null=True)
    _original_art = models.ImageField(null=True, upload_to=uploadTiny('card/art'))
    _tthumbnail_art = models.ImageField(null=True, upload_to=uploadTthumb('card/art'))
    _2x_art = models.ImageField(null=True, upload_to=upload2x('card/art'))
    show_art_on_homepage = models.BooleanField(default=True)

    ############################################################
    # Images settings and utils

    tinypng_settings = {
        'art': {
            'resize': 'scale',
            'height': 402,
        },
        'image': {
            'resize': 'scale',
            'height': 402,
        },
    }

    top_image = property(lambda _s: _s.image_url or _s.art_url or staticImageURL('default/default_card.png'))
    top_image_hd = property(lambda _s: _s.image_2x_url or _s.image_original_url
                            or _s.art_url or staticImageURL('default/default_card.png'))

    ############################################################
    # Statistics fields

    acts = models.ManyToManyField(Act, related_name='%(class)ss', blank=True, verbose_name=_('Acts'))

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

    min_level_hp = models.PositiveIntegerField(string_concat(u'Min level ', _('HP')), null=True)
    min_level_act_power = models.PositiveIntegerField(string_concat(u'Min level ', _('ACT Power')), null=True)
    min_level_normal_defense = models.PositiveIntegerField(
        string_concat(u'Min level ', _('Normal defense')), null=True)
    min_level_special_defense = models.PositiveIntegerField(
        string_concat(u'Min level ', _('Special defense')), null=True)
    min_level_agility = models.PositiveIntegerField(string_concat(u'Min level ', _('Agility')), null=True)

    max_level_hp = models.PositiveIntegerField(string_concat(u'Max level ', _('HP')), null=True)
    max_level_act_power = models.PositiveIntegerField(string_concat(u'Max level ', _('ACT Power')), null=True)
    max_level_normal_defense = models.PositiveIntegerField(
        string_concat(u'Max level ', _('Normal defense')), null=True)
    max_level_special_defense = models.PositiveIntegerField(
        string_concat(u'Max level ', _('Special defense')), null=True)
    max_level_agility = models.PositiveIntegerField(string_concat(u'Max level ', _('Agility')), null=True)

    ############################################################
    # Statistics utils

    STATISTICS_FIELDS = ['hp', 'act_power', 'normal_defense', 'special_defense', 'agility']
    STATISTICS_PREFIXES = OrderedDict([
        ('base_', lambda _s: _('Base')),
        ('min_level_', lambda _s: _('Level {level}').format(level=_s.min_level)),
        ('delta_', lambda _s: u'Δ'),
        ('max_level_', lambda _s: _('Level {level}').format(level=_s.max_level)),
    ])
    ALL_STATISTICS_FIELDS = [
        u'{}{}'.format(_prefix, _statistic)
        for _statistic in STATISTICS_FIELDS
        for _prefix in STATISTICS_PREFIXES.keys()
    ]

    def get_statistic(self, statistic, prefix):
        return getattr(self, u'{}{}'.format(prefix, statistic)) or 0

    def has_any_statistic(self, prefix='delta_'):
        for statistic in self.STATISTICS_FIELDS:
            if self.get_statistic(statistic, prefix):
                return True
        return False

    def get_statistics_prefixes_to_display(self):
        statistics_prefixes = OrderedDict([
            (prefix, verbose_name(self))
            for prefix, verbose_name in self.STATISTICS_PREFIXES.items()
            if self.has_any_statistic(prefix=prefix)
        ])
        if 'min_level_' in statistics_prefixes and 'base_' in statistics_prefixes:
            del(statistics_prefixes['base_'])
        if 'max_level_' in statistics_prefixes and 'delta_' in statistics_prefixes:
            del(statistics_prefixes['delta_'])
        return statistics_prefixes

    def statistic_percent(self, statistic, prefix):
        return (
            self.get_statistic(statistic, prefix) / getMaxStatistic(self.collection_name, statistic)
        ) * 100

    def display_statistic_rank(self, statistic):
        if not getattr(self, 'cached_statistics_ranks', None):
            return ''
        rank = self.cached_statistics_ranks.get(statistic, None)
        if not rank:
            return ''
        return (
            u'#{}'.format(rank)
            if rank > 3
            else u'<img class="statistic-rank" src="{url}" alt="{rank}">'.format(
                    url=staticImageURL(u'medal{}'.format(4 - rank), folder='badges', extension='png'),
                    rank=rank,
            )
        )

    def display_statistic(self, statistic, prefix):
        field_name = u'{}{}'.format(prefix, statistic)
        value = self.get_statistic(statistic, prefix)
        if not value:
            return None
        rank = self.display_statistic_rank(statistic)
        return u"""
	<div class="row">
	  <div class="col-xs-4 text-left"><span class="stat-label-{statistic}">{verbose_name}</span></div>
	  {rank}
	  <div class="col-xs-2 text-right">{value}</div>
	  <div class="col-xs-{stat_size}">
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
            verbose_name=self._meta.get_field(u'base_{}'.format(statistic)).verbose_name,
            value=value,
            percent=self.statistic_percent(statistic, prefix),
            rank=u'<div class="col-xs-2 text-center"><a href="{rank_url}" target="_blank">{rank}</a></div>'.format(
                rank=rank,
                rank_url=u'/{}s/?i_rarity={}&ordering=delta_{}&reverse_order=on'.format(
                    type(self).collection_name, self.i_rarity, statistic),
            ) if rank else '',
            stat_size=4 if rank else 6,
        )

    @property
    def display_statistics(self):
        statistics_prefixes = self.get_statistics_prefixes_to_display()
        if not statistics_prefixes:
            return None
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
                active='active' if i == 1 else '',
                checked='checked' if i == 1 else '',
                width=100 / len(statistics_prefixes),
                card_number=self.number,
                prefix=prefix[:-1],
                verbose_name=verbose_name,
            ) for i, (prefix, verbose_name) in enumerate(statistics_prefixes.items())]),
            tabs=u''.join([u"""
            <div class="tab-pane {active}" data-tab="card-{card_number}-{prefix}">
            {statistics}
      </div>
            """.format(
                active='active' if i == 1 else '',
                card_number=self.number,
                prefix=prefix[:-1],
                statistics=u''.join([s for s in [
                    self.display_statistic(statistic, prefix)
                    for statistic in self.STATISTICS_FIELDS
                ] if s]),
            ) for i, (prefix, verbose_name) in enumerate(statistics_prefixes.items())]),
        )

    ############################################################
    # Types

    TYPES = OrderedDict([
        ('permanent', {
            'icon': 'chest',
            'translation': _('Permanent'),
            'filter': lambda _q: _q.filter(is_limited=False, is_event=False, is_seasonal=False),
            'is': lambda _s: not _s.is_limited and not _s.is_event and not _s.is_seasonal,
            'not_a_real_field': True,
        }),
        ('limited', {
            'icon': 'hourglass',
            'translation': _('Limited'),
            'filter': lambda _q: _q.filter(Q(is_limited=True) | Q(is_seasonal=True) | Q(is_event=True)),
            'is': lambda _s: _s.is_limited or _s.is_seasonal or _s.is_event,
        }),
        ('event', {
            'icon': 'event',
            'translation': _('Event'),
            'filter': lambda _q: _q.filter(is_event=True),
            'is': lambda _s: _s.is_event,
        }),
        ('seasonal', {
            'icon': 'scout-box',
            'translation': _('Seasonal'),
            'filter': lambda _q: _q.filter(is_seasonal=True),
            'is': lambda _s: _s.is_seasonal,
        }),
    ])

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

    @property
    def type_icon(self):
        return self.TYPES[self.type]['icon']

    ############################################################
    # Views utils

    default_image = property(lambda _s: staticImageURL('default/default_card.png'))
    default_icon = property(lambda _s: staticImageURL('default/default.png'))
    image_for_prefetched = property(lambda _s: _s.icon_url or _s.base_icon_url or _s.default_icon)

    @property
    def top_image_list(self):
        if self.request.GET.get('view', None) == 'icons':
            return self.icon_url or self.default_icon
        return self.image_url or self.default_image

    ############################################################
    # Reverse relations

    reverse_related = [
        { 'field_name': 'acts', 'verbose_name': _('Acts'), 'max_per_line': None },
    ]

    ############################################################
    # Meta

    class Meta(MagiModel.Meta):
        abstract = True

############################################################
# Card

class Card(BaseCard):
    collection_name = 'card'

    ############################################################
    # Basic details: Element, damage, position, ...

    LIMIT_TO_RARITIES = [2, 3, 4]

    max_level = 80

    stage_girl = models.ForeignKey(StageGirl, verbose_name=_('Stage girl'), related_name='%(class)ss')

    ELEMENT_CHOICES = ELEMENT_CHOICES
    i_element = models.PositiveIntegerField(_('Element'), choices=i_choices(ELEMENT_CHOICES), db_index=True)
    element_image = property(lambda _s: staticImageURL(_s.element, folder='color', extension='png'))
    element_color = property(getInfoFromChoices('element', ELEMENTS, 'color'))
    elements_resists_against = property(getInfoFromChoices('element', ELEMENTS, 'resists_against'))
    elements_weak_against = property(getInfoFromChoices('element', ELEMENTS, 'weak_against'))

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

    ############################################################
    # Fan made details

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

    ############################################################
    # Long texts

    profile = models.TextField(_('Profile'), null=True)
    PROFILES_CHOICES = ALL_ALT_LANGUAGES
    d_profiles = models.TextField(_('Profile'), null=True)

    description = models.TextField(_('Description'), null=True)
    DESCRIPTIONS_CHOICES = ALL_ALT_LANGUAGES
    d_descriptions = models.TextField(_('Description'), null=True)

    message = models.TextField(_('Message'), null=True)
    MESSAGES_CHOICES = ALL_ALT_LANGUAGES
    d_messages = models.TextField(_('Message'), null=True)

    ############################################################
    # Images

    transparent = models.ImageField(_('Transparent'), upload_to=uploadItem('card/transparent'), null=True)
    _original_transparent = models.ImageField(null=True, upload_to=uploadTiny('card/transparent'))
    _tthumbnail_transparent = models.ImageField(null=True, upload_to=uploadTthumb('card/transparent'))
    _2x_transparent = models.ImageField(null=True, upload_to=upload2x('card/transparent'))

    rank1_rarity2_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank1_rarity3_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank1_rarity4_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank1_rarity5_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank1_rarity6_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank2_rarity2_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank2_rarity3_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank2_rarity4_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank2_rarity5_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank2_rarity6_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank3_rarity2_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank3_rarity3_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank3_rarity4_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank3_rarity5_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank3_rarity6_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank4_rarity2_icon = property(lambda _s: _s.rank3_rarity2_icon)
    rank4_rarity3_icon = property(lambda _s: _s.rank3_rarity3_icon)
    rank4_rarity4_icon = property(lambda _s: _s.rank3_rarity4_icon)
    rank4_rarity5_icon = property(lambda _s: _s.rank3_rarity5_icon)
    rank4_rarity6_icon = property(lambda _s: _s.rank3_rarity6_icon)
    rank5_rarity2_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank5_rarity3_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank5_rarity4_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank5_rarity5_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank5_rarity6_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank6_rarity2_icon = property(lambda _s: _s.rank5_rarity2_icon)
    rank6_rarity3_icon = property(lambda _s: _s.rank5_rarity3_icon)
    rank6_rarity4_icon = property(lambda _s: _s.rank5_rarity4_icon)
    rank6_rarity5_icon = property(lambda _s: _s.rank5_rarity5_icon)
    rank6_rarity6_icon = property(lambda _s: _s.rank5_rarity6_icon)
    rank7_rarity3_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank7_rarity4_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank7_rarity5_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)
    rank7_rarity6_icon = models.ImageField(upload_to=uploadItem('card/icon'), null=True)

    def get_icon(self, rank=7, rarity=None, prefix='', suffix=''):
        if rarity is None:
            rarity = self.rarity
        if rank == 7 and rarity == self.rarity:
            return getattr(self, '{prefix}icon{suffix}'.format(prefix=prefix, suffix=suffix))
        if rarity < self.rarity:
            return None
        return getattr(self, u'{prefix}rank{rank}_rarity{rarity}_icon{suffix}'.format(
            rank=rank, rarity=rarity, prefix=prefix, suffix=suffix))

    def get_all_icons(self, prefix='', suffix=''):
        icons = []
        for rank in range(1, 7 + 1):
            for rarity in range(self.rarity, 6 + 1):
                icon = self.get_icon(rank=rank, rarity=rarity, prefix=prefix, suffix=suffix)
                if icon:
                    icons.append({
                        'rarity': rarity,
                        'rank': rank,
                        'icon': icon,
                    })
        return icons

    ALL_ALT_ICONS_FIELDS = [
        'rank1_rarity2_icon', 'rank1_rarity3_icon', 'rank1_rarity4_icon', 'rank1_rarity5_icon',
        'rank1_rarity6_icon', 'rank2_rarity2_icon', 'rank2_rarity3_icon', 'rank2_rarity4_icon',
        'rank2_rarity5_icon', 'rank2_rarity6_icon', 'rank3_rarity2_icon', 'rank3_rarity3_icon',
        'rank3_rarity4_icon', 'rank3_rarity5_icon', 'rank3_rarity6_icon', 'rank5_rarity2_icon',
        'rank5_rarity3_icon', 'rank5_rarity4_icon', 'rank5_rarity5_icon', 'rank5_rarity6_icon',
        'rank7_rarity3_icon', 'rank7_rarity4_icon', 'rank7_rarity5_icon', 'rank7_rarity6_icon',
    ]

    live2d_model_package = models.FileField(upload_to=uploadItem('card/live2d'), null=True)

    ############################################################
    # Statistics cache

    _cache_j_statistics_ranks = models.TextField(null=True)
    _cache_statistics_ranks_update_on_none = True

    def to_cache_statistics_ranks(self):
        """
        Rank is calculated per rarity and per statistic
        """
        return {
            statistic: (
                type(self).objects.filter(
                    i_rarity=self.i_rarity
                ).filter(**{
                    u'delta_{}__gt'.format(statistic):
                    getattr(self, u'delta_{}'.format(statistic))
                }).values(u'delta_{}'.format(statistic)).distinct().count() + 1
            ) if getattr(self, u'delta_{}'.format(statistic)) else None
            for statistic in self.STATISTICS_FIELDS
        }

    ############################################################
    # Cache stage girl

    _cached_stage_girl_collection_name = 'stagegirl'

    @property
    def cached_stage_girl(self):
        if not self.stage_girl_id:
            return None
        d = {
            'id': self.stage_girl_id,
            'image_url': getStageGirlImageFromPk(self.stage_girl_id),
        }
        d.update(getStageGirlNamesFromPk(self.stage_girl_id))
        return AttrDict(self.cached_json_extra('stage_girl', d))

    ############################################################
    # Cache totals

    _cache_total_collectedcards_days = 1
    _cache_total_collectedcards_last_update = models.DateTimeField(null=True)
    _cache_total_collectedcards = models.PositiveIntegerField(null=True)

    def to_cache_total_collectedcards(self):
        return self.collectedcards.all().count()

    ############################################################
    # Reverse relations

    reverse_related = BaseCard.reverse_related + [
        {
            'field_name': 'collectedcards',
            'verbose_name': lambda: _('Collected {things}').format(things=_('Cards').lower()),
        },
    ]

    ############################################################
    # Views utils

    default_icon = property(lambda _s: staticImageURL('default/default_card_icon.png'))

    ############################################################
    # Unicode

    def __unicode__(self):
        if self.pk:
            return u'{rarity} {element} {stage_girl_name} {name}'.format(
                rarity=self.t_rarity,
                element=self.t_element,
                stage_girl_name=self.cached_stage_girl.t_name if self.stage_girl_id else '',
                name=self.t_name or '',
            )
        return u''

############################################################
# Memoir

class Memoir(BaseCard):
    collection_name = 'memoir'

    ############################################################
    # Basic details: Stage girls, cost, ...

    stage_girls = models.ManyToManyField(
        StageGirl, related_name='%(class)ss', blank=True, verbose_name=_('Stage girls'),
    )

    LIMIT_TO_RARITIES = [1, 2, 3, 4]

    RARITIES = OrderedDict([
        (1, {
            'cost': getStaffConfiguration('memoir_rarity_1_cost', 2),
        }),
        (2, {
            'cost': getStaffConfiguration('memoir_rarity_2_cost', 4),
        }),
        (3, {
            'cost': getStaffConfiguration('memoir_rarity_3_cost', 6),
        }),
        (4, {
            'cost': getStaffConfiguration('memoir_rarity_4_cost', 9),
        }),
        (5, {
            'cost': getStaffConfiguration('memoir_rarity_5_cost', 12),
        }),
        (6, {
            'cost': getStaffConfiguration('memoir_rarity_6_cost', 12),
        }),
    ])
    cost_per_rarity = property(getInfoFromChoices('rarity', RARITIES, 'cost'))
    cost = property(lambda _s: None if _s.is_upgrade else _s.cost_per_rarity)

    is_upgrade = models.BooleanField(_('Upgrade'), default=False)
    is_vs_revue_reward = models.BooleanField(_('VS. Revue reward'), default=False)

    sell_price = models.PositiveIntegerField(_('Selling price'), null=True)

    ############################################################
    # Long texts

    explanation = models.TextField(_('Explanation'), null=True)
    EXPLANATIONS_CHOICES = ALL_ALT_LANGUAGES
    d_explanations = models.TextField(_('Explanation'), null=True)

    ############################################################
    # Images

    rank1_icon = models.ImageField(upload_to=uploadItem('memoir/icon'), null=True)
    rank2_icon = models.ImageField(upload_to=uploadItem('memoir/icon'), null=True)
    rank3_icon = models.ImageField(upload_to=uploadItem('memoir/icon'), null=True)
    rank4_icon = models.ImageField(upload_to=uploadItem('memoir/icon'), null=True)
    rank5_icon = property(lambda _s: _s.icon)

    def get_icon(self, rank=5, prefix='', suffix=''):
        if rank == 5:
            return getattr(self, u'{prefix}icon{suffix}'.format(prefix=prefix, suffix=suffix))
        return getattr(self, u'{prefix}rank{rank}_icon{suffix}'.format(rank=rank, prefix=prefix, suffix=suffix))

    def get_all_icons(self, prefix='', suffix=''):
        icons = []
        for rank in range(1, 5 + 1):
            icon = self.get_icon(rank=rank, prefix=prefix, suffix=suffix)
            if icon:
                icons.append({
                    'rank': rank,
                    'icon': icon,
                })
        return icons

    ALL_ALT_ICONS_FIELDS = [
        'rank1_icon', 'rank2_icon', 'rank3_icon', 'rank4_icon',
    ]

    ############################################################
    # Type

    TYPES = OrderedDict([
        ('upgrade', {
            'icon': 'idolized',
            'translation': _('Upgrade'),
            'filter': lambda _q: _q.filter(is_upgrade=True),
            'is': lambda _s: _s.is_upgrade,
        }),
        ('vs_revue_reward', {
            'icon': 'leaderboard',
            'translation': _('VS. Revue reward'),
            'filter': lambda _q: _q.filter(is_vs_revue_reward=True),
            'is': lambda _s: _s.is_vs_revue_reward,
        }),
    ])
    TYPES.update(BaseCard.TYPES)

    ############################################################
    # Cache totals

    _cache_total_collectedmemoirs_days = 1
    _cache_total_collectedmemoirs_last_update = models.DateTimeField(null=True)
    _cache_total_collectedmemoirs = models.PositiveIntegerField(null=True)

    def to_cache_total_collectedmemoirs(self):
        return self.collectedmemoirs.all().count()

    ############################################################
    # Reverse relations

    reverse_related = BaseCard.reverse_related + [
        {
            'field_name': 'stage_girls',
            'url': 'stagegirls',
            'verbose_name': _('Stage girls'),
            'max_per_line': None,
        },
        {
            'field_name': 'collectedmemoirs',
            'verbose_name': lambda: _('Collected {things}').format(things=_('Memoirs').lower()),
        },
    ]

    ############################################################
    # Views utils

    @property
    def stage_girl(self):
        return list(self.stage_girls.all())[0]

    t_description = property(lambda _s: _s.t_profile)
    element = 'flower'

    default_icon = property(lambda _s: staticImageURL('default/default_memoir_icon.png'))

    ############################################################
    # Unicode

    def __unicode__(self):
        if self.pk:
            return u'{rarity} {name}'.format(
                rarity=self.t_rarity,
                name=self.t_name or '',
            )
        return u''

############################################################
############################################################
# Relive collectible models
############################################################
############################################################

############################################################
# Base collected card

class BaseCollectedCard(AccountAsOwnerModel):
    account = models.ForeignKey(Account, related_name='%(class)ss')

    max_leveled = models.NullBooleanField(_('Max leveled'))

    ############################################################
    # Utils

    @property
    def item_parent(self):
        return getattr(self, self.item_parent_name)

    ############################################################
    # Views utils

    def get_image(self, prefix='', suffix=''):
        raise NotImplementedError('Collected cards require a get_image method.')

    image = property(lambda _s: _s.get_image())
    image_url = property(lambda _s: _s.get_image(suffix='_url'))
    http_image_url = property(lambda _s: _s.get_image(prefix='http_', suffix='_url'))

    art = property(lambda _s: _s.item_parent.art)
    art_url = property(lambda _s: _s.item_parent.art_url)
    http_art_url = property(lambda _s: _s.item_parent.http_art_url)
    art_url_original = property(lambda _s: _s.item_parent.art_original_url)

    color = property(lambda _s: _s.item_parent.element)

    ############################################################
    # Unicode

    def __unicode__(self):
        if self.pk:
            return unicode(self.item_parent)
        return super(BaseCollectedCard, self).__unicode__()

    ############################################################
    # Meta

    class Meta(MagiModel.Meta):
        abstract = True

############################################################
# Collected card

class CollectedCard(BaseCollectedCard):
    collection_name = 'collectedcard'
    item_parent_name = 'card'
    card = models.ForeignKey(Card, related_name='collectedcards', verbose_name=_('Card'))

    max_bonded = models.NullBooleanField(_('Max bonded'))

    RARITIES = BaseCard.RARITIES
    RARITY_CHOICES = BaseCard.RARITY_CHOICES
    RARITY_WITHOUT_I_CHOICES = True
    i_rarity = models.PositiveIntegerField(_('Rarity'), choices=RARITY_CHOICES)
    rarity_image = property(lambda _s: staticImageURL(_s.i_rarity, folder='i_rarity', extension='png'))
    small_rarity_image = property(lambda _s: staticImageURL(_s.i_rarity, folder='small_rarity', extension='png'))

    rank = models.PositiveIntegerField(_('Rank'), default=7, validators=[
        MinValueValidator(1),
        MaxValueValidator(7),
    ])
    rank_image = property(lambda _s: staticImageURL(_s.rank, folder='rank', extension='png'))

    ############################################################
    # Views utils

    def get_image(self, prefix='', suffix=''):
        return (
            self.item_parent.get_icon(rank=self.rank, rarity=self.rarity, prefix=prefix, suffix=suffix)
            or getattr(self.item_parent, u'{prefix}base_icon{suffix}'.format(prefix=prefix, suffix=suffix))
            or staticImageURL('default/default_card_icon.png')
        )

############################################################
# Collected memoir

class CollectedMemoir(BaseCollectedCard):
    collection_name = 'collectedmemoir'
    item_parent_name = 'memoir'
    memoir = models.ForeignKey(Memoir, related_name='collectedmemoirs', verbose_name=_('Memoir'))

    ############################################################
    # Views utils

    @property
    def rank(self):
        if self.max_leveled == False:
            return 1
        return 5

    def get_image(self, prefix='', suffix=''):
        return (
            self.item_parent.get_icon(rank=self.rank, prefix=prefix, suffix=suffix)
            or getattr(self.item_parent, u'{prefix}base_icon{suffix}'.format(prefix=prefix, suffix=suffix))
            or staticImageURL('default/default_memoir_icon.png')
        )
