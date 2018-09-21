# Generated by Django 2.0.4 on 2018-09-21 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0036_sensorrelay_identifier'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelaySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('hour', models.IntegerField()),
                ('minute', models.IntegerField()),
                ('relay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='grows.SensorRelay')),
            ],
        ),
    ]
