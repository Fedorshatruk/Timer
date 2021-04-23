import json

from rest_framework.views import APIView
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Session, CeleryTask
from timer.celery import start_timer

TURN_TIME = ((30, 15), (25, 10), (15, 10), (15, 5))


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

    def post(self, request):
        session_id = request.data.get('session_pk')
        turn_phase = 'negotiation'
        session_turn = 1
        turn_count = request.data.get('turn_count')
        try:
            session = Session.objects.create(session_id=session_id, session_phase=turn_phase,
                                   session_turn=session_turn, turn_count=turn_count)
            session.save()
            task_id = start_timer.delay(TURN_TIME[0][0], session_id)
            task = CeleryTask.objects.create(task_id=task_id, session_id=session_id)
            task.save()
        except:
            print('Что то пошло не так')
        return Response(json.dumps({"session_id": session_id}))


class SessionPlayerChange(APIView):
    def get(self, request, pk):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'session_{pk}',
                                                {"type": "change_player"})
        return Response('OK')


class NextStep(APIView):
    def post(self, request):
        session_id = request.data.get('session_pk')
        session = Session.objects.get(session_id=session_id)
        turn_phase = session.session_phase
        session_turn = session.session_turn if session.session_turn <= 4 else 4
        turn_count = session.turn_count
        step = 0 if turn_phase == 'negotiation' else 1
        if session_turn <= turn_count:
            task_id = start_timer.delay(TURN_TIME[session_turn - 1][step], session_id)
            task = CeleryTask.objects.create_or_update(task_id=task_id, session_id=session_id)
            task.save()
            return Response('Ok')
        else:
            return Response('Ne Ok')


class KillTask(APIView):
    pass

