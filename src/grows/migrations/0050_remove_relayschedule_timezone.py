# Generated by Django 2.0.4 on 2018-09-22 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0049_auto_20180922_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relayschedule',
            name='timezone',
        ),
    ]
