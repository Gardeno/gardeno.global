import jwt
from django.conf import settings
from accounts.models import User
from grows.models import SensorAuthenticationToken
from datetime import datetime, timezone


def lookup_auth_token(authorization_token):
    '''
    returns {errorCode, errorMessage}, user, sensor
    '''
    try:
        payload = jwt.decode(authorization_token, settings.JWT_SECRET, algorithms=['HS256'])
    except:
        return (401, 'Authorization value is invalid'), None, None
    if 'sensor_authentication_token_id' in payload:
        try:
            sensor_authentication_token = SensorAuthenticationToken.objects.get(
                id=payload['sensor_authentication_token_id'])
        except:
            return (401, 'Sensor token is invalid'), None, None
        if sensor_authentication_token.date_deactivated:
            return (403, 'Sensor token has been deactivated'), None, None
        sensor_authentication_token.date_last_used = datetime.now(timezone.utc)
        sensor_authentication_token.save()
        return None, None, sensor_authentication_token.sensor
    else:
        try:
            user = User.objects.get(email=payload['email'])
        except:
            return (403, 'User with that email address does not exist'), None, None
        if not user.is_active:
            return (403, 'User has been deactivated'), None, None
    return None, user, None
