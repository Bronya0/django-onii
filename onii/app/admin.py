#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.model.auth.auth_model import User, Role, AuditLog, LoginLog
from app.model.auth.permissions import (
    PERM_USER_LIST, PERM_USER_CREATE, PERM_USER_UPDATE, PERM_USER_DELETE, PERM_USER_RESET_PWD,
    PERM_ROLE_LIST, PERM_ROLE_CREATE, PERM_ROLE_UPDATE, PERM_ROLE_DELETE, PERM_ROLE_ASSIGN,
    PERM_AUDIT_LOG_VIEW, PERM_LOGIN_LOG_VIEW,
    PERM_CONFIG_IP_WHITELIST, PERM_CONFIG_PASSWORD_POLICY,
    PERM_CONFIG_VIEW, PERM_CONFIG_EDIT,
    PERM_DICT_VIEW, PERM_DICT_EDIT,
    PERM_MONITOR_VIEW,
    PERM_TASK_VIEW, PERM_TASK_EDIT,
)
from app.model.system.system_model import DictData, CronSchedule

# 所有可选权限列表
ALL_PERMISSIONS = [
    ('用户管理', [
        (PERM_USER_LIST, '查看用户'),
        (PERM_USER_CREATE, '创建用户'),
        (PERM_USER_UPDATE, '编辑用户'),
        (PERM_USER_DELETE, '删除用户'),
        (PERM_USER_RESET_PWD, '重置密码'),
    ]),
    ('角色管理', [
        (PERM_ROLE_LIST, '查看角色'),
        (PERM_ROLE_CREATE, '创建角色'),
        (PERM_ROLE_UPDATE, '编辑角色'),
        (PERM_ROLE_DELETE, '删除角色'),
        (PERM_ROLE_ASSIGN, '分配角色'),
    ]),
    ('审计', [
        (PERM_AUDIT_LOG_VIEW, '查看审计日志'),
        (PERM_LOGIN_LOG_VIEW, '查看登录日志'),
    ]),
    ('系统配置', [
        (PERM_CONFIG_VIEW, '查看配置'),
        (PERM_CONFIG_EDIT, '编辑配置'),
        (PERM_CONFIG_IP_WHITELIST, 'IP 白名单'),
        (PERM_CONFIG_PASSWORD_POLICY, '密码策略'),
    ]),
    ('字典', [
        (PERM_DICT_VIEW, '查看字典'),
        (PERM_DICT_EDIT, '编辑字典'),
    ]),
    ('监控', [
        (PERM_MONITOR_VIEW, '查看监控'),
    ]),
    ('定时任务', [
        (PERM_TASK_VIEW, '查看任务'),
        (PERM_TASK_EDIT, '编辑任务'),
    ]),
]


class RoleForm(forms.ModelForm):
    permissions = forms.TypedMultipleChoiceField(
        choices=[
            (group, choices) for group, choices in ALL_PERMISSIONS
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='权限',
        coerce=str,
    )

    class Meta:
        model = Role
        fields = ['code', 'name', 'description', 'permissions', 'is_builtin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['permissions'] = self.instance.permissions or []

    def clean_permissions(self):
        return list(self.cleaned_data.get('permissions', []))


# ──────────── 用户 & 角色 ────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'phone', 'is_active', 'last_login']
    list_display_links = ['id', 'username']
    list_filter = ['is_active', 'roles']
    search_fields = ['username', 'email', 'phone']
    filter_horizontal = ['roles', 'groups', 'user_permissions']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('phone', 'avatar', 'roles')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('phone', 'roles')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleForm
    list_display = ['id', 'code', 'name', 'is_builtin', 'created_at']
    list_display_links = ['id', 'code', 'name']
    list_filter = ['is_builtin']
    search_fields = ['code', 'name']


# ──────────── 审计日志（只读） ────────────

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'method', 'path', 'ip', 'status_code', 'duration_ms', 'created_at']
    list_display_links = ['id', 'username']
    list_filter = ['method', 'status_code']
    search_fields = ['username', 'path']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'ip', 'success', 'reason', 'created_at']
    list_display_links = ['id', 'username']
    list_filter = ['success']
    search_fields = ['username', 'ip']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ──────────── 字典管理 ────────────

@admin.register(DictData)
class DictDataAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'is_active', 'updated_at']
    list_display_links = ['key']
    list_filter = ['is_active']
    search_fields = ['key', 'value', 'description']


# ──────────── 定时任务 ────────────

@admin.register(CronSchedule)
class CronScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'func', 'schedule_type', 'enabled', 'last_run', 'updated_at']
    list_display_links = ['name']
    list_filter = ['schedule_type', 'enabled']
    search_fields = ['name', 'func']
    list_editable = ['enabled']
