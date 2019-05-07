from django.conf import settings as django_settings
from starlight import models

# Configure and personalize your website here.

SITE_NAME = 'Sample Website'
SITE_URL = 'http://starlight.com/'
SITE_IMAGE = 'starlight.png'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.starlight.com/'
GAME_NAME = 'Sample Game'
DISQUS_SHORTNAME = 'starlight'
ACCOUNT_MODEL = models.Account
COLOR = '#4a86e8'
