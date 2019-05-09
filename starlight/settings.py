# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _, get_language, string_concat
from magi.default_settings import (
    DEFAULT_ENABLED_NAVBAR_LISTS,
    DEFAULT_NAVBAR_ORDERING,
    DEFAULT_ENABLED_PAGES,
    DEFAULT_LANGUAGES_CANT_SPEAK_ENGLISH,
)
from starlight import models

############################################################
# License, game and site settings

SITE_NAME = 'Revue Starlight International'
GAME_NAME = u'SHOUJO☆KAGEKI REVUE STARLIGHT'
LICENSE_NAME = 'Revue Starlight'
SMARTPHONE_GAME = 'ReLIVE'

# todo GAME_DESCRIPTION = ''
# todo GAME_URL = ''

COLOR = '#1A1D24'

# SITE_LONG_DESCRIPTION = 'todo'

############################################################
# Prelaunch details

LAUNCH_DATE = True
# todo LAUNCH_DATE = datetime.datetime(2019, 06, 01, 12, 0, 0, tzinfo=pytz.UTC)

############################################################
# Images

SITE_IMAGE = 'starlight.png'
# todo SITE_NAV_LOGO = ''

ABOUT_PHOTO = 'about.png'

# todo DONATE_IMAGE = ''
# todo EMAIL_IMAGE = ''

EMPTY_IMAGE = 'empty_crown.png'

############################################################
# Settings per languages

GAME_NAME_PER_LANGUAGE = {
    'ja': u'少女 歌劇 レヴュースタァライト',
}

LICENSE_NAME_PER_LANGUAGE = {
    'ja': u'レヴュースタァライト',
}

SMARTPHONE_GAME_PER_LANGUAGE = {
    'ja': 'Re LIVE',
}

############################################################
# Contact & Social

# todo CONTACT_EMAIL = ''
# todo CONTACT_REDDIT = ''
# todo CONTACT_FACEBOOK = ''

# todo FEEDBACK_FORM = ''
GITHUB_REPOSITORY = ('MagiCircles', 'RevueStarlight')

TWITTER_HANDLE = 'r_starlight_en'
HASHTAGS = ['スタァライト', 'RevueStarlight', 'Starira', 'RevueStarlightReLIVE']

############################################################
# User preferences and profiles

FAVORITE_CHARACTER_NAME = _('Stage girl')
FAVORITE_CHARACTER_TO_URL = lambda link: (
    '/stagegirl/{pk}/{name}/'.format(pk=link.raw_value, name=tourldash(link.value)))

############################################################
# Donators

# todo DONATORS_STATUS_CHOICES = ''

############################################################
# Activities

ACTIVITY_TAGS = [
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
        'translation': _('Staff picks'),
        'has_permission_to_add': lambda r: r.user.is_staff,
    }),
    ('communityevent', {
        'translation': _('Community event'),
        'has_permission_to_add': lambda r: r.user.hasPermission('post_community_event_activities'),
    }),
    ('unrelated',  (_('Not about %(game)s') % { 'game': _('BanG Dream!') })),
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
SITE_URL = 'https://starlight-sandbox.db0.company/'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.starlight-sandbox.db0.company/'

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
TOTAL_DONATORS = getattr(django_settings, 'TOTAL_DONATORS', 0) or 2
FAVORITE_CHARACTERS = getattr(django_settings, 'FAVORITE_CHARACTERS', None)
# todo BACKGROUNDS = getattr(django_settings, 'BACKGROUNDS', None)
LATEST_NEWS = getattr(django_settings, 'LATEST_NEWS', None)

############################################################
# Customize pages

ENABLED_PAGES = DEFAULT_ENABLED_PAGES.copy()

ENABLED_PAGES['wiki'][0]['enabled'] = True
ENABLED_PAGES['wiki'][1]['enabled'] = True
ENABLED_PAGES['wiki'][0]['divider_before'] = True
ENABLED_PAGES['wiki'][0]['navbar_link_list'] = 'relive'

ENABLED_PAGES['index']['custom'] = True
ENABLED_PAGES['index']['enabled'] = True

ENABLED_PAGES['about_revuestarlight'] = {
    'title': lambda _l: _('About {thing}').format(thing=LICENSE_NAME_PER_LANGUAGE.get(
        get_language(),LICENSE_NAME)),
    'redirect': u'{}what-is-revue-starlight/'.format(MAIN_SITE_URL),
    'icon': 'about',
    'navbar_link_list': 'revuestarlight',
    'divider_after': True,
}

ENABLED_PAGES['news'] = {
    'title': _('News'),
    'redirect': u'{}category/news/'.format(MAIN_SITE_URL),
    'icon': 'new',
    'navbar_link_list': 'revuestarlight',
    'divider_before': True,
}

ENABLED_PAGES['lyrics'] = {
    'title': _('Lyrics'),
    'redirect': u'{}category/lyrics/'.format(MAIN_SITE_URL),
    'icon': 'music',
    'navbar_link_list': 'revuestarlight',
}

ENABLED_PAGES['about_relive'] = {
    'title': lambda _l: _('About {thing}').format(thing=SMARTPHONE_GAME_PER_LANGUAGE.get(
        get_language(),SMARTPHONE_GAME)),
    'redirect': u'{}relive_wiki/Beginner%27s_Guide'.format(MAIN_SITE_URL),
    'icon': 'about',
    'navbar_link_list': 'relive',
    'divider_after': True,
}

SOCIAL_MEDIA_LINKS = OrderedDict([
    ('discord', {
        'image': 'discord',
        'url': 'https://discordapp.com/invite/dZ93wsW',
        'title': 'Discord',
        'divider_before': True,
    }),
    ('reddit', {
        'image': 'reddit',
        'url': 'https://www.reddit.com/r/RevueStarlight',
        'title': 'Reddit',
    }),
    ('twitter', {
        'icon': 'twitter',
        'url': 'https://twitter.com/r_starlight_en',
        'title': 'Twitter',
    }),
    ('facebook', {
        'image': 'facebook',
        'url': 'https://www.facebook.com/revuestarlight.en',
        'title': 'Facebook',
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

if django_settings.DEBUG:

    ENABLED_PAGES['gallery'] = {
        'title': _('Gallery'),
        'redirect': '#',
        'icon': 'pictures',
        'divider_before': True,
        'navbar_link_list': 'relive',
    }

    ENABLED_PAGES['stageofdream'] = {
        'title': _('Stage of dream'),
        'redirect': '#',
        'icon': 'leaderboard',
        'navbar_link_list': 'relive',
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

        'news',
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

        'account_list',

        'gallery',
        'comic_list',
    ],
}

ENABLED_NAVBAR_LISTS['community'] = {
    'title': _('Community'),
    'icon': 'users',
    'order': [
        'user_list',
        'activity_list',
    ] + SOCIAL_MEDIA_LINKS.keys(),
}

NAVBAR_ORDERING = [
    'revuestarlight',
    'relive',
    'community',
] + DEFAULT_NAVBAR_ORDERING
