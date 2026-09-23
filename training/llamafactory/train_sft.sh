#!/bin/bash
#
# MechVQA SFT Training Script
# 使用 LLaMA-Factory 在 Qwen3.8-27B 上训练
#

set -e

echo "============================================"
echo "MechVQA SFT Training - LLaMA-Factory"
echo "============================================"

# 环境变量
export PT_HPU_LAZY_MODE=0
export PT_HPU_RECIPE_CACHE_CONFIG=/root/.cache/habana/recipe_cache,true,1024,false
export PT_HPU_ENABLE_LAZY_COLLECTIVES=true
export OMPI_MCA_btl_vader_single_copy_mechanism=none

# 工作目录
cd /workspace/gaudi-training-base

# 添加 dataset_info.json 到 LLaMA-Factory
echo ">>> Copying dataset_info.json to LLaMA-Factory..."
cp data/mechvqa/dataset_info.json /workspace/LLaMA-Factory/data/dataset_info.json

# 创建输出目录
mkdir -p results/sft/checkpoints
mkdir -p results/sft/logs

echo ">>> Training Configuration:"
echo "  Model: Qwen3.8-27B"
echo "  Dataset: MechVQA (12749 train)"
echo "  Method: LoRA (rank=64)"
echo "  Batch size: 1 x 8 (gradient accumulation) x 8 (HPU)"
echo "  Epochs: 3"
echo "  Output: results/sft/"

echo ""
echo ">>> Starting training..."
cd /workspace/LLaMA-Factory

llamafactory-cli train \
    /workspace/gaudi-training-base/training/llamafactory/configs/mechvqa_sft.yaml

echo ""
echo "============================================"
echo "✓ Training completed!"
echo "============================================"
echo ""
echo "Checkpoints: /workspace/gaudi-training-base/results/sft/checkpoints"
echo "Logs: /workspace/gaudi-training-base/results/sft/logs"
echo ""
echo "Next steps:"
echo "  1. Evaluate: python evaluation/evaluate_mechvqa.py --model_path results/sft/checkpoints"
echo "  2. Visualize: python evaluation/visualize.py --log_dir results/sft/logs"
