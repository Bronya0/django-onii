#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==== 执行数据库迁移 ===="
python manage.py migrate --noinput

echo "==== 初始化安全数据 ===="
python manage.py init_security

echo "==== 注册定时任务 ===="
python jobs/cron.py 2>/dev/null || true

echo "==== 启动 qcluster (后台) ===="
python manage.py qcluster &
QCLUSTER_PID=$!

echo "==== 启动 gunicorn ===="
gunicorn -c gunicorn.conf.py onii.wsgi:application &
GUNICORN_PID=$!

# 捕获信号，优雅关闭
trap "kill $GUNICORN_PID $QCLUSTER_PID 2>/dev/null; wait; exit 0" SIGTERM SIGINT

echo "==== 服务已启动 (gunicorn=$GUNICORN_PID, qcluster=$QCLUSTER_PID) ===="
wait