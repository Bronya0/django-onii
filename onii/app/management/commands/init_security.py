#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from app.model.auth.auth_model import User, Role
from app.model.auth.permissions import init_builtin_roles


class Command(BaseCommand):
    help = '初始化内置角色和超级管理员'

    def handle(self, *args, **options):
        # 1. 初始化内置角色
        self.stdout.write('正在初始化内置角色...')
        init_builtin_roles()

        # 2. 创建超级管理员（如果不存在）
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='Admin@123456',
            )
            # 给超级管理员分配所有内置角色
            for role in Role.objects.filter(is_builtin=True):
                admin.roles.add(role)
            self.stdout.write(self.style.SUCCESS(
                '超级管理员创建成功: admin / Admin@123456'
            ))
        else:
            self.stdout.write('超级管理员已存在，跳过创建')

        self.stdout.write(self.style.SUCCESS('初始化完成'))
