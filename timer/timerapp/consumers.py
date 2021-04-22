from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class SessionTimerConsumer(WebsocketConsumer):
    def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to room group
        if text_data_json['type'] == 'time':
            time = text_data_json['time']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_timer',
                    'time': time
                }
            )
        elif text_data_json['type'] == 'start_game':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "start_game",
                    'start_game': True,
                    'action': 'start_game'
                }
            )
        elif text_data_json['type'] == 'change_player':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "change_player",
                }
            )


    # Receive message from room group
    def send_timer(self, event):
        time = event['time']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'time': time,
            'action': 'timer'
        }))

    def start_game(self, event):
        self.send(text_data=json.dumps({
            'start_game': 'true',
            'action': 'start_game'
        }))

    def change_player(self, event):
        self.send(text_data=json.dumps({
            'action': 'change_player'
        }))


class SessionConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'all'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to room group
        if text_data_json['type'] == 'join_player':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'join_player',
                    'time': True
                }
            )
        elif text_data_json['type'] == 'exit_player':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "exit_player",
                    'exit_player': True,
                }
            )
        elif text_data_json['type'] == 'start_game':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "start_game",
                }
            )

    def join_player(self, event):
        self.send(text_data=json.dumps({
            'action': 'join_player',
            'data': True}))

    def exit_player(self, event):
        self.send(text_data=json.dumps({
            'action': 'exit_player',
            'data': True}))

    def start_game(self, event):
        self.send(text_data=json.dumps({
            'start_game': 'true',
            'action': 'start_game'
        }))