#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
独立 APScheduler 进程 — 不随 Django 启动，避免多进程冲突。

用法:
    python jobs/scheduler.py                   # 生产 (settings.py)
    DJANGO_SETTINGS_MODULE=onii.settings_dev python jobs/scheduler.py  # 开发
"""

import importlib
import logging
import os
import signal
import sys
from pathlib import Path

# ── Django 环境初始化 ──
_APP_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_APP_PATH))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onii.settings")

import django
django.setup()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.model.system.system_model import CronSchedule
from jobs.cron import register_code_jobs

logger = logging.getLogger('app')

_SYNC_INTERVAL = 30  # 每 N 秒同步一次数据库任务


def _resolve_func(dotted_path: str):
    """通过点分路径导入函数，支持 module.path:func 和 module.path.func 两种写法"""
    if ':' in dotted_path:
        module_path, func_name = dotted_path.rsplit(':', 1)
    else:
        module_path, func_name = dotted_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def _build_trigger(job: CronSchedule):
    if job.schedule_type == 'cron':
        return CronTrigger.from_crontab(job.cron_expression)
    return IntervalTrigger(seconds=job.interval_seconds)


def sync_db_jobs(scheduler: BlockingScheduler):
    """从数据库同步定时任务到 scheduler"""
    try:
        db_jobs = CronSchedule.objects.filter(enabled=True)
    except Exception as e:
        logger.warning("同步数据库任务失败: %s", e)
        return

    db_job_ids = set()
    for job_config in db_jobs:
        job_id = f"db_{job_config.id}"
        db_job_ids.add(job_id)

        try:
            func = _resolve_func(job_config.func)
            trigger = _build_trigger(job_config)
        except Exception as e:
            logger.warning("任务 %s 配置错误: %s", job_config.name, e)
            continue

        existing = scheduler.get_job(job_id)
        if existing:
            existing.reschedule(trigger)
        else:
            scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                name=job_config.name,
                args=job_config.args or [],
                kwargs=job_config.kwargs or {},
                replace_existing=True,
            )

    # 移除数据库中已删除 / 禁用的任务
    for job in scheduler.get_jobs():
        if job.id.startswith('db_') and job.id not in db_job_ids:
            job.remove()


def main():
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')

    # 注册代码定义的任务
    register_code_jobs(scheduler)

    # 注册数据库同步任务
    scheduler.add_job(
        sync_db_jobs,
        trigger=IntervalTrigger(seconds=_SYNC_INTERVAL),
        id='_sync_db_jobs',
        name='同步数据库任务配置',
        args=[scheduler],
        replace_existing=True,
    )

    # 初始同步
    sync_db_jobs(scheduler)

    # 优雅关闭
    def _shutdown(signum, frame):
        print("\n==== 收到信号, 正在关闭调度器 ====")
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    print("==== APScheduler 已启动 ====")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
