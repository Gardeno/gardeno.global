# Generated by Django 2.0.4 on 2018-09-21 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0039_relayschedule_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='relayschedule',
            name='job_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
