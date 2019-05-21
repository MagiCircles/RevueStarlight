from django.conf import settings as django_settings
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
    AttrDict,
    CuteFormType,
    CuteFormTransform,
    ordinalNumber,
    setSubField,
    staticImageURL,
)
from starlight.django_translated import t
from starlight.utils import (
    getElementsCuteForm,
    getSchoolsCuteForm,
    getStageGirlsCuteForm,
    getVoiceActressNameFromPk,
    getVoiceActressThumbnailFromPk,
    getVoiceActressURLFromPk,
    mergeSchoolStageGirlCuteForm,
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
    icon = 'users'
    navbar_link = True
    navbar_link_list = 'community'

    def navbar_link_title(self, context):
        return t['users'].title()

    class ItemView(_UserCollection.ItemView):

        def get_meta_links(self, user, *args, **kwargs):
            first_links, meta_links, links = super(UserCollection.ItemView, self).get_meta_links(
                user, *args, **kwargs)
            # Add link to favorite voice actresses from preferences
            for nth in reversed(range(1, 4)):
                field_name = 'favorite_voiceactress{}'.format(nth)
                voiceactress_pk = user.preferences.extra.get(field_name, None)
                if voiceactress_pk:
                    meta_links.insert(0, AttrDict({
                        'name': field_name,
                        'verbose_name': _('{nth} Favorite {thing}').format(
                            thing=_('Voice actress').lower(), nth=_(ordinalNumber(nth))),
                        'value': getVoiceActressNameFromPk(voiceactress_pk),
                        'raw_value': voiceactress_pk,
                        'url': getVoiceActressURLFromPk(voiceactress_pk),
                        'image': getVoiceActressThumbnailFromPk(voiceactress_pk),
                    }))
            return (first_links, meta_links, links)

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
    plural_name = 'voiceactresses'
    title = _('Voice actress')
    plural_title = _('Voice actresses')
    navbar_link_list = 'revuestarlight'
    navbar_link_title = _('Cast')
    icon = 'voice-actress'
    form_class = forms.VoiceActressForm
    translated_fields = ('name', 'specialty', 'hobbies', 'm_description')
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
        'links': 'url',
        'video': 'film',
    }

    fields_images = {
        'astrological_sign': lambda _i: _i.astrological_sign_image_url,
    }

    filter_cuteform = {
        'i_astrological_sign': {
        },
        'i_blood': {
            'type': CuteFormType.HTML,
        },
        'school': getSchoolsCuteForm(),
    }

    def to_fields(self, view, item, *args, **kwargs):
        fields = super(VoiceActressCollection, self).to_fields(
            view, item, *args, **kwargs)

        # Age
        setSubField(fields, 'birthday', key='type', value='text_annotation')
        setSubField(fields, 'birthday', key='annotation', value=item.display_age)

        return fields

    class ListView(MainItemCollection.ListView):
        per_line = 5
        page_size = 20
        show_items_names = True
        default_ordering = 'name'
        filter_form = forms.VoiceActressFilterForm

        def ordering_fields(self, item, only_fields=None, *args, **kwargs):
            # Show birthday when ordring by birthday
            return super(VoiceActressCollection.ListView, self).ordering_fields(
                item, only_fields=(only_fields or []) + (
                    ['birthday'] if 'birthday_month' in only_fields
                    else []), *args, **kwargs)

    class ItemView(MainItemCollection.ItemView):
        fields_prefetched = ['stagegirls']
        fields_prefetched_together = ['links']
        comments_enabled = False

############################################################
# Voice Actress Link Collection

class VoiceActressLinkCollection(MainItemCollection):
    queryset = models.VoiceActressLink.objects.all().select_related('voice_actress')
    title = string_concat(_('Voice actress'), ' - ', _('Link'))
    plural_title = string_concat(_('Voice actress'), ' - ', _('Links'))
    icon = 'link'
    navbar_link_list = 'staff'
    one_permissions_required = ['manage_main_items', 'translate_items']
    translated_fields = ('name',)
    form_class = forms.VoiceActressLinkForm

    class ListView(MainItemCollection.ListView):
        display_style = 'table'
        display_style_table_fields = ['voice_actress', 'name', 'url']
        show_item_buttons_as_icons = True

    class ItemView(MainItemCollection.ItemView):
        enabled = False
        fields_preselected = ['voice_actress'] # used by table_fields in list view

    class AddView(MainItemCollection.AddView):
        back_to_list_button = False

        def redirect_after_add(self, request, item, ajax):
            return item.voice_actress.item_url if not ajax else '/ajax/successadd/'

    class EditView(MainItemCollection.EditView):
        back_to_list_button = False

        def redirect_after_edit(self, request, item, ajax):
            return item.voice_actress.item_url if not ajax else '/ajax/successedit/'

