#!/bin/bash

# LoRA 权重合并脚本

set -e

BASE_MODEL=${1:-"Qwen/Qwen2-VL-7B-Instruct"}
LORA_PATH=${2:-"../outputs/models/qwen2_vl_lora"}
OUTPUT_PATH=${3:-"../outputs/models/qwen2_vl_merged"}

echo "======================================"
echo "🔄 LoRA 权重合并"
echo "======================================"
echo "基座模型: $BASE_MODEL"
echo "LoRA路径: $LORA_PATH"
echo "输出路径: $OUTPUT_PATH"
echo "======================================"

python merge_lora.py \
    --base_model "$BASE_MODEL" \
    --lora_path "$LORA_PATH" \
    --output_path "$OUTPUT_PATH"

echo ""
echo "✅ 合并完成！"
echo "模型保存在: $OUTPUT_PATH"
