from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class SensorConsumer(WebsocketConsumer):
    def connect(self, **kwargs):
        self.group_name = 'grow-{}'.format(self.scope['url_route']['kwargs']['grow_id'])
        # self.channel_name = 'sensors'
        print('group name: {}'.format(self.group_name))
        print('channel name: {}'.format(self.channel_name))
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

    def sensor_core_update(self, event):
        self.send(text_data=json.dumps({
            'type': 'sensor_core_update',
            'update': event['update']
        }))
