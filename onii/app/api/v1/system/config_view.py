#!/usr/bin/env python
# -*- coding: utf-8 -*-

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from app.model.system.system_model import SystemConfig
from app.serializer.system.system_serializer import SystemConfigSerializer
from utils.drf_util import SuccessResponse
from utils.page_util import MyPageNumberPagination


@extend_schema_view(
    list=extend_schema(summary='配置列表', tags=['系统配置']),
    create=extend_schema(summary='创建配置', tags=['系统配置']),
    retrieve=extend_schema(summary='配置详情', tags=['系统配置']),
    update=extend_schema(summary='更新配置', tags=['系统配置']),
    partial_update=extend_schema(summary='部分更新配置', tags=['系统配置']),
    destroy=extend_schema(summary='删除配置', tags=['系统配置']),
    public=extend_schema(summary='公开配置(无需认证)', tags=['系统配置']),
    groups=extend_schema(summary='配置分组列表', tags=['系统配置']),
)
class SystemConfigView(ModelViewSet):
    """系统配置管理"""

    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permissions(self):
        if self.action in ('list', 'retrieve'):
            return ['config:view']
        return ['config:edit']

    @property
    def required_permissions(self):
        return self.get_required_permissions()

    @action(methods=['get'], detail=False, permission_classes=[AllowAny], authentication_classes=[])
    def public(self, request):
        """获取公开配置（无需认证）"""
        configs = SystemConfig.objects.filter(is_public=True)
        data = {c.key: c.value for c in configs}
        return SuccessResponse(data=data)

    @action(methods=['get'], detail=False)
    def groups(self, request):
        """获取所有配置分组"""
        groups = SystemConfig.objects.values_list('group', flat=True).distinct()
        return SuccessResponse(data=list(groups))
