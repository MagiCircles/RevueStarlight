from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from starlight.import_data import import_data

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        import_data(
            local='local' in args,
            to_import=[arg for arg in args if arg != 'local'] or None,
            log_function=print,
        )