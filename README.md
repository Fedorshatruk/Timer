# Timer
для запуска сервера: python manage.py runserver
для запуска celery: celery -A timer worker --loglevel=INFO
для запуска таймера использую в шел вследующие команды:
from timer.celery import start_timer
start_timer.delay(1234, 3) -> время в секундах, id сессии
