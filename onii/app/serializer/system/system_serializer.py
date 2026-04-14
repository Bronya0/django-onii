#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from app.model.system.system_model import DictData


class DictDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictData
        fields = ['id', 'key', 'value', 'description', 'is_active']
        read_only_fields = ['id']
