from collections import OrderedDict
from django.conf import settings as django_settings
from django.db.models import Prefetch
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat, get_language
from magi.forms import get_account_simple_form
from magi.magicollections import (
    MagiCollection,
    MainItemCollection,
    SubItemCollection,
    custom_item_template,
    StaffConfigurationCollection as _StaffConfigurationCollection,
    DonateCollection as _DonateCollection,
    ActivityCollection as _ActivityCollection,
    AccountCollection as _AccountCollection,
    UserCollection as _UserCollection,
    BadgeCollection as _BadgeCollection,
    PrizeCollection as _PrizeCollection,
)
from magi.middleware.httpredirect import HttpRedirectException # Todo: Should be removed after launch
from magi.utils import (
    AttrDict,
    CuteFormType,
    CuteFormTransform,
    getMagiCollection,
    ordinalNumber,
    setSubField,
    staticImageURL,
)
from starlight.django_translated import t
from starlight.settings import SMARTPHONE_GAME_PER_LANGUAGE, SMARTPHONE_GAME
from starlight.utils import (
    getElementsCuteForm,
    getSchoolsCuteForm,
    getStageGirlsCuteForm,
    getVoiceActressNameFromPk,
    getVoiceActressThumbnailFromPk,
    getVoiceActressURLFromPk,
    mergeSchoolStageGirlCuteForm,
    mergeSingersCuteForm,
)
from starlight import models, forms

############################################################
############################################################
# MagiCircles' default collections
############################################################
############################################################

############################################################
# Badge Collection

class BadgeCollection(_BadgeCollection):
    enabled = True

############################################################
# Prize Collection

class PrizeCollection(_PrizeCollection):
    enabled = True

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

    filter_cuteform = _UserCollection.filter_cuteform.copy()
    filter_cuteform.update({
        'favorite_voice_actress': {
            'to_cuteform': lambda k, v: getVoiceActressThumbnailFromPk(k),
            'title': _('Voice actress'),
            'extra_settings': {
                'modal': 'true',
                'modal-text': 'true',
            },
        },
    })

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

    class ListView(_UserCollection.ListView):
        filter_form = forms.UserFilterForm
        ajax_callback = 'loadUsersFilters'

############################################################
# News Collection

class NewsCollection(_ActivityCollection):
    queryset = _ActivityCollection.queryset.filter(c_tags__contains='"staff"')
    plural_name = 'news'
    title = _('News')
    plural_title = _('News')

    def buttons_per_item(self, view, *args, **kwargs):
        buttons = super(NewsCollection, self).buttons_per_item(view, *args, **kwargs)

        # Change URLs to use /news/ instead of /activities/

        for button in buttons.values():
            for field_name in ['url', 'ajax_url']:
                if button.get(field_name, None):
                    button[field_name] = button[field_name].replace(
                        '/activity/', '/news/').replace('/activities/', '/news/')

        return buttons

    class ItemView(_ActivityCollection.ItemView):
        template = 'activityItem'
        ajax_callback = 'loadActivities'

    class ListView(_ActivityCollection.ListView):
        item_template = 'activityItem'
        shortcut_urls = ['']
        default_ordering = '-creation'
        filter_form = forms.NewsFilterForm
        add_button_subtitle = None
        ajax_pagination_callback = 'loadActivities'

        def top_buttons(self, request, context):
            # Call parents super to avoid adding warning button
            return super(_ActivityCollection.ListView, self).top_buttons(request, context)

        def extra_context(self, context):
            super(NewsCollection.ListView, self).extra_context(context)
            context['activity_tabs'] = None
            context['show_bump'] = True

            # Show a popup to tell people about the feed
            if (context['request'].user.is_authenticated()
                and context['request'].LANGUAGE_CODE == 'en'):
                context['corner_popups']['about_feed'] = {
                    'title': u'Starlight Academy is a social network.',
                    'content': 'Did you know? You can post activities and scroll through hundreds of activities posted by our community of Revue Starlight fans like you.',
                    'image': context['corner_popup_image'],
                    'image_overflow': context['corner_popup_image_overflow'],
                    'buttons': {
                        'feed': {
                            'title': 'Take me to the feed!',
                            'url': '/activities/',
                        },
                    },
                    'allow_close_remind': 5,
                    'allow_close_forever': True,
                }

    def _redirect_after_modification(self, request, item, ajax):
        return (item.ajax_item_url if ajax else item.item_url).replace(
            '/activity/', '/news/').replace('/activities/', '/news/')

    def _after_save(self, request, instance, type=None):
        if hasattr(instance, 'forced_creation'):
            instance.creation = instance.forced_creation
            instance.save()
        return instance

    class AddView(_ActivityCollection.AddView):
        staff_required = True
        permissions_required = ['mark_activities_as_staff_pick']
        form_class = forms.NewsForm
        max_per_user_per_hour = None

        def after_save(self, request, instance, type=None):
            instance = super(NewsCollection.AddView, self).after_save(request, instance, type=type)
            return self.collection._after_save(request, instance)

        def redirect_after_add(self, *args, **kwargs):
            return self.collection._redirect_after_modification(*args, **kwargs)

    class EditView(_ActivityCollection.EditView):
        staff_required = True
        permissions_required = ['mark_activities_as_staff_pick']
        form_class = forms.NewsForm

        def after_save(self, request, instance, type=None):
            instance = super(NewsCollection.EditView, self).after_save(request, instance, type=type)
            return self.collection._after_save(request, instance)

        def redirect_after_edit(self, *args, **kwargs):
            return self.collection._redirect_after_modification(*args, **kwargs)

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
        ] + ['feed']
        ajax_pagination_callback = 'loadActivities'

        def show_homepage(self, context):
            return True

        def show_sidebar_on_homepage(self, context):
            return False

        def extra_context(self, context):
            super(ActivityCollection.ListView, self).extra_context(context)
            context['hide_header'] = True
            context['show_title'] = True
            context['art'] = None
            context['h1_page_title'] = string_concat(_('Community'), ' - ', _('Feed'))

    class ItemView(_ActivityCollection.ItemView):
        ajax_callback = 'loadActivities'

