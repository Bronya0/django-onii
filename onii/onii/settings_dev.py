import os
from pathlib import Path
import yaml

from utils.common import DJANGO_CONF_PATH, build_database_config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-ujv6*iavz)nu&g#x7-w64ia4p#oj2&z&eh13$7o^phk=7w@pa('
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 为true时会加载dev配置，否则加载prod配置
DEBUG = True
with open(os.path.join(DJANGO_CONF_PATH, "dev.yaml"), 'r', encoding='utf-8') as file:
    YAML_CONF: dict = yaml.safe_load(file)

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'app',
]

DATABASES = build_database_config(YAML_CONF, BASE_DIR)

# 规定日志的格式
STANDARD_LOG_FORMAT = (
    "[%(asctime)s][%(name)s.%(funcName)s():%(lineno)d] [%(levelname)s] %(message)s"
)

LOG_PATH = YAML_CONF['log']['path']
LOG_LEVEL = YAML_CONF['log']['level']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    "formatters": {
        "standard": {"format": STANDARD_LOG_FORMAT},
        "console": {
            "format": STANDARD_LOG_FORMAT,
        },
        "file": {
            "format": STANDARD_LOG_FORMAT,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'default': {
            'level': 'DEBUG',
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, YAML_CONF['log']['default']),
            'maxBytes': YAML_CONF['log']['maxBytes'],
            'backupCount': YAML_CONF['log']['backupCount'],
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'filename': os.path.join(LOG_PATH, YAML_CONF['log']['error']),
            'maxBytes': YAML_CONF['log']['maxBytes'],
            'backupCount': YAML_CONF['log']['backupCount'],
            'formatter': 'standard',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'django': {
            'handlers': ["console"],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'async_task': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': True,
        }
    },
}

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'app.model.auth.drf_permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '300/minute',
    },
    'EXCEPTION_HANDLER': 'utils.exception.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Onii API',
    'DESCRIPTION': '后台管理系统接口文档 (开发环境)',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

MIDDLEWARE = [
    'middleware.time_middleware.TimeMiddleware',
    'middleware.ip_whitelist_middleware.IPWhitelistMiddleware',
    'middleware.api_sign_middleware.ApiSignMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.audit_middleware.AuditMiddleware',
]

ROOT_URLCONF = 'onii.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'onii.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'app.User'

# JWT 配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ──────────── CORS（开发环境允许全部来源）────────────
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ──────────── 安全加固 ────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 请求体上限 10 MB
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
