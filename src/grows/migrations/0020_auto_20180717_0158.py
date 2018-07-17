# Generated by Django 2.0.4 on 2018-07-17 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0019_auto_20180717_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='grow',
            name='greengrass_core_policy_arn',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='grow',
            name='greengrass_core_policy_document',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='grow',
            name='greengrass_core_policy_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='grow',
            name='greengrass_core_policy_version_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
