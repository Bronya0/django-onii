#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class DjangoQProcess(models.Model):
    task_name = models.CharField(max_length=100, null=False, blank=False, verbose_name="任务名，唯一，会校验")
    task_id = models.CharField(max_length=32, verbose_name="django-q的任务id")
    func = models.CharField(max_length=256, verbose_name="函数名")
    args = models.TextField(null=True, verbose_name="参数")
    kwargs = models.TextField(null=True, verbose_name="参数")
    hook = models.CharField(max_length=256, null=True)
    group = models.CharField(max_length=100, null=True, verbose_name="任务组")
    started = models.DateTimeField(verbose_name="任务开始时间")
    process = models.DecimalField(max_digits=5, decimal_places=4, verbose_name="任务进度，需要调用下面的api手动更新，范围0.0-1.0")

    class Meta:
        managed = False
        db_table = 'django_q_process'