############################################################
# School Collection

class SchoolCollection(MainItemCollection):
    queryset = models.School.objects.all()
    title = _('School')
    plural_title = _('Schools')
    navbar_link_list = 'staff'
    icon = 'school'
    translated_fields = ('name', 'm_description')
    multipart = True

    fields_icons = {
        'name': 'school',
        'description': 'about',
        'students': 'idol',
    }

    class ItemView(MainItemCollection.ItemView):
        fields_prefetched_together = ['students']

    class ListView(MainItemCollection.ListView):
        show_items_names = True
        staff_required = True
        permissions_required = ['manage_main_items']

        def has_permissions_to_see_in_navbar(self, request, context):
            super(SchoolCollection.ListView, self).has_permissions_to_see_in_navbar(request, context)
            return (request.user.is_authenticated()
                    and request.user.hasPermission('manage_main_items'))

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
        'weapon_type',
        'favorite_food',
        'least_favorite_food',
        'likes', 'dislikes',
        'hobbies',
        'm_description',
    ]

    fields_icons = {
        'name': 'id',
        'voice_actress': 'voice-actress',
        'school': 'school',
        'birthday': 'event',
        'color': 'palette',
        'year': 'education',
        'weapon': 'skill',
        'favorite_food': 'food-like',
        'least_favorite_food': 'food-dislike',
        'likes': 'heart',
        'dislikes': 'heart-empty',
        'hobbies': 'hobbies',
        'description': 'id',
        'video': 'film',
    }

    fields_images = {
        'astrological_sign': lambda _i: _i.astrological_sign_image_url,
        'cards': 'dresses.png',
    }

    filter_cuteform = {
        'i_astrological_sign': {
        },
        'school': getSchoolsCuteForm(),
        'i_year': {
            'type': CuteFormType.HTML,
        },
    }

    def after_save(self, request, instance, type=None):
        super(StageGirlCollection, self).after_save(request, instance, type=type)
        # Update cards caches when stage girls get edited
        for card in instance.cards.all():
            card.force_update_cache('stage_girl')
        return instance

    class ListView(MainItemCollection.ListView):
        show_items_names = True
        default_ordering = 'school'
        per_line = 5
        page_size = 20
        filter_form = forms.StageGirlFilterForm

    class ItemView(MainItemCollection.ItemView):
        fields_preselected = ['voice_actress', 'school']
        fields_prefetched_together = ['cards']
        fields_exclude = ['small_image', 'weapon_type']

        def to_fields(self, item, *args, **kwargs):
            fields = super(StageGirlCollection.ItemView, self).to_fields(item, *args, **kwargs)
            if item.weapon_type:
                setSubField(fields, 'weapon', key='type', value='text_annotation')
                setSubField(fields, 'weapon', key='annotation', value=item.t_weapon_type)
            return fields

############################################################
# Staff Collection

