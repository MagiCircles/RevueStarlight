# -*- coding: utf-8 -*-
import datetime, pytz
from collections import OrderedDict
from django.conf import settings as django_settings
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language, string_concat
from magi.utils import (
    ordinalNumber,
    tourldash,
)
from magi.default_settings import (
    DEFAULT_ENABLED_NAVBAR_LISTS,
    DEFAULT_ENABLED_PAGES,
    DEFAULT_EXTRA_PREFERENCES,
    DEFAULT_HOME_ACTIVITY_TABS,
    DEFAULT_JAVASCRIPT_TRANSLATED_TERMS,
    DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
    DEFAULT_NAVBAR_ORDERING,
    DEFAULT_PRELAUNCH_ENABLED_PAGES,
)
from starlight.raw import *
from starlight.utils import starlightGlobalContext
from starlight import models

############################################################
# License, game and site settings

SITE_NAME = SITE_NAME
GAME_NAME = GAME_NAME

GAME_DESCRIPTION = _(u"""
Shoujo☆Kageki Revue Starlight (Lit. Girls☆Opera Revue Starlight) is a multi-media project produced by Bushiroad and Nelke Planning. It aims to link the world of anime and musicals together. Besides the anime series and the musical performances, the voice actresses also perform live concerts and various events for fans. The characters from the license also appear in 3 manga series and a mobile game called "Relive".
""")

GAME_URL = '/wiki/About%20Revue%20Starlight/'

COLOR = '#1A1D24'

############################################################
# Images

CORNER_POPUP_IMAGE = 'giraffe.png'
CORNER_POPUP_IMAGE_OVERFLOW = True

SITE_IMAGE = 'starlight_academy.png'
SITE_LOGO = 'starlight_academy_logo.png'

ABOUT_PHOTO = 'about.png'

DONATE_IMAGE = 'donate.png'
EMAIL_IMAGE = 'email.png'

EMPTY_IMAGE = 'empty_crown.png'

############################################################
# Settings per languages

SITE_NAME_PER_LANGUAGE = SITE_NAME_PER_LANGUAGE

SITE_LOGO_PER_LANGUAGE = {
    'ja': 'starlight_academy_logo_japanese.png',
}

SITE_IMAGE_PER_LANGUAGE = {
    'ja': 'starlight_academy_japanese.png',
}

############################################################
# Contact & Social

CONTACT_EMAIL = 'contact@starlight.academy'
CONTACT_REDDIT = 'Ragefire2b'
CONTACT_FACEBOOK = 'revuestarlight.en'
CONTACT_DISCORD = 'https://discordapp.com/invite/dZ93wsW'

FEEDBACK_FORM = 'https://forms.gle/6aRWq6zNhPBz9UGHA'
GITHUB_REPOSITORY = ('MagiCircles', 'RevueStarlight')
WIKI = GITHUB_REPOSITORY

TWITTER_HANDLE = 'r_starlight_en'
HASHTAGS = ['スタァライト', 'RevueStarlight', 'Starira', 'RevueStarlightReLIVE']

############################################################
# Homepage

HOMEPAGE_BACKGROUND = 'background_gradient.png'
HOMEPAGE_BACKGROUND = 'background.png'
HOMEPAGE_ART_GRADIENT = True

HOMEPAGE_ART_SIDE = 'right'
HOMEPAGE_ART_POSITION = {
    'position': 'center left',
    'size': '150%',
    'y': '40%',
    'x': '0%',
}

HOME_ACTIVITY_TABS = DEFAULT_HOME_ACTIVITY_TABS.copy()
if 'staffpicks' in HOME_ACTIVITY_TABS:
    del(HOME_ACTIVITY_TABS['staffpicks'])

############################################################
# First steps

FIRST_COLLECTION = 'collectedcard'
GET_STARTED_VIDEO = 'WLfi932cfFI'

############################################################
# User preferences and profiles

FAVORITE_CHARACTER_NAME = _('Stage girl')
FAVORITE_CHARACTER_TO_URL = lambda link: (
    u'/stagegirl/{pk}/{name}/'.format(pk=link.raw_value, name=tourldash(link.value)))

CUSTOM_PREFERENCES_FORM = True

EXTRA_PREFERENCES = DEFAULT_EXTRA_PREFERENCES + [
    ('favorite_voiceactress1', lambda: _('{nth} Favorite {thing}').format(
        thing=_('Voice actress').lower(), nth=_(ordinalNumber(1)))),
    ('favorite_voiceactress2', lambda: _('{nth} Favorite {thing}').format(
        thing=_('Voice actress').lower(), nth=_(ordinalNumber(2)))),
    ('favorite_voiceactress3', lambda: _('{nth} Favorite {thing}').format(
        thing=_('Voice actress').lower(), nth=_(ordinalNumber(3)))),
]

