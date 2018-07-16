from grows.models import VISIBILITY_OPTION_VALUES


def analytics(request):
    return {
        'google_analytics_id': 'UA-119548677-1'
    }


def globals(request):
    return {
        'grow_visibility_options': VISIBILITY_OPTION_VALUES,
    }
