from collections import OrderedDict
from django import forms
from django.conf import settings as django_settings
from django.core.validators import MaxValueValidator
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language, string_concat
from magi.forms import (
    AutoForm,
    MagiFilter,
    MagiFiltersForm,
    AccountForm as _AccountForm,
    AccountFilterForm as _AccountFilterForm,
    ActivityForm as _ActivityForm,
    FilterActivities as _ActivityFilterForm,
)
from magi.item_model import i_choices
from magi.utils import (
    birthdayOrderingQueryset,
    FormShowMore,
    getStaffConfiguration,
    PastOnlyValidator,
    presetsFromCharacters,
    presetsFromChoices,
    staticImageURL,
)
from starlight import models
from starlight.raw import (
    LICENSE_NAME,
    LICENSE_NAME_PER_LANGUAGE,
    SMARTPHONE_GAME,
    SMARTPHONE_GAME_PER_LANGUAGE,
)
from starlight import settings
from starlight.utils import (
    calculateMemoirStatistics,
    getSchoolChoices,
    getSchoolYearChoices,
    getCharactersChoices,
    presetsFromSchools,
)

############################################################
############################################################
# Utils
############################################################
############################################################

class ImportableItemForm(AutoForm):
    def __init__(self, *args, **kwargs):
        super(ImportableItemForm, self).__init__(*args, **kwargs)
        if self.is_creating:
            self.beforeform = mark_safe(
                '<br><div class="alert alert-danger">{}s are imported automatically and shouldn\'t be added manually.'
                .format(self.Meta.model.collection_name.title()))
        configuration = django_settings.IMPORTABLE_FIELDS[self.Meta.model.collection_name]
        for field_name, field in self.fields.items():
            if field_name in configuration['ok_to_edit_fields']:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' editable-imported-field'
                field.help_text = mark_safe(u'<span class="text-warning">{}</span><br>{}'.format(
                    'Can be changed, but may get overwitten by automatic import.',
                    field.help_text,
                ))
            elif field_name in configuration['imported_fields']:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' imported-field'
                if field_name in configuration['many2many_fields']:
                    message = 'Imported automatically, but you may add more.'
                else:
                    message = 'Don\'t change. Imported automatically.'
                field.help_text = mark_safe(u'<span class="text-danger">{}</span><br>{}'.format(
                    message, field.help_text,
                ))

############################################################
############################################################
# MagiCircles' default collections
############################################################
############################################################

############################################################
# Activity

class NewsForm(_ActivityForm):
    creation = forms.DateField(required=False, label=_('Creation'), validators=[
        PastOnlyValidator,
    ])

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)

        # Ensure staff is selected by default when creating a news
        self.fields['c_tags'].initial = ['staff']

        # Delete useless fields
        for field_name in ['save_activities_language']:
            if field_name in self.fields:
                del(self.fields[field_name])

    def save(self, commit=False):
        instance = super(NewsForm, self).save(commit=False)

        # Set forced_creation in the instance to be saved in after_save in collection
        creation = self.cleaned_data.get('creation')
        if creation:
            instance.forced_creation = creation
            instance.last_bump = instance.forced_creation

        if commit:
            instance.save()
        return instance

    class Meta(_ActivityForm.Meta):
        fields = ['creation'] + list(_ActivityForm.Meta.fields)

class NewsFilterForm(_ActivityFilterForm):
    ordering_fields = None

    show_presets_in_navbar = False
    presets = OrderedDict([
        ('revuestarlight', {
            'verbose_name': lambda: LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME),
            'fields': {
                'c_tags': 'revuestarlight',
            },
            'image': u'revuestarlight_icon.png',
            'label': lambda: u'{} {}'.format(
                LICENSE_NAME_PER_LANGUAGE.get(get_language(), LICENSE_NAME),
                _('News').lower(),
            ),
        }),
        ('relive', {
            'verbose_name': lambda: SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(), SMARTPHONE_GAME),
            'fields': {
                'c_tags': 'relive',
            },
            'image': u'relive_icon.png',
            'label': lambda: u'{} {}'.format(
                SMARTPHONE_GAME_PER_LANGUAGE.get(get_language(), SMARTPHONE_GAME),
                _('News').lower(),
            ),
        }),
    ])

    def __init__(self, *args, **kwargs):
        super(NewsFilterForm, self).__init__(*args, **kwargs)

        # Delete filters that don't make sense for news
        for field in ['is_popular', 'hide_archived', 'is_following', 'with_image']:
            if field in self.fields:
                del(self.fields[field])

        self.reorder_fields(['search', 'liked'])

