# Generated by Django 2.0.4 on 2018-07-16 19:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grows', '0010_auto_20180716_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='created_by_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sensor',
            name='identifier',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='type',
            field=models.CharField(choices=[('Ambient', 'Ambient'), ('Outdoor', 'Outdoor'), ('Camera', 'Camera'), ('CO2', 'CO2'), ('pH / EOC', 'pH / EOC'), ('Air Quality', 'Air Quality')], max_length=50),
        ),
    ]
