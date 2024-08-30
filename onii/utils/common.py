#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

# 本项目根路径：
DJANGO_PATH = Path(__file__).resolve().parent.parent
DJANGO_APPS_PATH = os.path.join(DJANGO_PATH, 'apps')
DJANGO_CONF_PATH = os.path.join(DJANGO_PATH, 'conf')


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_MS = '%Y.%m.%d_%H.%M.%S.%f'
FORMAT_DATETIME2 = "%Y-%m-%d_%H_%M_%S"
FORMAT_DATETIME3 = "%Y-%m-%d"
FORMAT_DATETIME4 = "%Y-%m-%d %H:00:00"
FORMAT_DATETIME5 = "%Y-%m-%d 00:00:00"
FORMAT_DATETIME6 = "%m-%d"
FORMAT_DATETIME7 = "yyyy-MM-dd HH:mm:ss"


