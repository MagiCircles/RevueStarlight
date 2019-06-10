# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('starlight', '0008_auto_20190604_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='_cache_j_stage_girl',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='_cache_j_statistics_ranks',
        ),
        migrations.AddField(
            model_name='card',
            name='base_icon',
            field=models.ImageField(help_text=b'Icon without border, as originally extracted from the game', upload_to=magi.utils.uploadItem(b'card/icon'), null=True, verbose_name=b'Base icon'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='is_seasonal',
            field=models.BooleanField(default=False, verbose_name='Seasonal'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_icon',
            field=models.ImageField(help_text=b'Icon without border, as originally extracted from the game', upload_to=magi.utils.uploadItem(b'card/icon'), null=True, verbose_name=b'Base icon'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='is_seasonal',
            field=models.BooleanField(default=False, verbose_name='Seasonal'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='is_vs_revue_reward',
            field=models.BooleanField(default=False, verbose_name='VS. Revue reward'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='_original_birthday_banner',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'stagegirl/birthday')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='birthday_banner',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'stagegirl/birthday')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='d_introductions',
            field=models.TextField(help_text=b'In-game introduction', null=True, verbose_name='Introduction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='d_school_departments',
            field=models.TextField(null=True, verbose_name='Department'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='introduction',
            field=models.TextField(help_text=b'In-game introduction', null=True, verbose_name='Introduction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='school_department',
            field=models.CharField(max_length=100, null=True, verbose_name='Department'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='_original_birthday_banner',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'voiceactress/birthday')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='birthday_banner',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadItem(b'voiceactress/birthday')),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='bound_break_value',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collectedcard',
            name='card',
            field=models.ForeignKey(related_name='collectedcards', verbose_name='Card', to='starlight.Card'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='collectedmemoir',
            name='memoir',
            field=models.ForeignKey(related_name='collectedmemoirs', verbose_name='Memoir', to='starlight.Memoir'),
            preserve_default=True,
        ),
    ]
