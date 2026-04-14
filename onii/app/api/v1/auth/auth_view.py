#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging

from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from app.model.auth.auth_model import User, Role, AuditLog, LoginLog, PasswordHistory
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
# 密码历史记录数 (禁止复用最近 N 次密码)
PASSWORD_HISTORY_COUNT = 5
# 最大同时在线设备数 (0 = 不限制)
MAX_SESSIONS = 3


def _get_security_conf():
    """从 YAML 配置读取安全参数"""
    from django.conf import settings
    return getattr(settings, 'YAML_CONF', {}).get('security', {})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _check_password_history(user, raw_password):
    """检查密码是否在历史记录中"""
    conf = _get_security_conf()
    count = conf.get('password_history_count', PASSWORD_HISTORY_COUNT)
    if count <= 0:
        return False
    history = user.password_history.all()[:count]
    from django.contrib.auth.hashers import check_password
    return any(check_password(raw_password, h.password_hash) for h in history)


def _save_password_history(user):
    """保存当前密码到历史"""
    PasswordHistory.objects.create(user=user, password_hash=user.password)
    # 只保留最近 N 条
    conf = _get_security_conf()
    keep = conf.get('password_history_count', PASSWORD_HISTORY_COUNT)
    ids_to_keep = list(
        user.password_history.order_by('-created_at').values_list('id', flat=True)[:keep]
    )
    user.password_history.exclude(id__in=ids_to_keep).delete()


def _enforce_session_limit(user):
    """会话并发控制：超出限制则踢掉最早的 token"""
    conf = _get_security_conf()
    max_sessions = conf.get('max_sessions', MAX_SESSIONS)
    if max_sessions <= 0:
        return
    try:
        from rest_framework_simplejwt.token_blacklist.models import (
            OutstandingToken, BlacklistedToken,
        )
        active_tokens = (
            OutstandingToken.objects.filter(user=user)
            .exclude(id__in=BlacklistedToken.objects.values_list('token_id', flat=True))
            .order_by('-created_at')
        )
        excess = list(active_tokens[max_sessions:])
        for token in excess:
            BlacklistedToken.objects.get_or_create(token=token)
    except Exception as e:
        logger.warning(f"会话并发控制异常: {e}")


@extend_schema_view(
    login=extend_schema(summary='用户登录', tags=['认证']),
    info=extend_schema(summary='当前用户信息', tags=['认证']),
    change_password=extend_schema(summary='修改密码', tags=['认证']),
    logout=extend_schema(summary='登出', tags=['认证']),
)
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

        # 会话并发控制
        _enforce_session_limit(user)

        return SuccessResponse(data={
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'must_change_password': user.must_change_password,
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

        new_password = serializer.validated_data['new_password']

        # 密码历史检查
        if _check_password_history(user, new_password):
            return ErrorResponse(msg='不能使用最近使用过的密码', code=4000)

        # 保存旧密码到历史
        _save_password_history(user)

        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.must_change_password = False
        user.save(update_fields=['password', 'password_changed_at', 'must_change_password'])
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


@extend_schema_view(
    list=extend_schema(summary='用户列表', tags=['用户管理']),
    create=extend_schema(summary='创建用户', tags=['用户管理']),
    retrieve=extend_schema(summary='用户详情', tags=['用户管理']),
    update=extend_schema(summary='更新用户', tags=['用户管理']),
    partial_update=extend_schema(summary='部分更新用户', tags=['用户管理']),
    destroy=extend_schema(summary='禁用用户', tags=['用户管理']),
    reset_password=extend_schema(summary='重置密码', tags=['用户管理']),
    assign_roles=extend_schema(summary='分配角色', tags=['用户管理']),
)
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

        # 密码历史检查
        if _check_password_history(target_user, new_password):
            return ErrorResponse(msg='不能使用该用户最近使用过的密码', code=4000)

        # 保存旧密码到历史
        _save_password_history(target_user)

        target_user.set_password(new_password)
        target_user.password_changed_at = timezone.now()
        target_user.login_fail_count = 0
        target_user.locked_until = None
        target_user.must_change_password = True  # 管理员重置后要求用户首次登录改密
        target_user.save(update_fields=['password', 'password_changed_at', 'login_fail_count', 'locked_until', 'must_change_password'])
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


@extend_schema_view(
    list=extend_schema(summary='角色列表', tags=['角色管理']),
    create=extend_schema(summary='创建角色', tags=['角色管理']),
    retrieve=extend_schema(summary='角色详情', tags=['角色管理']),
    update=extend_schema(summary='更新角色', tags=['角色管理']),
    partial_update=extend_schema(summary='部分更新角色', tags=['角色管理']),
    destroy=extend_schema(summary='删除角色', tags=['角色管理']),
)
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


@extend_schema_view(
    list=extend_schema(summary='审计日志列表', tags=['审计日志'],
        parameters=[
            OpenApiParameter('start', str, description='开始时间'),
            OpenApiParameter('end', str, description='结束时间'),
            OpenApiParameter('username', str, description='用户名'),
        ]),
)
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


@extend_schema_view(
    list=extend_schema(summary='登录日志列表', tags=['审计日志'],
        parameters=[
            OpenApiParameter('username', str, description='用户名'),
            OpenApiParameter('success', str, description='是否成功'),
        ]),
)
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
