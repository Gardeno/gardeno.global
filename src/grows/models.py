from django.db import models
from django.contrib.gis.db import models
from gardeno.models import BaseModel
from accounts.models import User

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
    created_by_user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

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
