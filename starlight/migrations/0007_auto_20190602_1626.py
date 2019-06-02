# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('starlight', '0006_auto_20190529_1218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='card',
            old_name='limited',
            new_name='is_limited',
        ),
        migrations.RenameField(
            model_name='memoir',
            old_name='limited',
            new_name='is_limited',
        ),
        migrations.AddField(
            model_name='act',
            name='bound_break_value',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='d_m_tipss',
            field=models.TextField(null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='d_other_targets',
            field=models.TextField(null=True, verbose_name='Target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='hits',
            field=models.PositiveIntegerField(default=1, verbose_name=b'How many hits?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='i_target',
            field=models.PositiveIntegerField(null=True, verbose_name='Target', choices=[(0, 'Front enemy'), (1, 'Front group of enemies'), (2, 'All enemies')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='m_tips',
            field=models.TextField(help_text=b'Extra details not present in the game that can be good to know for players.', null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='other_target',
            field=models.CharField(max_length=100, null=True, verbose_name='Target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='unlock_at_rank',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='_cache_j_statistics_ranks',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='d_m_tipss',
            field=models.TextField(null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='is_event',
            field=models.BooleanField(default=False, verbose_name='Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='jp_release_date',
            field=models.DateField(null=True, verbose_name='Release date - Japanese version', db_index=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='m_tips',
            field=models.TextField(help_text=b'Extra details not present in the game that can be good to know for players.', null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='show_art_on_homepage',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='ww_release_date',
            field=models.DateField(null=True, verbose_name='Release date - Worldwide version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='_cache_j_statistics_ranks',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='d_m_tipss',
            field=models.TextField(null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='is_event',
            field=models.BooleanField(default=False, verbose_name='Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='jp_release_date',
            field=models.DateField(null=True, verbose_name='Release date - Japanese version', db_index=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='m_tips',
            field=models.TextField(help_text=b'Extra details not present in the game that can be good to know for players.', null=True, verbose_name='Tips'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='show_art_on_homepage',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='ww_release_date',
            field=models.DateField(null=True, verbose_name='Release date - Worldwide version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='monochrome_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'school')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='white_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'school')),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='friend_id',
            field=models.CharField(max_length=100, null=True, verbose_name='ID', validators=[django.core.validators.RegexValidator(b'^[0-9]+$', 'Enter a number.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='description',
            field=models.CharField(max_length=600, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='i_element',
            field=models.PositiveIntegerField(db_index=True, verbose_name='Element', choices=[(0, 'Flower'), (1, 'Wind'), (2, 'Snow'), (3, 'Cloud'), (4, 'Moon'), (5, 'Space'), (6, 'Dream')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='i_category',
            field=models.PositiveIntegerField(verbose_name='Category', choices=[(0, 'Anime - Cast'), (1, 'Anime - Staff'), (2, 'General'), (3, 'Stage play'), (4, 'Additional')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='role',
            field=models.CharField(max_length=150, verbose_name='Role', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='social_media_url',
            field=models.CharField(max_length=600, null=True, verbose_name='Social media'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='dislikes',
            field=models.CharField(max_length=150, null=True, verbose_name='Dislikes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='hobbies',
            field=models.CharField(max_length=200, null=True, verbose_name='Hobbies'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='likes',
            field=models.CharField(max_length=150, null=True, verbose_name='Likes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='weapon',
            field=models.CharField(help_text=b'Example: Possibility of Puberty', max_length=200, null=True, verbose_name='Weapon'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='voiceactress',
            name='hobbies',
            field=models.CharField(max_length=600, null=True, verbose_name='Hobbies'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='voiceactress',
            name='specialty',
            field=models.CharField(max_length=600, null=True, verbose_name='Specialty'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='voiceactresslink',
            name='url',
            field=models.CharField(max_length=600, verbose_name='URL'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='act',
            unique_together=set([('name', 'description', 'unlock_at_rank')]),
        ),
    ]
