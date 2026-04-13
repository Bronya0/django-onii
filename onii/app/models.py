#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Django 模型聚合入口，确保 makemigrations 能发现模型。"""

from app.model.auth.auth_model import User, Role, AuditLog, LoginLog  # noqa: F401
from app.model.async_task.async_task_model import DjangoQProcess  # noqa: F401