ACCOUNT_TAB_ORDERING = [
    'about',
    'collectedcard',
    'collectedmemoir',
]

MAX_LEVEL_BEFORE_SCREENSHOT_REQUIRED = 70

############################################################
# Donators

DONATORS_STATUS_CHOICES = (
    ('THANKS', 'Thanks'),
    ('SUPPORTER', 'Seisho student'),
    ('LOVER', 'Revue performer'),
    ('AMBASSADOR', 'Play stage manager'),
    ('PRODUCER', 'Revue producer'),
    ('DEVOTEE', 'Starlight reached'),
)

############################################################
# Activities

MINIMUM_LIKES_POPULAR = 5

ACTIVITY_TAGS = [
    # Revue Starlight
    ('revuestarlight', lambda: LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME)),
    ('stagegirls', _('Stage girls')),
    ('voiceactresses', _('Voice actresses')),
    ('anime', lambda: u'{} / {} / {} ({})'.format(
        _('Anime'),
        _('Manga'),
        _('Movie'),
        LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME),
    )),
    ('irlevent', lambda: u'{} / {} ({})'.format(
        _('Meetups'),
        _('Events'),
        LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME),
    )),

    # Relive
    ('relive', lambda: SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(), SMARTPHONE_GAME)),
    ('cards', _('Cards')),
    ('gacha', _('Gacha')),
    ('event', lambda: u'{} ({})'.format(
        _('Events'),
        SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(), SMARTPHONE_GAME),
    )),
    ('mytheater', _('My theater')),
    ('song', _('Songs')),
] + [
    (_version, _details['translation'])
    for _version, _details in models.VERSIONS.items()
] + [

    # Community
    ('introduction', _('Introduce yourself')),
    ('comedy', _('Comedy')),
    ('meme', _('Meme')),
    ('birthday', _('Birthday')),
    ('cosplay', _('Cosplay')),
    ('fanart', _('Fanart')),
    ('edit', _('Graphic edit')),
    ('merch', _('Merchandise')),
    ('community', _('Community')),
    ('question', _('Question')),

    # Restricted / meta
    ('staff', {
        'translation': _('News'),
        'has_permission_to_add': lambda r: r.user.is_staff and r.user.hasPermission('mark_activities_as_staff_pick'),
    }),
    ('communityevent', {
        'translation': _('Community event'),
        'has_permission_to_add': lambda r: r.user.hasPermission('post_community_event_activities'),
    }),
    ('unrelated', lambda: _('Not about {thing}').format(
        thing=LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME),
    )),
    ('swearing', _('Swearing')),
    ('questionable', {
        'translation': _('Questionable'),
    }),
    ('nsfw', {
        'translation': _('NSFW'),
        'hidden_by_default': True,
        'has_permission_to_show': lambda r: u'{} {}'.format(_('You need to be over 18 years old.'), _('You can change your birthdate in your settings.') if not r.user.preferences.age else u'') if r.user.is_authenticated() and r.user.preferences.age < 18 else True,
    }),
]

############################################################
# Technical settings

MAIN_SITE_URL = 'https://revuestarlight-en.net/'
SITE_URL = 'https://starlight.academy/'
SITE_URL = 'http://localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else 'https://starlight.academy/'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.starlight.academy/'

GET_GLOBAL_CONTEXT = starlightGlobalContext

DISQUS_SHORTNAME = 'starlight-academy'
GOOGLE_ANALYTICS = 'UA-142986850-1'

ACCOUNT_MODEL = models.Account

USER_COLORS = [
    (_element, _details['translation'], _element, _details['color'])
    for _element, _details in models.ELEMENTS.items()
]

JAVASCRIPT_TRANSLATED_TERMS = DEFAULT_JAVASCRIPT_TRANSLATED_TERMS + [
    'Lyrics',
    'Open {thing}',
    'Close',
]

############################################################
# From settings or generated_settings

STATIC_FILES_VERSION = django_settings.STATIC_FILES_VERSION
STAFF_CONFIGURATIONS = getattr(django_settings, 'STAFF_CONFIGURATIONS', {})
HOMEPAGE_ARTS = getattr(django_settings, 'HOMEPAGE_ARTS', None)
TOTAL_DONATORS = getattr(django_settings, 'TOTAL_DONATORS', 0) or 2
FAVORITE_CHARACTERS = getattr(django_settings, 'FAVORITE_CHARACTERS', None)
# todo BACKGROUNDS = getattr(django_settings, 'BACKGROUNDS', None)
LATEST_NEWS = getattr(django_settings, 'LATEST_NEWS', None)

############################################################
# Customize pages

ENABLED_PAGES = DEFAULT_ENABLED_PAGES.copy()

