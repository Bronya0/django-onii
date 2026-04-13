#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from app.model.auth.auth_model import User, Role, AuditLog, LoginLog
from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from app.model.auth.permissions import (
    PERM_USER_LIST, PERM_USER_CREATE, PERM_USER_UPDATE,
    PERM_USER_DELETE, PERM_USER_RESET_PWD,
    PERM_ROLE_LIST, PERM_ROLE_CREATE, PERM_ROLE_UPDATE,
    PERM_ROLE_DELETE, PERM_ROLE_ASSIGN,
    PERM_AUDIT_LOG_VIEW, PERM_LOGIN_LOG_VIEW,
)
from app.serializer.auth.auth_serializer import (
    UserListSerializer, UserCreateSerializer, ChangePasswordSerializer,
    RoleSerializer, AuditLogSerializer, LoginLogSerializer,
)
from utils.drf_util import SuccessResponse, ErrorResponse
from utils.page_util import MyPageNumberPagination

logger = logging.getLogger('app')

# 登录失败锁定配置
MAX_LOGIN_FAIL = 5
LOCK_DURATION_MINUTES = 30


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class AuthView(GenericViewSet):
    """认证接口：登录、登出、修改密码、获取当前用户信息"""

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')[:512]

        if not username or not password:
            return ErrorResponse(msg='用户名和密码不能为空', code=4000)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=False, reason='用户不存在')
            return ErrorResponse(msg='用户名或密码错误', code=4001)

        # 检查锁定
        if user.locked_until and user.locked_until > timezone.now():
            remaining = (user.locked_until - timezone.now()).seconds // 60
            LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=False, reason='账号锁定中')
            return ErrorResponse(msg=f'账号已锁定，请 {remaining + 1} 分钟后重试', code=4003)

        if not user.check_password(password):
            user.login_fail_count += 1
            if user.login_fail_count >= MAX_LOGIN_FAIL:
                user.locked_until = timezone.now() + datetime.timedelta(minutes=LOCK_DURATION_MINUTES)
                user.save(update_fields=['login_fail_count', 'locked_until'])
                LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=False, reason=f'密码错误，账号已锁定 {LOCK_DURATION_MINUTES} 分钟')
                return ErrorResponse(msg=f'密码错误次数过多，账号已锁定 {LOCK_DURATION_MINUTES} 分钟', code=4003)
            user.save(update_fields=['login_fail_count'])
            LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=False, reason=f'密码错误({user.login_fail_count}/{MAX_LOGIN_FAIL})')
            return ErrorResponse(msg='用户名或密码错误', code=4001)

        if not user.is_active:
            LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=False, reason='账号已禁用')
            return ErrorResponse(msg='账号已被禁用', code=4003)

        # 登录成功，重置失败计数
        user.login_fail_count = 0
        user.locked_until = None
        user.last_login = timezone.now()
        user.last_login_ip = ip
        user.save(update_fields=['login_fail_count', 'locked_until', 'last_login', 'last_login_ip'])

        # 生成 JWT
        refresh = RefreshToken.for_user(user)
        LoginLog.objects.create(username=username, ip=ip, user_agent=ua, success=True)

        return SuccessResponse(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': list(user.roles.values_list('code', flat=True)),
            }
        })

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def info(self, request):
        user = request.user
        return SuccessResponse(data={
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'roles': RoleSerializer(user.roles.all(), many=True).data,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
        })

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return ErrorResponse(msg='原密码错误', code=4001)

        user.set_password(serializer.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save(update_fields=['password', 'password_changed_at'])
        return SuccessResponse(msg='密码修改成功')

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return SuccessResponse(msg='已登出')


class UserManageView(ModelViewSet):
    """用户管理（系统管理员）"""

    queryset = User.objects.all().order_by('-id')
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_required_permissions(self):
        perm_map = {
            'list': [PERM_USER_LIST],
            'retrieve': [PERM_USER_LIST],
            'create': [PERM_USER_CREATE],
            'update': [PERM_USER_UPDATE],
            'partial_update': [PERM_USER_UPDATE],
            'destroy': [PERM_USER_DELETE],
        }
        return perm_map.get(self.action, [])

    @property
    def required_permissions(self):
        return self.get_required_permissions()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return ErrorResponse(msg='不能删除超级管理员', code=4003)
        if user.id == request.user.id:
            return ErrorResponse(msg='不能删除自己', code=4003)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return SuccessResponse(msg='用户已禁用')

    @action(methods=['post'], detail=True, url_path='reset-password')
    def reset_password(self, request, pk=None):
        if not request.user.is_authenticated:
            return ErrorResponse(msg='未登录', code=4001)
        # 检查权限
        user_perms = set()
        for role in request.user.roles.all():
            user_perms.update(role.permissions or [])
        if PERM_USER_RESET_PWD not in user_perms and not request.user.is_superuser:
            return ErrorResponse(msg='无权限', code=4003)

        target_user = self.get_object()
        new_password = request.data.get('new_password', '')
        if len(new_password) < 8:
            return ErrorResponse(msg='密码长度不少于8位', code=4000)
        target_user.set_password(new_password)
        target_user.password_changed_at = timezone.now()
        target_user.login_fail_count = 0
        target_user.locked_until = None
        target_user.save(update_fields=['password', 'password_changed_at', 'login_fail_count', 'locked_until'])
        return SuccessResponse(msg='密码已重置')

    @action(methods=['post'], detail=True, url_path='assign-roles')
    def assign_roles(self, request, pk=None):
        if not request.user.is_authenticated:
            return ErrorResponse(msg='未登录', code=4001)
        user_perms = set()
        for role in request.user.roles.all():
            user_perms.update(role.permissions or [])
        if PERM_ROLE_ASSIGN not in user_perms and not request.user.is_superuser:
            return ErrorResponse(msg='无权限', code=4003)

        target_user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        roles = Role.objects.filter(id__in=role_ids)
        target_user.roles.set(roles)
        return SuccessResponse(msg='角色分配成功')


class RoleManageView(ModelViewSet):
    """角色管理（安全管理员）"""

    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    @property
    def required_permissions(self):
        perm_map = {
            'list': [PERM_ROLE_LIST],
            'retrieve': [PERM_ROLE_LIST],
            'create': [PERM_ROLE_CREATE],
            'update': [PERM_ROLE_UPDATE],
            'partial_update': [PERM_ROLE_UPDATE],
            'destroy': [PERM_ROLE_DELETE],
        }
        return perm_map.get(self.action, [])

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_builtin:
            return ErrorResponse(msg='内置角色不能删除', code=4003)
        return super().destroy(request, *args, **kwargs)


class AuditLogView(GenericViewSet):
    """审计日志查看（审计管理员）"""

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PERM_AUDIT_LOG_VIEW]

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持按时间范围过滤
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        username = request.query_params.get('username')
        if start:
            queryset = queryset.filter(created_at__gte=start)
        if end:
            queryset = queryset.filter(created_at__lte=end)
        if username:
            queryset = queryset.filter(username__icontains=username)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data)


class LoginLogView(GenericViewSet):
    """登录日志查看（审计管理员）"""

    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = [PERM_LOGIN_LOG_VIEW]

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        username = request.query_params.get('username')
        success = request.query_params.get('success')
        if username:
            queryset = queryset.filter(username__icontains=username)
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data)
