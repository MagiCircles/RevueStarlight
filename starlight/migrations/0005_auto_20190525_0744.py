# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import magi.utils


class Migration(migrations.Migration):

    dependencies = [
        ('starlight', '0004_auto_20190520_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='act',
            name='_original_small_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'act')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='d_descriptions',
            field=models.TextField(null=True, verbose_name='Description'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='description',
            field=models.CharField(default='', max_length=100, verbose_name='Description'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='act',
            name='j_details',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='small_image',
            field=models.ImageField(upload_to=magi.utils.uploadItem(b'act'), null=True, verbose_name=b'Small image'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='acts',
            field=models.ManyToManyField(related_name='cards', to='starlight.Act'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='memoir',
            name='acts',
            field=models.ManyToManyField(related_name='memoirs', to='starlight.Act'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='_original_image',
            field=models.ImageField(null=True, upload_to=magi.utils.uploadTiny(b'act')),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='i_type',
            field=models.PositiveIntegerField(verbose_name='Type', choices=[(0, 'Basic'), (1, 'Climax'), (2, 'Auto'), (3, 'Finishing'), (4, 'Event')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='act',
            name='image',
            field=models.ImageField(upload_to=magi.utils.uploadItem(b'act'), null=True, verbose_name='Image'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='act',
            unique_together=set([('name', 'description')]),
        ),
        migrations.RemoveField(
            model_name='act',
            name='template',
        ),
        migrations.RemoveField(
            model_name='act',
            name='d_templates',
        ),
    ]
