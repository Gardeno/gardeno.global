from django.db import models
from django.contrib.gis.db import models
from gardeno.models import BaseModel
from accounts.models import User
from django.conf import settings
import logging
import json
from .greengrass_policy import GREENGRASS_POLICY

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

    # AWS Greengrass configuration

    greengrass_group_arn = models.CharField(max_length=255, null=True, blank=True)
    greengrass_group_id = models.CharField(max_length=255, null=True, blank=True)

    greengrass_core_thing_name = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_thing_arn = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_thing_id = models.CharField(max_length=255, null=True, blank=True)

    greengrass_core_certificate_arn = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_certificate_id = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_certificate_pem = models.TextField(null=True, blank=True)
    greengrass_core_certificate_keypair_public = models.TextField(null=True, blank=True)
    greengrass_core_certificate_keypair_private = models.TextField(null=True, blank=True)

    greengrass_core_policy_name = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_policy_arn = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_policy_document = models.TextField(null=True, blank=True)
    greengrass_core_policy_version_id = models.CharField(max_length=255, null=True, blank=True)

    greengrass_core_arn = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_id = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_latest_version = models.CharField(max_length=255, null=True, blank=True)
    greengrass_core_latest_version_arn = models.CharField(max_length=255, null=True, blank=True)

    def create_greengrass_group(self):
        try:
            greengrass_group_response = settings.GREENGRASS_CLIENT.create_group(Name='{}'.format(self.identifier))
            self.greengrass_group_arn = greengrass_group_response['Arn']
            self.greengrass_group_id = greengrass_group_response['Id']
            self.save()
            return True
        except Exception as exception:
            logging.error(exception)
            return False

    def create_greengrass_core(self):
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
                self.greengrass_core_thing_name = greengrass_core_thing_response['thingName']
                self.greengrass_core_thing_arn = greengrass_core_thing_response['thingArn']
                self.greengrass_core_thing_id = greengrass_core_thing_response['thingId']
            except Exception as exception:
                logging.error('Unable to create the Thing')
                logging.error(exception)
                return False
            try:
                # See if the policy already exists
                existing_policy = settings.IOT_CLIENT.get_policy(
                    policyName=core_name
                )
                self.greengrass_core_policy_name = existing_policy['policyName']
                self.greengrass_core_policy_arn = existing_policy['policyArn']
                self.greengrass_core_policy_document = existing_policy['policyDocument']
                self.greengrass_core_policy_version_id = existing_policy['defaultVersionId']
            except:
                try:
                    # We then create a policy since one does not exist
                    greengrass_core_policy_response = settings.IOT_CLIENT.create_policy(
                        policyName=core_name,
                        policyDocument=json.dumps(GREENGRASS_POLICY)
                    )
                    self.greengrass_core_policy_name = greengrass_core_policy_response['policyName']
                    self.greengrass_core_policy_arn = greengrass_core_policy_response['policyArn']
                    self.greengrass_core_policy_document = greengrass_core_policy_response['policyDocument']
                    self.greengrass_core_policy_version_id = greengrass_core_policy_response['policyVersionId']
                except Exception as exception:
                    logging.error('Unable to create the policy')
                    logging.error(exception)
                    return False
            try:
                # We then create a certificate
                greengrass_core_thing_certificate_response = settings.IOT_CLIENT.create_keys_and_certificate(
                    setAsActive=True
                )
                self.greengrass_core_certificate_arn = greengrass_core_thing_certificate_response['certificateArn']
                self.greengrass_core_certificate_id = greengrass_core_thing_certificate_response['certificateId']
                self.greengrass_core_certificate_pem = greengrass_core_thing_certificate_response['certificatePem']
                self.greengrass_core_certificate_keypair_public = greengrass_core_thing_certificate_response['keyPair'][
                    'PublicKey']
                self.greengrass_core_certificate_keypair_private = \
                    greengrass_core_thing_certificate_response['keyPair']['PrivateKey']
            except Exception as exception:
                logging.error('Unable to create the certificate')
                logging.error(exception)
                return False
            try:
                # We then attach the certificate to the policy
                settings.IOT_CLIENT.attach_policy(policyName=self.greengrass_core_policy_name,
                                                  target=self.greengrass_core_certificate_arn)
            except Exception as exception:
                logging.error('Unable to attach the certificate to the policy')
                logging.error(exception)
                return False
            try:
                # We then attach the thing to the certificate
                settings.IOT_CLIENT.attach_thing_principal(thingName=self.greengrass_core_thing_name,
                                                           principal=self.greengrass_core_certificate_arn)
            except Exception as exception:
                logging.error('Unable to attach the Thing to the certificate')
                logging.error(exception)
                return False
            try:
                response = settings.GREENGRASS_CLIENT.create_core_definition(
                    InitialVersion={
                        'Cores': [
                            {
                                'CertificateArn': self.greengrass_core_certificate_arn,
                                'Id': '{}'.format(self.identifier),
                                'SyncShadow': True,
                                'ThingArn': self.greengrass_core_thing_arn
                            },
                        ]
                    },
                    Name=core_name,
                )
                self.greengrass_core_arn = response['Arn']
                self.greengrass_core_id = response['Id']
                self.greengrass_core_latest_version = response['LatestVersion']
                self.greengrass_core_latest_version_arn = response['LatestVersionArn']
            except Exception as exception:
                logging.error('Unable to create the core definition')
                logging.error(exception)
                return False
            try:
                settings.GREENGRASS_CLIENT.create_group_version(
                    GroupId=self.greengrass_group_id,
                    CoreDefinitionVersionArn=self.greengrass_core_latest_version_arn,
                )
            except Exception as exception:
                logging.error('Unable to create the core definition')
                logging.error(exception)
                return False
            self.save()
            return True
        except Exception as exception:
            logging.error('Unable to create the core')
            logging.error(exception)
            return False

    @property
    def has_created_greengrass_group(self):
        return self.greengrass_group_arn and self.greengrass_group_id

    @property
    def has_created_greengrass_core(self):
        # May return differently if we've created the thing or certificate but not the full core, so stubbed out
        # the conditionals appropriately.
        if not self.greengrass_core_thing_name or not self.greengrass_core_thing_arn or not self.greengrass_core_thing_id:
            return False
        if not self.greengrass_core_certificate_arn or not self.greengrass_core_certificate_id or not self.greengrass_core_certificate_pem or not self.greengrass_core_certificate_keypair_public or not self.greengrass_core_certificate_keypair_private:
            return False
        if not self.greengrass_core_policy_name or not self.greengrass_core_policy_arn or not self.greengrass_core_policy_document or not self.greengrass_core_policy_version_id:
            return False
        if not self.greengrass_core_arn or not self.greengrass_core_id or not self.greengrass_core_latest_version or not self.greengrass_core_latest_version_arn:
            return False
        return True

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
    type = models.CharField(max_length=50, choices=[(x, x) for x in SENSOR_TYPE_VALUES])
    # AWS specific values
    aws_thing_name = models.CharField(max_length=255, null=True, blank=True)
    aws_thing_arn = models.CharField(max_length=255, null=True, blank=True)
    aws_thing_id = models.CharField(max_length=255, null=True, blank=True)
