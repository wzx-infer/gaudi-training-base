#!/bin/bash
# Docker容器快速启动脚本

set -e

# 配置参数
IMAGE_NAME="gaudi-training-base:latest"
CONTAINER_NAME="gaudi-train-$(date +%Y%m%d-%H%M%S)"

# 目录挂载（请根据实际路径修改）
WORKSPACE_DIR=$(cd .. && pwd)  # 上级目录，即项目根目录
MODEL_DIR="${HOME}/models"
DATA_DIR="${HOME}/data"
OUTPUT_DIR="${HOME}/output"

# 创建必要目录
mkdir -p $OUTPUT_DIR

echo "================================================"
echo "🐳 启动Gaudi2训练容器"
echo "================================================"
echo "镜像: $IMAGE_NAME"
echo "容器: $CONTAINER_NAME"
echo "工作目录: $WORKSPACE_DIR"
echo "模型目录: $MODEL_DIR"
echo "数据目录: $DATA_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "================================================"

# 检测是否有habana runtime
if docker info 2>/dev/null | grep -q "habana"; then
    # 有habana runtime
    RUNTIME_ARGS="--runtime=habana"
else
    # 没有habana runtime，使用device方式
    echo "⚠️  未检测到habana runtime，使用--device方式"
    RUNTIME_ARGS="--device=/dev/accel:/dev/accel --device=/dev/accel_controlD0:/dev/accel_controlD0"
fi

docker run -it --rm \
  --name $CONTAINER_NAME \
  $RUNTIME_ARGS \
  -e HABANA_VISIBLE_DEVICES=all \
  -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
  --cap-add=sys_nice \
  --net=host \
  --ipc=host \
  -v $WORKSPACE_DIR:/workspace/gaudi-training-base \
  -v $MODEL_DIR:/models \
  -v $DATA_DIR:/data \
  -v $OUTPUT_DIR:/output \
  $IMAGE_NAME \
  /bin/bash

echo "✅ 容器已退出"