############################################################
# Account Collection

class AccountCollection(_AccountCollection):
    title = _('Relive account')
    navbar_link_list = 'relive'
    icon = 'trophy'
    form_class = forms.AccountForm

    filter_cuteform = _AccountCollection.filter_cuteform.copy()
    filter_cuteform.update({
        'accept_friend_requests': {
            'type': CuteFormType.YesNo,
        },
        'i_vs_revue_rank': {
        },
        'i_version': {
            'to_cuteform': lambda _k, _v: models.VERSIONS[
                models.Account.get_reverse_i('version', _k)
            ]['image'],
            'image_folder': 'language',
            'transform': CuteFormTransform.ImagePath,
        },
        'i_play_style': {
            'type': CuteFormType.HTML,
        },
        'i_play_style': {
            'type': CuteFormType.HTML,
        },
        'i_os': {
            'to_cuteform': lambda _k, _v: models.Account.OS_CHOICES[_k].lower(),
            'transform': CuteFormTransform.FlaticonWithText,
        },
        'center': {
            'to_cuteform': lambda _k, _v: _v.image_url,
            'title': _('Center'),
            'extra_settings': {
                'modal': 'true',
                'modal-text': 'true',
            },
        }
    })

    fields_icons = {
        'play_style': lambda _i: _i.play_style_icon,
        'os': lambda _i: _i.os_icon,
        'device': lambda _i: _i.os_icon or 'id',
    }

    fields_images = {
        'version': lambda _i: _i.version_image,
        'stage_of_dreams_level': 'stage_of_dreams.png',
        'vs_revue_rank': lambda _i: _i.vs_revue_rank_image,
        'bought_stars': 'stars.png',
    }

    class ListView(_AccountCollection.ListView):
        filter_form = forms.AccountFilterForm
        ajax_callback = 'loadAccountsFilters'

    class AddView(_AccountCollection.AddView):
        simpler_form = get_account_simple_form(forms.AccountForm, simple_fields=[
            'nickname', 'i_version', 'level', 'friend_id',
        ])

        def redirect_after_add(self, request, item, ajax):
            if not ajax:
                return '/cards/?get_started&add_to_collectedcard={account_id}&view=icons&version={account_version}&ordering=number&reverse_order='.format(
                    account_id=item.id,
                    account_version=item.version,
                )
            return super(AccountCollection.AddView, self).redirect_after_add(request, item, ajax)

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
    translated_fields = [
        'name',
        'specialty',
        'hobbies',
        'm_description',
        'm_staff_description',
        'video',
    ]

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
        'fans': 'heart',
        'songs': 'song',
        'staff_description': 'chat',
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
        'school': getSchoolsCuteForm(white=True),
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

        def get_queryset(self, queryset, parameters, request):
            queryset = super(VoiceActressCollection.ListView, self).get_queryset(queryset, parameters, request)

            # When ordering by stage girl name, prefetch stage girls
            if parameters.get('ordering', None) == 'stagegirls__name':
                queryset = queryset.prefetch_related('stagegirls')

            return queryset

        def ordering_fields(self, item, only_fields=None, prefetched_together=None, *args, **kwargs):
            if prefetched_together is None: prefetched_together = []
            only_fields = (only_fields or [])[:]

            # Show stage girl(s) when ordering by stage girl name
            if 'stagegirls__name' in only_fields:
                prefetched_together.append('stagegirls')
                only_fields.append('stagegirls')

            # Show birthday when ordring by birthday
            if 'birthday_month' in only_fields:
                only_fields.append('birthday')

            fields = super(VoiceActressCollection.ListView, self).ordering_fields(
                item, only_fields=only_fields, prefetched_together=prefetched_together, *args, **kwargs)

            return fields

    class ItemView(MainItemCollection.ItemView):
        fields_prefetched = ['stagegirls']
        fields_prefetched_together = ['links', 'songs']
        fields_exclude = ['birthday_banner']
        comments_enabled = False

        def to_fields(self, item, prefetched_together=None, *args, **kwargs):
            if prefetched_together is None: prefetched_together = []
            prefetched_together += [
                'fans',
            ]
            fields = super(VoiceActressCollection.ItemView, self).to_fields(
                item, *args, prefetched_together=prefetched_together, **kwargs)
            return fields

    class EditView(MainItemCollection.EditView):
        def to_translate_form_class(self):
            super(VoiceActressCollection.EditView, self).to_translate_form_class()
            self._translate_form_class = forms.to_translate_voice_actress_form_class(self._translate_form_class)

