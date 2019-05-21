from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from magi.forms import (
    AutoForm,
    MagiFilter,
    MagiFiltersForm,
    UserPreferencesForm as _UserPreferencesForm,
)
from magi.utils import (
    birthdayOrderingQueryset,
)
from starlight import models
from starlight.utils import (
    getSchoolChoices,
    getVoiceActressChoices,
    getStageGirlChoices,
)

############################################################
############################################################
# MagiCircles' default collections
############################################################
############################################################

############################################################
# Users

class UserPreferencesForm(_UserPreferencesForm):
    def __init__(self, *args, **kwargs):
        super(UserPreferencesForm, self).__init__(*args, **kwargs)
        # Make voice actress preferences a choice field
        for nth in range(1, 4):
            field_name = 'd_extra-favorite_voiceactress{}'.format(nth)
            if field_name in self.fields:
                self.fields[field_name] = forms.ChoiceField(
                    required=False,
                    choices=getVoiceActressChoices(),
                    label=self.fields[field_name].label,
                    initial=self.fields[field_name].initial,
                )
        self.reorder_fields([
            'm_description', 'location',
        ] + [
            u'd_extra-favorite_voiceactress{}'.format(nth)
            for nth in range(1, 4)
        ] + [
            u'favorite_character{}'.format(nth)
            for nth in range(1, 4)
        ])

############################################################
############################################################
# Revue Starlight forms
############################################################
############################################################

############################################################
# Voice Actress

class VoiceActressForm(AutoForm):
    def __init__(self, *args, **kwargs):
        super(VoiceActressForm, self).__init__(*args, **kwargs)
        if not self.is_creating:
            self.belowform = mark_safe(u'<h1 class="text-center padding50 form-title">Links</h1><ul class="container_form list-group">{links}<li class="list-group-item"><a href="{add_url}" data-ajax-url="{ajax_add_url}" data-ajax-handle-form="true" class="btn btn-secondary btn-sm pull-right">Add link</a><br></li></ul>'.format(
                links=u''.join([
                    u'<li class="list-group-item"><a href="{edit_url}" class="btn btn-secondary btn-sm pull-right" data-ajax-url="{ajax_edit_url}" data-ajax-handle-form="true">Edit link</a><a href="{url}">{name}</a></li>'.format(
                        edit_url=link.edit_url,
                        ajax_edit_url=link.ajax_edit_url,
                        url=link.url,
                        name=link.t_name,
                    ) for link in self.instance.links.all()
                ]),
                add_url=u'/voiceactresslinks/add/?voice_actress={}'.format(self.instance.pk),
                ajax_add_url=u'/ajax/voiceactresslinks/add/?voice_actress={}'.format(self.instance.pk),
            ))

    class Meta(AutoForm.Meta):
        model = models.VoiceActress

class VoiceActressFilterForm(MagiFiltersForm):
    search_fields = [
        'name', 'd_names',
        'specialty', 'd_specialtys',
        'hobbies', 'd_hobbiess',
        'm_description', 'd_m_descriptions',
    ]

    ordering_fields = [
        ('name', _('Name')),
        ('birthday_month,birthday_day', _('Birthday')),
        ('birthday', _('Age')),
        ('height', _('Height')),
    ]

    school = forms.ChoiceField(label=_('School'))
    school_filter = MagiFilter(selector='stagegirls__school', distinct=True)

    def __init__(self, *args, **kwargs):
        super(VoiceActressFilterForm, self).__init__(*args, **kwargs)
        if 'school' in self.fields:
            self.fields['school'].choices = getSchoolChoices()

    def filter_queryset(self, queryset, parameters, request, *args, **kwargs):
        queryset = super(VoiceActressFilterForm, self).filter_queryset(
            queryset, parameters, request, *args, **kwargs)
        # Prepare fields for ordering for birthday
        if parameters.get('ordering') == 'birthday_month,birthday_day':
            queryset = birthdayOrderingQueryset(queryset)
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
# Voice actress link

class VoiceActressLinkForm(AutoForm):
    class Meta(AutoForm.Meta):
        model = models.VoiceActressLink
        allow_initial_in_get = ('voice_actress',)

############################################################
# Stage girl

class StageGirlForm(AutoForm):
    def save(self, commit=False):
        instance = super(StageGirlForm, self).save(commit=False)
        # Make sure all the stage girls have the same year to allow ordering by date
        if instance.birthday:
            instance.birthday = instance.birthday.replace(year=2017)
        if commit:
            instance.save()
        return instance

    class Meta(AutoForm.Meta):
        model = models.StageGirl
        tinypng_on_save = ('small_image',)

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
        ('birthday', _('Birthday')),
    ]

    school = forms.ChoiceField(label=_('School'))

    def __init__(self, *args, **kwargs):
        super(StageGirlFilterForm, self).__init__(*args, **kwargs)
        if 'school' in self.fields:
            self.fields['school'].choices = getSchoolChoices()

    class Meta(MagiFiltersForm.Meta):
        model = models.StageGirl
        fields = [
            'search',
            'school', 'i_year',
            'i_astrological_sign',
            'ordering', 'reverse_order',
        ]

############################################################
############################################################
# Relive forms
############################################################
############################################################

class CardForm(AutoForm):
    def save(self, commit=False):
        instance = super(CardForm, self).save(commit=False)
        instance.update_cache('stage_girl')
        if commit:
            instance.save()
        return instance

    class Meta(AutoForm.Meta):
        model = models.Card

class CardFilterForm(MagiFiltersForm):
    search_fields = [
        '_cache_j_stage_girl',
        'name', 'd_names',
        'description', 'd_descriptions',
        'profile', 'd_profiles',
        'message', 'd_messages',
    ]
    search_fields_labels = {
        '_cache_j_stage_girl': _('Stage girl'),
    }
    ordering_fields = [
        ('number', _('Number')),
    ] + [
        (
            u'base_{}'.format(_statistic),
            models.Card._meta.get_field(u'base_{}'.format(_statistic)).verbose_name,
        ) for _statistic in models.Card.STATISTICS_FIELDS
    ]
    merge_fields = [
        ('school', 'stage_girl'),
    ]

    stage_girl = forms.ChoiceField(label=_('Stage girl'), choices=getStageGirlChoices())

    school = forms.ChoiceField(label=_('School'), choices=getSchoolChoices())
    school_filter = MagiFilter(selector='stagegirl__school', distinct=True)

    type = forms.ChoiceField(label=_('Type'), choices=models.Card.TYPE_CHOICES)
    type_filter = MagiFilter(to_queryset=(
        lambda form, queryset, request, value: models.Card.TYPES[value]['filter'](queryset)
    ))

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

    resists_against = forms.ChoiceField(label=_('Resists against'), choices=models.ELEMENT_CHOICES)
    resists_against_filter = MagiFilter(selector='i_element', to_value=_against_to_value('resists', 'weak'))

    weak_against = forms.ChoiceField(label=_('Weak against'), choices=models.ELEMENT_CHOICES)
    weak_against_filter = MagiFilter(selector='i_element', to_value=_against_to_value('weak', 'resists'))

    def __init__(self, *args, **kwargs):
        super(CardFilterForm, self).__init__(*args, **kwargs)
        if 'school' in self.fields:
            self.fields['school'].choices = getSchoolChoices()

    class Meta(MagiFiltersForm.Meta):
        model = models.Card
        fields = [
            'search',
            'stage_girl', 'school',
            'i_rarity', 'i_element',
            'type', 'i_damage', 'i_position',
            'c_roles',
            'resists_against', 'weak_against',
        ]
