import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as django_settings
from django.utils import timezone
from magi import urls # unused, loads static
from magi.utils import (
    staticImageURL,
)
from magi.tools import (
    totalDonatorsThisMonth,
    latestDonationMonth,
    getStaffConfigurations,
    generateSettings,
    getUsersBirthdaysToday,
    getCharactersBirthdays,
)
from starlight import models

def generate_settings():

    now = timezone.now()
    two_days_ago = now - datetime.timedelta(days=2)

    print 'Get total donators'
    total_donators = totalDonatorsThisMonth() or '\'\''

    print 'Get latest donation month'
    donation_month = latestDonationMonth(failsafe=True)

    print 'Get staff configurations and latest news'
    staff_configurations, latest_news = getStaffConfigurations()

    print 'Show a banner for current and upcoming birthdays of characters'
    def get_name_image_url_from_character(character):
        card = models.Card.objects.filter(idol=character).filter(
            show_art_on_homepage=True).order_by('-i_rarity', '-id')[0]
        return character.first_name, card.art_original_url, character.item_url
    latest_news = getCharactersBirthdays(
        models.StageGirl.objects.all(),
        get_name_image_url_from_character,
        latest_news=latest_news,
        days_after=12, days_before=1,
        field_name='birthday',
    )
    # todo same for voice actresses

    print 'Show a happy birthday banner for the users whose birthday is today'
    latest_news = getUsersBirthdaysToday(
        staticImageURL('happy_birthday.png'),
        latest_news=latest_news,
        max_usernames=4,
    )

    # print 'Add events to latest news'
    # recent_events = models.Event.objects.get(end_date__gte=two_days_ago)
    # latest_news += [{
    #     'title': event.name,
    #     'image': event.image_url,
    #     'url': event.item_url,
    # } for event in recent_events]

    print 'Get the characters'
    all_stage_girls = models.StageGirl.objects.all().order_by('name')
    favorite_characters = [(
        stage_girl.pk,
        stage_girl.name,
        stage_girl.image_url,
    ) for stage_girl in all_stage_girls]

    # print 'Get the backgrounds'
    # backgrounds = [
    # {
    #         'id': background.id,
    #         'thumbnail': background.thumbnail_image_url,
    #         'image': background.image_url,
    #           'name': background.name,
    #         'd_names': background.names,
    #     }
    #     for background in models.Background.objects.all()
    # ]

    print 'Save generated settings'
    generateSettings({
        'LATEST_NEWS': latest_news,
        'TOTAL_DONATORS': total_donators,
        'DONATION_MONTH': donation_month,
        'STAFF_CONFIGURATIONS': staff_configurations,
        'FAVORITE_CHARACTERS': favorite_characters,
        # 'BACKGROUNDS': backgrounds,
    })

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        generate_settings()