############################################################
# Voice Actress Link Collection

class VoiceActressLinkCollection(SubItemCollection):
    main_collection = 'voiceactress'
    main_fk = 'voice_actress'
    main_related = 'links'

    queryset = models.VoiceActressLink.objects.all().select_related('voice_actress')
    title = string_concat(_('Voice actress'), ' - ', _('Link'))
    plural_title = string_concat(_('Voice actress'), ' - ', _('Links'))
    icon = 'link'
    translated_fields = ('name',)

    class ListView(SubItemCollection.ListView):
        display_style = 'table'
        display_style_table_fields = ['voice_actress', 'name', 'url']
        show_item_buttons_as_icons = True
        auto_filter_form = True

    class ItemView(SubItemCollection.ItemView):
        enabled = False
        fields_preselected = ['voice_actress'] # used by table_fields in list view

############################################################
# School Collection

class SchoolCollection(SubItemCollection):
    main_collection = 'stagegirl'
    main_many2many = True
    main_related = 'school'

    queryset = models.School.objects.all()
    title = _('School')
    plural_title = _('Schools')
    form_class = forms.SchoolForm

    icon = 'school'
    translated_fields = ('name', 'm_description')

    fields_icons = {
        'name': 'school',
        'description': 'about',
        'students': 'idol',
    }

    class ItemView(SubItemCollection.ItemView):
        fields_exclude = [
            'white_image',
            'monochrome_image',
        ]
        fields_prefetched_together = ['students']

    class ListView(SubItemCollection.ListView):
        default_ordering = 'id'
        show_items_names = True

############################################################
# Stage Girl Collection

class StageGirlCollection(MainItemCollection):
    queryset = models.StageGirl.objects.all()
    title = _('Stage girl')
    plural_title = _('Stage girls')
    navbar_link_list = 'revuestarlight'
    icon = 'idol'
    form_class = forms.StageGirlForm
    translated_fields = [
        'name',
        'weapon',
        'weapon_type',
        'school_department',
        'favorite_food',
        'least_favorite_food',
        'likes', 'dislikes',
        'hobbies',
        'introduction',
        'm_description',
        'video',
    ]

    fields_icons = {
        'name': 'id',
        'voice_actress': 'voice-actress',
        'school': 'school',
        'school_department': 'school',
        'birthday': 'event',
        'color': 'palette',
        'year': 'education',
        'weapon': 'skill',
        'favorite_food': 'food-like',
        'least_favorite_food': 'food-dislike',
        'likes': 'heart',
        'dislikes': 'heart-empty',
        'hobbies': 'hobbies',
        'introduction': 'id',
        'description': 'about',
        'video': 'film',
        'fans': 'heart',
    }

    fields_images = {
        'astrological_sign': lambda _i: _i.astrological_sign_image_url,
        'cards': 'dresses.png',
        'memoirs': 'memoirs.png',
    }

    filter_cuteform = {
        'i_astrological_sign': {
        },
        'i_year': {
            'type': CuteFormType.HTML,
        },
    }

    class ListView(MainItemCollection.ListView):
        show_items_names = True
        default_ordering = 'school'
        per_line = 5
        page_size = 30
        filter_form = forms.StageGirlFilterForm
        show_section_header_on_change = 'school_id'

        def get_queryset(self, queryset, parameters, request):
            queryset = super(StageGirlCollection.ListView, self).get_queryset(queryset, parameters, request)

            # When ordering by voice actress name, select related voice actress
            if parameters.get('ordering', None) == 'voice_actress__name':
                queryset = queryset.select_related('voice_actress')

            return queryset

        def ordering_fields(self, item, only_fields=None, preselected=None, *args, **kwargs):
            if preselected is None: preselected = []
            only_fields = (only_fields or [])[:]

            # Show voice actress when ordering by voice actress name
            if 'voice_actress__name' in only_fields:
                preselected.append('voice_actress')
                only_fields.append('voice_actress')

            fields = super(StageGirlCollection.ListView, self).ordering_fields(
                item, only_fields=only_fields, preselected=preselected, *args, **kwargs)

            return fields

    class ItemView(MainItemCollection.ItemView):
        fields_preselected = ['voice_actress', 'school']
        fields_prefetched_together = ['cards', 'memoirs']
        fields_exclude = ['small_image', 'uniform_image', 'square_image', 'weapon_type', 'birthday_banner']

        def to_fields(self, item, prefetched_together=None, *args, **kwargs):
            if prefetched_together is None: prefetched_together = []
            prefetched_together += [
                'fans',
            ]
            fields = super(StageGirlCollection.ItemView, self).to_fields(
                item, *args, prefetched_together=prefetched_together, **kwargs)
            if item.weapon_type:
                setSubField(fields, 'weapon', key='type', value='text_annotation')
                setSubField(fields, 'weapon', key='annotation', value=item.t_weapon_type)
            return fields

