from functools import wraps
from django.http import JsonResponse
import json


def api_decorator(allowed_methods=None):
    def wrapper(view_func):
        def wrapped_view(request, *args, **kwargs):
            if allowed_methods and request.method not in allowed_methods:
                return JsonResponse({"error": 'Only {} allowed'.format(', '.join(allowed_methods))}, status=405)
            json_body = {}
            if request.method == 'POST':
                if request.body:
                    try:
                        json_body = json.loads(request.body)
                    except:
                        return JsonResponse({"error": 'Unable to parse JSON body'}, status=400)
            request.json_body = json_body
            return view_func(request, *args, **kwargs)

        wrapped_view.csrf_exempt = True
        return wraps(view_func)(wrapped_view)

    return wrapper


def required_fields(list_of_required_fields):
    def wrapper(function):
        def wrap(request, *args, **kwargs):
            for required_field in list_of_required_fields:
                if required_field not in request.json_body or not request.json_body[required_field]:
                    return JsonResponse({"error": 'Field `{}` is required'.format(required_field)}, status=400)
            return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__

        return wrap

    return wrapper
