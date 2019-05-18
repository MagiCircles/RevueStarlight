# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('starlight', '0002_auto_20190509_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='Memoir',
            fields=[
                ('number', models.PositiveIntegerField(unique=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Title')),
                ('d_names', models.TextField(null=True, verbose_name='Title')),
                ('i_rarity', models.PositiveIntegerField(db_index=True, verbose_name='Rarity', choices=[(1, '\u2605'), (2, '\u2605\u2605'), (3, '\u2605\u2605\u2605'), (4, '\u2605\u2605\u2605\u2605')])),
                ('c_elements', models.TextField(null=True, verbose_name='Elements', blank=True)),
                ('i_damage', models.PositiveIntegerField(default=0, verbose_name='Damage', choices=[(0, 'Normal'), (1, 'Special')])),
                ('i_position', models.PositiveIntegerField(default=0, verbose_name='Position', choices=[(0, 'Front'), (1, 'Center'), (2, 'Rear')])),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'card'), null=True, verbose_name='Image')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card'))),
                ('_2x_image', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card'))),
                ('icon', models.ImageField(upload_to=magi.utils.uploadItem(b'card/icon'), null=True, verbose_name='Icon')),
                ('_original_icon', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/icon'))),
                ('art', models.ImageField(upload_to=magi.utils.uploadItem(b'card/art'), null=True, verbose_name='Art')),
                ('_original_art', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/art'))),
                ('_tthumbnail_art', models.ImageField(null=True, upload_to=magi.utils.uploadTthumb(b'card/art'))),
                ('_2x_art', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card/art'))),
                ('transparent', models.ImageField(upload_to=magi.utils.uploadItem(b'card/transparent'), null=True, verbose_name='Transparent')),
                ('_original_transparent', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/transparent'))),
                ('_tthumbnail_transparent', models.ImageField(null=True, upload_to=magi.utils.uploadTthumb(b'card/transparent'))),
                ('_2x_transparent', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card/transparent'))),
                ('live2d_model_package', models.FileField(null=True, upload_to=magi.utils.uploadItem(b'card/live2d'))),
                ('_cache_j_stage_girl', models.TextField(null=True)),
                ('owner', models.ForeignKey(related_name='added_memoirs', to=settings.AUTH_USER_MODEL)),
                ('stage_girl', models.ForeignKey(related_name='memoirs', verbose_name='Stage girl', to='starlight.StageGirl')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('d_names', models.TextField(null=True, verbose_name='Name')),
                ('role', models.CharField(max_length=100, verbose_name='Role', db_index=True)),
                ('d_roles', models.TextField(null=True, verbose_name='Role')),
                ('social_media_url', models.CharField(max_length=100, null=True, verbose_name='Social media')),
                ('importance', models.IntegerField(default=0, help_text=b'Allows to re-order how the staff appear. Highest number shows first.', verbose_name=b'Importance', db_index=True)),
                ('owner', models.ForeignKey(related_name='added_staff', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoiceActressLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Platform')),
                ('d_names', models.TextField(null=True, verbose_name='Platform')),
                ('url', models.CharField(max_length=100, verbose_name='URL')),
                ('owner', models.ForeignKey(related_name='added_voiceactresslinks', to=settings.AUTH_USER_MODEL)),
                ('voice_actress', models.ForeignKey(related_name='links', verbose_name='Voice actress', to='starlight.VoiceActress')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='small_image',
            field=models.ImageField(help_text=b'Map pins, favorite characters on profile and character selectors.', null=True, upload_to=magi.utils.uploadItem(b'stagegirl/s')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='video',
            field=magi.utils.YouTubeVideoField(null=True, verbose_name='Video'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='_tthumbnail_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTthumb(b'voiceactress')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='voiceactress',
            name='video',
            field=magi.utils.YouTubeVideoField(null=True, verbose_name='Video'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='_original_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'stagegirl')),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='image',
            field=models.ImageField(upload_to=magi.utils.uploadItem(b'stagegirl'), null=True, verbose_name='Image'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='voiceactress',
            name='name',
            field=models.CharField(unique=True, max_length=100, verbose_name='Name', db_index=True),
            preserve_default=True,
        ),
    ]
