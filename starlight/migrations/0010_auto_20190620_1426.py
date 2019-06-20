# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('starlight', '0009_auto_20190610_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'song'), null=True, verbose_name=b'Album cover')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'song'))),
                ('name', models.CharField(max_length=100, verbose_name='Title')),
                ('d_names', models.TextField(null=True, verbose_name='Title')),
                ('romaji_name', models.CharField(max_length=100, null=True, verbose_name='Title (Romaji)')),
                ('itunes_id', models.PositiveIntegerField(help_text=b'iTunes ID', null=True, verbose_name='Preview')),
                ('length', models.PositiveIntegerField(help_text=b'in seconds', null=True, verbose_name='Length')),
                ('bpm', models.PositiveIntegerField(null=True, verbose_name='Beats per minute')),
                ('release_date', models.DateField(null=True, verbose_name='Release date')),
                ('buy_url', models.URLField(null=True, verbose_name=b'Buy URL')),
                ('composer', models.CharField(max_length=100, null=True, verbose_name='Composer')),
                ('d_composers', models.TextField(null=True, verbose_name='Composer')),
                ('lyricist', models.CharField(max_length=100, null=True, verbose_name='Lyricist')),
                ('d_lyricists', models.TextField(null=True, verbose_name='Lyricist')),
                ('arranger', models.CharField(max_length=100, null=True, verbose_name='Arranger')),
                ('d_arrangers', models.TextField(null=True, verbose_name='Arranger')),
                ('orchestral_arrangement', models.CharField(max_length=100, null=True, verbose_name='Orchestral arrangement')),
                ('d_orchestral_arrangements', models.TextField(null=True, verbose_name='Orchestral arrangement')),
                ('m_romaji_lyrics', models.TextField(null=True, verbose_name='Lyrics (Romaji)')),
                ('_cache_romaji_lyrics', models.TextField(null=True)),
                ('m_japanese_lyrics', models.TextField(null=True, verbose_name='Lyrics (Japanese)')),
                ('_cache_japanese_lyrics', models.TextField(null=True)),
                ('m_lyrics', models.TextField(null=True, verbose_name='Lyrics (Translations)')),
                ('d_m_lyricss', models.TextField(null=True, verbose_name='Lyrics (Translations)')),
                ('_cache_lyrics', models.TextField(null=True)),
                ('owner', models.ForeignKey(related_name='added_songs', to=settings.AUTH_USER_MODEL)),
                ('singers', models.ManyToManyField(related_name='songs', verbose_name='Singers', to='starlight.VoiceActress', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='act',
            name='_cache_tips',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='internal_id',
            field=models.PositiveIntegerField(null=True, verbose_name=b'Internal ID'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='japanese_description',
            field=models.CharField(max_length=191, null=True, verbose_name='Description (Japanese)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='japanese_name',
            field=models.CharField(max_length=100, null=True, verbose_name='Title (Japanese)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='_cache_tips',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collectedmemoir',
            name='rank',
            field=models.PositiveIntegerField(default=5, verbose_name='Rank', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='_cache_tips',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='_cache_description',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='_cache_description',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='_cache_description',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='d_videos',
            field=models.TextField(help_text=b'Enter a valid YouTube URL with format: https://www.youtube.com/watch?v=xxxxxxxxxxx', null=True, verbose_name='Video'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='_cache_description',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='_cache_staff_description',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='d_videos',
            field=models.TextField(help_text=b'Enter a valid YouTube URL with format: https://www.youtube.com/watch?v=xxxxxxxxxxx', null=True, verbose_name='Video'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='description',
            field=models.CharField(max_length=191, null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='name',
            field=models.CharField(max_length=100, null=True, verbose_name='Title', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='voiceactresslink',
            name='url',
            field=models.URLField(max_length=191, verbose_name=b'URL'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='act',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='act',
            name='j_details',
        ),
    ]
