#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import django.db.transaction
from django_q.models import Task
from django_q.tasks import async_task

from apps.async_task.models.async_task_model import DjangoQProcess


class AsyncTaskService:

    def __init__(self):
        pass

    def create_async_task(self, func, *args, **kwargs):
        """
        执行任务前，先写进度表
        不能后写，也不能用task_id
        """
        task_name = kwargs['task_name']

        with django.db.transaction.atomic():
            if DjangoQProcess.objects.filter(task_name=task_name).exists():
                raise Exception("异步任务名 {} 已经存在！必须传递唯一的任务名".format(task_name))

            task_id = async_task(
                func, *args, **kwargs
            )

            DjangoQProcess.objects.create(
                task_name=kwargs.get('task_name'),
                task_id=task_id,
                func=func.__name__,
                args=args,
                kwargs=kwargs,
                hook=kwargs.get('hook').__name__ if kwargs.get('hook') else None,
                group=kwargs.get('group'),
                started=datetime.datetime.now(),
                process=0.0,
            )

        return task_id

    def update_task_process(self, task_name, process):
        DjangoQProcess.objects.filter(task_name=task_name).update(process=process)

    @staticmethod
    def calculate_percentage(numerator, denominator):
        if denominator == 0:  # 处理分母为0的情况
            return "0.00%"
        result = (numerator / denominator) * 100
        return "{:.2f}%".format(result)

    def get_result_by_names(self, names: list):
        """
        根据task name直接批量查任务进度和结果
        :param names:
        :return:
        """
        processes = DjangoQProcess.objects.filter(task_name__in=names)
        tasks = Task.objects.filter(name__in=names)
        task_map = {task.name: task for task in tasks}
        res = {}
        for i in processes:
            i: DjangoQProcess
            task_obj: Task = task_map.get(i.task_name)
            res[i.task_name] = {
                "id": i.id,
                "task_id": i.task_id,
                "name": i.task_name,
                "result": task_obj.result if task_obj else None,  # 结果
                "group": i.group,
                "started": i.started.strftime('%Y-%m-%d %H:%M:%S'),
                "stopped": task_obj.stopped.strftime('%Y-%m-%d %H:%M:%S') if task_obj else None,
                "success": task_obj.success if task_obj else None,
                "process": i.process,
                "process_label": self.calculate_percentage(i.process, 1) if i.process is not None else "0%"
            }
        return res
