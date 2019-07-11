from django.conf import settings as django_settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from magi.views import (
    custom_wiki,
    settingsContext,
)
from magi.utils import (
    cuteFormFieldsForContext,
    ordinalNumber,
)
from starlight.settings import (
    MAIN_SITE_URL,
    WIKI,
)
from starlight.utils import (
    getVoiceActressThumbnailFromPk,
)

############################################################
############################################################
# MagiCircles' default views
############################################################
############################################################

############################################################
# Wiki

def wiki(request, wiki_url='_Sidebar'):
    return custom_wiki(WIKI, _('Wiki'), request, wiki_url)

############################################################
# Settings

def settings(request):
    context = settingsContext(request)
    cuteFormFieldsForContext({
        'd_extra-favorite_voiceactress{}'.format(nth): {
            'to_cuteform': lambda k, v: getVoiceActressThumbnailFromPk(k),
            'title': _('{nth} Favorite {thing}').format(
                nth=_(ordinalNumber(nth)),
                thing=_('Voice actress').lower(),
            ),
            'extra_settings': {
                'modal': 'true',
                'modal-text': 'true',
            },
        }
        for nth in range(1, 4)
    }, context, context['forms']['preferences'])
    return render(request, 'pages/settings.html', context)
