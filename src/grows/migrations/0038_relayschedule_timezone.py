# Generated by Django 2.0.4 on 2018-09-21 01:36

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0037_relayschedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='relayschedule',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(null=True),
        ),
    ]
