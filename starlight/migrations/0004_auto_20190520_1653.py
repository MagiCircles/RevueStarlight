# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('starlight', '0003_auto_20190518_0413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Act',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('i_type', models.PositiveIntegerField(verbose_name='Type', choices=[(0, 'Basic'), (1, 'Climax'), (2, 'Auto'), (3, 'Finishing')])),
                ('name', models.CharField(max_length=100, verbose_name='Title', db_index=True)),
                ('d_names', models.TextField(null=True, verbose_name='Title')),
                ('template', models.CharField(max_length=100, verbose_name='Template', db_index=True)),
                ('d_templates', models.TextField(null=True, verbose_name='Template')),
                ('image', models.ImageField(upload_to=magi.utils.uploadItem(b'card'), null=True, verbose_name='Image')),
                ('_original_image', models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'card'))),
                ('cost', models.PositiveIntegerField(default=1, verbose_name=b'AP')),
                ('owner', models.ForeignKey(related_name='added_acts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='card',
            name='c_elements',
        ),
        migrations.RemoveField(
            model_name='memoir',
            name='c_elements',
        ),
        migrations.AddField(
            model_name='card',
            name='base_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='base_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='base_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='base_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='base_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='c_roles',
            field=models.TextField(null=True, verbose_name='Roles'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='d_descriptions',
            field=models.TextField(null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='d_messages',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='d_profiles',
            field=models.TextField(null=True, verbose_name='Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='delta_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='delta_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='delta_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='delta_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='delta_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='description',
            field=models.TextField(null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='i_element',
            field=models.PositiveIntegerField(default=0, db_index=True, verbose_name='Element', choices=[(0, 'Flower'), (1, 'Wind'), (2, 'Snow'), (3, 'Cloud'), (4, 'Moon'), (5, 'Cosmos'), (6, 'Dream')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='card',
            name='limited',
            field=models.BooleanField(default=False, verbose_name='Limited'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='message',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='profile',
            field=models.TextField(null=True, verbose_name='Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='base_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='c_roles',
            field=models.TextField(null=True, verbose_name='Roles'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='d_descriptions',
            field=models.TextField(null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='d_messages',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='d_profiles',
            field=models.TextField(null=True, verbose_name='Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='delta_act_power',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 ACT Power'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='delta_agility',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Agility'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='delta_hp',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 HP'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='delta_normal_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Normal defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='delta_special_defense',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0394 Special defense'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='description',
            field=models.TextField(null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='i_element',
            field=models.PositiveIntegerField(default=0, db_index=True, verbose_name='Element', choices=[(0, 'Flower'), (1, 'Wind'), (2, 'Snow'), (3, 'Cloud'), (4, 'Moon'), (5, 'Cosmos'), (6, 'Dream')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='memoir',
            name='limited',
            field=models.BooleanField(default=False, verbose_name='Limited'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='message',
            field=models.TextField(null=True, verbose_name='Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='profile',
            field=models.TextField(null=True, verbose_name='Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='d_weapon_types',
            field=models.TextField(null=True, verbose_name='Weapon'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stagegirl',
            name='weapon_type',
            field=models.CharField(help_text=b'Example: Saber', max_length=100, null=True, verbose_name='Weapon'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='i_position',
            field=models.PositiveIntegerField(default=1, verbose_name='Position', choices=[(0, 'Rear'), (1, 'Center'), (2, 'Front')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='card',
            name='i_rarity',
            field=models.PositiveIntegerField(db_index=True, verbose_name='Rarity', choices=[(1, '\u2605'), (2, '\u2605\u2605'), (3, '\u2605\u2605\u2605'), (4, '\u2605\u2605\u2605\u2605'), (5, '\u2605\u2605\u2605\u2605\u2605'), (6, '\u2605\u2605\u2605\u2605\u2605\u2605')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='memoir',
            name='i_position',
            field=models.PositiveIntegerField(default=1, verbose_name='Position', choices=[(0, 'Rear'), (1, 'Center'), (2, 'Front')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='memoir',
            name='i_rarity',
            field=models.PositiveIntegerField(db_index=True, verbose_name='Rarity', choices=[(1, '\u2605'), (2, '\u2605\u2605'), (3, '\u2605\u2605\u2605'), (4, '\u2605\u2605\u2605\u2605'), (5, '\u2605\u2605\u2605\u2605\u2605'), (6, '\u2605\u2605\u2605\u2605\u2605\u2605')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='color',
            field=magi.utils.ColorField(max_length=10, null=True, verbose_name='Color'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stagegirl',
            name='weapon',
            field=models.CharField(help_text=b'Example: Possibility of Puberty', max_length=100, null=True, verbose_name='Weapon'),
            preserve_default=True,
        ),
    ]
