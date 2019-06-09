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
    DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
    DEFAULT_NAVBAR_ORDERING,
    DEFAULT_PRELAUNCH_ENABLED_PAGES,
)
from starlight.utils import starlightGlobalContext
from starlight import models

############################################################
# License, game and site settings

SITE_NAME = 'Starlight Academy'
LICENSE_NAME = 'Revue Starlight'
GAME_NAME = LICENSE_NAME
SMARTPHONE_GAME = 'ReLIVE'

# todo GAME_DESCRIPTION = ''
# todo GAME_URL = ''

COLOR = '#1A1D24'

# SITE_LONG_DESCRIPTION = 'todo'

############################################################
# Prelaunch details

LAUNCH_DATE = datetime.datetime(2019, 06, 11, 4, 0, 0, tzinfo=pytz.UTC)

PRELAUNCH_ENABLED_PAGES = DEFAULT_PRELAUNCH_ENABLED_PAGES
PRELAUNCH_ENABLED_PAGES += [
    'news_list',
]

############################################################
# Images

CORNER_POPUP_IMAGE = 'giraffe.png'
CORNER_POPUP_IMAGE_OVERFLOW = True

SITE_IMAGE = 'starlight_academy.png'
SITE_LOGO = 'starlight_academy_logo.png'

ABOUT_PHOTO = 'about.png'

# todo DONATE_IMAGE = ''
# todo EMAIL_IMAGE = ''

EMPTY_IMAGE = 'empty_crown.png'

############################################################
# Settings per languages

SITE_NAME_PER_LANGUAGE = {
    'ja': u'スタァライト アカデミー',
    'kr': u'스타라이트 아카데미',
    'zh-hant': u'星光學院',
}

GAME_NAME_PER_LANGUAGE = {
    'ja': u'少女☆歌劇 レヴュースタァライト',
    'kr': u'소녀가극 레뷰 스타라이트',
    'zh-hant': u'少女☆歌劇 Revue Starlight',
}

LICENSE_NAME_PER_LANGUAGE = {
    'ja': u'レヴュースタァライト',
    'kr': u'레뷰 스타라이트',
    'zh-hant': u'Revue Starlight',
}

SMARTPHONE_GAME_PER_LANGUAGE = {
    'ja': 'Re LIVE',
    'kr': u'스타리라',
    'zh-hant': 'Relive',
}

SITE_LOGO_PER_LANGUAGE = {
    'ja': 'starlight_academy_logo_japanese.png',
}

SITE_IMAGE_PER_LANGUAGE = {
    'ja': 'starlight_academy_japanese.png',
}

############################################################
# Contact & Social

# todo CONTACT_EMAIL = ''
CONTACT_REDDIT = 'Ragefire2b'
# todo CONTACT_FACEBOOK = ''

FEEDBACK_FORM = 'https://forms.gle/6aRWq6zNhPBz9UGHA'
GITHUB_REPOSITORY = ('MagiCircles', 'RevueStarlight')

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
    '/stagegirl/{pk}/{name}/'.format(pk=link.raw_value, name=tourldash(link.value)))

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

MAX_LEVEL_BEFORE_SCREENSHOT_REQUIRED = 50

############################################################
# Donators

# todo DONATORS_STATUS_CHOICES = ''

############################################################
# Activities

ACTIVITY_TAGS = [
    ('revuestarlight', lambda: LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME)),
    ('relive', lambda: SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(), SMARTPHONE_GAME)),
    ('comedy', _('Comedy')),
    ('meme', _('Meme')),
    ('cards', _('Cards')),
    ('scout', _('Scouting')),
    ('event', _('Event')),
    ('song', _('Songs')),
    ('introduction', _('Introduce yourself')),
    ('members', _('Characters')),
    ('birthday', _('Birthday')),
    ('anime', string_concat(_('Anime'), ' / ', _('Manga'))),
    ('cosplay', _('Cosplay')),
    ('fanart', _('Fanart')),
    ('edit', _('Graphic edit')),
    ('merch', _('Merchandise')),
    ('community', _('Community')),
    ('question', _('Question')),
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
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.starlight.academy/'

GET_GLOBAL_CONTEXT = starlightGlobalContext

DISQUS_SHORTNAME = 'starlight'
# todo GOOGLE_ANALYTICS = ''

ACCOUNT_MODEL = models.Account

USER_COLORS = [
    (_element, _details['translation'], _element, _details['color'])
    for _element, _details in models.ELEMENTS.items()
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
ENABLED_PAGES['wiki'][1]['enabled'] = True
ENABLED_PAGES['wiki'][0]['divider_before'] = True
ENABLED_PAGES['wiki'][0]['navbar_link_list'] = 'relive'

# Add voice actress cuteform to settings
ENABLED_PAGES['settings']['custom'] = True

def _externalLinkIcon(title):
    return mark_safe(u'{} <i class="flaticon-link fontx0-8"></i>'.format(title))

# Redirect to main site for some non-migrated pages
ENABLED_PAGES['about_revuestarlight'] = {
    'title': lambda _l: _externalLinkIcon(_('About {thing}').format(thing=LICENSE_NAME_PER_LANGUAGE.get(
        get_language(), LICENSE_NAME))),
    'redirect': u'{}what-is-revue-starlight/'.format(MAIN_SITE_URL),
    'icon': 'about',
    'navbar_link_list': 'revuestarlight',
    'divider_after': True,
}

ENABLED_PAGES['news_revuestarlight'] = {
    'title': _('News'),
    'redirect': '/news/?c_tags=revuestarlight',
    'icon': 'new',
    'navbar_link_list': 'revuestarlight',
    'divider_before': True,
}

ENABLED_PAGES['lyrics'] = {
    'title': lambda _l: _externalLinkIcon(_('Lyrics')),
    'redirect': u'{}category/lyrics/'.format(MAIN_SITE_URL),
    'icon': 'music',
    'navbar_link_list': 'revuestarlight',
}

ENABLED_PAGES['about_relive'] = {
    'title': lambda _l: _externalLinkIcon(_('About {thing}').format(thing=SMARTPHONE_GAME_PER_LANGUAGE.get(
        get_language(),SMARTPHONE_GAME))),
    'redirect': u'{}relive_wiki/Beginner%27s_Guide'.format(MAIN_SITE_URL),
    'icon': 'about',
    'navbar_link_list': 'relive',
    'divider_after': True,
}

ENABLED_PAGES['news_relive'] = {
    'title': _('News'),
    'redirect': '/news/?c_tags=relive',
    'icon': 'new',
    'navbar_link_list': 'relive',
    'divider_before': True,
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
