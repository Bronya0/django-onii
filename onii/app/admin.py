#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from app.model.auth.auth_model import User, Role, AuditLog, LoginLog
from app.model.system.system_model import SystemConfig, DictType, DictData, CronSchedule


# ──────────── 用户 & 角色 ────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'phone', 'is_active', 'last_login']
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
class RoleAdmin(UnfoldModelAdmin):
    list_display = ['id', 'code', 'name', 'is_builtin', 'created_at']
    list_filter = ['is_builtin']
    search_fields = ['code', 'name']


# ──────────── 审计日志（只读） ────────────

@admin.register(AuditLog)
class AuditLogAdmin(UnfoldModelAdmin):
    list_display = ['id', 'username', 'method', 'path', 'ip', 'status_code', 'duration_ms', 'created_at']
    list_filter = ['method', 'status_code']
    search_fields = ['username', 'path']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginLog)
class LoginLogAdmin(UnfoldModelAdmin):
    list_display = ['id', 'username', 'ip', 'success', 'reason', 'created_at']
    list_filter = ['success']
    search_fields = ['username', 'ip']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ──────────── 系统配置 ────────────

@admin.register(SystemConfig)
class SystemConfigAdmin(UnfoldModelAdmin):
    list_display = ['key', 'value', 'value_type', 'group', 'is_public', 'updated_at']
    list_filter = ['group', 'value_type', 'is_public']
    search_fields = ['key', 'description']


# ──────────── 字典管理 ────────────

class DictDataInline(admin.TabularInline):
    model = DictData
    extra = 1
    fields = ['label', 'value', 'sort', 'is_active', 'remark']


@admin.register(DictType)
class DictTypeAdmin(UnfoldModelAdmin):
    list_display = ['code', 'name', 'description', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    inlines = [DictDataInline]


@admin.register(DictData)
class DictDataAdmin(UnfoldModelAdmin):
    list_display = ['dict_type', 'label', 'value', 'sort', 'is_active']
    list_filter = ['dict_type', 'is_active']
    search_fields = ['label', 'value']
    list_editable = ['sort', 'is_active']


# ──────────── 定时任务 ────────────

@admin.register(CronSchedule)
class CronScheduleAdmin(UnfoldModelAdmin):
    list_display = ['name', 'func', 'schedule_type', 'enabled', 'last_run', 'updated_at']
    list_filter = ['schedule_type', 'enabled']
    search_fields = ['name', 'func']
    list_editable = ['enabled']
