# Generated by Django 2.0.4 on 2018-07-17 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0024_auto_20180717_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='awsgreengrasscore',
            name='has_been_setup',
            field=models.BooleanField(default=False),
        ),
    ]
