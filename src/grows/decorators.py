from .models import Grow
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