############################################################
# Staff Collection

class StaffCollection(MainItemCollection):
    queryset = models.Staff.objects.all()
    plural_name = 'staff'
    title = _('Staff')
    plural_title = ('Staff')
    navbar_link_list = 'revuestarlight'
    navbar_link_list_divider_before = True
    icon = 'list'
    translated_fields = ('name', 'role', 'm_description')

    class ListView(MainItemCollection.ListView):
        default_ordering = 'i_category,-importance,-role'
        display_style = 'table'
        display_style_table_fields = ['role', 'name', 'm_description']
        show_item_buttons_as_icons = True
        show_section_header_on_change = 'i_category'
        ajax_pagination_callback = 'loadStaff'

        def table_fields(self, item, *args, **kwargs):
            fields = super(StaffCollection.ListView, self).table_fields(item, *args, **kwargs)
            if item.social_media_url:
                setSubField(fields, 'name', key='type', value='link')
                setSubField(fields, 'name', key='link_text', value=item.display_name)
                setSubField(fields, 'name', key='value', value=item.social_media_url)
            return fields

        def table_fields_headers(self, fields, view=None):
            return []

        # Show voice actresses before all staff
        # 1st school = anime staff, go before staff
        # Other schools = game only staff, go staff

        before_template = 'include/staffAllVoiceActressesAnime'
        after_template = 'include/staffAllVoiceActressesGame'

        def extra_context(self, context):
            super(StaffCollection.ListView, self).extra_context(context)
            context['anime_voice_actresses_section_header'] = string_concat(_('Anime'), ' - ', _('Cast'))
            context['game_voice_actresses_section_header'] = string_concat(
                SMARTPHONE_GAME_PER_LANGUAGE.get(
                    context['request'].LANGUAGE_CODE, SMARTPHONE_GAME,
                ), ' - ', _('Cast'),
            )
            context['anime_voice_actresses'] = []
            context['game_voice_actresses'] = []
            for item in models.VoiceActress.objects.prefetch_related(
                    'stagegirls').order_by('stagegirls__school_id').distinct():
                stage_girls = list(item.stagegirls.all())
                item.table_fields = OrderedDict([
                    ('role', {
                        'type': 'list_links',
                        'links': [{
                            'value': mark_safe(u'<span style="color: {color};">{stage_girl}</span>'.format(
                                color=stage_girl.color, stage_girl=unicode(stage_girl)
                            )),
                            'link': stage_girl.item_url,
                            'ajax_stage_girl': stage_girl.ajax_item_url,
                        } for stage_girl in stage_girls],
                    } if stage_girls else {
                        'type': 'text',
                        'value': _('Voice actress'),
                    }),
                    ('name', {
                        'type': 'link',
                        'link_text': item.display_name,
                        'value': item.item_url,
                        'ajax_link': item.ajax_item_url,
                    }),
                    ('description', {
                        'type': 'markdown',
                        'value': (False, item.t_m_staff_description),
                    } if item.m_staff_description else {}),
                ])
                if stage_girls and stage_girls[0].school_id in [1, 5]:
                    context['anime_voice_actresses'].append(item)
                else:
                    context['game_voice_actresses'].append(item)

    class ItemView(MainItemCollection.ItemView):
        enabled = False

############################################################
# Song Collection

