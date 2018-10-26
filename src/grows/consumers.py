from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class GrowConsumer(WebsocketConsumer):
    def connect(self, **kwargs):
        self.group_name = 'grow-{}'.format(self.scope['url_route']['kwargs']['grow_id'])
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()
        else:
            print('Unable to authenticate user.')

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print('Received message...: {}'.format(text_data))

    def sensor_update(self, event):
        self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data']
        }))


class SensorConsumer(WebsocketConsumer):
    def connect(self, **kwargs):
        self.group_name = 'grow-{}-sensor-{}'.format(self.scope['url_route']['kwargs']['grow_id'],
                                                     self.scope['url_route']['kwargs']['sensor_id'])
        self.user = self.scope["user"]
        self.sensor = self.scope["sensor"]
        if (self.user and self.user.is_authenticated) or self.sensor:
            if self.user:
                print('Connected as user!')
            else:
                print('Connected as sensor!')
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        if self.sensor:
            try:
                message = json.loads(text_data)
            except Exception as err:
                print('Unable to handle message {}: {}'.format(text_data, err))
                return
            if message['id'] == 'ping':
                self.send(text_data=json.dumps({
                    'id': 'pong',
                }))
                return
            print('Received message from sensor {}...: {}'.format(self.sensor.name, text_data))

    def relay_update(self, event):
        if self.sensor and event['data']['sensor_identifier'] == str(self.sensor.identifier):
            self.send(text_data=json.dumps({
                'id': 'turn_on_relay' if event['data']['action_type'] == 'on' else 'turn_off_relay',
                'data': {
                    'pin': event['data']['pin'],
                }
            }))
        else:
            print('throwing away...')
