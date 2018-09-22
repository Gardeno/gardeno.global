from django.db import models
from django.contrib.gis.db import models
from gardeno.models import BaseModel
from accounts.models import User
from django.conf import settings
import logging
import json
from .greengrass_policy import GREENGRASS_POLICY
from django_countries.fields import CountryField
import jwt
from timezone_field import TimeZoneField
import requests
from datetime import datetime, timedelta
from pytz import timezone
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from grows.jobs import execute_relay_schedule

VISIBILITY_OPTIONS = [
    {
        'value': 'Public',
    },
    {
        'value': 'Private',
    },
    {
        'value': 'Unlisted',
    },
]

SENSOR_TYPES = [
    {
        'value': 'Relay / Switch',
        'ionicon_name': 'switch',
        'help_text': 'Uses relay(s) to turn grow components on and off.',
        'aws_thing_type_name': 'Ambient_Indoor_Grow_Sensor',
    },
    {
        'value': 'Ambient',
        'ionicon_name': 'thermometer',
        'help_text': 'Measures ambient temperature, humidity, pressure, etc for the grow.',
        'aws_thing_type_name': 'Ambient_Indoor_Grow_Sensor',
    },
    {
        'value': 'Outdoor',
        'ionicon_name': 'rainy',
        'help_text': 'Measures outdoor conditions',
        'aws_thing_type_name': 'Outdoor_Grow_Sensor',
    },
    {
        'value': 'Camera',
        'ionicon_name': 'camera',
        'help_text': 'Takes pictures of the grow or components of the grow',
        'aws_thing_type_name': 'Camera_Sensor',
    },
    {
        'value': 'CO2',
        'ionicon_name': 'globe',
        'help_text': 'Measures CO2 levels',
        'aws_thing_type_name': 'CO2_Sensor',
    },
    {
        'value': 'pH / EOC',
        'ionicon_name': 'flask',
        'help_text': 'Measures and logs water quality and content',
        'aws_thing_type_name': 'Water_Quality_Sensor',
    },
    {
        'value': 'Air Quality',
        'ionicon_name': 'nuclear',
        'help_text': 'Keeps track of the air quality',
        'aws_thing_type_name': 'Air_Quality_Sensor',
    },
]

VISIBILITY_OPTION_VALUES = [x['value'] for x in VISIBILITY_OPTIONS]
SENSOR_TYPE_VALUES = [x['value'] for x in SENSOR_TYPES]
SENSOR_AWS_TYPE_LOOKUP = dict((x['value'], x['aws_thing_type_name']) for x in SENSOR_TYPES)


class Grow(BaseModel):
    """
    A grow is the highest level of an individual operation.
    It may be a rooftop, a living room, a greenhouse, or other
    contained system that is comprised of individual grow components.
    A grow can have multiple stories, but this is designated
    by the Z position of a given rack.
    """
    identifier = models.UUIDField(null=True)
    title = models.CharField(max_length=255, null=True)
    '''
    To update a PointField:

    from django.contrib.gis.geos import Point
    grow = Grow.objects.all()[0]
    grow.location = Point(-104.813959, 39.752304)
    grow.save()
    '''
    location = models.PointField(null=True, blank=True)
    timezone = TimeZoneField(null=True)

    is_live = models.BooleanField(default=True,
                                  help_text="A live grow has consistent setup and testing procedures,"
                                            "reliable sensor data, regular harvesting and maintenance, etc."
                                            "A non-live grow is for testing, R&D, or some other sort of grow.")

    date_published = models.DateTimeField(null=True, blank=True)
    visibility = models.CharField(max_length=255,
                                  choices=[(x, x) for x in VISIBILITY_OPTION_VALUES],
                                  default='Public')

    created_by_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_grows')

    def is_owned_by_user(self, user):
        return self.created_by_user and user.id == self.created_by_user.id

    def __str__(self):
        return self.title


class Rack(BaseModel):
    """
    A rack is used for small, homegrown vertical farming systems.
    You can find a rack at Costco or other similar retailers:
        https://www.costco.com/Alera-4-Shelf-Wire-Rack-48%22-x-24%22-x-72%22-NSF.product.11316751.html
    """
    identifier = models.UUIDField(null=True)
    grow = models.ForeignKey(Grow, null=True, on_delete=models.CASCADE)
    '''
    Looking at a grow from above...coordinate system as follows
    # TODO: Can we get internal GPS resolution precise enough to move racks around and understand where they are?
    # Should we use some sort of internal GPS standard?
    # Perhaps it doesn't matter because we are standardizing rack sizes for now?
    x
    |
    |
    |
    |
    |
    |
    |______________ y
    '''
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    '''
    The position_z field allows for multiple stories in a grow.
    '''
    position_z = models.IntegerField(default=0, help_text='The vertical position of the grow in stories. Default is 0'
                                                          'for ground or first-floor racks.')

    alphabetical_nickname = models.CharField(max_length=255, null=True,
                                             help_text="A memorable nickname for the rack, for quick reference"
                                                       " while inside a grow. Reference Six Sigma lab procedures.")

    def __str__(self):
        return '{}'.format(self.grow.title if self.grow else 'No Grow')


