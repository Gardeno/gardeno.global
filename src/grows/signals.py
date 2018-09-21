from django.db.models.signals import pre_save
from grows.models import RelaySchedule
from django.conf import settings

from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import timedelta
from grows.jobs import execute_relay_schedule


def relay_schedule_saved(sender, instance, **kwargs):
    scheduler = Scheduler(connection=Redis(host=settings.REDIS_HOST, port=6379))
    if instance.job_id and instance.job_id in scheduler:
        scheduler.cancel(instance.job_id)
    enqueued_job = scheduler.enqueue_in(timedelta(seconds=30), execute_relay_schedule, instance.id)
    instance.job_id = enqueued_job.id


pre_save.connect(relay_schedule_saved, sender=RelaySchedule)
