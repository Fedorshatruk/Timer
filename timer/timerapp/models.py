from __future__ import absolute_import, unicode_literals
from django.db import models


class CeleryTask(models.Model):
    task_id = models.CharField(max_length=255, verbose_name="Айдишник задачи")
    session_id = models.IntegerField(verbose_name="Айдишник сессии")


class Session(models.Model):
    session_id = models.IntegerField(verbose_name="Айдишник сессии")
    session_turn = models.IntegerField(verbose_name='Номер хода')
    session_phase = models.CharField(max_length=125, verbose_name="Статус хода")
    turn_count = models.IntegerField(verbose_name='Количество ходов')
