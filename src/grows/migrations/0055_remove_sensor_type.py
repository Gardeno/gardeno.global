# Generated by Django 2.0.4 on 2018-10-28 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0054_auto_20181028_2321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensor',
            name='type',
        ),
    ]
