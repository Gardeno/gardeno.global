# Generated by Django 2.0.4 on 2018-09-21 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0044_auto_20180921_1816'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relayscheduleitem',
            options={'ordering': ['-date_cancelled', '-date_scheduled']},
        ),
        migrations.AddField(
            model_name='relayschedule',
            name='second',
            field=models.IntegerField(default=0),
        ),
    ]