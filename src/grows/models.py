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
    is_live = models.BooleanField(default=True,
                                  help_text="A live grow has consistent setup and testing procedures,"
                                            "reliable sensor data, regular harvesting and maintenance, etc."
                                            "A non-live grow is for testing, R&D, or some other sort of grow.")

    date_published = models.DateTimeField(null=True, blank=True)
    visibility = models.CharField(max_length=255,
                                  choices=[(x, x) for x in VISIBILITY_OPTION_VALUES],
                                  default='Public')

    created_by_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='created_grows')

    def create_greengrass_group(self):
        try:
            greengrass_group_response = settings.GREENGRASS_CLIENT.create_group(Name='{}'.format(self.identifier))
            AWSGreengrassGroup.objects.create(grow=self, arn=greengrass_group_response['Arn'],
                                              group_id=greengrass_group_response['Id'])
            return True
        except Exception as exception:
            logging.error(exception)
            return False

    def create_greengrass_core(self):
        if not hasattr(self, 'aws_greengrass_group'):
            logging.error('Cannot create core until the AWS Greengrass group exists.')
            return False
        core, _ = AWSGreengrassCore.objects.get_or_create(grow=self)
        try:
            core_name = '{}_Core'.format(self.identifier)
            try:
                # We first create a thing
                greengrass_core_thing_response = settings.IOT_CLIENT.create_thing(
                    thingName=core_name,
                    thingTypeName=settings.GREENGRASS_CORE_TYPE_NAME,
                    attributePayload={
                        'attributes': {
                            'grow_id': '{}'.format(self.identifier),
                        }
                    }
                )
                core.thing_name = greengrass_core_thing_response['thingName']
                core.thing_arn = greengrass_core_thing_response['thingArn']
                core.thing_id = greengrass_core_thing_response['thingId']
            except Exception as exception:
                logging.error('Unable to create the Thing')
                logging.error(exception)
                return False
            try:
                # See if the policy already exists
                existing_policy = settings.IOT_CLIENT.get_policy(
                    policyName=core_name
                )
                core.policy_name = existing_policy['policyName']
                core.policy_arn = existing_policy['policyArn']
                core.policy_document = existing_policy['policyDocument']
                core.policy_version_id = existing_policy['defaultVersionId']
            except:
                try:
                    # We then create a policy since one does not exist
                    greengrass_core_policy_response = settings.IOT_CLIENT.create_policy(
                        policyName=core_name,
                        policyDocument=json.dumps(GREENGRASS_POLICY)
                    )
                    core.policy_name = greengrass_core_policy_response['policyName']
                    core.policy_arn = greengrass_core_policy_response['policyArn']
                    core.policy_document = greengrass_core_policy_response['policyDocument']
                    core.policy_version_id = greengrass_core_policy_response['policyVersionId']
                except Exception as exception:
                    logging.error('Unable to create the policy')
                    logging.error(exception)
                    return False
            try:
                # We then create a certificate
                greengrass_core_thing_certificate_response = settings.IOT_CLIENT.create_keys_and_certificate(
                    setAsActive=True
                )
                core.certificate_arn = greengrass_core_thing_certificate_response['certificateArn']
                core.certificate_id = greengrass_core_thing_certificate_response['certificateId']
                core.certificate_pem = greengrass_core_thing_certificate_response['certificatePem']
                core.certificate_keypair_public = greengrass_core_thing_certificate_response['keyPair'][
                    'PublicKey']
                core.certificate_keypair_private = \
                    greengrass_core_thing_certificate_response['keyPair']['PrivateKey']
            except Exception as exception:
                logging.error('Unable to create the certificate')
                logging.error(exception)
                return False
            try:
                # We then attach the certificate to the policy
                settings.IOT_CLIENT.attach_policy(policyName=core.policy_name,
                                                  target=core.certificate_arn)
            except Exception as exception:
                logging.error('Unable to attach the certificate to the policy')
                logging.error(exception)
                return False
            try:
                # We then attach the thing to the certificate
                settings.IOT_CLIENT.attach_thing_principal(thingName=core.thing_name,
                                                           principal=core.certificate_arn)
            except Exception as exception:
                logging.error('Unable to attach the Thing to the certificate')
                logging.error(exception)
                return False
            try:
                response = settings.GREENGRASS_CLIENT.create_core_definition(
                    InitialVersion={
                        'Cores': [
                            {
                                'CertificateArn': core.certificate_arn,
                                'Id': '{}'.format(self.identifier),
                                'SyncShadow': True,
                                'ThingArn': core.thing_arn
                            },
                        ]
                    },
                    Name=core_name,
                )
                core.arn = response['Arn']
                core.core_id = response['Id']
                core.latest_version = response['LatestVersion']
                core.latest_version_arn = response['LatestVersionArn']
            except Exception as exception:
                logging.error('Unable to create the core definition')
                logging.error(exception)
                return False
            try:
                settings.GREENGRASS_CLIENT.create_group_version(
                    GroupId=self.aws_greengrass_group.group_id,
                    CoreDefinitionVersionArn=core.latest_version_arn,
                )
            except Exception as exception:
                logging.error('Unable to create the core definition')
                logging.error(exception)
                return False
            core.save()
            return True
        except Exception as exception:
            logging.error('Unable to create the core')
            logging.error(exception)
            return False

    @property
    def has_created_greengrass_group(self):
        if not hasattr(self, 'aws_greengrass_group'):
            return False
        return self.aws_greengrass_group.arn and self.aws_greengrass_group.group_id

    @property
    def has_created_greengrass_core(self):
        # May return differently if we've created the thing or certificate but not the full core, so stubbed out
        # the conditionals appropriately.
        if not hasattr(self, 'aws_greengrass_core'):
            return False
        if not self.aws_greengrass_core.thing_name or not self.aws_greengrass_core.thing_arn or not self.aws_greengrass_core.thing_id:
            return False
        if not self.aws_greengrass_core.certificate_arn or not self.aws_greengrass_core.certificate_id or not self.aws_greengrass_core.certificate_pem or not self.aws_greengrass_core.certificate_keypair_public or not self.aws_greengrass_core.certificate_keypair_private:
            return False
        if not self.aws_greengrass_core.policy_name or not self.aws_greengrass_core.policy_arn or not self.aws_greengrass_core.policy_document or not self.aws_greengrass_core.policy_version_id:
            return False
        if not self.aws_greengrass_core.arn or not self.aws_greengrass_core.core_id or not self.aws_greengrass_core.latest_version or not self.aws_greengrass_core.latest_version_arn:
            return False
        return True

    def is_owned_by_user(self, user):
        return self.created_by_user and user.id == self.created_by_user.id

    def __str__(self):
        return self.title


