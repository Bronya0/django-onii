#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

# 本项目根路径：
DJANGO_PATH = Path(__file__).resolve().parent.parent
DJANGO_APPS_PATH = os.path.join(DJANGO_PATH, 'app/api')
DJANGO_CONF_PATH = os.path.join(DJANGO_PATH, 'conf')


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_MS = '%Y.%m.%d_%H.%M.%S.%f'
FORMAT_DATETIME2 = "%Y-%m-%d_%H_%M_%S"
FORMAT_DATETIME3 = "%Y-%m-%d"
FORMAT_DATETIME4 = "%Y-%m-%d %H:00:00"
FORMAT_DATETIME5 = "%Y-%m-%d 00:00:00"
FORMAT_DATETIME6 = "%m-%d"
FORMAT_DATETIME7 = "yyyy-MM-dd HH:mm:ss"


# 数据库引擎映射
_DB_ENGINE_MAP = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'pgsql': 'django.db.backends.postgresql',
    'postgresql': 'django.db.backends.postgresql',
}


def build_database_config(yaml_conf: dict, base_dir) -> dict:
    """根据 YAML 配置构建 Django DATABASES dict"""
    db_conf = yaml_conf.get('database', {})
    engine = db_conf.get('engine', 'sqlite')

    django_engine = _DB_ENGINE_MAP.get(engine)
    if not django_engine:
        raise ValueError(f"不支持的数据库引擎: {engine}，可选: {list(_DB_ENGINE_MAP.keys())}")

    if engine == 'sqlite':
        return {
            'default': {
                'ENGINE': django_engine,
                'NAME': base_dir / db_conf.get('name', 'db.sqlite3'),
            }
        }

    return {
        'default': {
            'ENGINE': django_engine,
            'NAME': db_conf.get('db_name', 'onii'),
            'HOST': db_conf.get('host', '127.0.0.1'),
            'PORT': db_conf.get('port', 3306 if engine == 'mysql' else 5432),
            'USER': db_conf.get('user', 'root'),
            'PASSWORD': db_conf.get('password', ''),
            'OPTIONS': {'charset': 'utf8mb4'} if engine == 'mysql' else {},
        }
    }


