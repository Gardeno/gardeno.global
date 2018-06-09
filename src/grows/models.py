from django.db import models
from django.contrib.gis.db import models
from gardeno.models import BaseModel


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
    location = models.PointField(null=True)

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
