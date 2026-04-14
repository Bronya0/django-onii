#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 签名 + 防重放中间件 (可选)

YAML 配置:
    security:
      api_sign_enabled: false
      api_sign_secret: 'your-hmac-secret-key'

客户端需在请求头中携带:
    X-Timestamp : 当前 Unix 时间戳 (秒)
    X-Nonce     : 每次请求唯一的随机字符串 (≤64 字符)
    X-Signature : HMAC-SHA256(secret, METHOD + \n + PATH + \n + TIMESTAMP + \n + NONCE)

验证逻辑:
    1. 时间戳偏差 ≤ 300 秒 (5 分钟)
    2. Nonce 在窗口内未使用过 (防重放)
    3. 签名匹配
"""

import hashlib
import hmac
import logging
import time

from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger('app')

TIMESTAMP_TOLERANCE = 300  # 秒
NONCE_CACHE_PREFIX = 'api_nonce:'
NONCE_CACHE_TIMEOUT = TIMESTAMP_TOLERANCE * 2  # nonce 缓存时长

# 不验证签名的路径前缀
EXEMPT_PATHS = ['/admin/', '/api/health', '/api/auth/login']


class ApiSignMiddleware:
    """API 签名验证中间件 (默认关闭，YAML security.api_sign_enabled=true 开启)"""

    def __init__(self, get_response):
        self.get_response = get_response
        self._load_config()

    def _load_config(self):
        from django.conf import settings
        security = getattr(settings, 'YAML_CONF', {}).get('security', {})
        self.enabled = security.get('api_sign_enabled', False)
        self.secret = security.get('api_sign_secret', '')

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        # 豁免路径
        if any(request.path.startswith(p) for p in EXEMPT_PATHS):
            return self.get_response(request)

        # 仅验证写操作 (GET 不要求签名可降低前端接入成本)
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return self.get_response(request)

        timestamp = request.META.get('HTTP_X_TIMESTAMP', '')
        nonce = request.META.get('HTTP_X_NONCE', '')
        signature = request.META.get('HTTP_X_SIGNATURE', '')

        if not all([timestamp, nonce, signature]):
            return JsonResponse(
                {'code': 4010, 'msg': '缺少签名参数 (X-Timestamp / X-Nonce / X-Signature)', 'data': None},
                status=401,
            )

        # 1. 时间戳校验
        try:
            ts = int(timestamp)
        except ValueError:
            return JsonResponse({'code': 4010, 'msg': '时间戳格式错误', 'data': None}, status=401)

        if abs(time.time() - ts) > TIMESTAMP_TOLERANCE:
            return JsonResponse({'code': 4010, 'msg': '请求已过期', 'data': None}, status=401)

        # 2. Nonce 防重放
        if len(nonce) > 64:
            return JsonResponse({'code': 4010, 'msg': 'Nonce 长度不合法', 'data': None}, status=401)

        nonce_key = f'{NONCE_CACHE_PREFIX}{nonce}'
        if cache.get(nonce_key):
            return JsonResponse({'code': 4010, 'msg': '重复请求', 'data': None}, status=401)
        cache.set(nonce_key, 1, NONCE_CACHE_TIMEOUT)

        # 3. 签名校验
        sign_string = f'{request.method}\n{request.path}\n{timestamp}\n{nonce}'
        expected = hmac.HMAC(
            self.secret.encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            return JsonResponse({'code': 4010, 'msg': '签名验证失败', 'data': None}, status=401)

        return self.get_response(request)
