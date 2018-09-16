# Generated by Django 2.0.4 on 2018-08-12 20:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_team_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammembership',
            old_name='person',
            new_name='user',
        ),
        migrations.AddField(
            model_name='team',
            name='created_by_user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='created_teams', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]