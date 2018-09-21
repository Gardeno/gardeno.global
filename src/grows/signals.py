from django.db.models.signals import pre_save
from grows.models import RelaySchedule
from django.conf import settings

from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import timedelta
from grows.jobs import execute_relay_schedule

from pytz import timezone
from datetime import datetime


def relay_schedule_saved(sender, instance, **kwargs):
    if not instance.timezone:
        return
    # TODO: Daylight savings. Lol
    local_now = datetime.now(instance.timezone)
    local_datetime = instance.timezone.localize(
        datetime(local_now.year, local_now.month, local_now.day, instance.hour, instance.minute, 0))
    localized_utc_datetime = local_datetime.astimezone(timezone('UTC'))

    scheduler = Scheduler(connection=Redis(host=settings.REDIS_HOST, port=6379))
    if instance.job_id and instance.job_id in scheduler:
        scheduler.cancel(instance.job_id)
    enqueued_job = scheduler.cron(
        '{} {} * * *'.format(localized_utc_datetime.strftime('%M'),
                             localized_utc_datetime.strftime('%H')),
        func=execute_relay_schedule,
        args=[instance.id]
    )
    instance.job_id = enqueued_job.id


pre_save.connect(relay_schedule_saved, sender=RelaySchedule)
