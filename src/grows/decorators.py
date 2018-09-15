from .models import Grow, Sensor, SensorSetupToken
from django.http import HttpResponseRedirect, Http404, JsonResponse


def lookup_grow(function):
    def wrap(request, *args, **kwargs):
        grow_id = kwargs.pop('grow_id')
        try:
            grow = Grow.objects.get(identifier=grow_id)
        except Exception as exception:
            raise Http404
        request.grow = grow
        if request.grow.is_owned_by_user(request.user):
            # If we've never created the Greengrass group (likely an error)
            # we force a redirect. The system does not function without one.
            if not request.grow.has_created_greengrass_group:
                create_group_url = '/grows/{}/group/'.format(request.grow.identifier)
                if request.get_full_path() != create_group_url:
                    return HttpResponseRedirect(create_group_url)
        elif not grow.date_published or grow.visibility == 'Private':
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


def must_have_created_core(function):
    def wrap(request, *args, **kwargs):
        if not request.grow.has_created_greengrass_core:
            return HttpResponseRedirect("/grows/{}/sensors/".format(request.grow.identifier))
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def grow_sensor_setup_token_is_valid(function):
    def wrap(request, *args, **kwargs):
        grow_id = kwargs.pop('grow_id')
        sensor_id = kwargs.pop('sensor_id')
        setup_id = kwargs.pop('setup_id')
        try:
            setup_token = SensorSetupToken.objects.get(identifier=setup_id,
                                                       sensor__identifier=sensor_id,
                                                       sensor__grow__identifier=grow_id)
        except Exception as err:
            print(err)
            raise Http404
        request.setup_token = setup_token
        request.sensor = setup_token.sensor
        request.grow = setup_token.sensor.grow
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