class AWSGreengrassGroup(models.Model):
    grow = models.OneToOneField(Grow, on_delete=models.CASCADE, related_name='aws_greengrass_group')
    arn = models.CharField(max_length=255, null=True, blank=True)
    group_id = models.CharField(max_length=255, null=True, blank=True)


class AWSGreengrassCore(models.Model):
    grow = models.OneToOneField(Grow, on_delete=models.CASCADE, related_name='aws_greengrass_core')

    has_been_setup = models.BooleanField(default=False)

    # AWS Greengrass configuration

    thing_name = models.CharField(max_length=255, null=True, blank=True)
    thing_arn = models.CharField(max_length=255, null=True, blank=True)
    thing_id = models.CharField(max_length=255, null=True, blank=True)

    certificate_arn = models.CharField(max_length=255, null=True, blank=True)
    certificate_id = models.CharField(max_length=255, null=True, blank=True)
    certificate_pem = models.TextField(null=True, blank=True)
    certificate_keypair_public = models.TextField(null=True, blank=True)
    certificate_keypair_private = models.TextField(null=True, blank=True)

    policy_name = models.CharField(max_length=255, null=True, blank=True)
    policy_arn = models.CharField(max_length=255, null=True, blank=True)
    policy_document = models.TextField(null=True, blank=True)
    policy_version_id = models.CharField(max_length=255, null=True, blank=True)

    arn = models.CharField(max_length=255, null=True, blank=True)
    core_id = models.CharField(max_length=255, null=True, blank=True)
    latest_version = models.CharField(max_length=255, null=True, blank=True)
    latest_version_arn = models.CharField(max_length=255, null=True, blank=True)


class AWSGreengrassCoreSetupToken(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    aws_greengrass_core = models.ForeignKey(AWSGreengrassCore, related_name='setup_tokens', on_delete=models.CASCADE)
    identifier = models.UUIDField()
    date_last_downloaded = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)


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
    timezone = TimeZoneField(null=True)
    action = models.CharField(max_length=10, null=True, choices=(('On', 'On'), ('Off', 'Off')))
    job_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '{} - {}:{} ({}) - {}'.format(self.relay, self.hour, self.minute, self.timezone, self.action)


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
