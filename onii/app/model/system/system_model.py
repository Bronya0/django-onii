#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class SystemConfig(models.Model):
    """系统配置：KV 键值对，支持在线修改"""

    key = models.CharField(max_length=128, unique=True, verbose_name="配置键")
    value = models.TextField(default='', verbose_name="配置值")
    value_type = models.CharField(
        max_length=20, default='string',
        choices=[
            ('string', '字符串'),
            ('number', '数字'),
            ('boolean', '布尔'),
            ('json', 'JSON'),
        ],
        verbose_name="值类型",
    )
    group = models.CharField(max_length=64, blank=True, default='default', verbose_name="配置分组")
    description = models.CharField(max_length=256, blank=True, default='', verbose_name="描述")
    is_public = models.BooleanField(default=False, verbose_name="是否公开(无需登录可读)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_config'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        ordering = ['group', 'key']

    def __str__(self):
        return f"{self.key} = {self.value}"


class DictType(models.Model):
    """字典类型"""

    code = models.CharField(max_length=64, unique=True, verbose_name="字典编码")
    name = models.CharField(max_length=128, verbose_name="字典名称")
    description = models.CharField(max_length=256, blank=True, default='', verbose_name="描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_dict_type'
        verbose_name = '字典类型'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"


class DictData(models.Model):
    """字典数据"""

    dict_type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, related_name='items', verbose_name="字典类型"
    )
    label = models.CharField(max_length=128, verbose_name="显示标签")
    value = models.CharField(max_length=256, verbose_name="数据值")
    sort = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    remark = models.CharField(max_length=256, blank=True, default='', verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_dict_data'
        verbose_name = '字典数据'
        verbose_name_plural = verbose_name
        ordering = ['dict_type', 'sort', 'id']
        unique_together = [('dict_type', 'value')]

    def __str__(self):
        return f"{self.label}: {self.value}"


class CronSchedule(models.Model):
    """定时任务调度配置"""

    SCHEDULE_TYPE_CHOICES = [
        ('interval', '固定间隔'),
        ('cron', 'Cron 表达式'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="任务名称")
    func = models.CharField(max_length=256, verbose_name="执行函数路径")
    args = models.JSONField(default=list, blank=True, verbose_name="位置参数")
    kwargs = models.JSONField(default=dict, blank=True, verbose_name="关键字参数")
    schedule_type = models.CharField(
        max_length=20, choices=SCHEDULE_TYPE_CHOICES, verbose_name="调度类型",
    )
    cron_expression = models.CharField(
        max_length=100, blank=True, default='', verbose_name="Cron 表达式",
        help_text="schedule_type=cron 时必填，格式: 分 时 日 月 周",
    )
    interval_seconds = models.IntegerField(
        null=True, blank=True, verbose_name="间隔秒数",
        help_text="schedule_type=interval 时必填",
    )
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    description = models.CharField(max_length=256, blank=True, default='', verbose_name="描述")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="上次执行时间")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_cron_schedule'
        verbose_name = '定时任务'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.name