class SongCollection(MainItemCollection):
    queryset = models.Song.objects.all()
    title = _('Song')
    plural_title = _('Songs')
    navbar_link_list = 'revuestarlight'
    navbar_link_title = string_concat(_('Discography'), ' / ', _('Lyrics'))
    icon = 'song'
    form_class = forms.SongForm

    translated_fields = ['name', 'm_lyrics'] + models.Song.CREDITS_FIELDS

    filter_cuteform = {}
    mergeSingersCuteForm(filter_cuteform)

    fields_icons = {
        'name': 'song',
        'itunes_id': 'play',
        'length': 'times',
        'bpm': 'hp',
        'release_date': 'date',
        'lyrics': 'translate',
        'japanese_lyrics': 'list',
        'romaji_lyrics': 'list',
        'singers': 'voice-actress',
        'buy_url': 'shop',
    }
    fields_icons.update({ _f: 'id' for _f in models.Song.CREDITS_FIELDS })

    def to_fields(self, view, item, *args, **kwargs):
        fields = super(SongCollection, self).to_fields(view, item, *args, **kwargs)

        # Buy URL labels
        label = _('Buy {thing}').format(thing=_('CD'))
        setSubField(fields, 'buy_url', key='link_text', value=label)
        setSubField(fields, 'buy_url', key='verbose_name', value=label)

        return fields

    class ListView(MainItemCollection.ListView):
        default_ordering = '-release_date'
        filter_form = forms.SongFilterForm
        show_title = True
        show_items_names = True
        per_line = 4
        page_size = 24

        def buttons_per_item(self, request, context, item):
            buttons = OrderedDict()

            # Buy CD button
            if item.buy_url:
                buttons[u'buy_url'] = {
                    'classes': self.item_buttons_classes,
                    'show': True,
                    'url': item.buy_url,
                    'open_in_new_window': True,
                    'icon': 'shop',
                    'title': _('Buy {thing}').format(thing=_('CD')),
                    'has_permissions': True,
                    'tooltip': _('When you buy from this link, it costs you nothing extra, but we get a percentage which helps support the community and pay for the servers!'),
                }

            buttons.update(super(SongCollection.ListView, self).buttons_per_item(request, context, item))
            return buttons

        def extra_context(self, context):
            super(SongCollection.ListView, self).extra_context(context)
            context['h1_page_title'] = self.collection.navbar_link_title
            context['h1_page_title_icon'] = self.collection.icon

    class ItemView(MainItemCollection.ItemView):
        ajax_callback = 'loadSong'

        fields_prefetched_together = ['singers']

        fields_exclude = [
            'romaji_name',
        ]

    class AddView(MainItemCollection.AddView):
        savem2m = True

    class EditView(MainItemCollection.EditView):
        savem2m = True

############################################################
############################################################
# Re LIVE collections
############################################################
############################################################

############################################################
# Act Collection

class ActCollection(SubItemCollection):
    main_collections = ['card', 'memoir']
    main_many2many = True
    main_related = 'acts'

    queryset = models.Act.objects.all().select_related('card')
    title = _('Act')
    plural_title = _('Acts')
    icon = 'skill'
    translated_fields = [
        'name',
        'description',
        'm_tips',
        'other_target',
    ]
    form_class = forms.ActForm

    filter_cuteform = {
        'i_target': {
            'type': CuteFormType.HTML,
        },
    }

    class ListView(SubItemCollection.ListView):
        per_line = 1
        item_template = custom_item_template
        auto_filter_form = True

    class ItemView(SubItemCollection.ItemView):
        template = custom_item_template

    class AddView(SubItemCollection.AddView):
        ajax_callback = 'loadActForm'

    class EditView(SubItemCollection.EditView):
        ajax_callback = 'loadActForm'

############################################################
# BaseCard Collection

