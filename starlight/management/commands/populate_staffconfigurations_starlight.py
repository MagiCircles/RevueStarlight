from django.core.management.base import BaseCommand, CommandError
from magi.utils import LANGUAGES_DICT
from magi.management.commands.populate_staffconfigurations import create
from starlight import models

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):

        ##################################
        # Non translatable

        for rarity in models.Card.RARITIES.keys():
            create({
                'key': u'rarity_{}_cost'.format(rarity),
                'verbose_key': u'Cost of a card rarity {}'.format(rarity),
            })
