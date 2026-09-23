#!/bin/bash
# Gaudi2 多模态训练环境部署脚本
# 适用于 Intel Gaudi2 + Qwen3.5 多模态模型训练

set -e

echo "=========================================="
echo "Gaudi2 多模态训练环境部署"
echo "=========================================="

# 1. 停止并清理旧容器
echo ">>> 清理旧容器..."
docker stop gaudi-train-v2 2>/dev/null || true
docker rm gaudi-train-v2 2>/dev/null || true
docker stop gaudi-mutimodel-training 2>/dev/null || true
docker rm gaudi-mutimodel-training 2>/dev/null || true
docker stop docker-mutimodel-training 2>/dev/null || true
docker rm docker-mutimodel-training 2>/dev/null || true

# 2. 构建镜像
echo ">>> 构建 Docker 镜像..."
docker build -t gaudi-train-qwen35:v2 .

# 3. 启动容器
echo ">>> 启动容器 docker-mutimodel-training..."
docker run -it -d \
  --name docker-mutimodel-training \
  --privileged \
  -v /dev/accel:/dev/habanalabs \
  -e HABANA_VISIBLE_DEVICES=all \
  -e PT_HPU_LAZY_MODE=0 \
  -e PT_HPU_RECIPE_CACHE_CONFIG=/root/.cache/habana/recipe_cache,true,1024,false \
  -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
  -v /data/models:/models \
  -v /home/wzx/workspace:/workspace \
  -v /root/.cache/habana:/root/.cache/habana \
  --ipc=host --cap-add=sys_nice --security-opt label=disable \
  gaudi-train-qwen35:v2 \
  /bin/bash

# 4. 验证容器状态
echo ">>> 验证容器状态..."
docker ps --filter name=docker-mutimodel-training

echo ""
echo "=========================================="
echo "✓ 部署完成"
echo "=========================================="
echo ""
echo "下一步操作："
echo "  1. 进入容器: docker exec -it docker-mutimodel-training bash"
echo "  2. 运行验证脚本: cd /workspace/gaudi-training-base/docker && bash verify_env.sh"
echo ""
