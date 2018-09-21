import django
import os


def _setup():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gardeno.settings")
    django.setup()


def execute_relay_schedule(relay_schedule_id, **kwargs):
    _setup()
    from grows.models import RelaySchedule
    print('Executing!')
    relay_schedule = RelaySchedule.objects.get(id=relay_schedule_id)
    print('Running schedule: {}'.format(relay_schedule))
    print('Kwargs: {}'.format(kwargs))
