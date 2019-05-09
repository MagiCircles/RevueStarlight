# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('starlight', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('number', models.PositiveIntegerField(unique=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Title')),
                ('d_names', models.TextField(null=True, verbose_name='Title')),
                ('i_rarity', models.PositiveIntegerField(db_index=True, verbose_name='Rarity', choices=[(1, '\u2605'), (2, '\u2605\u2605'), (3, '\u2605\u2605\u2605'), (4, '\u2605\u2605\u2605\u2605')])),
                ('c_elements', models.TextField(null=True, verbose_name='Elements', blank=True)),
                ('i_damage', models.PositiveIntegerField(default=0, verbose_name='Damage', choices=[(0, 'Normal'), (1, 'Special')])),
                ('i_position', models.PositiveIntegerField(default=0, verbose_name='Position', choices=[(0, 'Front'), (1, 'Center'), (2, 'Rear')])),
                ('_2x_image', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card'))),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card'))),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'card'), null=True, verbose_name='Image')),
                ('_original_icon', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/icon'))),
                ('icon', models.ImageField(upload_to=magi.utils.uploadItem(b'card/icon'), null=True, verbose_name='Icon')),
                ('_2x_art', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card/art'))),
                ('_original_art', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/art'))),
                ('_tthumbnail_art', models.ImageField(null=True, upload_to=magi.utils.uploadTthumb(b'card/art'))),
                ('art', models.ImageField(upload_to=magi.utils.uploadItem(b'card/art'), null=True, verbose_name='Art')),
                ('_2x_transparent', models.ImageField(null=True, upload_to=magi.utils.upload2x(b'card/transparent'))),
                ('_original_transparent', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card/transparent'))),
                ('_tthumbnail_transparent', models.ImageField(null=True, upload_to=magi.utils.uploadTthumb(b'card/transparent'))),
                ('transparent', models.ImageField(upload_to=magi.utils.uploadItem(b'card/transparent'), null=True, verbose_name='Transparent')),
                ('live2d_model_package', models.FileField(null=True, upload_to=magi.utils.uploadItem(b'card/live2d'))),
                ('_cache_j_stage_girl', models.TextField(null=True)),
                ('owner', models.ForeignKey(related_name='added_cards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('d_names', models.TextField(null=True, verbose_name='Name')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'school'))),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'school'), null=True, verbose_name='Image')),
                ('m_description', models.TextField(null=True, verbose_name='Description')),
                ('d_m_descriptions', models.TextField(null=True, verbose_name='Description')),
                ('owner', models.ForeignKey(related_name='added_schools', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StageGirl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('d_names', models.TextField(null=True, verbose_name='Name')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'idol'))),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'idol'), null=True, verbose_name='Image')),
                ('birthday', models.DateField(help_text=b'The year will be ignored.', null=True, verbose_name='Birthday')),
                ('i_astrological_sign', models.PositiveIntegerField(null=True, verbose_name='Astrological sign', choices=[(0, 'Leo'), (1, 'Aries'), (2, 'Libra'), (3, 'Virgo'), (4, 'Scorpio'), (5, 'Capricorn'), (6, 'Pisces'), (7, 'Gemini'), (8, 'Cancer'), (9, 'Sagittarius'), (10, 'Aquarius'), (11, 'Taurus')])),
                ('color', magi.utils.ColorField(max_length=10, null=True, verbose_name='Color', blank=True)),
                ('i_year', models.PositiveIntegerField(null=True, verbose_name='School year', choices=[(0, '1st year'), (1, '2nd year'), (2, '3rd year')])),
                ('weapon', models.CharField(max_length=100, null=True, verbose_name='Weapon')),
                ('d_weapons', models.TextField(null=True, verbose_name='Weapon')),
                ('favorite_food', models.CharField(max_length=100, null=True, verbose_name='Liked food')),
                ('d_favorite_foods', models.TextField(null=True, verbose_name='Liked food')),
                ('least_favorite_food', models.CharField(max_length=100, null=True, verbose_name='Disliked food')),
                ('d_least_favorite_foods', models.TextField(null=True, verbose_name='Disliked food')),
                ('likes', models.CharField(max_length=100, null=True, verbose_name='Likes')),
                ('d_likess', models.TextField(null=True, verbose_name='Likes')),
                ('dislikes', models.CharField(max_length=100, null=True, verbose_name='Dislikes')),
                ('d_dislikess', models.TextField(null=True, verbose_name='Dislikes')),
                ('hobbies', models.CharField(max_length=100, null=True, verbose_name='Hobbies')),
                ('d_hobbiess', models.TextField(null=True, verbose_name='Hobbies')),
                ('m_description', models.TextField(null=True, verbose_name='Description')),
                ('d_m_descriptions', models.TextField(null=True, verbose_name='Description')),
                ('owner', models.ForeignKey(related_name='added_stagegirls', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(related_name='students', verbose_name='School', to='starlight.School')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoiceActress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('d_names', models.TextField(null=True, verbose_name='Name')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'voiceactress'))),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'voiceactress'), null=True, verbose_name='Image')),
                ('birthday', models.DateField(null=True, verbose_name='Birthday')),
                ('i_astrological_sign', models.PositiveIntegerField(null=True, verbose_name='Astrological sign', choices=[(0, 'Leo'), (1, 'Aries'), (2, 'Libra'), (3, 'Virgo'), (4, 'Scorpio'), (5, 'Capricorn'), (6, 'Pisces'), (7, 'Gemini'), (8, 'Cancer'), (9, 'Sagittarius'), (10, 'Aquarius'), (11, 'Taurus')])),
                ('i_blood', models.PositiveIntegerField(null=True, verbose_name='Blood type', choices=[(0, b'O'), (1, b'A'), (2, b'B'), (3, b'AB')])),
                ('height', models.PositiveIntegerField(default=None, null=True, verbose_name='Height')),
                ('specialty', models.CharField(max_length=100, null=True, verbose_name='Specialty')),
                ('d_specialtys', models.TextField(null=True, verbose_name='Specialty')),
                ('hobbies', models.CharField(max_length=100, null=True, verbose_name='Hobbies')),
                ('d_hobbiess', models.TextField(null=True, verbose_name='Hobbies')),
                ('m_description', models.TextField(null=True, verbose_name='Description')),
                ('d_m_descriptions', models.TextField(null=True, verbose_name='Description')),
                ('owner', models.ForeignKey(related_name='added_voiceactresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='voice_actress',
            field=models.ForeignKey(related_name='stagegirls', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Voice actress', to='starlight.VoiceActress', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='stage_girl',
            field=models.ForeignKey(related_name='cards', verbose_name='Stage girl', to='starlight.StageGirl'),
            preserve_default=True,
        ),
    ]
