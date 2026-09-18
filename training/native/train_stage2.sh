#!/bin/bash
# Gaudi2 8卡训练启动脚本 - 阶段2：LoRA指令微调
# 用法: bash scripts/train_stage2.sh

set -e

# 加载环境变量
source env.sh

# 训练参数
MODEL_PATH="Qwen/Qwen2.5-VL-7B-Instruct"
DATA_PATH="data/train_cad.jsonl"
IMAGE_FOLDER="data/images"
OUTPUT_DIR="output/stage2_lora"

# LoRA配置
LORA_R=64
LORA_ALPHA=128
LORA_DROPOUT=0.05
LORA_TARGET_MODULES="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"

# DeepSpeed配置
NUM_GPUS=8
NUM_NODES=1
DEEPSPEED_CONFIG="ds_config_gaudi_z2.json"

echo "================================================"
echo "🚀 阶段2：LoRA指令微调"
echo "================================================"
echo "模型: $MODEL_PATH"
echo "数据: $DATA_PATH"
echo "输出: $OUTPUT_DIR"
echo "LoRA秩: $LORA_R, Alpha: $LORA_ALPHA"
echo "卡数: ${NUM_GPUS}x${NUM_NODES}"
echo "================================================"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 启动训练
deepspeed --num_gpus $NUM_GPUS --num_nodes $NUM_NODES \
  --hostfile /tmp/hostfile \
  train_qwen_multimodal.py \
  --model_name_or_path $MODEL_PATH \
  --data_path $DATA_PATH \
  --image_folder $IMAGE_FOLDER \
  --stage 2 \
  --output_dir $OUTPUT_DIR \
  --num_train_epochs 5 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --weight_decay 0.01 \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 10 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --bf16 true \
  --deepspeed $DEEPSPEED_CONFIG \
  --ddp_timeout 3600 \
  --dataloader_num_workers 4 \
  --remove_unused_columns false \
  --lora_r $LORA_R \
  --lora_alpha $LORA_ALPHA \
  --lora_dropout $LORA_DROPOUT \
  --lora_target_modules $LORA_TARGET_MODULES \
  --report_to tensorboard \
  --logging_dir $OUTPUT_DIR/logs \
  --seed 42

echo "✅ 阶段2训练完成！"
echo "   输出目录: $OUTPUT_DIR"
echo "   下一步: python merge_lora.py --base_model $MODEL_PATH --lora_adapter $OUTPUT_DIR/checkpoint-final --output output/merged_model"
