from django.db import models
from django.contrib.gis.db import models


class Grow(models.Model):
    """
    A grow is the highest level of an individual operation.
    It may be a rooftop, a living room, a greenhouse, or other
    contained system that is comprised of individual grow components.
    """
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


class Rack(models.Model):
    """
    A rack is used for small, homegrown vertical farming systems.
    You can find a rack at Costco or other similar retailers:
        https://www.costco.com/Alera-4-Shelf-Wire-Rack-48%22-x-24%22-x-72%22-NSF.product.11316751.html
    """
    # TODO: Can we get internal GPS resolution precise enough to move racks around and understand where they are?
    # Should we use some sort of internal GPS standard?
    grow = models.ForeignKey(Grow, null=True, blank=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.grow.title if self.grow else 'No Grow')
