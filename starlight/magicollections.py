from django.utils.translation import ugettext_lazy as _, string_concat
from magi.magicollections import (
    MagiCollection,
    MainItemCollection,
    StaffConfigurationCollection as _StaffConfigurationCollection,
    DonateCollection as _DonateCollection,
    ActivityCollection as _ActivityCollection,
    AccountCollection as _AccountCollection,
    UserCollection as _UserCollection,
)
from starlight import models, forms

############################################################
############################################################
# MagiCircles' default collections
############################################################
############################################################

############################################################
# StaffConfiguration Collection

class StaffConfigurationCollection(_StaffConfigurationCollection):
    enabled = True

############################################################
# Donate Collection

class DonateCollection(_DonateCollection):
    enabled = True

############################################################
# User Collection

class UserCollection(_UserCollection):
    navbar_link = True
    navbar_link_list = 'community'
    navbar_link_title = _('Users')
    icon = 'users'

############################################################
# Activity Collection

class ActivityCollection(_ActivityCollection):
    navbar_link = True
    navbar_link_list = 'community'
    navbar_link_title = _('Feed')

    class ListView(_ActivityCollection.ListView):
        shortcut_urls = [
            _url for _url in _ActivityCollection.ListView.shortcut_urls
            if _url != ''
        ]

        def show_homepage(self, context):
            return True

        def show_sidebar_on_homepage(self, context):
            return True

############################################################
# Account Collection

class AccountCollection(_AccountCollection):
    navbar_link_list = 'relive'
    icon = 'trophy'

############################################################
############################################################
# Revue Starlight collections
############################################################
############################################################

############################################################
# Voice Actress Collection

class VoiceActressCollection(MainItemCollection):
    queryset = models.VoiceActress.objects.all()
    title = _('Voice actress')
    plural_title = _('Voice actresses')
    navbar_link_list = 'revuestarlight'
    navbar_link_title = _('Cast')
    icon = 'voice-actress'
    translated_fields = ('name', 'specialty', 'hobbies', 'm_description')
    form_class = forms.VoiceActressForm
    multipart = True

############################################################
# School Collection

class SchoolCollection(MainItemCollection):
    queryset = models.School.objects.all()
    title = _('School')
    plural_title = _('Schools')
    navbar_link_list = 'staff'
    icon = 'school'
    form_class = forms.SchoolForm
    translated_fields = ('name', 'm_description')
    multipart = True

############################################################
# Stage Girl Collection

class StageGirlCollection(MainItemCollection):
    queryset = models.StageGirl.objects.all()
    title = _('Stage girl')
    plural_title = _('Stage girls')
    navbar_link_list = 'revuestarlight'
    icon = 'idol'
    form_class = forms.StageGirlForm
    multipart = True
    translated_fields = [
        'name',
        'weapon',
        'favorite_food',
        'least_favorite_food',
        'likes', 'dislikes',
        'hobbies',
        'm_description',
    ]

    def after_save(self, request, instance, type=None):
        super(StageGirlCollection, self).after_save(request, instance, type=type)
        # Update cards caches when stage girls get edited
        for card in instance.cards.all():
            card.force_update_cache('stage_girl')
        return instance

############################################################
# Staff Collection

class StaffCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Staff')
    plural_title = ('Staff')
    navbar_link_list = 'revuestarlight'
    navbar_link_list_divider_before = True
    icon = 'list'

############################################################
# Song Collection

class SongCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Song')
    plural_title = _('Songs')
    navbar_link_list = 'revuestarlight'
    navbar_link_title = _('Discography')
    icon = 'album'

############################################################
############################################################
# Re LIVE collections
############################################################
############################################################

############################################################
# Card Collection

class CardCollection(MainItemCollection):
    queryset = models.Card.objects.all()
    title = _('Card')
    plural_title = _('Cards')
    navbar_link_list = 'relive'
    icon = 'cards'
    form_class = forms.CardForm
    multipart = True
    translated_fields = [
        'name',
    ]

    class ListView(MainItemCollection.ListView):
        default_ordering = 'number'

############################################################
# Memoir Collection

class MemoirCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Memoir')
    plural_title = _('Memoirs')
    navbar_link_list = 'relive'
    icon = 'idolized'

############################################################
# Event Collection

class EventCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Event')
    plural_title = _('Events')
    navbar_link_list = 'relive'
    icon = 'event'

############################################################
# Conversation Collection

class ConversationCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Conversation')
    plural_title = _('Conversations')
    navbar_link_list = 'relive'
    navbar_link_title = _('My theater')
    icon = 'chat'

############################################################
# Comic Collection

class ComicCollection(MainItemCollection):
    queryset = models.Account.objects.all() # todo
    title = _('Comic')
    plural_title = _('Comics')
    navbar_link_list = 'relive'
    icon = 'album'
