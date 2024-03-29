# Generated by Django 2.0.4 on 2018-10-29 21:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('events', '0005_auto_20181029_1758'),
        ('salads', '0002_auto_20181029_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='salad',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.Event'),
        ),
        migrations.AddField(
            model_name='salad',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.Order'),
        ),
    ]
