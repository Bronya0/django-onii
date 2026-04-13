#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import serializers
from app.model.auth.auth_model import User, Role, AuditLog, LoginLog


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'description', 'permissions', 'is_builtin', 'created_at']
        read_only_fields = ['id', 'is_builtin', 'created_at']


class UserListSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, write_only=True, source='roles', required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'is_active',
            'roles', 'role_ids', 'last_login', 'date_joined',
        ]
        read_only_fields = ['id', 'last_login', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, write_only=True, source='roles', required=False
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password', 'role_ids']
        read_only_fields = ['id']

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if roles:
            user.roles.set(roles)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_new_password(self, value):
        """密码复杂度校验"""
        import re
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('密码必须包含至少一个小写字母')
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('密码必须包含至少一个数字')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise serializers.ValidationError('密码必须包含至少一个特殊字符')
        return value


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'method', 'path', 'query_params', 'ip', 'status_code', 'duration_ms', 'created_at']


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = ['id', 'username', 'ip', 'success', 'reason', 'created_at']
