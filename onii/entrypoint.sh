#!/bin/bash
set -e

echo "==== 执行数据库迁移 ===="
python manage.py migrate --noinput

echo "==== 收集静态文件 ===="
python manage.py collectstatic --noinput 2>/dev/null || true

echo "==== 初始化安全数据 ===="
python manage.py init_security

echo "==== 注册定时任务 ===="
python jobs/cron.py 2>/dev/null || true

echo "==== 启动服务 ===="
exec "$@"