class BaseCardCollection(MainItemCollection):
    enabled = False
    navbar_link_list = 'relive'

    translated_fields = [
        'name',
        'm_tips',
    ]

    filter_cuteform = {
        'i_rarity': {
            'image_folder': 'small_rarity',
        },
        'type': {
            'transform': CuteFormTransform.Flaticon,
        },
        'stage_girl': getStageGirlsCuteForm(),
        'version': {
            'to_cuteform': lambda _k, _v: models.VERSIONS[_k]['image'],
            'image_folder': 'language',
            'transform': CuteFormTransform.ImagePath,
        },
    }
    mergeSchoolStageGirlCuteForm(filter_cuteform)

    fields_icons = {
        'name': 'id',
        'acts': 'skill',
        'art': 'pictures',
        'icon': 'pictures',
        'ww_release_date': 'date',
        'jp_release_date': 'date',
        'tips': 'idea',
    }
    fields_icons.update({
        _statistic: 'hp' if '_hp' in _statistic else 'statistics'
        for _statistic in models.BaseCard.ALL_STATISTICS_FIELDS
    })

    fields_images = {
        'rarity': 'rarity.png',
    }

    def to_fields(self, view, item, exclude_fields=None, extra_fields=None, icons=None,
                  only_fields=None, *args, **kwargs):
        if exclude_fields is None: exclude_fields = []
        if extra_fields is None: extra_fields = []
        if icons is None: icons = {}

        # Set icons based on types + don't show types when value is False
        for type, details in self.queryset.model.TYPES.items():
            field_name = u'is_{}'.format(type)
            if details['is'](item):
                icons[field_name] = details['icon']
                if details.get('not_a_real_field', False):
                    if not only_fields or field_name in only_fields:
                        extra_fields.append((field_name, {
                            'type': 'bool',
                            'verbose_name': details['translation'],
                            'value': True,
                            'icon': details['icon'],
                        }))
                elif not getattr(item, field_name):
                    exclude_fields.append(field_name)
            else:
                exclude_fields.append(field_name)

        fields = super(BaseCardCollection, self).to_fields(
            view, item, *args, exclude_fields=exclude_fields,
            extra_fields=extra_fields, only_fields=only_fields, icons=icons, **kwargs)

        # Show rarity as images
        setSubField(fields, 'rarity', key='type', value='image')
        setSubField(fields, 'rarity', key='value', value=item.rarity_image)

        # Show rank under stats when ordering by stat
        for statistic in models.BaseCard.STATISTICS_FIELDS:
            field_name = u'delta_{}'.format(statistic)
            setSubField(fields, field_name, key='type', value='text_annotation')
            setSubField(fields, field_name, key='annotation', value=(
                lambda f: mark_safe(item.display_statistic_rank(statistic))))

        return fields

    def buttons_per_item(self, view, request, context, item):
        buttons = super(BaseCardCollection, self).buttons_per_item(view, request, context, item)

        # Show a button to test if the art looks good on the homepage
        if (request.user.is_authenticated()
            and request.user.hasPermission('manage_main_items')):
            if item.art:
                buttons[u'preview_art'] = {
                    'classes': view.item_buttons_classes + ['staff-only'],
                    'show': True,
                    'url': u'/?preview={}'.format(
                        getattr(item, u'art_2x_url')
                        or getattr(item, u'art_original_url'),
                    ),
                    'icon': 'home',
                    'title': u'Preview art on homepage',
                    'has_permissions': True,
                    'open_in_new_window': True,
                }
        return buttons

    class ListView(MainItemCollection.ListView):
        default_ordering = '-jp_release_date'
        show_collect_button = True
        show_item_buttons_as_icons = True
        item_buttons_classes = ['btn', 'btn-link-main', 'btn-lines']
        item_padding = 0

        quick_add_view = 'icons'

        alt_views = MainItemCollection.ListView.alt_views + [
            ('icons', {
                'verbose_name': string_concat(_('Icons'), ' (', _('Quick add'), ')'),
                'per_line': 6,
                'page_size': 42,
                'show_item_buttons_as_icons': False,
                'show_collect_button': True,
                'show_edit_button': False,
                'item_buttons_classes': ['btn', 'btn-secondary', 'btn-lines'],
            }),
        ]

    class ItemView(MainItemCollection.ItemView):
        fields_exclude = [
            'number',
            'show_art_on_homepage',
            'base_icon',
        ] + models.BaseCard.ALL_STATISTICS_FIELDS
        fields_prefetched_together = ['acts']
        ajax_callback = 'loadBaseCard'

        def get_queryset(self, queryset, parameters, request):
            # Order acts by type, unlock_at_rank, cost
            queryset = queryset.prefetch_related(Prefetch(
                'acts', queryset=models.Act.objects.order_by('i_type', 'unlock_at_rank', 'cost'),
            ))
            queryset = super(BaseCardCollection.ItemView, self).get_queryset(queryset, parameters, request)
            return queryset

        def to_fields(self, item, extra_fields=None, exclude_fields=None, *args, **kwargs):
            if extra_fields is None: extra_fields = []
            if exclude_fields is None: exclude_fields = []

            # Exclude all alt icons fields
            exclude_fields += item.ALL_ALT_ICONS_FIELDS

            # Cost
            if item.cost:
                extra_fields.append(('cost', {
                    'verbose_name': _('Cost'),
                    'type': 'text',
                    'value': item.cost,
                    'icon': 'money',
                }))

            # Statistics
            display_statistics = item.display_statistics
            if display_statistics:
                extra_fields.append(('statistics', {
                    'verbose_name': _('Statistics'),
                    'icon': 'statistics',
                    'type': 'html',
                    'value': item.display_statistics,
                    'spread_across': True
                }))

            fields = super(BaseCardCollection.ItemView, self).to_fields(
                item, *args, extra_fields=extra_fields, exclude_fields=exclude_fields, **kwargs)

            # Icons
            setSubField(fields, 'icon', key='type', value='images')
            setSubField(fields, 'icon', key='images', value=[
                {
                    'value': icon['icon'],
                    'verbose_name': u'{} - {} {} {}'.format(
                        unicode(item),
                        (models.BaseCard.get_verbose_i('rarity', icon['rarity'])
                         if 'rarity' in icon else ''),
                        _('Rank'), icon['rank'],
                    ),
                    'attributes': { k: v for k, v in {
                        'data-rarity': icon.get('rarity', None),
                        'data-rank': icon['rank'],
                    }.items() if v },
                } for icon in item.get_all_icons(suffix='_url')
            ])

            return fields

    class AddView(MainItemCollection.AddView):
        savem2m = True
        ajax_callback = 'loadBaseCardForm'

    class EditView(MainItemCollection.EditView):
        savem2m = True
        ajax_callback = 'loadBaseCardForm'

############################################################
# Card Collection

