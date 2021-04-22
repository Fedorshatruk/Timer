from rest_framework.views import APIView
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ChangeFromAll(APIView):
    def get(self, request, format=None):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"all",
                                                {"type": "join_player"})
        return Response('OK')


class StartSession(APIView):
    def get(self, request, format=None):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"all",
                                                {"type": "start_game"})
        return Response('OK')


class SessionPlayerChange(APIView):
    def get(self, request, pk):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'session_{pk}',
                                                {"type": "change_player"})
        return Response('OK')
