#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from app.model.system.system_model import DictData
from app.serializer.system.system_serializer import DictDataSerializer
from utils.page_util import MyPageNumberPagination

_DICT_CACHE_PREFIX = 'dict:'
_DICT_CACHE_TTL = 300  # 5 分钟


@extend_schema_view(
    list=extend_schema(summary='字典数据列表', tags=['字典管理']),
    create=extend_schema(summary='创建字典数据', tags=['字典管理']),
    retrieve=extend_schema(summary='字典数据详情', tags=['字典管理']),
    update=extend_schema(summary='更新字典数据', tags=['字典管理']),
    destroy=extend_schema(summary='删除字典数据', tags=['字典管理']),
)
class DictDataView(ModelViewSet):
    """字典数据管理"""

    queryset = DictData.objects.all()
    serializer_class = DictDataSerializer
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_required_permissions(self):
        if self.action in ('list', 'retrieve'):
            return ['dict:view']
        return ['dict:edit']

    @property
    def required_permissions(self):
        return self.get_required_permissions()

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete(f"{_DICT_CACHE_PREFIX}{instance.key}")

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"{_DICT_CACHE_PREFIX}{instance.key}")

    def perform_destroy(self, instance):
        key = instance.key
        instance.delete()
        cache.delete(f"{_DICT_CACHE_PREFIX}{key}")
