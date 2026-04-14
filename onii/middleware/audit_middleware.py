#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging

logger = logging.getLogger('app')


def get_client_ip(request):
    """获取真实客户端 IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class AuditMiddleware:
    """审计日志中间件：记录所有写操作（POST/PUT/PATCH/DELETE）"""

    # 不记录审计日志的路径前缀
    EXCLUDE_PATHS = [
        '/static/',
        '/admin/jsi18n/',
        '/admin/autocomplete/',
        '/admin/login/',
        '/admin/logout/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # 记录 API 和 Admin 的写操作
        is_write = request.method in ('POST', 'PUT', 'PATCH', 'DELETE')
        is_target = request.path.startswith('/api/') or request.path.startswith('/admin/')
        if is_write and is_target:
            if any(request.path.startswith(p) for p in self.EXCLUDE_PATHS):
                return response

            try:
                from app.model.auth.auth_model import AuditLog
                user = request.user if request.user.is_authenticated else None
                AuditLog.objects.create(
                    user=user,
                    username=getattr(user, 'username', 'anonymous'),
                    method=request.method,
                    path=request.path,
                    query_params=request.META.get('QUERY_STRING', ''),
                    ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:512],
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )
            except Exception as e:
                logger.error(f"审计日志写入失败: {e}")

        return response