class StaffCollection(MainItemCollection):
    queryset = models.Staff.objects.all()
    title = _('Staff')
    plural_title = ('Staff')
    navbar_link_list = 'revuestarlight'
    navbar_link_list_divider_before = True
    icon = 'list'
    translated_fields = ('name', 'role')

    class ListView(MainItemCollection.ListView):
        default_ordering = '-importance,role'
        display_style = 'table'
        display_style_table_fields = ['role', 'name']
        show_item_buttons_as_icons = True

        def table_fields(self, item, *args, **kwargs):
            fields = super(StaffCollection.ListView, self).table_fields(item, *args, **kwargs)
            if item.social_media_url:
                setSubField(fields, 'name', key='type', value='link')
                setSubField(fields, 'name', key='link_text', value=item.display_name)
                setSubField(fields, 'name', key='value', value=item.social_media_url)
            return fields

    class ItemView(MainItemCollection.ItemView):
        enabled = False

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
    navbar_link_title = string_concat(_('Dresses'), ' (', _('Cards'), ')')
    image = 'red_dresses'
    form_class = forms.CardForm
    multipart = True
    translated_fields = [
        'name',
        'description',
        'profile',
        'message',
    ]

    filter_cuteform = {
        'i_rarity': {
            'image_folder': 'small_rarity',
        },
        'i_element': getElementsCuteForm(models.Card),
        'i_damage': {
        },
        'i_position': {
        },
        'type': {
            'to_cuteform': lambda _k, _v: models.Card.TYPES[_k]['icon'],
            'transform': CuteFormTransform.Flaticon,
        },
        'stage_girl': getStageGirlsCuteForm(),
        'resists_against': getElementsCuteForm(),
        'weak_against': getElementsCuteForm(),
    }
    mergeSchoolStageGirlCuteForm(filter_cuteform)

    fields_icons = {
        'number': 'hashtag',
        'stage_girl': 'idol',
        'name': 'id',
        'limited': 'hourglass',
        'description': 'about',
        'profile': 'id',
        'message': 'chat',
        'roles': 'staff',
    }
    fields_icons.update({
        _statistic: 'hp' if '_hp' in _statistic else 'statistics'
        for _statistic in models.Card.ALL_STATISTICS_FIELDS
    })

    fields_images = {
        'position': lambda _i: _i.position_image,
        'rarity': 'rarity.png',
        'element': lambda _i: _i.element_image,
        'damage': lambda _i: _i.damage_icon_image,
    }

    def to_fields(self, view, item, *args, **kwargs):
        fields = super(CardCollection, self).to_fields(
            view, item, *args, **kwargs)

        # Show rarity as images
        setSubField(fields, 'rarity', key='type', value='image')
        setSubField(fields, 'rarity', key='value', value=item.rarity_image)

        # Limited / permanent
        if not item.limited:
            setSubField(fields, 'limited', key='icon', value='chest')
            setSubField(fields, 'limited', key='verbose_name', value=_('Permanent'))
            setSubField(fields, 'limited', key='value', value=True)

        # Roles -> Role
        if len(item.roles) == 1:
            setSubField(fields, 'roles', key='verbose_name', value=_('Role'))
        return fields

    class ListView(MainItemCollection.ListView):
        default_ordering = 'number'
        filter_form = forms.CardFilterForm
        ajax_callback = 'loadCardsFilters'

    class ItemView(MainItemCollection.ItemView):
        fields_exclude = models.Card.ALL_STATISTICS_FIELDS
        ajax_callback = 'loadCard'

        def to_fields(self, item, extra_fields=None, *args, **kwargs):
            if extra_fields is None: extra_fields = []

            # Resists / Weak
            for field_name, verbose_name in [
                    ('resists', _('Resists against')),
                    ('weak', _('Weak against')),
            ]:
                images = []
                for element in getattr(item, u'elements_{}_against'.format(field_name)):
                    i_element = models.Card.get_i('element', element)
                    t_element = models.Card.get_verbose_i('element', i_element)
                    parameters = { 'i_element': i_element }
                    images.append({
                        'link': self.collection.get_list_url(parameters=parameters),
                        'ajax_link': self.collection.get_list_url(
                            ajax=True, modal_only=True, parameters=parameters),
                        'link_text': t_element,
                        'tooltip': t_element,
                        'value': staticImageURL(element, folder='color', extension='png'),
                    })
                if images:
                    extra_fields.append((field_name, {
                        'image': staticImageURL(field_name, extension='png'),
                        'verbose_name': verbose_name,
                        'type': 'images_links',
                        'images': images,
                    }))
                else:
                    extra_fields.append((field_name, {
                        'image': staticImageURL(field_name, extension='png'),
                        'verbose_name': verbose_name,
                        'type': 'text',
                        'value': _('None'),
                    }))

            # Cost
            extra_fields.append(('cost', {
                'verbose_name': _('Cost'),
                'type': 'text',
                'value': item.cost,
                'icon': 'money',
            }))

            # Statistics
            extra_fields.append(('statistics', {
                'verbose_name': _('Statistics'),
                'icon': 'statistics',
                'type': 'html',
                'value': item.display_statistics,
                'spread_across': True
            }))

            fields = super(CardCollection.ItemView, self).to_fields(
                item, *args, extra_fields=extra_fields, **kwargs)
            return fields

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
