#!/bin/bash
#
# MechVQA SFT Training - 8卡分布式训练
#

set -e

echo "============================================"
echo "MechVQA SFT Training - 8-Card Distributed"
echo "============================================"

# 检查HPU设备
echo ">>> Checking HPU devices..."
python -c "import torch; print(f'HPU available: {torch.hpu.is_available()}'); print(f'HPU count: {torch.hpu.device_count()}')"

# 环境变量
export PT_HPU_LAZY_MODE=0
export PT_HPU_RECIPE_CACHE_CONFIG=/root/.cache/habana/recipe_cache,true,1024,false
export PT_HPU_ENABLE_LAZY_COLLECTIVES=true
export OMPI_MCA_btl_vader_single_copy_mechanism=none

# 工作目录
cd /workspace/gaudi-training-base

# 创建输出目录
mkdir -p results/sft/checkpoints
mkdir -p results/sft/logs

echo ""
echo ">>> Training Configuration:"
echo "  Model: Qwen3.8-27B"
echo "  Dataset: MechVQA (12749 train)"
echo "  Method: LoRA (rank=64) + DeepSpeed ZeRO-2"
echo "  Devices: 8 x Gaudi2"
echo "  Batch size: 1 x 8 (grad_accum) x 8 (devices) = 64 effective"
echo "  Epochs: 3"
echo "  Output: results/sft/"

echo ""
echo ">>> Starting 8-card distributed training..."
cd /workspace/LLaMA-Factory

# 8卡分布式训练
llamafactory-cli train \
    /workspace/gaudi-training-base/training/llamafactory/configs/mechvqa_sft_8card.yaml \
    --nnodes 1 \
    --nproc_per_node 8

echo ""
echo "============================================"
echo "✓ Training completed!"
echo "============================================"
echo ""
echo "Checkpoints: /workspace/gaudi-training-base/results/sft/checkpoints"
echo "Logs: /workspace/gaudi-training-base/results/sft/logs"
