# Generated by Django 2.0.4 on 2018-09-21 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0045_auto_20180921_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='relayscheduleitem',
            name='failure_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
