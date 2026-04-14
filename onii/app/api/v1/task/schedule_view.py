#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django_q.models import Schedule
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from utils.drf_util import SuccessResponse
from utils.page_util import MyPageNumberPagination


class ScheduleSerializer(serializers.ModelSerializer):
    schedule_type_display = serializers.CharField(
        source='get_schedule_type_display', read_only=True
    )

    class Meta:
        model = Schedule
        fields = [
            'id', 'name', 'func', 'hook', 'args', 'kwargs',
            'schedule_type', 'schedule_type_display',
            'minutes', 'cron',
            'repeats', 'next_run', 'task',
        ]
        read_only_fields = ['id', 'task', 'next_run']


@extend_schema_view(
    list=extend_schema(summary='定时任务列表', tags=['定时任务']),
    create=extend_schema(summary='创建定时任务', tags=['定时任务']),
    retrieve=extend_schema(summary='定时任务详情', tags=['定时任务']),
    update=extend_schema(summary='更新定时任务', tags=['定时任务']),
    destroy=extend_schema(summary='删除定时任务', tags=['定时任务']),
)
class ScheduleManageView(ModelViewSet):
    """定时任务管理 (Django-Q Schedule)"""

    queryset = Schedule.objects.all().order_by('-id')
    serializer_class = ScheduleSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permissions(self):
        if self.action in ('list', 'retrieve'):
            return ['task:view']
        return ['task:edit']

    @property
    def required_permissions(self):
        return self.get_required_permissions()
