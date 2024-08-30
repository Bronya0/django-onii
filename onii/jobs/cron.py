#!/usr/bin/env python
# -*- coding: utf-8 -*-

import django
import os
import sys
from pathlib import Path

_APP_PATH = Path(__file__).resolve().parent.parent
sys.path.append(str(_APP_PATH))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onii.settings")
django.setup()

from django_q.models import Schedule
from django_q.tasks import schedule


def job1():
    # 每次启动时要重新注册更合适
    task_name = 'print_demo'
    Schedule.objects.filter(name=task_name).delete()
    schedule(
        func='apps.async_task.tasks.demo.demo_task',
        schedule_type=Schedule.MINUTES,
        minutes=1,
        name=task_name,
    )
    print("注册定时任务", task_name)


def start_cron():
    """
    在此处注册多个定时任务
    :return:
    """
    job1()

    print("定时任务全部注册完成")


if __name__ == '__main__':
    start_cron()
