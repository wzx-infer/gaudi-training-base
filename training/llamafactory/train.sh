#!/bin/bash

# LLaMA-Factory 一键训练脚本 (Gaudi2 8卡)
# 适合小白用户快速上手

set -e

# 加载环境变量
source ../../configs/env.sh

# 检查 LLaMA-Factory 是否安装
if ! python -c "import llmtuner" 2>/dev/null; then
    echo "❌ LLaMA-Factory 未安装，正在安装..."
    pip install llmtuner[torch,metrics] -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 设置数据集配置路径
export DATASET_DIR=../../configs/llamafactory

# 显示训练配置
echo "======================================"
echo "🚀 LLaMA-Factory 训练启动"
echo "======================================"
echo "模型: Qwen/Qwen2-VL-7B-Instruct"
echo "方法: LoRA (rank=64)"
echo "数据: cad_multimodal"
echo "卡数: 8 x Gaudi2"
echo "输出: ../../outputs/models/qwen2_vl_lora"
echo "======================================"

# 启动训练 (8卡分布式)
llamafactory-cli train qwen2_vl_lora.yaml

echo "✅ 训练完成！模型保存在: ../../outputs/models/qwen2_vl_lora"
