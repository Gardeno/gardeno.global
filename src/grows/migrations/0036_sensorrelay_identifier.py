# Generated by Django 2.0.4 on 2018-09-18 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0035_sensorrelay'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensorrelay',
            name='identifier',
            field=models.UUIDField(null=True),
        ),
    ]