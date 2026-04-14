#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """角色表：三权分立 + 自定义角色"""

    # 内置角色代码
    SYSTEM_ADMIN = 'system_admin'       # 系统管理员：用户管理、系统配置
    SECURITY_ADMIN = 'security_admin'   # 安全管理员：角色权限管理、IP白名单、密码策略
    AUDIT_ADMIN = 'audit_admin'         # 审计管理员：审计日志查看、操作日志查询
    USER = 'user'                       # 普通用户

    BUILTIN_ROLES = [SYSTEM_ADMIN, SECURITY_ADMIN, AUDIT_ADMIN, USER]

    code = models.CharField(max_length=64, unique=True, verbose_name="角色代码")
    name = models.CharField(max_length=128, verbose_name="角色名称")
    description = models.TextField(blank=True, default='', verbose_name="角色描述")
    permissions = models.JSONField(default=list, verbose_name="权限列表")
    is_builtin = models.BooleanField(default=False, verbose_name="是否内置角色")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_role'
        verbose_name = '角色'

    def __str__(self):
        return f"{self.name} ({self.code})"


class User(AbstractUser):
    """自定义用户模型"""

    phone = models.CharField(max_length=20, blank=True, default='', verbose_name="手机号")
    avatar = models.CharField(max_length=512, blank=True, default='', verbose_name="头像URL")
    roles = models.ManyToManyField(Role, blank=True, related_name='users', verbose_name="角色")
    login_fail_count = models.IntegerField(default=0, verbose_name="连续登录失败次数")
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name="锁定截止时间")
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="密码最后修改时间")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="最后登录IP")
    must_change_password = models.BooleanField(default=False, verbose_name="是否需要强制改密")

    class Meta:
        db_table = 'auth_user'
        verbose_name = '用户'

    def has_role(self, role_code: str) -> bool:
        return self.roles.filter(code=role_code).exists()

    def has_any_role(self, *role_codes) -> bool:
        return self.roles.filter(code__in=role_codes).exists()

    def role_codes(self) -> list:
        return list(self.roles.values_list('code', flat=True))


class AuditLog(models.Model):
    """审计日志"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="操作用户")
    username = models.CharField(max_length=150, verbose_name="用户名")
    method = models.CharField(max_length=10, verbose_name="请求方法")
    path = models.CharField(max_length=512, verbose_name="请求路径")
    query_params = models.TextField(blank=True, default='', verbose_name="查询参数")
    ip = models.GenericIPAddressField(verbose_name="请求IP")
    user_agent = models.CharField(max_length=512, blank=True, default='', verbose_name="User-Agent")
    status_code = models.IntegerField(default=0, verbose_name="响应状态码")
    duration_ms = models.IntegerField(default=0, verbose_name="耗时(ms)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = '审计日志'
        ordering = ['-created_at']


class LoginLog(models.Model):
    """登录日志"""

    username = models.CharField(max_length=150, verbose_name="用户名")
    ip = models.GenericIPAddressField(verbose_name="登录IP")
    user_agent = models.CharField(max_length=512, blank=True, default='')
    success = models.BooleanField(verbose_name="是否成功")
    reason = models.CharField(max_length=256, blank=True, default='', verbose_name="失败原因")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'login_log'
        verbose_name = '登录日志'
        ordering = ['-created_at']


class PasswordHistory(models.Model):
    """密码历史：防止复用最近 N 次密码"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=256, verbose_name="密码哈希")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_password_history'
        verbose_name = '密码历史'
        ordering = ['-created_at']
