# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('starlight', '0007_auto_20190602_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='max_level_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='max_level_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='max_level_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='max_level_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='max_level_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='min_level_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='min_level_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='min_level_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='min_level_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='min_level_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank1_rarity2_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank1_rarity3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank1_rarity4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank1_rarity5_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank1_rarity6_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank2_rarity2_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank2_rarity3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank2_rarity4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank2_rarity5_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank2_rarity6_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank3_rarity2_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank3_rarity3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank3_rarity4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank3_rarity5_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank3_rarity6_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank5_rarity2_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank5_rarity3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank5_rarity4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank5_rarity5_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank5_rarity6_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank7_rarity3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank7_rarity4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank7_rarity5_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rank7_rarity6_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'card/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='max_level_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='max_level_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='max_level_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='max_level_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='max_level_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Max level Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='min_level_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='min_level_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='min_level_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='min_level_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='min_level_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Min level Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='rank1_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'memoir/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='rank2_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'memoir/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='rank3_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'memoir/icon')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='rank4_icon',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'memoir/icon')),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collectedcard',
            name='rank',
            field=models.PositiveIntegerField(default=7, verbose_name='Rank', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
            preserve_default=True,
        ),
    ]
