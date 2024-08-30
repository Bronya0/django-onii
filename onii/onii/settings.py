import os
from pathlib import Path
import yaml

from utils.common import DJANGO_CONF_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-ujv6*iavz)nu&g#x7-w64ia4p#oj2&z&eh13$7o^phk=7w@pa('

# 为true时会加载dev配置，否则加载prod配置
DEBUG = True

config_file = "dev.yaml" if DEBUG else "prod.yaml"
with open(os.path.join(DJANGO_CONF_PATH, config_file), 'r', encoding='utf-8') as file:
    YAML_CONF: dict = yaml.safe_load(file)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'django_q',
    'apps',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, YAML_CONF['log']['default']),
            'maxBytes': YAML_CONF['log']['maxBytes'],
            'backupCount': YAML_CONF['log']['backupCount'],
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, YAML_CONF['log']['error']),
            'maxBytes': YAML_CONF['log']['maxBytes'],
            'backupCount': YAML_CONF['log']['backupCount'],
            'formatter': 'standard',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'django': {
            'handlers': ["default"],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'app': {
            'handlers': ['error', 'default'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'async_task': {
            'handlers': ['error', 'default'],
            'level': LOG_LEVEL,
            'propagate': True,
        }
    },
}


REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",  # 日期时间格式配置
    "DATE_FORMAT": "%Y-%m-%d",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# django-q配置
Q_CLUSTER = {
    # 任务队列命令
    'name': 'app',
    # worker数量，默认cpu数
    'workers': 4,
    # 在回收之前要处理的任务数量。对于定期释放内存资源很有用。默认为 500
    'recycle': 500,
    # 最大重试次数
    'max_attempts': -1,
    'ack_failures': True,
    # 在任务终止之前允许worker在任务上花费的秒数。默认为 None ，这意味着它永远不会超时
    'timeout': 604800,  # 一周
    # 重启触发秒数，任务在达到秒数后会被其他worker再次启动。必须大于timeout
    'retry': 604801,
    # 将任务包压缩到代理。对于大型有效负载很有用，但与许多小包一起使用时会增加开销。默认为 False
    'compress': False,
    # 设置每个worker可以使用的处理器数量。这不会影响哨兵或监视器等辅助进程，并且仅适用于调整非常高流量的集群的性能。
    # 关联数必须大于零且小于处理器总数才能产生任何效果.默认使用所有处理器;cpu_affinity 设置需要可选的 psutil 模块。
    # 'cpu_affinity': 3,
    # 限制保存到 Django 的成功任务数量。设置为 0 表示无限制。  设置为 -1 则根本不会成功存储。 默认为 250。失败总是可以被挽救的
    'save_limit': 0,
    # 排队的任务数量。将其设置为合理的数字可以帮助平衡每个集群的工作负载和内存开销。默认为 workers**2
    'queue_limit': 500,
    # 用于 Django 管理页面的标签。默认为 'Django Q'
    'label': 'Django异步任务队列',
    # 可以配置从redis读信息
    # 'redis': {
    #     'host': '',
    #     'port': 6379,
    #     'password': '',
    #     'db': 1,
    # }
    'orm': 'default',
    'has_replica': True
}

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

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
