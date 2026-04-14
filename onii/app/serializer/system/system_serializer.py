#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from app.model.system.system_model import SystemConfig, DictType, DictData


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'value_type', 'group', 'description', 'is_public', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class DictDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictData
        fields = ['id', 'dict_type', 'label', 'value', 'sort', 'is_active', 'remark']
        read_only_fields = ['id']


class DictTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictType
        fields = ['id', 'code', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class DictTypeSerializer(serializers.ModelSerializer):
    """详情包含字典数据列表"""
    items = DictDataSerializer(many=True, read_only=True)

    class Meta:
        model = DictType
        fields = ['id', 'code', 'name', 'description', 'is_active', 'items']
        read_only_fields = ['id']
