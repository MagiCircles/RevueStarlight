from collections import OrderedDict
from django.conf import settings as django_settings
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat
from magi.utils import (
    CuteFormTransform,
    FAVORITE_CHARACTERS_IMAGES,
    getTranslatedName,
    globalContext,
    listUnique,
    mergedFieldCuteForm,
    tourldash,
)

############################################################
# Global context

def starlightGlobalContext(request):
    context = globalContext(request)
    context['extracss_template'] = 'include/extracss.css'
    return context

############################################################
# Models display utils

def displayNames(item):
    """
    Returns the list of displayable names from an item
    """
    return listUnique([
        name for name in [
            unicode(item.t_name),
            item.name,
            item.japanese_name,
        ] if name
    ])

def displayNameHTML(item):
    names = displayNames(item)
    return mark_safe(u'<span>{}</span>{}'.format(
        names[0],
        u'<br><small class="text-muted">{}</small>'.format(
            u'<br>'.join(names[1:])
        ) if len(names) > 1 else '',
    ))

############################################################
# Form choices utils

def getSchoolChoices():
    return BLANK_CHOICE_DASH + [
        (school_id, getTranslatedName(school_details))
        for school_id, school_details in django_settings.SCHOOLS.items()
    ]

def getStageGirlChoices():
    return [
        (id, full_name) for (id, full_name, image) in getattr(
            django_settings, 'FAVORITE_CHARACTERS', [],
        )]

def getVoiceActressChoices():
    return BLANK_CHOICE_DASH + [
        (voiceactress_id, getTranslatedName(voiceactress_details))
        for voiceactress_id, voiceactress_details in django_settings.VOICE_ACTRESSES.items()
    ]

def getVoiceActressNameFromPk(pk):
    return getTranslatedName(django_settings.VOICE_ACTRESSES[int(pk)])

def getVoiceActressThumbnailFromPk(pk):
    return django_settings.VOICE_ACTRESSES[int(pk)]['thumbnail']

def getVoiceActressURLFromPk(pk):
    voiceactress = django_settings.VOICE_ACTRESSES[int(pk)]
    return u'/voiceactress/{}/{}/'.format(pk, tourldash(getTranslatedName(voiceactress)))

############################################################
# CuteForm utils

def getElementsCuteForm(model=None):
    return {
        'to_cuteform': (
            (lambda _k, _v: model.get_reverse_i('element', _k))
            if model
            else 'key'
        ),
        'image_folder': 'color',
        'transform': CuteFormTransform.ImagePath,
    }

def getSchoolsCuteForm():
    return {
        'to_cuteform': lambda _k, _v: django_settings.SCHOOLS[_k]['image'],
    }

def getStageGirlsCuteForm():
    return {
        'to_cuteform': lambda k, v: FAVORITE_CHARACTERS_IMAGES[k],
        'title': _('Stage girl'),
        'extra_settings': {
            'modal': 'true',
            'modal-text': 'true',
        },
    }

def mergeSchoolStageGirlCuteForm(filter_cuteform, ):
    mergedFieldCuteForm(filter_cuteform, {
        'title': string_concat(_('School'), '/', _('Stage girl')),
        'extra_settings': {
            'modal': 'true',
            'modal-text': 'true',
        },
    }, OrderedDict ([
        ('school', lambda k, v: django_settings.SCHOOLS[int(k)]['image']),
        ('stage_girl', lambda k, v: FAVORITE_CHARACTERS_IMAGES[int(k)]),
    ]))

############################################################
# Max statistics

def getMaxStatistic(statistic):
    return django_settings.MAX_STATISTICS.get(statistic, None)
