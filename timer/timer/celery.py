from __future__ import absolute_import, unicode_literals
import os
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from celery import Celery
from django.apps import apps
from django.conf import settings

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
    t = time.time()
    end_time = t + second
    last_time = round(end_time - t) + 1
    while end_time > time.time():
        last_time -= 1
        send_sok_change_session_id(last_time, session_id)
        time.sleep(1.0)

    return True


@app.task(bind=True)
def start_timer(self, second, session_id):
    my_timer(second, session_id)


# from timer.celery import start_timer
# start_timer.delay(1234, 3)


