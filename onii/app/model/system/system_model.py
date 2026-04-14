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
        ordering = ['dict_type', 'sort', 'id']
        unique_together = [('dict_type', 'value')]

    def __str__(self):
        return f"{self.label}: {self.value}"
