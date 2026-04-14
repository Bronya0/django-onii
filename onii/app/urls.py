import datetime

from django.http import JsonResponse
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from app.api.v1.auth.auth_view import (
    AuthView, UserManageView, RoleManageView,
    AuditLogView, LoginLogView,
)
from app.api.v1.system.monitor_view import MonitorView
from app.api.v1.system.health_view import HealthCheckView
from app.api.v1.system.dict_view import DictDataView
from app.api.v1.task.schedule_view import ScheduleManageView

urlpatterns = [
    path('', lambda request: JsonResponse({"now": datetime.datetime.now()})),
    # JWT token 刷新
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # 健康检查（无需认证）
    path('health', HealthCheckView.as_view(), name='health-check'),
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
# 系统监控
router.register("monitor", MonitorView, basename="monitor")
# 字典数据
router.register("dict-data", DictDataView, basename="dict-data")
# 定时任务
router.register("schedules", ScheduleManageView, basename="schedules")

urlpatterns += router.urls
