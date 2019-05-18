from django.conf import settings as django_settings
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from magi.utils import (
    getTranslatedName,
    listUnique,
    tourldash,
)

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
