from django.db.models.signals import pre_save
from grows.models import RelaySchedule


def relay_schedule_saved(sender, instance, **kwargs):
    next_runtime_utc = instance.calculate_next_runtime_utc()
    instance.enqueue_item_at(next_runtime_utc)


pre_save.connect(relay_schedule_saved, sender=RelaySchedule)
