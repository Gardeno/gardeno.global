# Generated by Django 2.0.4 on 2018-09-22 16:07

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0047_auto_20180921_1920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relayscheduleitem',
            options={'ordering': ['-date_created']},
        ),
        migrations.AddField(
            model_name='grow',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(null=True),
        ),
    ]