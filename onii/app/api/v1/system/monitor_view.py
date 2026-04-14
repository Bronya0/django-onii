#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import platform

import django
import psutil
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import GenericViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from utils.drf_util import SuccessResponse


@extend_schema_view(
    list=extend_schema(summary='系统监控信息', tags=['系统监控']),
)
class MonitorView(GenericViewSet):
    """系统监控：CPU / 内存 / 磁盘 / 网络"""

    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ['monitor:view']

    def list(self, request):
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())

        data = {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'freq_mhz': round(cpu_freq.current) if cpu_freq else None,
            },
            'memory': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent,
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
            },
            'network': {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
            },
            'system': {
                'os': platform.system(),
                'os_version': platform.version(),
                'hostname': platform.node(),
                'python_version': platform.python_version(),
                'django_version': django.get_version(),
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        }

        return SuccessResponse(data=data)
