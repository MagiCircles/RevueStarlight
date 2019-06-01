import datetime
from collections import OrderedDict
from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from magi import urls # unused, loads static
from magi.tools import (
    totalDonatorsThisMonth,
    latestDonationMonth,
    getStaffConfigurations,
    generateSettings,
    getUsersBirthdaysToday,
    getCharactersBirthdays,
)
from magi.utils import (
    staticImageURL,
    birthdays_within,
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
        try:
            card = models.Card.objects.filter(stage_girl=character).all().order_by('-i_rarity', '-number')[0]
        except IndexError:
            return (None, None, None)
        return character.first_name, card.art_original_url, character.item_url
    latest_news = getCharactersBirthdays(
        models.StageGirl.objects.all(),
        get_name_image_url_from_character,
        latest_news=latest_news,
        days_after=12, days_before=1,
        field_name='birthday',
    )
    def get_name_image_url_from_voice_actress(voice_actress):
        return voice_actress.t_name, voice_actress.image_url, voice_actress.item_url
    latest_news = getCharactersBirthdays(
        models.VoiceActress.objects.all(),
        get_name_image_url_from_voice_actress,
        latest_news=latest_news,
        days_after=12, days_before=1,
        field_name='birthday',
    )

    print 'Show a happy birthday banner for the users whose birthday is today'
    latest_news = getUsersBirthdaysToday(
        staticImageURL('generic_banner.png'),
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
        stage_girl.small_image_url,
    ) for stage_girl in all_stage_girls]

    print 'Cache schools'
    all_schools = OrderedDict([
        (school.pk, {
            'name': school.name,
            'names': school.names,
            'white_image': school.white_image_url or school.image_url,
            'image': school.image_url,
        })
        for school in models.School.objects.all().order_by('name')
    ])

    print 'Cache voice actresses'
    all_voiceactresses = OrderedDict([
        (voiceactress.pk, {
            'name': voiceactress.name,
            'names': voiceactress.names,
            'thumbnail': voiceactress.image_thumbnail_url,
        })
        for voiceactress in models.VoiceActress.objects.all().order_by('name')
    ])

    print 'Max statistics'
    max_statistics = {
        statistic: getattr(
            models.Card.objects.order_by(u'-delta_{}'.format(statistic))[0],
            u'delta_{}'.format(statistic),
        ) for statistic in models.Card.STATISTICS_FIELDS
    }

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

    print 'Get homepage cards'
    cards = models.Card.objects.exclude(
        (Q(art__isnull=True) | Q(art=''))
        & (Q(transparent__isnull=True) | Q(transparent='')),
    ).exclude(
        # show_art_on_homepage=False,
    ).order_by('-number')

    is_character_birthday = False
    birthday_today_stage_girls_id = models.StageGirl.objects.filter(
        birthdays_within(days_after=1, days_before=1)).values_list(
            'id', flat=True)
    if birthday_today_stage_girls_id:
        filtered_cards = cards.filter(stage_girl_id__in=birthday_today_stage_girls_id)[:20]
        is_character_birthday = True
    else:
        filtered_cards = None

    if filtered_cards:
        filtered_cards = filtered_cards[:20]
    else:
        filtered_cards = cards[:10]
        is_character_birthday = False

    homepage_arts = []
    position = { 'size': 'cover', 'x': 'center', 'y': 'center' }
    for c in filtered_cards:
        if c.art:
            homepage_arts.append({
                'url': c.art_url,
                'hd_url': c.art_2x_url or c.art_original_url,
                'about_url': c.item_url,
            })
        elif c.transparent:
            homepage_arts.append({
                'foreground_url': c.transparent_url,
                'about_url': c.item_url,
                'position': position,
            })

    homepage_arts.append({
        'url': staticImageURL('default_art.png'),
        'hd_url': staticImageURL('default_art_hd.png'),
    })

    print 'Save generated settings'
    generateSettings({
        'LATEST_NEWS': latest_news,
        'TOTAL_DONATORS': total_donators,
        'DONATION_MONTH': donation_month,
        'HOMEPAGE_ARTS': homepage_arts,
        'IS_CHARACTER_BIRTHDAY': is_character_birthday,
        'STAFF_CONFIGURATIONS': staff_configurations,
        'FAVORITE_CHARACTERS': favorite_characters,
        'SCHOOLS': all_schools,
        'VOICE_ACTRESSES': all_voiceactresses,
        'MAX_STATISTICS': max_statistics,
        # 'BACKGROUNDS': backgrounds,
    }, imports=[
        'from collections import OrderedDict',
    ])

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        generate_settings()
