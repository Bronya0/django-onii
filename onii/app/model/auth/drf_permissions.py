#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """要求用户已登录"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class HasRole(BasePermission):
    """检查用户是否拥有指定角色（在 view 上设置 required_roles）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True
        return request.user.has_any_role(*required_roles)


class HasPermission(BasePermission):
    """检查用户是否拥有指定权限（在 view 上设置 required_permissions）"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        required_perms = getattr(view, 'required_permissions', [])
        if not required_perms:
            return True
        # 收集用户所有角色的权限
        user_perms = set()
        for role in request.user.roles.all():
            user_perms.update(role.permissions or [])
        return all(p in user_perms for p in required_perms)
