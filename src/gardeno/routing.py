from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter

from grows.consumers import GrowConsumer, SensorConsumer

from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from api.auth import lookup_auth_token


class QueryAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        user = AnonymousUser()
        sensor = None
        parsed_url = parse_qs(scope["query_string"])
        if b'auth_token' in parsed_url and parsed_url[b'auth_token']:
            error, looked_up_user, looked_up_sensor = lookup_auth_token(parsed_url[b'auth_token'][0].decode("utf-8"))
            if not error:
                user = looked_up_user
                sensor = looked_up_sensor
            close_old_connections()
        return self.inner(dict(scope, user=user, sensor=sensor))


application = ProtocolTypeRouter({
    "websocket": QueryAuthMiddleware(
        URLRouter([
            path("ws/grows/<grow_id>/", GrowConsumer),
            path("ws/grows/<grow_id>/sensors/<sensor_id>/", SensorConsumer),
        ]),
    ),
})
