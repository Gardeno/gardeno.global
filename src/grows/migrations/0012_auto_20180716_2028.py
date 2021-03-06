# Generated by Django 2.0.4 on 2018-07-16 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grows', '0011_auto_20180716_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='aws_thing_arn',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='sensor',
            name='aws_thing_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='sensor',
            name='aws_thing_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='grow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='grows.Grow'),
        ),
    ]
