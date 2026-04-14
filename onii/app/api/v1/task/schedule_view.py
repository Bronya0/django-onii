#!/usr/bin/env python
# -*- coding: utf-8 -*-

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from app.model.system.system_model import CronSchedule
from utils.page_util import MyPageNumberPagination


class CronScheduleSerializer(serializers.ModelSerializer):
    schedule_type_display = serializers.CharField(
        source='get_schedule_type_display', read_only=True
    )

    class Meta:
        model = CronSchedule
        fields = [
            'id', 'name', 'func', 'args', 'kwargs',
            'schedule_type', 'schedule_type_display',
            'interval_seconds', 'cron_expression',
            'enabled', 'description', 'last_run',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'last_run', 'created_at', 'updated_at']


@extend_schema_view(
    list=extend_schema(summary='定时任务列表', tags=['定时任务']),
    create=extend_schema(summary='创建定时任务', tags=['定时任务']),
    retrieve=extend_schema(summary='定时任务详情', tags=['定时任务']),
    update=extend_schema(summary='更新定时任务', tags=['定时任务']),
    destroy=extend_schema(summary='删除定时任务', tags=['定时任务']),
)
class ScheduleManageView(ModelViewSet):
    """定时任务管理 (APScheduler)"""

    queryset = CronSchedule.objects.all().order_by('-id')
    serializer_class = CronScheduleSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permissions(self):
        if self.action in ('list', 'retrieve'):
            return ['task:view']
        return ['task:edit']

    @property
    def required_permissions(self):
        return self.get_required_permissions()
