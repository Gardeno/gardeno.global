# Generated by Django 2.0.4 on 2018-07-16 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_grow_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='grow_limit',
            field=models.IntegerField(default=10, help_text='Maximum number of grows this user can create.', null=True),
        ),
    ]
