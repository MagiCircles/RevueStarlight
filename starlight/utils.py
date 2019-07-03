from __future__ import division
from collections import OrderedDict
from math import floor
from django.conf import settings as django_settings
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat, get_language
from magi.utils import (
    CuteFormTransform,
    FAVORITE_CHARACTERS_IMAGES,
    FAVORITE_CHARACTERS_NAMES,
    getFavoriteCharacterChoices,
    getFavoriteCharacterImageFromPk,
    getFavoriteCharacterNamesFromPk,
    getFavoriteCharacterNameFromPk,
    getTranslatedName,
    globalContext,
    listUnique,
    ordinalNumber,
    mergedFieldCuteForm,
    staticImageURL,
    tourldash,
    translationURL,
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

def displayNamesRomajiFirst(item):
    """
    Returns the list of displayable names from an item, with priority to romaji is exists
    """
    language = get_language()
    if language == 'ja':
        names = [
            item.japanese_name or item.name,
        ]
    elif language in ['kr', 'zh-hant', 'zh-hans']:
        names = [
            item.japanese_name or item.name,
            item.names.get(language, None),
        ]
    else:
        names = [
            item.romaji_name or item.name,
            unicode(item.t_name),
            item.names.get('ja', None),
        ]
    return listUnique([name for name in names if name])

def displayNameHTML(item, romaji_first=False):
    if romaji_first:
        names = displayNamesRomajiFirst(item)
    else:
        names = displayNames(item)
    if not names:
        return ''
    return mark_safe(u'<span>{}</span>{}'.format(
        names[0],
        u'<br><small class="text-muted">{}</small>'.format(
            u'<br>'.join(names[1:])
        ) if len(names) > 1 else '',
    ))

############################################################
# Form choices utils

def getSchoolChoices(without_other=False):
    return BLANK_CHOICE_DASH + [
        (school_id, getTranslatedName(school_details))
        for school_id, school_details in django_settings.SCHOOLS.items()
        if not without_other or (without_other and school_details['name'] != 'Other')
    ]

getStageGirlNamesFromPk = getFavoriteCharacterNamesFromPk
getStageGirlNameFromPk = getFavoriteCharacterNameFromPk
getStageGirlChoices = getFavoriteCharacterChoices

def getStageGirlImageFromPk(pk):
    return getFavoriteCharacterImageFromPk(pk, default=staticImageURL('default/default_stagegirl.png'))

def getVoiceActressChoices():
    return BLANK_CHOICE_DASH + [
        (voiceactress_id, getTranslatedName(voiceactress_details))
        for voiceactress_id, voiceactress_details in django_settings.VOICE_ACTRESSES.items()
    ]

def getVoiceActressNameFromPk(pk):
    return getTranslatedName(django_settings.VOICE_ACTRESSES[int(pk)])

def getVoiceActressThumbnailFromPk(pk):
    return django_settings.VOICE_ACTRESSES[int(pk)]['thumbnail'] or staticImageURL('default/default.png')

def getVoiceActressURLFromPk(pk):
    voiceactress = django_settings.VOICE_ACTRESSES[int(pk)]
    return u'/voiceactress/{}/{}/'.format(pk, tourldash(getTranslatedName(voiceactress)))

def getSchoolNameFromPk(pk):
    return getTranslatedName(django_settings.SCHOOLS[int(pk)])

def getSchoolImageFromPk(pk):
    return django_settings.SCHOOLS[int(pk)]['image'] or staticImageURL('default/default_school.png')

def getSchoolURLFromPk(pk, ajax=False):
    school = django_settings.SCHOOLS[int(pk)]
    return u'{}/school/{}/{}'.format(
        u'/ajax' if ajax else u'', pk,
        u'' if ajax else u'{}/'.format(tourldash(getSchoolNameFromPk(pk))))

def getSchoolYearChoices():
    return [
        ('first', _(u'{nth} year').format(nth=_(ordinalNumber(1)))),
        ('second', _(u'{nth} year').format(nth=_(ordinalNumber(2)))),
        ('third', _(u'{nth} year').format(nth=_(ordinalNumber(3)))),
    ]

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

def getSchoolsCuteForm(white=False):
    return {
        'to_cuteform': lambda k, v: getSchoolImageFromPk(k),
    }

def getStageGirlsCuteForm():
    return {
        'to_cuteform': lambda k, v: getStageGirlImageFromPk(k),
        'title': _('Stage girl'),
        'extra_settings': {
            'modal': 'true',
            'modal-text': 'true',
        },
    }

def mergeSchoolStageGirlCuteForm(filter_cuteform):
    mergedFieldCuteForm(filter_cuteform, {
        'title': string_concat(_('School'), '/', _('Stage girl')),
        'extra_settings': {
            'modal': 'true',
            'modal-text': 'true',
        },
    }, OrderedDict ([
        ('school', lambda k, v: getSchoolImageFromPk(k)),
        ('stage_girl', lambda k, v: getStageGirlImageFromPk(int(k))),
    ]))

def mergeSingersCuteForm(filter_cuteform):
    mergedFieldCuteForm(filter_cuteform, {
        'title': _('Singers'),
        'extra_settings': {
            'modal': 'true',
            'modal-text': 'true',
        },
    }, OrderedDict ([
        ('singers', lambda k, v: getVoiceActressThumbnailFromPk(int(k))),
        ('stage_girl', lambda k, v: getStageGirlImageFromPk(int(k))),
        ('school', lambda k, v: getSchoolImageFromPk(k)),
    ]), merged_field_name='singer')

############################################################
# Max statistics

def getMaxStatistic(collection_name, statistic, prefix, default=0):
    prefix = {
        'base_': 'delta_',
        'min_level_': 'max_level_',
    }.get(prefix, prefix)
    return (
        django_settings.MAX_STATISTICS.get(collection_name, {}).get(prefix, {}).get(statistic, None)
        or default
    )

############################################################
# Statistics formulas

def memoirStatisticFormula(base, delta, level):
    if base is None or delta is None:
        return None
    return base + floor((delta * (level - 1)) / 1000)

def calculateMemoirStatistics(memoir):
    for statistic in memoir.STATISTICS_FIELDS:
        setattr(memoir, u'min_level_{}'.format(statistic), memoirStatisticFormula(
            base=getattr(memoir, u'base_{}'.format(statistic)),
            delta=getattr(memoir, u'delta_{}'.format(statistic)),
            level=memoir.min_level,
        ))
        setattr(memoir, u'max_level_{}'.format(statistic), memoirStatisticFormula(
            base=getattr(memoir, u'base_{}'.format(statistic)),
            delta=getattr(memoir, u'delta_{}'.format(statistic)),
            level=memoir.max_level,
        ))

############################################################
# Translations utils

def displayTextWithJapaneseFallback(item, field_name, one_line=False):
    language = get_language()
    if language == 'en':
        value_in_language = getattr(item, field_name)
    elif language == 'ja':
        value_in_language = getattr(item, u'japanese_{}'.format(field_name))
    else:
        value_in_language = getattr(item, u'{}s'.format(field_name)).get(language, None)
    if value_in_language:
        return value_in_language
    fallback_value = ('en', getattr(item, field_name))
    if not fallback_value[1]:
        fallback_value = ('ja', getattr(item, u'japanese_{}'.format(field_name)))
    if not fallback_value[1]:
        return ''
    return mark_safe(translationURL(
        fallback_value[1], from_language=fallback_value[0], to_language=language,
        with_wrapper=True, one_line=one_line,
    ))
