#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
在此注册代码写死的定时任务（不通过数据库管理）。
scheduler.py 启动时会调用 register_code_jobs()。
"""

from apscheduler.triggers.interval import IntervalTrigger


def register_code_jobs(scheduler):
    """注册代码定义的定时任务"""

    scheduler.add_job(
        'jobs.tasks.demo:demo_task',
        trigger=IntervalTrigger(minutes=1),
        id='code_print_demo',
        name='print_demo',
        replace_existing=True,
    )
    print("代码定时任务注册完成")
