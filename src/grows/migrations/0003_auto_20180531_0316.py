# Generated by Django 2.0.4 on 2018-05-31 03:16

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0002_auto_20180531_0309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rack',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='rack',
            name='longitude',
        ),
        migrations.AddField(
            model_name='grow',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]
