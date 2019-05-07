# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_cache_owner_last_update', models.DateTimeField(null=True)),
                ('_cache_owner_username', models.CharField(max_length=32, null=True)),
                ('_cache_owner_email', models.EmailField(max_length=75, blank=True)),
                ('_cache_owner_preferences_i_status', models.CharField(max_length=12, null=True)),
                ('_cache_owner_preferences_twitter', models.CharField(max_length=32, null=True, blank=True)),
                ('_cache_owner_color', models.CharField(max_length=100, null=True, blank=True)),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='Join date')),
                ('nickname', models.CharField(help_text="Give a nickname to your account to easily differentiate it from your other accounts when you're managing them.", max_length=200, null=True, verbose_name='Nickname')),
                ('start_date', models.DateField(null=True, verbose_name='Start date')),
                ('level', models.PositiveIntegerField(null=True, verbose_name='Level')),
                ('default_tab', models.CharField(max_length=100, null=True, verbose_name='Default tab')),
                ('_cache_leaderboards_last_update', models.DateTimeField(null=True)),
                ('_cache_leaderboard', models.PositiveIntegerField(null=True)),
                ('owner', models.ForeignKey(related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