class Tray(BaseModel):
    """
    A tray (also known as a 1020 flat) holds the product.
    You can find a really good tray from the Bootstrap Farmer:
        https://www.bootstrapfarmer.com/products/1020-trays-multi-color?variant=302800109582
    """
    identifier = models.UUIDField(null=True)


class TrayPosition(BaseModel):
    """
    Trays can be moved around between racks.
    """
    tray = models.ForeignKey(Tray, null=True, on_delete=models.CASCADE)
    '''
    Looking at a rack from the side...coordinate system as follows
    x
    |
    |
    |
    |
    |
    |
    |______________ y
    '''
    rack = models.ForeignKey(Rack, null=True, on_delete=models.CASCADE)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)


class Sensor(BaseModel):
    grow = models.ForeignKey(Grow, null=True, related_name='sensors', on_delete=models.CASCADE)
    identifier = models.UUIDField(null=True)
    created_by_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=50, choices=[(x, x) for x in SENSOR_TYPE_VALUES])
    has_been_setup = models.BooleanField(default=False)
    vpn_config = models.TextField(null=True, blank=True)
    vpn_diagnostics = models.TextField(null=True, blank=True)

    # AWS specific values
    aws_thing_name = models.CharField(max_length=255, null=True, blank=True)
    aws_thing_arn = models.CharField(max_length=255, null=True, blank=True)
    aws_thing_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)

    def generate_auth_token(self):
        active_authentication_tokens = self.authentication_tokens.filter(date_deactivated__isnull=True)
        if not active_authentication_tokens:
            active_authentication_token = SensorAuthenticationToken.objects.create(sensor=self)
        else:
            active_authentication_token = active_authentication_tokens[0]
        return jwt.encode({"sensor_authentication_token_id": active_authentication_token.id}, settings.JWT_SECRET,
                          algorithm='HS256').decode('utf-8')

    def setup_vpn_config(self):
        result = requests.post(
            settings.VPN_SECRET_URL,
            json={
                "grow_id": str(self.grow.identifier),
                "client_type": "sensor",
            }
        )
        result_json = result.json()
        self.vpn_config = result_json['config']
        self.vpn_diagnostics = json.dumps(result_json['device'])
        self.save()

    @property
    def vpn_diagnostics_object(self):
        if not self.vpn_diagnostics:
            return {}
        return json.loads(self.vpn_diagnostics)

    def to_json(self):
        return {
            "identifier": str(self.identifier),
            "name": self.name,
        }


class SensorSetupToken(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(Sensor, related_name='setup_tokens', on_delete=models.CASCADE)
    identifier = models.UUIDField()
    date_last_downloaded = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)

    def to_json(self):
        return {
            "identifier": str(self.identifier),
        }


