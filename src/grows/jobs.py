import django
import os
from datetime import datetime, timedelta
from pytz import timezone


def _setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gardeno.settings")
    django.setup()


def execute_relay_schedule(relay_schedule_id, **kwargs):
    _setup()
    from grows.models import RelayScheduleItem
    # TODO: Put this logic somewhere that is not protected
    from api.views import _sensor_relay_update
    relay_schedule_item = RelayScheduleItem.objects.get(id=relay_schedule_id)
    # Send the command (on or off, for now)
    sensor_relay = relay_schedule_item.relay_schedule.relay
    action = relay_schedule_item.relay_schedule.action.lower()
    _sensor_relay_update(sensor_relay, action)
    # Update the item
    try:
        relay_schedule_item.date_completed = datetime.now(timezone('UTC'))
    except Exception as error:
        relay_schedule_item.failure_text = str(error)
        relay_schedule_item.date_failed = datetime.now(timezone('UTC'))
    relay_schedule_item.save()
    # Schedule the next run
    next_runtime_utc = relay_schedule_item.relay_schedule.calculate_next_runtime_utc(relay_schedule_item.date_scheduled)
    relay_schedule_item.relay_schedule.enqueue_item_at(next_runtime_utc)
