from django.conf import settings as django_settings
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from magi.views import (
    settingsContext,
)
from magi.utils import (
    cuteFormFieldsForContext,
    ordinalNumber,
)
from starlight.settings import MAIN_SITE_URL
from starlight.utils import (
    getVoiceActressThumbnailFromPk,
)

############################################################
############################################################
# MagiCircles' default views
############################################################
############################################################

############################################################
# Index

def index(request):
    return redirect('/prelaunch/')
    # todo when prelaunch ends return redirect(MAIN_SITE_URL)

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