class SensorAuthenticationToken(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_deactivated = models.DateTimeField(null=True, blank=True)
    sensor = models.ForeignKey(Sensor, related_name='authentication_tokens', on_delete=models.CASCADE)
    date_last_used = models.DateTimeField(null=True, blank=True)


class SensorUpdate(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(Sensor, related_name='updates', on_delete=models.CASCADE)
    update = models.TextField(null=True)

    @property
    def update_object(self):
        return json.loads(self.update)

    def __str__(self):
        return '{} - {}'.format(self.sensor, self.date_created)

    class Meta:
        ordering = ['-date_created']


class SensorRelay(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(Sensor, related_name='relays', on_delete=models.CASCADE)
    identifier = models.UUIDField(null=True)
    name = models.CharField(max_length=255, null=True)
    pin = models.IntegerField()

    def __str__(self):
        return '{} - {}'.format(self.sensor, self.name)


class RelaySchedule(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    relay = models.ForeignKey(SensorRelay, related_name='schedules', on_delete=models.CASCADE)
    hour = models.IntegerField()
    minute = models.IntegerField()
    second = models.IntegerField(default=0)
    action = models.CharField(max_length=10, null=True, choices=(('On', 'On'), ('Off', 'Off')))
    is_enabled = models.BooleanField(default=True)

    @property
    def timezone(self):
        return self.relay.sensor.grow.timezone

    @property
    def pretty_time(self):
        local_time_now = datetime.now(self.timezone)
        localized_time = self.timezone.localize(datetime(local_time_now.year, local_time_now.month, local_time_now.day,
                                                         self.hour, self.minute, self.second))
        return localized_time.strftime('%-I:%M:%S %p')

    @property
    def last_run_time(self):
        items = self.schedule_items.filter(date_scheduled__lte=datetime.now(timezone('UTC')))
        if items:
            return items[0].date_scheduled
        return None

    @property
    def next_run_time(self):
        items = self.schedule_items.filter(date_scheduled__gt=datetime.now(timezone('UTC')))
        if items:
            return items[0].date_scheduled
        return None

    def calculate_next_runtime_utc(self, last_scheduled_datetime_utc=None):
        if not last_scheduled_datetime_utc:
            local_time_now = datetime.now(self.timezone)
            first_execution_time = datetime(local_time_now.year, local_time_now.month, local_time_now.day,
                                            self.hour, self.minute, self.second,
                                            tzinfo=local_time_now.tzinfo)
            if first_execution_time < local_time_now:
                first_execution_time = first_execution_time + timedelta(hours=24)
            return first_execution_time.astimezone(timezone('UTC'))
        else:
            last_scheduled_datetime_local = last_scheduled_datetime_utc.astimezone(self.timezone)
            next_execution_time_utc = last_scheduled_datetime_utc + timedelta(days=1)
            print('Next execution time UTC: {}'.format(next_execution_time_utc))
            next_execution_time_local = next_execution_time_utc.astimezone(self.timezone)
            print('Next execution time local: {}'.format(next_execution_time_local))
            if last_scheduled_datetime_local.hour > next_execution_time_local.hour:
                # If we have a relay schedule item that was scheduled for 11pm on 2018-11-03
                # in the America/Denver timezone then +24 hours will be 10pm on 2018-11-03
                # We are therefore falling back an hour and need to add 1 hour to the
                # desired execution time.
                next_execution_time_local = next_execution_time_local + timedelta(hours=1)
            elif last_scheduled_datetime_local.hour < next_execution_time_local.hour:
                # Same deal, only we are springing forward so we need to subtract an hour
                # from the desired execution time.
                next_execution_time_local = next_execution_time_local - timedelta(hours=1)
            return next_execution_time_local.astimezone(timezone('UTC'))

    def enqueue_item_at(self, date_scheduled_utc=None, is_new_schedule=False):
        utc_time_now = datetime.now(timezone('UTC'))
        # First, cancel all existing jobs for this relay because we re-create the schedule
        scheduler = Scheduler(connection=Redis(host=settings.REDIS_HOST, port=6379))
        schedule_items_to_cancel = self.schedule_items.filter(job_id__isnull=False, date_cancelled__isnull=True,
                                                              date_completed__isnull=True, date_failed__isnull=True)
        print('cancelling... {}'.format(schedule_items_to_cancel))
        for schedule_item_to_cancel in schedule_items_to_cancel:
            if schedule_item_to_cancel.job_id in scheduler:
                scheduler.cancel(schedule_item_to_cancel.job_id)
            schedule_item_to_cancel.date_cancelled = utc_time_now
            schedule_item_to_cancel.save()
        # If the relay gets disabled then we return, and because we cancel the schedule items above we are all done
        if not self.is_enabled:
            return
        # Now we create the scheduled job and add a database entry
        relay_schedule_item = RelayScheduleItem.objects.create(relay_schedule=self,
                                                               is_new_schedule=is_new_schedule,
                                                               date_scheduled=date_scheduled_utc)
        scheduled_job = scheduler.enqueue_at(date_scheduled_utc, execute_relay_schedule, relay_schedule_item.id)
        relay_schedule_item.job_id = scheduled_job.id
        relay_schedule_item.save()

    def __str__(self):
        return '{} - {}:{} ({}) - {}'.format(self.relay, self.hour, self.minute, self.timezone, self.action)


class RelayScheduleItem(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    relay_schedule = models.ForeignKey(RelaySchedule, related_name='schedule_items', on_delete=models.CASCADE)
    is_new_schedule = models.BooleanField(default=False,
                                          help_text='If checked, this item began a new schedule for the relay.')
    date_scheduled = models.DateTimeField(null=True)
    job_id = models.UUIDField(null=True)
    date_cancelled = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    date_failed = models.DateTimeField(null=True, blank=True)
    failure_text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date_created']


class GrowSensorPreferences(BaseModel):
    grow = models.OneToOneField(Grow, related_name='preferences', on_delete=models.CASCADE)
    wifi_network_name = models.CharField(max_length=255, null=True, blank=True)
    wifi_password = models.CharField(max_length=255, null=True, blank=True)
    wifi_type = models.CharField(max_length=10, null=True, blank=True,
                                 choices=(('WPA/WPA2', 'WPA/WPA2'), ('WEP', 'WEP'), ('Open', 'Open (no password)')))
    wifi_country_code = CountryField(null=True, blank=True)
    publish_ssh_key_for_authentication = models.TextField(null=True, blank=True)
    sensor_user_password = models.CharField(max_length=255, null=True, blank=True,
                                            help_text='Will be auto-generated if left blank.')
