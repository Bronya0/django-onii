#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==== 停止现有服务 ===="
pkill -f "gunicorn.*onii.wsgi" 2>/dev/null && echo "gunicorn 已停止" || echo "gunicorn 未运行"
pkill -f "python.*jobs/scheduler" 2>/dev/null && echo "scheduler 已停止" || echo "scheduler 未运行"

sleep 1

echo "==== 重新启动 ===="
exec bash "$(dirname "$0")/start.sh"
