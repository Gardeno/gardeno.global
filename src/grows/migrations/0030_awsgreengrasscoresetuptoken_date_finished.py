# Generated by Django 2.0.4 on 2018-07-24 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0029_awsgreengrasscoresetuptoken_date_last_downloaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='awsgreengrasscoresetuptoken',
            name='date_finished',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]