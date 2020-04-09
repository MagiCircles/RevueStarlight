from collections import OrderedDict
from django.db.models.fields.related import ManyToManyField
from magi.tools import (
    generateSettings,
)
from magi.utils import (
    listUnique,
)
from starlight.import_data import (
    IMPORT_CONFIGURATION,
    ACT_IMPORT_CONFIGURATION,
)
from starlight import models

def generate_settings():
    print 'Cache schools'
    schools = OrderedDict([
        (school.pk, {
            'name': school.name,
            'names': school.names,
            'white_image': school.white_image_url or school.image_url,
            'image': school.image_url,
        })
        for school in models.School.objects.all().order_by('id')
    ])

    # print 'Add events to latest news'
    # recent_events = models.Event.objects.get(end_date__gte=two_days_ago)
    # latest_news += [{
    #     'title': event.name,
    #     'image': event.image_url,
    #     'url': event.item_url,
    # } for event in recent_events]

    print 'Max statistics'
    try:
        max_statistics = {
            model.collection_name: {
                prefix: {
                    statistic: getattr(model.objects.order_by(u'-{prefix}{statistic}'.format(
                        prefix=prefix, statistic=statistic,
                    ))[0], u'{prefix}{statistic}'.format(
                        prefix=prefix, statistic=statistic,
                    )) for statistic in model.STATISTICS_FIELDS
                } for prefix in ['delta_', 'max_level_']
            } for model in (models.Card, models.Memoir)
        }
    except IndexError:
        max_statistics = {}

    print 'Cache importable fields'
    importable_fields = {}
    for configuration in IMPORT_CONFIGURATION.values() + [ACT_IMPORT_CONFIGURATION]:
        ok_to_edit_fields = configuration.get('dont_erase_existing_value_fields', [])
        imported_fields = listUnique(
            configuration.get('unique_fields', [])
            + configuration.get('fields', [])
            + configuration.get('mapped_fields', []),
        )
        many2many_fields = []
        for field in imported_fields:
            if isinstance(configuration['model']._meta.get_field(field), ManyToManyField):
                many2many_fields.append(field)
        importable_fields[configuration['model'].collection_name] = {
            'imported_fields': imported_fields,
            'ok_to_edit_fields': ok_to_edit_fields,
            'many2many_fields': many2many_fields,
        }

    print 'Save generated settings'
    generateSettings({
        'MAX_STATISTICS': max_statistics,
        'IMPORTABLE_FIELDS': importable_fields,
        'SCHOOLS': schools,
    })
