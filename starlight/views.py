from django.utils.translation import ugettext_lazy as _
from magi.views import (
    custom_wiki,
)
from starlight.settings import (
    WIKI,
)

############################################################
############################################################
# MagiCircles' default views
############################################################
############################################################

############################################################
# Wiki

def wiki(request, context, wiki_url='_Sidebar'):
    return custom_wiki(WIKI, 'wiki', _('Wiki'), request, context, wiki_url)
