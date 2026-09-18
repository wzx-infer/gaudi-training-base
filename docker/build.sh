#!/bin/bash

# Docker 镜像构建脚本

set -e

IMAGE_NAME="gaudi-training-base"
IMAGE_TAG="latest"

echo "======================================"
echo "🐳 开始构建 Docker 镜像"
echo "======================================"
echo "镜像名称: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "======================================"

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile ..

echo ""
echo "✅ 镜像构建完成！"
echo ""
echo "运行容器:"
echo "  bash run.sh"
echo ""
echo "或手动运行:"
echo "  docker run --runtime=habana -e HABANA_VISIBLE_DEVICES=all \\"
echo "    -v \$(pwd)/..:/workspace \\"
echo "    ${IMAGE_NAME}:${IMAGE_TAG}"
