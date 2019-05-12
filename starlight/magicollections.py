from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat, get_language
from magi.magicollections import (
    MagiCollection,
    MainItemCollection,
    StaffConfigurationCollection as _StaffConfigurationCollection,
    DonateCollection as _DonateCollection,
    ActivityCollection as _ActivityCollection,
    AccountCollection as _AccountCollection,
    UserCollection as _UserCollection,
)
from magi.utils import (
    setSubField,
    listUnique,
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

    fields_icons = {
        'name': 'id',
        'birthday': 'event',
        'height': 'measurements',
        'blood': 'healer',
        'specialty': 'star',
        'hobbies': 'hobbies',
        'description': 'id',
        'stagegirls': 'idol',
    }

    fields_images = {
        'astrological_sign': lambda _i: _i.astrological_sign_image_url,
    }

    def to_fields(self, view, item, *args, **kwargs):
        fields = super(VoiceActressCollection, self).to_fields(
            view, item, *args, **kwargs)

        names = listUnique([
            unicode(item.t_name),
            item.name,
            item.japanese_name,
        ])
        if len(names) > 1:
            setSubField(fields, 'name', key='type', value='text_annotation')
            setSubField(fields, 'name', key='annotation', value=mark_safe(u'<br>'.join(names[1:])))
        return fields

    class ListView(MainItemCollection.ListView):
        per_line = 3
        show_items_names = True

    class ItemView(MainItemCollection.ItemView):
        def get_queryset(self, queryset, parameters, request):
            queryset = super(VoiceActressCollection.ItemView, self).get_queryset(queryset, parameters, request)
            queryset = queryset.prefetch_related('stagegirls')
            return queryset

        def to_fields(self, item, prefetched_together=None, *args, **kwargs):

            # Prefetched
            if prefetched_together is None: prefetched_together = []
            prefetched_together += ['stagegirls']

            fields = super(VoiceActressCollection.ItemView, self).to_fields(
                item, prefetched_together=prefetched_together, *args, **kwargs)
            return fields

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
