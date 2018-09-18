from django.http import JsonResponse
from .decorators import api_decorator, required_fields, authentication_required
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
from grows.models import SensorRelay
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@api_decorator(allowed_methods=['POST'])
@required_fields(['email', 'password'])
def accounts_sign_in(request):
    try:
        user = User.objects.get(email=request.json_body['email'])
    except ObjectDoesNotExist:
        user = None
    if not user or not user.check_password(request.json_body['password']):
        return JsonResponse({"error": "Unable to login, check email/password"}, status=400)
    return JsonResponse({"data": {
        "token": user.generate_auth_token(),
    }})


@api_decorator(allowed_methods=['POST'])
@required_fields(['email', 'firstName', 'lastName', 'password'])
def accounts_sign_up(request):
    error, user = User.objects.create_user_with_info(email=request.json_body['email'],
                                                     first_name=request.json_body['firstName'],
                                                     last_name=request.json_body['lastName'],
                                                     password=request.json_body['password'])
    if error:
        return JsonResponse({"error": error}, status=400)
    return JsonResponse({"data": {
        "token": user.generate_auth_token(),
    }})


@api_decorator(allowed_methods=['GET'])
@authentication_required()
def accounts_me(request):
    return JsonResponse({"data": {
        "email": request.user.email,
        "invitations": [],
        "grows": [x.to_json() for x in request.user.grows()],
        "team_memberships": [x.to_json() for x in request.user.team_memberships()],
    }})


@api_decorator(allowed_methods=['GET'])
@authentication_required()
def accounts_my_grows(request):
    return JsonResponse({"data": [x.to_json() for x in request.user.grows()]})


def _sensor_relay_update(relay, action_type):
    message = {
        'type': 'relay_update',
        'data': {
            'sensor_identifier': str(relay.sensor.identifier),
            'pin': relay.pin,
            'action_type': action_type
        }
    }
    '''
    SensorUpdate.objects.create(
        sensor=sensor,
        update=json.dumps(message),
    )
    '''
    layer = get_channel_layer()
    async_to_sync(layer.group_send)('grow-{}-sensor-{}'.format(relay.sensor.grow.identifier, relay.sensor.identifier),
                                    message)


@api_decorator(allowed_methods=['POST'])
@authentication_required()
def grow_sensor_relay_action(request, grow_id=None, sensor_id=None, relay_id=None, action_type=None):
    try:
        sensor_relay = SensorRelay.objects.get(identifier=relay_id,
                                               sensor__identifier=sensor_id,
                                               sensor__grow__identifier=grow_id)
    except:
        return JsonResponse({"error": "Not found"}, status=404)
    if action_type not in ['on', 'off']:
        return JsonResponse({"error": "Expected action type of `on` or `off`"}, status=400)
    _sensor_relay_update(sensor_relay, action_type)
    return JsonResponse({})
