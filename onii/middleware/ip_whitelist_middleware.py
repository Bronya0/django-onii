#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django.http import JsonResponse

logger = logging.getLogger('app')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class IPWhitelistMiddleware:
    """
    IP 白名单中间件

    在 YAML 配置中设置：
    security:
      ip_whitelist_enabled: true
      ip_whitelist:
        - 127.0.0.1
        - 192.168.1.0/24
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._load_config()

    def _load_config(self):
        from django.conf import settings
        security = getattr(settings, 'YAML_CONF', {}).get('security', {})
        self.enabled = security.get('ip_whitelist_enabled', False)
        self.whitelist = security.get('ip_whitelist', [])

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        client_ip = get_client_ip(request)

        if not self._is_allowed(client_ip):
            logger.warning(f"IP 白名单拦截: {client_ip} -> {request.path}")
            return JsonResponse(
                {"code": 4003, "msg": "IP 不在白名单中", "data": None},
                status=403
            )

        return self.get_response(request)

    def _is_allowed(self, ip: str) -> bool:
        """检查 IP 是否在白名单中（支持 CIDR）"""
        import ipaddress
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            return False

        for entry in self.whitelist:
            try:
                if '/' in str(entry):
                    if addr in ipaddress.ip_network(entry, strict=False):
                        return True
                else:
                    if addr == ipaddress.ip_address(entry):
                        return True
            except ValueError:
                continue
        return False
