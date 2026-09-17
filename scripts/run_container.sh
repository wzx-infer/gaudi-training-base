#!/bin/bash
# Docker容器快速启动脚本
# 用法: bash scripts/run_container.sh

set -e

# 配置参数（根据实际环境修改）
IMAGE_NAME="gaudi-multimodal-train:1.24.1"
CONTAINER_NAME="gaudi-train-$(date +%Y%m%d-%H%M%S)"

# 目录挂载（请根据实际路径修改）
WORKSPACE_DIR=$(pwd)
MODEL_DIR="${HOME}/models"              # 预下载的模型权重
DATA_DIR="${HOME}/data"                 # 训练数据集
OUTPUT_DIR="${HOME}/output"             # 训练输出

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

docker run -it --rm \
  --name $CONTAINER_NAME \
  --runtime=habana \
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
