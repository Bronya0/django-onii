#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
危险操作二次确认

用法:
    from utils.confirm_password import RequirePasswordConfirmation

    class UserManageView(ModelViewSet):
        # 删除操作需要密码确认
        def get_permissions(self):
            if self.action == 'destroy':
                return [IsAuthenticated(), RequirePasswordConfirmation()]
            return [IsAuthenticated()]

前端需在请求头中携带:
    X-Confirm-Password: <当前用户密码>
"""

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class RequirePasswordConfirmation(BasePermission):
    """要求请求头 X-Confirm-Password 携带当前用户密码"""

    message = '此操作需要密码确认，请在请求头中携带 X-Confirm-Password'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        confirm_password = request.META.get('HTTP_X_CONFIRM_PASSWORD', '')
        if not confirm_password:
            raise PermissionDenied(self.message)

        if not request.user.check_password(confirm_password):
            raise PermissionDenied('确认密码错误')

        return True