# Enable wiki for relive
ENABLED_PAGES['wiki'][0]['enabled'] = True
ENABLED_PAGES['wiki'][0]['custom'] = True
ENABLED_PAGES['wiki'][1]['enabled'] = True
ENABLED_PAGES['wiki'][0]['navbar_link'] = False

# Add voice actress cuteform to settings
ENABLED_PAGES['settings']['custom'] = True

def _externalLinkIcon(title):
    return mark_safe(u'{} <i class="flaticon-link fontx0-8"></i>'.format(title))

# Redirect to main site for some non-migrated pages
ENABLED_PAGES['about_revuestarlight'] = {
    'title': lambda _l: _('About {thing}').format(thing=LICENSE_NAME_PER_LANGUAGE.get(
        get_language(), LICENSE_NAME)),
    'redirect': '/wiki/About%20Revue%20Starlight/',
    'icon': 'about',
    'navbar_link_list': 'revuestarlight',
    'divider_after': True,
    'check_permissions': lambda c: c['request'].LANGUAGE_CODE not in DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
}

ENABLED_PAGES['news_revuestarlight'] = {
    'title': _('News'),
    'redirect': '/news/revuestarlight/',
    'icon': 'new',
    'navbar_link_list': 'revuestarlight',
    'divider_before': True,
    'check_permissions': lambda c: c['request'].LANGUAGE_CODE not in DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
}

ENABLED_PAGES['about_relive'] = {
    'title': lambda _l: _('About {thing}').format(thing=SMARTPHONE_GAME_PER_LANGUAGE.get(
        get_language(),SMARTPHONE_GAME)),
    'redirect': '/wiki/Get%20started%20with%20Relive/',
    'icon': 'about',
    'navbar_link_list': 'relive',
    'divider_after': True,
    'check_permissions': lambda c: c['request'].LANGUAGE_CODE not in DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
}

ENABLED_PAGES['news_relive'] = {
    'title': _('News'),
    'redirect': '/news/relive/',
    'icon': 'new',
    'navbar_link_list': 'relive',
    'divider_before': True,
    'divider_after': True,
    'check_permissions': lambda c: c['request'].LANGUAGE_CODE not in DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
}

SOCIAL_MEDIA_LINKS = OrderedDict([
    ('discord', {
        'image': 'discord',
        'url': 'https://discordapp.com/invite/dZ93wsW',
        'title': _externalLinkIcon('Discord'),
        'divider_before': True,
    }),
    ('reddit', {
        'image': 'reddit',
        'url': 'https://www.reddit.com/r/RevueStarlight',
        'title': _externalLinkIcon('Reddit'),
    }),
    ('twitter', {
        'icon': 'twitter',
        'url': 'https://twitter.com/r_starlight_en',
        'title': _externalLinkIcon('Twitter'),
    }),
    ('facebook', {
        'image': 'facebook',
        'url': 'https://www.facebook.com/revuestarlight.en',
        'title': _externalLinkIcon('Facebook'),
    }),
])

for _link_name, _link in SOCIAL_MEDIA_LINKS.items():
    ENABLED_PAGES[_link_name] = {
        'title': _link['title'],
        'icon': _link.get('icon', None),
        'image': _link.get('image', None),
        'redirect': _link['url'],
        'divider_before': _link.get('divider_before', False),
        'navbar_link_list': 'community',
        'new_tab': True,
        'check_permissions': lambda c: c['request'].LANGUAGE_CODE not in DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
}

############################################################
# Customize nav bar

ENABLED_NAVBAR_LISTS = DEFAULT_ENABLED_NAVBAR_LISTS.copy()

ENABLED_NAVBAR_LISTS['revuestarlight'] = {
    'title': lambda _l: LICENSE_NAME_PER_LANGUAGE.get(get_language(),LICENSE_NAME),
    'image': 'revuestarlight_icon',
    'order': [
        'about_revuestarlight',

        'stagegirl_list',
        'voiceactress_list',

        'news_revuestarlight',
        'song_list',
        'lyrics',

        'staff_list'
    ],
}

ENABLED_NAVBAR_LISTS['relive'] = {
    'title': lambda _l: SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(),SMARTPHONE_GAME),
    'image': 'relive_icon',
    'order': [
        'about_relive',

        'card_list',
        'memoir_list',
        'event_list',
        'conversation_list',
        'stageofdream',

        'wiki',
        'news_relive',

        'account_list',

        'gallery',
        'comic_list',
    ],
}

ENABLED_NAVBAR_LISTS['community'] = {
    'title': _('Community'),
    'icon': 'users',
    'order': [
        'activity_list',
        'user_list',
    ] + SOCIAL_MEDIA_LINKS.keys(),
}

NAVBAR_ORDERING = [
    'revuestarlight',
    'relive',
    'community',
] + DEFAULT_NAVBAR_ORDERING
