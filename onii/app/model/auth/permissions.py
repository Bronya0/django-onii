#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
权限定义：三权分立

系统管理员(system_admin): 用户CRUD、系统配置
安全管理员(security_admin): 角色管理、权限分配、IP白名单、密码策略
审计管理员(audit_admin): 审计日志查看、登录日志查看
普通用户(user): 业务接口访问
"""

# 权限代码定义
PERM_USER_LIST = 'user:list'
PERM_USER_CREATE = 'user:create'
PERM_USER_UPDATE = 'user:update'
PERM_USER_DELETE = 'user:delete'
PERM_USER_RESET_PWD = 'user:reset_password'

PERM_ROLE_LIST = 'role:list'
PERM_ROLE_CREATE = 'role:create'
PERM_ROLE_UPDATE = 'role:update'
PERM_ROLE_DELETE = 'role:delete'
PERM_ROLE_ASSIGN = 'role:assign'

PERM_AUDIT_LOG_VIEW = 'audit:log:view'
PERM_LOGIN_LOG_VIEW = 'audit:login_log:view'

PERM_CONFIG_IP_WHITELIST = 'config:ip_whitelist'
PERM_CONFIG_PASSWORD_POLICY = 'config:password_policy'
PERM_CONFIG_VIEW = 'config:view'
PERM_CONFIG_EDIT = 'config:edit'
PERM_DICT_VIEW = 'dict:view'
PERM_DICT_EDIT = 'dict:edit'
PERM_MONITOR_VIEW = 'monitor:view'
PERM_TASK_VIEW = 'task:view'
PERM_TASK_EDIT = 'task:edit'

# 内置角色的默认权限
BUILTIN_ROLE_PERMISSIONS = {
    'system_admin': [
        PERM_USER_LIST, PERM_USER_CREATE, PERM_USER_UPDATE, PERM_USER_DELETE, PERM_USER_RESET_PWD,
        PERM_CONFIG_VIEW, PERM_CONFIG_EDIT,
        PERM_DICT_VIEW, PERM_DICT_EDIT,
        PERM_MONITOR_VIEW,
        PERM_TASK_VIEW, PERM_TASK_EDIT,
    ],
    'security_admin': [
        PERM_ROLE_LIST, PERM_ROLE_CREATE, PERM_ROLE_UPDATE, PERM_ROLE_DELETE, PERM_ROLE_ASSIGN,
        PERM_CONFIG_IP_WHITELIST, PERM_CONFIG_PASSWORD_POLICY,
        PERM_USER_LIST,  # 安全管理员可查看用户列表（分配角色需要）
    ],
    'audit_admin': [
        PERM_AUDIT_LOG_VIEW, PERM_LOGIN_LOG_VIEW,
        PERM_USER_LIST,  # 审计管理员可查看用户列表（审计需要）
        PERM_MONITOR_VIEW,
    ],
    'user': [],
}


def init_builtin_roles():
    """初始化内置角色（首次 migrate 后调用）"""
    from app.model.auth.auth_model import Role

    for code, perms in BUILTIN_ROLE_PERMISSIONS.items():
        role, created = Role.objects.get_or_create(
            code=code,
            defaults={
                'name': {
                    'system_admin': '系统管理员',
                    'security_admin': '安全管理员',
                    'audit_admin': '审计管理员',
                    'user': '普通用户',
                }[code],
                'description': f'内置角色: {code}',
                'permissions': perms,
                'is_builtin': True,
            }
        )
        if created:
            print(f"创建内置角色: {role.name}")
