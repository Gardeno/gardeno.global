# Generated by Django 2.0.4 on 2018-06-09 04:02

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HazardIdentification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_archived', models.DateTimeField(blank=True, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_archived', models.DateTimeField(blank=True, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NearMiss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_archived', models.DateTimeField(blank=True, null=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
