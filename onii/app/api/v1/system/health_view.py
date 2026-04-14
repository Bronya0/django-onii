#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """健康检查（无需认证）"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(summary='健康检查', tags=['系统'])
    def get(self, request):
        checks = {}
        healthy = True

        # 数据库连通性
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks['database'] = 'ok'
        except Exception as e:
            checks['database'] = f'error: {e}'
            healthy = False

        # 磁盘
        try:
            disk = psutil.disk_usage('/')
            checks['disk_percent'] = disk.percent
            checks['disk'] = 'warning' if disk.percent > 90 else 'ok'
        except Exception:
            checks['disk'] = 'unknown'

        # 内存
        try:
            mem = psutil.virtual_memory()
            checks['memory_percent'] = mem.percent
            checks['memory'] = 'warning' if mem.percent > 90 else 'ok'
        except Exception:
            checks['memory'] = 'unknown'

        status_code = 200 if healthy else 503
        return Response(
            {'status': 'healthy' if healthy else 'unhealthy', 'checks': checks},
            status=status_code,
        )
