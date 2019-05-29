# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from magi.utils import LANGUAGES_DICT
from magi.management.commands.populate_staffconfigurations import create
from magi import models as magi_models
from magi.urls import RAW_CONTEXT
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
            create({
                'key': u'memoir_rarity_{}_cost'.format(rarity),
                'verbose_key': u'Cost of a memoir rarity {}'.format(rarity),
            })

        create({
            'key': 'max_level',
            'verbose_key': 'Max level',
        })

        ##################################
        # Fill up default values

        magi_models.StaffConfiguration.objects.update_or_create(
            key='get_started', i_language='en',
            defaults={
                'value': u"""# Start sharing your collection of cards!

1. Open the game, then:
    - Tap ![]({static_url}img/get_started_settings.png) **Other** ("その他")
    - Tap ![]({static_url}img/get_started_gallery.png) **Gallery** ("ギャラリー")
    - Tap ![]({static_url}img/get_started_stage_girls.png) **Stage Girls** ("舞台少女").
2. Tap the sorting button (top right) and sort by **ID**.
3. Go through the list of cards below and click "+" on the ones you have to add them to your Starlight Academy collection!

*For more options, go to your profile or the [list of cards](/cards/).*
""".format(
    static_url=RAW_CONTEXT['static_url'],
),
            })