class CardCollection(BaseCardCollection):
    enabled = True
    queryset = models.Card.objects.all()
    title = _('Card')
    plural_title = _('Cards')
    navbar_link_title = string_concat(_('Cards'), ' (', _('Stage girls'), ')')
    image = 'red_dresses'
    form_class = forms.CardForm

    collectible = models.CollectedCard

    def collectible_to_class(self, model_class):
	return to_CollectedCardCollection(super(CardCollection, self).collectible_to_class(model_class))

    translated_fields = BaseCardCollection.translated_fields + [
        'description',
        'profile',
        'message',
    ]

    filter_cuteform = BaseCardCollection.filter_cuteform.copy()
    filter_cuteform.update({
        'i_element': getElementsCuteForm(models.Card),
        'i_damage': {
        },
        'i_position': {
        },
        'resists_against': getElementsCuteForm(),
        'weak_against': getElementsCuteForm(),
    })
    filter_cuteform['type']['to_cuteform'] = lambda _k, _v: models.Card.TYPES[_k]['icon']

    fields_icons = BaseCardCollection.fields_icons.copy()
    fields_icons.update({
        'stage_girl': 'idol',
        'description': 'about',
        'message': 'chat',
        'roles': 'staff',
        'profile': 'id',
        'transparent': 'pictures',
    })

    fields_images = BaseCardCollection.fields_images.copy()
    fields_images.update({
        'position': lambda _i: _i.position_image,
        'element': lambda _i: _i.element_image,
        'damage': lambda _i: _i.damage_icon_image,
        'collectedcards': 'dresses.png',
    })

    def to_fields(self, view, item, *args, **kwargs):
        fields = super(CardCollection, self).to_fields(
            view, item, *args, **kwargs)

        # Roles -> Role
        if len(item.roles) == 1:
            setSubField(fields, 'roles', key='verbose_name', value=_('Role'))

        return fields

    class ListView(BaseCardCollection.ListView):
        filter_form = forms.CardFilterForm
        ajax_callback = 'loadCardsFilters'
        fields_exclude = ['number'] # Don't show number on ordering

    class ItemView(BaseCardCollection.ItemView):
        fields_order = [
            'name',
            'stage_girl',
            'rarity',
            'element',
            'resists',
            'weak',
            'damage',
            'position',
            'cost',
        ] + [
            u'is_{}'.format(_type)
            for _type in models.Card.TYPES
        ] + [
            'description',
            'profile',
            'message',
            'statistics',
            'acts',
            'ww_release_date',
            'jp_release_date',
            'roles',
            'tips',
            'icon',
            'art',
            'transparent',
        ]

        def to_fields(self, item, extra_fields=None, *args, **kwargs):
            if extra_fields is None: extra_fields = []

            # Resists / Weak

            for field_name, verbose_name, image in [
                    ('resists', _('Effective against'), 'weak'),
                    ('weak', _('Less effective against'), 'resists'),
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
                        'image': staticImageURL(image, extension='png'),
                        'verbose_name': verbose_name,
                        'type': 'images_links',
                        'images': images,
                    }))
                else:
                    extra_fields.append((field_name, {
                        'image': staticImageURL(image, extension='png'),
                        'verbose_name': verbose_name,
                        'type': 'text',
                        'value': _('None'),
                    }))

            fields = super(CardCollection.ItemView, self).to_fields(
                item, *args, extra_fields=extra_fields, **kwargs)

            # Set URL to accounts who collected the cards

            setSubField(fields, 'collectedcards', key='link', value=(
                u'/accounts/?collected_card={}'.format(item.pk)))
            setSubField(fields, 'collectedcards', key='ajax_link', value=(
                u'/ajax/accounts/?collected_card={}&ajax_modal_only'.format(item.pk)))

            return fields

############################################################
# Memoir Collection

class MemoirCollection(BaseCardCollection):
    enabled = True
    queryset = models.Memoir.objects.all()
    title = _('Memoir')
    plural_title = _('Memoirs')
    navbar_link_list = 'relive'
    image = 'red_memoirs'
    form_class = forms.MemoirForm

    collectible = models.CollectedMemoir

    def collectible_to_class(self, model_class):
	return to_CollectedMemoirCollection(super(MemoirCollection, self).collectible_to_class(model_class))

    translated_fields = BaseCardCollection.translated_fields + [
        'explanation',
    ]

    fields_icons = BaseCardCollection.fields_icons.copy()
    fields_icons.update({
        'explanation': 'about',
        'sell_price': 'money',
        'stage_girls': 'idol',
    })

    fields_images = BaseCardCollection.fields_images.copy()
    fields_images.update({
        'collectedmemoirs': 'memoirs.png',
    })

    filter_cuteform = BaseCardCollection.filter_cuteform.copy()
    filter_cuteform['type'] = filter_cuteform['type'].copy()
    filter_cuteform['type']['to_cuteform'] = lambda _k, _v: models.Memoir.TYPES[_k]['icon']

    def to_fields(self, view, item, exclude_fields=None, *args, **kwargs):
        if exclude_fields is None: exclude_fields = []

        # Hide upgrade if memoir is not upgrade
        if not item.is_upgrade:
            exclude_fields.append('is_upgrade')

        fields = super(MemoirCollection, self).to_fields(
            view, item, exclude_fields=exclude_fields, *args, **kwargs)

        # Show rarity as images
        setSubField(fields, 'rarity', key='value', value=item.small_rarity_image)

        return fields

    class ListView(BaseCardCollection.ListView):
        filter_form = forms.MemoirFilterForm

    class ItemView(BaseCardCollection.ItemView):
        fields_prefetched_together = BaseCardCollection.ItemView.fields_prefetched_together + [
            'stage_girls',
        ]

        fields_order = [
            'name',
            'rarity',
        ] + [
            u'is_{}'.format(_type)
            for _type in models.Memoir.TYPES
        ] + [
            'cost',
            'sell_price',
            'explanation',
            'statistics',
            'acts',
            'ww_release_date',
            'jp_release_date',
            'tips',
            'icon',
            'art',
            'transparent',
            'stage_girls',
        ]

        filter_cuteform = BaseCardCollection.filter_cuteform.copy()
        filter_cuteform.update({
            'is_upgrade': {
                'type': CuteFormType.YesNo,
            },
        })

        def to_fields(self, item, *args, **kwargs):
            fields = super(MemoirCollection.ItemView, self).to_fields(
                item, *args, **kwargs)

            # Set URL to accounts who collected the memoirs

            setSubField(fields, 'collectedmemoirs', key='link', value=(
                u'/accounts/?collected_memoir={}'.format(item.pk)))
            setSubField(fields, 'collectedmemoirs', key='ajax_link', value=(
                u'/ajax/accounts/?collected_memoir={}&ajax_modal_only'.format(item.pk)))

            return fields

