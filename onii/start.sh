#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==== 执行数据库迁移 ===="
python manage.py migrate --noinput

echo "==== 收集静态文件 ===="
python manage.py collectstatic --noinput

echo "==== 初始化安全数据 ===="
python manage.py init_security

echo "==== 启动 APScheduler (后台) ===="
python jobs/scheduler.py &
SCHEDULER_PID=$!

echo "==== 启动 gunicorn ===="
gunicorn -c gunicorn.conf.py onii.wsgi:application &
GUNICORN_PID=$!

# 捕获信号，优雅关闭
trap "kill $GUNICORN_PID $SCHEDULER_PID 2>/dev/null; wait; exit 0" SIGTERM SIGINT

echo ""
echo "============================================"
echo "  服务已启动"
echo "  gunicorn  PID: $GUNICORN_PID"
echo "  scheduler PID: $SCHEDULER_PID"
echo "--------------------------------------------"
echo "  Admin:    http://127.0.0.1:8000/admin/"
echo "  API:      http://127.0.0.1:8000/api/"
echo "  API Doc:  http://127.0.0.1:8000/api/docs/"
echo "  默认账号:  admin / Admin@123456"
echo "============================================"
echo ""

wait