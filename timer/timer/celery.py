from __future__ import absolute_import, unicode_literals
import os
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import json

from celery import Celery
from django.apps import apps
from django.conf import settings


BASE_URL = 'http://192.168.0.100:7000/'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timer.settings')

app = Celery('timer')
app.config_from_object(settings)
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


def send_sok_change_session_id(last_time, session_id):
    channel_layer = get_channel_layer()

    minutes = f'0{last_time//60}' if last_time // 60 < 10 else f'{last_time//60}'
    second = f'0{last_time % 60}' if last_time % 60 < 10 else f'{last_time % 60}'
    async_to_sync(channel_layer.group_send)(f"session_{session_id}",
                                            {"type": "send_timer", 'time': f'{minutes}:{second}'})


def my_timer(second, session_id):
    from timerapp.models import Session
    t = time.time()
    session = Session.objects.get(session_id=session_id)
    session_turn = session.session_turn
    end_time = t + second
    last_time = round(end_time - t) + 1
    while end_time > time.time():
        last_time -= 1
        send_sok_change_session_id(last_time, session_id)
        time.sleep(1.0)

    if session.session_phase == 'transaction':
        session.session_turn = session_turn + 1
        session.session_phase = 'negotiation'
        session.save()
        requests.get(url=f'{BASE_URL}game/session-admin/{session_id}/count-session/')
    elif session.session_phase == 'negotiation':
        session.session_phase = 'transaction'
        session.save()
        requests.put(url=f'{BASE_URL}game/session-admin/{session_id}/set-turn-phase/',
                        headers={"accept": "application/json", "Content-Type": "application/json"},
                        data=json.dumps({"phase": "transaction"}))


@app.task(bind=True)
def start_timer(self, second, session_id):
    my_timer(second, session_id)


# from timer.celery import start_timer
# start_timer.delay(10, 10)

"""
requests.post('http://0.0.0.0:8000/start/',
					  headers={"accept": "application/json", "Content-Type": "application/json"},
					  data=json.dumps({"session_pk": 2, 'turn_count': 5}))
"""
