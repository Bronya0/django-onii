#!/usr/bin/env python
# -*- coding: utf-8 -*-

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.viewsets import ModelViewSet

from app.model.auth.drf_permissions import IsAuthenticated, HasPermission
from app.model.system.system_model import DictType, DictData
from app.serializer.system.system_serializer import (
    DictTypeSerializer, DictTypeListSerializer, DictDataSerializer,
)
from utils.page_util import MyPageNumberPagination


@extend_schema_view(
    list=extend_schema(summary='字典类型列表', tags=['字典管理']),
    create=extend_schema(summary='创建字典类型', tags=['字典管理']),
    retrieve=extend_schema(summary='字典类型详情(含数据)', tags=['字典管理']),
    update=extend_schema(summary='更新字典类型', tags=['字典管理']),
    destroy=extend_schema(summary='删除字典类型', tags=['字典管理']),
)
class DictTypeView(ModelViewSet):
    """字典类型管理"""

    queryset = DictType.objects.all()
    pagination_class = MyPageNumberPagination
    permission_classes = [IsAuthenticated, HasPermission]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DictTypeSerializer  # 包含 items
        return DictTypeListSerializer

    def get_required_permissions(self):
        if self.action in ('list', 'retrieve'):
            return ['dict:view']
        return ['dict:edit']

    @property
    def required_permissions(self):
        return self.get_required_permissions()


@extend_schema_view(
    list=extend_schema(summary='字典数据列表', tags=['字典管理'],
        parameters=[OpenApiParameter('type_code', str, description='按字典类型编码过滤')]),
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

    def get_queryset(self):
        qs = super().get_queryset()
        dict_type_code = self.request.query_params.get('type_code')
        if dict_type_code:
            qs = qs.filter(dict_type__code=dict_type_code)
        return qs
