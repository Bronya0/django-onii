import datetime

from django.http import HttpResponse, JsonResponse
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.v1.async_task.async_task_view import AsyncTaskView
from app.api.v1.auth.auth_view import (
    AuthView, UserManageView, RoleManageView,
    AuditLogView, LoginLogView,
)

urlpatterns = [
    path('', lambda request: JsonResponse({"now": datetime.datetime.now()})),
    # JWT token 刷新
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
# DRF路由
router = routers.DefaultRouter(trailing_slash=False)

# 认证
router.register("auth", AuthView, basename="auth")
# 用户管理
router.register("users", UserManageView, basename="users")
# 角色管理
router.register("roles", RoleManageView, basename="roles")
# 审计日志
router.register("audit-logs", AuditLogView, basename="audit-logs")
# 登录日志
router.register("login-logs", LoginLogView, basename="login-logs")
# 异步任务
router.register("async_task", AsyncTaskView, basename="async_task")

urlpatterns += router.urls