############################################################
# Account

class AccountForm(_AccountForm):
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

        # Show a button to skip adding an account for users who only care about the license
        if 'advanced' not in self.request.GET and self.is_creating:
            self.otherbuttons = mark_safe('<a href="/" class="btn btn-link-secondary">{}</a>'.format(_('Skip')))

        # Fix show friend ID label to say ID
        if 'show_friend_id' in self.fields:
            friend_id_sentence = unicode(_('Friend ID'))
            friend_id_sentence = friend_id_sentence[0].lower() + friend_id_sentence[1:]
            self.fields['show_friend_id'].label = unicode(self.fields['show_friend_id'].label.replace(
                friend_id_sentence, unicode(_('ID')),
            ).replace(
                unicode(_('Friend ID')), unicode(_('ID')),
            ))

        # Order cards when selecting center
        if 'center' in self.fields:
            self.fields['center'].queryset = self.fields['center'].queryset.select_related(
                'card').order_by('-card__i_rarity', '-card__number')

        # Max level
        if 'level' in self.fields:
            try:
                max_level = int(getStaffConfiguration('max_level', None))
            except (ValueError, TypeError):
                max_level = None
            if max_level:
                self.fields['level'].validators += [
                    MaxValueValidator(max_level),
                ]

class AccountFilterForm(_AccountFilterForm):
    presets = OrderedDict([
        (_version, {
            'verbose_name': _version_details['translation'],
            'fields': {
                'i_version': models.Account.get_i('version', _version),
            },
            'image': u'language/{}.png'.format(_version_details['image']),
        }) for _version, _version_details in models.VERSIONS.items()
    ])

    collected_card = forms.IntegerField(widget=forms.HiddenInput)
    collected_card_filter = MagiFilter(selector='collectedcards__card__number')

    collected_memoir = forms.IntegerField(widget=forms.HiddenInput)
    collected_memoir_filter = MagiFilter(selector='collectedmemoirs__memoir__number')

    show_more = FormShowMore('i_version', until='ordering')

    class Meta(_AccountFilterForm.Meta):
        top_fields = _AccountFilterForm.Meta.top_fields + [
            'i_version',
        ]
        middle_fields = [
            'i_play_style', 'i_vs_revue_rank',
        ] + _AccountFilterForm.Meta.middle_fields
        fields = top_fields + middle_fields

############################################################
############################################################
# Revue Starlight forms
############################################################
############################################################

############################################################
# Voice Actress

