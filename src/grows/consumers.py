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
        if self.user.is_authenticated:
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
        print('Received message...: {}'.format(text_data))

    ''''
    def sensor_update(self, event):
        self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'data': event['data']
        }))
    '''



