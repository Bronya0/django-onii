#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import django_filters
from django_q.models import Task

from apps.async_task.models.async_task_model import DjangoQProcess


class AsyncTaskFilter(django_filters.FilterSet):

    start_time__gte = django_filters.CharFilter(method='filter_start_time_gte')
    start_time__lte = django_filters.CharFilter(method='filter_start_time_lte')
    success = django_filters.CharFilter(method='filter_success')
    name__icontains = django_filters.CharFilter(method='filter_name__icontains')

    class Meta:
        model = DjangoQProcess
        fields = {
            "group": ["exact"],
        }

    def filter_name__icontains(self, queryset, name, value):
        return queryset.filter(task_name__icontains=value)

    # 13位转10位
    def timestamp_to_datetime(self, value):
        value = str(value)
        if len(value) == 13:
            value = int(int(value) / 1000)
        try:
            new_value = datetime.datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            raise Exception("时间转换失败！请传时间戳！")
        return new_value

    # 接受前端用于时间查询的 13 位时间戳
    def filter_start_time_gte(self, queryset, name, value):
        return queryset.filter(started__gte=self.timestamp_to_datetime(value))

    def filter_start_time_lte(self, queryset, name, value):
        return queryset.filter(started__lte=self.timestamp_to_datetime(value))

    def convert_bool(self, value):
        if value.lower() in ['true']:
            res = True
        elif value.lower() in ['false']:
            res = False
        else:
            return None
        return res

    def filter_success(self, queryset, name, value):
        res = self.convert_bool(value)
        ids = Task.objects.filter(success=res).values_list('id', flat=True)
        return queryset.filter(task_id__in=ids)