def to_translate_voice_actress_form_class(cls):
    class _TranslateVoiceActressForm(cls):
        def __init__(self, *args, **kwargs):
            super(_TranslateVoiceActressForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                if field_name.startswith('d_m_descriptions-') and '<div' in field.help_text:
                    field.help_text = mark_safe(
                        field.help_text.split('<div')[0]
                        + field.help_text.split('</div>')[-1]
                    )
    return _TranslateVoiceActressForm

class VoiceActressFilterForm(MagiFiltersForm):
    search_fields = [
        'name', 'd_names',
        'specialty', 'd_specialtys',
        'hobbies', 'd_hobbiess',
        'm_description', 'd_m_descriptions',
    ]

    ordering_fields = [
        ('name', _('Name')),
        ('stagegirls__name', string_concat(_('Stage girl'), ' (', _('Name'), ')')),
        ('birthday_month,birthday_day', _('Birthday')),
        ('birthday', _('Age')),
        ('height', _('Height')),
    ]

    school = forms.ChoiceField(label=_('School'))
    school_filter = MagiFilter(selector='stagegirls__school', distinct=True)

    def __init__(self, *args, **kwargs):
        super(VoiceActressFilterForm, self).__init__(*args, **kwargs)
        if 'school' in self.fields:
            self.fields['school'].choices = getSchoolChoices(without_other=True)

    def filter_queryset(self, queryset, parameters, request, *args, **kwargs):
        queryset = super(VoiceActressFilterForm, self).filter_queryset(
            queryset, parameters, request, *args, **kwargs)

        # Prepare fields for ordering for birthday
        if parameters.get('ordering') == 'birthday_month,birthday_day':
            queryset = birthdayOrderingQueryset(queryset, order_by=False)

        return queryset

    class Meta(MagiFiltersForm.Meta):
        model = models.VoiceActress
        fields = [
            'search',
            'school',
            'i_astrological_sign', 'i_blood',
            'ordering', 'reverse_order',
        ]

############################################################
# School

class SchoolForm(AutoForm):
    class Meta(AutoForm.Meta):
        model = models.School
        tinypng_on_save = [
            'white_image',
            'monochrome_image',
        ]

############################################################
# Stage girl

class StageGirlForm(ImportableItemForm):
    def save(self, commit=False):
        instance = super(StageGirlForm, self).save(commit=False)

        # Make sure all the stage girls have the same year to allow ordering by date
        if instance.birthday:
            instance.birthday = instance.birthday.replace(year=2017)

        if commit:
            instance.save()
        return instance

    class Meta(ImportableItemForm.Meta):
        model = models.StageGirl
        tinypng_on_save = [
            'small_image',
            'square_image',
        ]

class StageGirlFilterForm(MagiFiltersForm):
    search_fields = [
        'name', 'd_names',
        'weapon', 'd_weapons',
        'favorite_food', 'd_favorite_foods',
        'least_favorite_food', 'd_least_favorite_foods',
        'likes', 'd_likess',
        'dislikes', 'd_dislikess',
        'hobbies', 'd_hobbiess',
        'm_description', 'd_m_descriptions',
    ]

    ordering_fields = [
        ('school', _('School')),
        ('name', _('Name')),
        ('voice_actress__name', string_concat(_('Voice actress'), ' (', _('Name'), ')')),
        ('birthday', _('Birthday')),
    ]

    presets = OrderedDict(
        presetsFromSchools()
    )

    def __init__(self, *args, **kwargs):
        super(StageGirlFilterForm, self).__init__(*args, **kwargs)
        if 'i_year' in self.fields:
            self.fields['i_year'].choices = BLANK_CHOICE_DASH + i_choices(getSchoolYearChoices())

    class Meta(MagiFiltersForm.Meta):
        model = models.StageGirl
        fields = [
            'search',
            'i_year',
            'i_astrological_sign',
            'school',
            'ordering', 'reverse_order',
        ]
        hidden_foreign_keys = ['school']

############################################################
# Song

class SongForm(ImportableItemForm):
    class Meta(ImportableItemForm.Meta):
        model = models.Song

class SongFilterForm(MagiFiltersForm):
    search_fields = [
        'name', 'd_names', 'romaji_name',
        'm_lyrics', 'm_japanese_lyrics', 'd_m_lyricss', 'm_romaji_lyrics',
    ]

    ordering_fields = [
        ('release_date', _('Release date')),
        ('name', _('Title')),
        ('romaji_name', string_concat(_('Title'), ' (', _('Romaji'), ')')),
        ('length', _('Length')),
        ('bpm', _('BPM')),
    ]

    merge_fields = {
        'singer': {
            'fields': OrderedDict([
                ('singers', {
                    'choices': lambda: getCharactersChoices(key='VOICE_ACTRESSES'),
                }),
                ('stage_girl', {
                    'choices': lambda: getCharactersChoices(),
                }),
                ('school', {
                    'choices': lambda: getSchoolChoices(),
                }),
            ]),
            'label': _('Singers'),
        },
    }

    presets = OrderedDict(
        presetsFromSchools(
            'singer', get_field_value=lambda _id: u'school-{}'.format(_id))
        + presetsFromCharacters('singer', get_field_value=lambda _pk, _name, _vname: u'singers-{}'.format(_pk), key='VOICE_ACTRESSES')
        + presetsFromCharacters(
            'singer', get_field_value=lambda _id, _name, _vname: u'stage_girl-{}'.format(_id))
    )

    stage_girl = forms.ChoiceField()
    stage_girl_filter = MagiFilter(selector='singers__stagegirls')

    school = forms.ChoiceField()
    school_filter = MagiFilter(selector='singers__stagegirls__school', distinct=True)

    class Meta(MagiFiltersForm.Meta):
        model = models.Song
        fields = (
            'search',
            'singers',
            'ordering', 'reverse_order',
        )

############################################################
############################################################
# Relive forms
############################################################
############################################################

############################################################
# Act

class ActForm(ImportableItemForm):
    i_target = forms.ChoiceField(label=_('Target'), choices=BLANK_CHOICE_DASH + i_choices(
        models.Act.TARGET_CHOICES
    ) + [
        ('other', _('Other'))
    ])

    def clean_i_target(self):
        i_target = self.cleaned_data.get('i_target')
        return None if i_target == 'other' else i_target

    class Meta(ImportableItemForm.Meta):
        model = models.Act

############################################################
# Base card

class BaseCardForm(ImportableItemForm):
    acts = forms.ModelMultipleChoiceField(
        queryset=models.Act.objects.all().order_by('i_type', 'name'),
        widget=forms.CheckboxSelectMultiple, required=False,
    )

    show_more = FormShowMore(
        cutoff='base_hp', including_cutoff=True, until='max_level_agility',
        message_more='Show statistics fields', message_less='Hide statistics fields',
        check_values=False,
    )

    def __init__(self, *args, **kwargs):
        super(BaseCardForm, self).__init__(*args, **kwargs)

        # Change help text of stats for min level / max level
        if not self.is_creating:
            for statistic in models.BaseCard.STATISTICS_FIELDS:
                for field_prefix in ['min_level', 'max_level']:
                    field_name = u'{}_{}'.format(field_prefix, statistic)
                    if field_name in self.fields:
                        self.fields[field_name].help_text = u'At level {level} (for rarity {rarity})'.format(
                            level=getattr(self.instance, field_prefix),
                            rarity=self.instance.t_rarity,
                        )

        # Limit to rarities
        if 'i_rarity' in self.fields:
            self.fields['i_rarity'].choices = [
                (k, v) for k, v in self.fields['i_rarity'].choices
                if k in self.Meta.model.LIMIT_TO_RARITIES
            ]

        # When uploading a new art of base_icon, delete all current generated derived images
        if not self.is_creating:
            self.previous_art = unicode(self.instance.art)
            self.previous_base_icon = unicode(self.instance.base_icon)

        # Fields that are auto-generated are indicat
        if 'image' in self.fields:
            self.fields['image'].help_text = 'This image will be automatically generated from the art. You don\'t need to upload your own.'
        for field_name in ['icon'] + self.Meta.model.ALL_ALT_ICONS_FIELDS:
            if field_name in self.fields:
                self.fields[field_name].help_text = 'This image will be automatically generated from the base icon. You don\'t need to upload your own.'

    def save(self, commit=False):
        instance = super(BaseCardForm, self).save(commit=False)

        # When uploading a new art of base_icon, delete all current generated derived images
        if not self.is_creating:
            if self.previous_art != unicode(instance.art):
                instance.image = None
                instance._original_image = None
                instance._2x_image = None
            if self.previous_base_icon != unicode(instance.base_icon):
                instance.icon = None
                for field_name in instance.ALL_ALT_ICONS_FIELDS:
                    setattr(instance, field_name, None)

        if commit:
            instance.save()
        return instance

class BaseCardFilterForm(MagiFiltersForm):
    search_fields = [
        'name', 'd_names', 'acts__name', 'acts__d_names',
    ]
    search_fields_labels = {
        'acts__name': _('Acts'),
        'acts__d_names': '',
    }
    ordering_fields = [
        ('jp_release_date', _('Release date')),
        ('number', _('Number')),
    ] + [
        (
            u'delta_{}'.format(_statistic),
            models.BaseCard._meta.get_field(u'base_{}'.format(_statistic)).verbose_name,
        ) for _statistic in models.BaseCard.STATISTICS_FIELDS
    ]
    merge_fields = [
        OrderedDict([
            ('school', {
                'choices': lambda: getSchoolChoices(),
            }),
            ('stage_girl', {
                'choices': lambda: getCharactersChoices(),
            }),
        ]),
    ]

    base_presets = (
        presetsFromSchools(
            'school_stage_girl', get_field_value=lambda _id: u'school-{}'.format(_id))
        + presetsFromCharacters(
            'school_stage_girl', get_field_value=lambda _id, _name, _vname: u'stage_girl-{}'.format(_id))
    )

    @classmethod
    def base_preset_get_key(self, i, value, verbose):
        return u'{}-star{}'.format(value, '' if value < 2 else 's')

    show_more = FormShowMore(cutoff='type', including_cutoff=True, until='ordering')

    version = forms.ChoiceField(label=_('Version'), choices=models.VERSION_CHOICES)
    version_filter = MagiFilter(to_queryset=(
        lambda form, queryset, request, value: queryset.filter(**{
            u'{}release_date__isnull'.format(models.VERSIONS[value]['prefix']): False
        })
    ))

    stage_girl = forms.ChoiceField(label=_('Stage girl'), choices=getCharactersChoices())

    school = forms.ChoiceField(label=_('School'), choices=getSchoolChoices())

    type = forms.ChoiceField(label=_('Type'))
    type_filter = MagiFilter(to_queryset=(
        lambda form, queryset, request, value: form.Meta.model.TYPES[value]['filter'](queryset)
    ))

    def __init__(self, *args, **kwargs):
        super(BaseCardFilterForm, self).__init__(*args, **kwargs)

        # Set type choices
        if 'type' in self.fields:
            self.fields['type'].choices = BLANK_CHOICE_DASH + [
                (type, type_details['translation'])
                for type, type_details in self.Meta.model.TYPES.items()
            ]

        # Limit to rarities
        if 'i_rarity' in self.fields:
            self.fields['i_rarity'].choices = BLANK_CHOICE_DASH + [
                (k, v) for k, v in self.fields['i_rarity'].choices
                if k in self.Meta.model.LIMIT_TO_RARITIES
            ]

############################################################
# Card

class CardForm(BaseCardForm):
    show_more = [
        BaseCardForm.show_more,
        FormShowMore(
            cutoff='rank1_rarity2_icon', including_cutoff=True, until='rank7_rarity6_icon',
            message_more='Show icons fields', message_less='Hide icons fields',
            check_values=False,
        ),
    ]

    def save(self, commit=False):
        instance = super(CardForm, self).save(commit=False)
        instance.update_cache('statistics_ranks')
        if commit:
            instance.save()
        return instance

    class Meta(BaseCardForm.Meta):
        model = models.Card

class CardFilterForm(BaseCardFilterForm):
    search_fields = BaseCardFilterForm.search_fields + [
        'stage_girl__name', 'stage_girl__d_names',
        'description', 'd_descriptions',
        'profile', 'd_profiles',
        'message', 'd_messages',
    ]
    search_fields_labels = BaseCardFilterForm.search_fields_labels.copy()
    search_fields_labels.update({
        'stage_girl__name': _('Stage girl'),
        'stage_girl__d_names': '',
    })
    merge_fields = BaseCardFilterForm.merge_fields + [
        {
            'label': _('Target'),
            'fields': ('act_target', 'act_other_target'),
        },
    ]

    presets = OrderedDict(
        presetsFromChoices(
            models.Card, 'rarity',
            get_key=BaseCardFilterForm.base_preset_get_key,
            should_include=lambda _i, _value, _verbose: _value in models.Card.LIMIT_TO_RARITIES)
        + presetsFromChoices(
            models.Card, 'element',
            get_image=lambda _i, _value, _verbose: 'color/{}.png'.format(_value))
        + BaseCardFilterForm.base_presets
    )

    school_filter = MagiFilter(selector='stage_girl__school', distinct=True)

    def _against_to_value(against, opposite):
        def _f(value):
            elements_to_filter = []
            for filtered_element in (value if isinstance(value, list) else [value]):
                for element, details in models.ELEMENTS.items():
                    against_elements = details.get(u'{}_against'.format(against), [])
                    if filtered_element in against_elements:
                        elements_to_filter.append(models.Card.get_i('element', element))
            return elements_to_filter
        return _f

    resists_against = forms.ChoiceField(label=_('Effective against'), choices=models.ELEMENT_CHOICES)
    resists_against_filter = MagiFilter(selector='i_element', to_value=_against_to_value('resists', 'weak'))

    weak_against = forms.ChoiceField(label=_('Less effective against'), choices=models.ELEMENT_CHOICES)
    weak_against_filter = MagiFilter(selector='i_element', to_value=_against_to_value('weak', 'resists'))

    act_hits = forms.BooleanField(label=_('Hits more than once'))
    act_hits_filter = MagiFilter(selector='acts__hits__gt', to_value=lambda _v: 1, multiple=False, distinct=True)

    act_target = forms.ChoiceField(label=_('Target'), choices=i_choices(models.Act.TARGET_CHOICES))
    act_target_filter = MagiFilter(selector='acts__i_target')

    act_other_target = forms.ChoiceField(choices=[('other', _('Other'))])
    act_other_target_filter = MagiFilter(
        selector='acts__other_target__isnull', to_value=lambda _v: False,
        multiple=False, distinct=True,
    )

    class Meta(BaseCardFilterForm.Meta):
        model = models.Card
        fields = [
            'search',
            'stage_girl', 'school',
            'i_rarity', 'i_element',
            'type', 'version',
            'i_damage', 'i_position',
            'c_roles',
            'resists_against', 'weak_against',
            'act_hits',
            'act_target',
        ]

############################################################
# Memoir

class MemoirForm(BaseCardForm):
    show_more = [
        BaseCardForm.show_more,
        FormShowMore(
            cutoff='rank1_icon', including_cutoff=True,
            message_more='Show icons fields', message_less='Hide icons fields',
            check_values=False,
        ),
    ]

    def save(self, commit=False):
        instance = super(MemoirForm, self).save(commit=False)

        # Auto calculate min_level and max_level from base and delta
        calculateMemoirStatistics(instance)

        if commit:
            instance.save()
        return instance

    class Meta(BaseCardForm.Meta):
        model = models.Memoir

class MemoirFilterForm(BaseCardFilterForm):
    search_fields = BaseCardFilterForm.search_fields + [
        'explanation', 'd_explanations',
    ]

    presets = OrderedDict(
        presetsFromChoices(
            models.Memoir, 'rarity',
            get_key=BaseCardFilterForm.base_preset_get_key,
            should_include=lambda _i, _value, _verbose: _value in models.Memoir.LIMIT_TO_RARITIES)
        + BaseCardFilterForm.base_presets
    )

    school_filter = MagiFilter(selector='stage_girls__school', distinct=True)
    stage_girl_filter = MagiFilter(selector='stage_girls')

    class Meta(BaseCardFilterForm.Meta):
        model = models.Memoir
        fields = [
            'search',
            'i_rarity',
            'type',
            'version',
            'stage_girl', 'school',
        ]

############################################################
############################################################
# Re LIVE collectible collections
############################################################
############################################################

############################################################
# Collected card

def to_CollectedCardForm(cls):

    class _CollectedCardForm(cls.form_class):
        rank = forms.ChoiceField(label=_('Rank'), initial=7, choices=[
            (i, i)
            for i in range(1, 7 + 1)
        ])

        def __init__(self, *args, **kwargs):
            super(_CollectedCardForm, self).__init__(*args, **kwargs)

            # Limit choices to rarities higher than base rarity
            base_rarity = int(self.collectible_variables['i_rarity'])
            if base_rarity and 'i_rarity' in self.fields:
                self.fields['i_rarity'].choices = [
                    (k, v) for k, v in self.fields['i_rarity'].choices
                    if k != '' and k >= base_rarity
                ]
                self.fields['i_rarity'].initial = base_rarity

        def save(self, commit=True):
            instance = super(_CollectedCardForm, self).save(commit=False)

            # Ensure rarity is higher than base rarity
            if instance.i_rarity < instance.card.i_rarity:
                instance.i_rarity = instance.card.i_rarity

            if commit:
                instance.save()
            return instance

    return _CollectedCardForm

############################################################
# Collected memoir

def to_CollectedMemoirForm(cls):

    class _CollectedMemoirForm(cls.form_class):
        rank = forms.ChoiceField(label=_('Rank'), initial=5, choices=[
            (i, i - 1)
            for i in range(1, 5 + 1)
        ])

    return _CollectedMemoirForm
