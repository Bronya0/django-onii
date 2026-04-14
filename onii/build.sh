#!/bin/bash
set -e

VERSION="${1:-latest}"
IMAGE_NAME="onii:${VERSION}"
TAR_NAME="onii-${VERSION}.tar"

echo "==== 构建镜像: ${IMAGE_NAME} ===="
docker build -t "${IMAGE_NAME}" .

echo "==== 导出镜像: ${TAR_NAME} ===="
docker save "${IMAGE_NAME}" > "${TAR_NAME}"

echo "==== 完成 ===="
echo "  镜像: ${IMAGE_NAME}"
echo "  文件: ${TAR_NAME}"
echo ""
echo "部署方式:"
echo "  1. Docker Compose: docker compose up -d"
echo "  2. 导入镜像:       docker load < ${TAR_NAME}"
echo "  3. 单机直接运行:    ./start.sh"