############################################################
# Event Collection

class EventCollection(MainItemCollection):
    enabled = False
    queryset = models.Account.objects.all() # todo
    title = _('Event')
    plural_title = _('Events')
    navbar_link_list = 'relive'
    icon = 'event'

############################################################
# Conversation Collection

class ConversationCollection(MainItemCollection):
    enabled = False
    queryset = models.Account.objects.all() # todo
    title = _('Conversation')
    plural_title = _('Conversations')
    navbar_link_list = 'relive'
    navbar_link_title = _('My theater')
    icon = 'chat'

############################################################
# Comic Collection

class ComicCollection(MainItemCollection):
    enabled = False
    queryset = models.Account.objects.all() # todo
    title = _('Comic')
    plural_title = _('Comics')
    navbar_link_list = 'relive'
    icon = 'album'

############################################################
############################################################
# Re LIVE collectible collections
############################################################
############################################################

############################################################
# Base collected card collection

def to_BaseCollectedCardCollection(cls):
    class _BaseCollectedCardCollection(cls):
        filter_cuteform = {
            'max_leveled': {
                'type': CuteFormType.YesNo,
            },
        }

        fields_icons = {
            'max_leveled': 'max-level',
        }

        def to_fields(self, view, item, *args, **kwargs):
            fields = super(_BaseCollectedCardCollection, self).to_fields(
                view, item, *args, **kwargs)

            # Show base icon to avoid confusion
            setSubField(fields, item.item_parent_name, key='icon', value=None)
            setSubField(fields, item.item_parent_name, key='image_for_link', value=item.item_parent.base_icon_url)

            # Show rank as images
            setSubField(fields, 'rank', key='type', value='image')
            setSubField(fields, 'rank', key='value', value=item.rank_image)

            return fields

        class AddView(cls.AddView):
            unique_per_owner = True
            add_to_collection_variables = cls.AddView.add_to_collection_variables + [
                'i_rarity',
            ]

            def quick_add_to_collection(self, request):
                return request.GET.get('view') == 'icons'

    return _BaseCollectedCardCollection

############################################################
# Collected card Collection

def to_CollectedCardCollection(cls):
    cls = to_BaseCollectedCardCollection(cls)

    class _CollectedCardCollection(cls):
        form_class = forms.to_CollectedCardForm(cls)

        filter_cuteform = cls.filter_cuteform.copy()
        filter_cuteform.update({
            'max_bonded': {
                'type': CuteFormType.YesNo,
            },
            'i_rarity': {
                'image_folder': 'i_rarity',
            },
            'rank': {
            },
        })

        fields_images = {
            'rarity': 'rarity.png',
            'rank': 'rank.png',
            'card': 'red_dresses.png',
        }

        fields_icons = cls.fields_icons.copy()
        fields_icons.update({
            'max_bonded': 'max-bond',
        })

        def to_fields(self, view, item, *args, **kwargs):
            fields = super(_CollectedCardCollection, self).to_fields(
                view, item, *args, **kwargs)
            setSubField(fields, 'card', key='icon', value=None)
            setSubField(fields, 'card', key='image_for_link', value=item.card.base_icon_url)

            # Show rarity as images
            setSubField(fields, 'rarity', key='type', value='image')
            setSubField(fields, 'rarity', key='value', value=item.rarity_image)

            return fields

    return _CollectedCardCollection

############################################################
# Collected memoir Collection

def to_CollectedMemoirCollection(cls):
    cls = to_BaseCollectedCardCollection(cls)

    class _CollectedMemoirCollection(cls):
        form_class = forms.to_CollectedMemoirForm(cls)

        filter_cuteform = cls.filter_cuteform.copy()
        filter_cuteform.update({
            'rank': {
                'image_folder': 'memoir_triangle_rank',
            },
        })

        fields_images = {
            'memoir': 'red_memoirs.png',
            'rank': 'memoir_rank.png',
        }

    return _CollectedMemoirCollection
