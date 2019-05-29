# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('starlight', '0005_auto_20190525_0744'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectedCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_cache_account_last_update', models.DateTimeField(null=True)),
                ('_cache_j_account', models.TextField(null=True)),
                ('max_leveled', models.NullBooleanField(verbose_name='Max leveled')),
                ('max_bonded', models.NullBooleanField(verbose_name='Max bonded')),
                ('i_rarity', models.PositiveIntegerField(verbose_name='Rarity', choices=[(1, '\u2605'), (2, '\u2605\u2605'), (3, '\u2605\u2605\u2605'), (4, '\u2605\u2605\u2605\u2605'), (5, '\u2605\u2605\u2605\u2605\u2605'), (6, '\u2605\u2605\u2605\u2605\u2605\u2605')])),
                ('rank', models.PositiveIntegerField(default=1, verbose_name='Rank', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('account', models.ForeignKey(related_name='collectedcards', to='starlight.Account')),
                ('card', models.ForeignKey(related_name='collectedcards', to='starlight.Card')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CollectedMemoir',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_cache_account_last_update', models.DateTimeField(null=True)),
                ('_cache_j_account', models.TextField(null=True)),
                ('max_leveled', models.NullBooleanField(verbose_name='Max leveled')),
                ('account', models.ForeignKey(related_name='collectedmemoirs', to='starlight.Account')),
                ('memoir', models.ForeignKey(related_name='collectedmemoirs', to='starlight.Memoir')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='_2x_transparent',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='_cache_j_stage_girl',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='_original_transparent',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='_tthumbnail_transparent',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='c_roles',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='d_descriptions',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='d_messages',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='d_profiles',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='description',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='i_damage',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='i_element',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='i_position',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='live2d_model_package',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='message',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='stage_girl',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='transparent',
        ),
        migrations.AddField(
            model_name='account',
            name='_thumbnail_screenshot',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadThumb(b'account_screenshot')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='bought_stars',
            field=models.PositiveIntegerField(null=True, verbose_name='Total stars bought'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='center',
            field=models.ForeignKey(related_name='center_of_account', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Center', to='starlight.CollectedCard', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='device',
            field=models.CharField(help_text='The model of your device. Example: Nexus 5, iPhone 4, iPad 2, ...', max_length=150, null=True, verbose_name='Device'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='friend_id',
            field=models.PositiveIntegerField(null=True, verbose_name='ID'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='i_os',
            field=models.PositiveIntegerField(null=True, verbose_name='Operating System', choices=[(0, b'Android'), (1, b'iOs')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='i_play_style',
            field=models.PositiveIntegerField(null=True, verbose_name='Play style', choices=[(0, 'Casual'), (1, 'Hardcore')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='i_version',
            field=models.PositiveIntegerField(default='en', verbose_name='Version', choices=[(0, 'Japanese version'), (1, 'Worldwide version')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='i_vs_revue_rank',
            field=models.PositiveIntegerField(null=True, verbose_name='Vs. Revue rank', choices=[(0, '\u2726 Bronze'), (1, '\u2726\u2726 Bronze'), (2, '\u2726\u2726\u2726 Bronze'), (3, '\u2726 Silver'), (4, '\u2726\u2726 Silver'), (5, '\u2726\u2726\u2726 Silver'), (6, '\u2726 Gold'), (7, '\u2726\u2726 Gold'), (8, '\u2726\u2726\u2726 Gold'), (9, '\u2726 Platinum'), (10, '\u2726\u2726 Platinum'), (11, '\u2726\u2726\u2726 Platinum'), (12, 'Legend')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='is_hidden_from_leaderboard',
            field=models.BooleanField(default=False, db_index=True, verbose_name=b'Hide from leaderboard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='is_playground',
            field=models.BooleanField(default=False, help_text="Check this box if this account doesn't exist in the game.", db_index=True, verbose_name='Playground'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='level_on_screenshot_upload',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='screenshot',
            field=models.ImageField(help_text='In-game profile screenshot', upload_to=magi.utils.uploadItem(b'account_screenshot'), null=True, verbose_name='Screenshot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='show_friend_id',
            field=models.BooleanField(default=True, verbose_name='Should your friend ID be visible to other players?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='stage_of_dreams_level',
            field=models.PositiveIntegerField(null=True, verbose_name='Stage of dreams level'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='_cache_total_collectedcards',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='_cache_total_collectedcards_last_update',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='_cache_total_collectedmemoirs',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='_cache_total_collectedmemoirs_last_update',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='d_explanations',
            field=models.TextField(null=True, verbose_name='Explanation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='explanation',
            field=models.TextField(null=True, verbose_name='Explanation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='is_upgrade',
            field=models.BooleanField(default=False, verbose_name='Upgrade'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='sell_price',
            field=models.PositiveIntegerField(null=True, verbose_name='Selling price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='stage_girls',
            field=models.ManyToManyField(related_name='memoirs', verbose_name='Stage girls', to='starlight.StageGirl', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='d_m_descriptions',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='i_category',
            field=models.PositiveIntegerField(default=0, verbose_name='Category', choices=[(0, 'Anime'), (1, 'Stage play'), (2, 'Additional')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='m_description',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='_original_uniform_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'stagegirl')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='square_image',
            field=models.ImageField(help_text=b'On list page.', null=True, upload_to=magi.utils.uploadItem(b'stagegirl/s')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='uniform_image',
            field=models.ImageField(upload_to=magi.utils.uploadItem(b'stagegirl'), null=True, verbose_name=b'Uniform image'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='d_m_staff_descriptions',
            field=models.TextField(help_text=b'Only visible in staff list.', null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='m_staff_description',
            field=models.TextField(help_text=b'Only visible in staff list.', null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='acts',
            field=models.ManyToManyField(related_name='cards', verbose_name='Acts', to='starlight.Act', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='memoir',
            name='acts',
            field=models.ManyToManyField(related_name='memoirs', verbose_name='Acts', to='starlight.Act', blank=True),
            preserve_default=True,
        ),
    ]
