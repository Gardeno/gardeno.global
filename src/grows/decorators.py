from .models import Grow, Sensor
from django.http import HttpResponseRedirect, Http404


def lookup_grow(function):
    def wrap(request, *args, **kwargs):
        grow_id = kwargs.pop('grow_id')
        try:
            grow = Grow.objects.get(identifier=grow_id)
        except Exception as exception:
            raise Http404
        request.grow = grow
        if not request.grow.is_owned_by_user(request.user) and (
                    not grow.date_published or grow.visibility == 'Private'):
            raise Http404
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def must_own_grow(function):
    def wrap(request, *args, **kwargs):
        if not request.grow.is_owned_by_user(request.user):
            return HttpResponseRedirect('/grows/{}'.format(request.grow.identifier))
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def lookup_sensor(function):
    def wrap(request, *args, **kwargs):
        sensor_id = kwargs.pop('sensor_id')
        try:
            sensor = Sensor.objects.get(grow=request.grow, identifier=sensor_id)
        except Exception as exception:
            raise Http404
        request.sensor = sensor
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
