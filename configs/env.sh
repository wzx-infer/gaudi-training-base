#!/bin/bash
# Gaudi2 训练环境变量配置
# 用法：source env.sh

# ============================================================
# Habana 基础环境
# ============================================================
export HABANA_VISIBLE_DEVICES=all
export HABANA_LOGS_DIR=/tmp/habana_logs

# ============================================================
# PyTorch Lazy 模式（必须开启，用于大模型训练）
# ============================================================
export PT_HPU_LAZY_MODE=1
export PT_HPU_ENABLE_LAZY_COLLECTIVES=true

# ============================================================
# HCCL 多卡通信配置
# ============================================================
export HCCL_OVER_TCP=1
export HCCL_SOCKET_IFNAME=eth0
export LOG_LEVEL_ALL=3

# ============================================================
# DeepSpeed 配置
# ============================================================
export DS_ACCELERATOR=hpu
export DS_ENABLE_DYNAMIC_LOSS_SCALE=true

# ============================================================
# 性能优化
# ============================================================
# 启用算子融合
export PT_HPU_ENABLE_REFINE_DYNAMIC_SHAPES=0
export PT_HPU_MAX_COMPOUND_OP_SIZE=10

# 显存优化
export PT_HPU_POOL_MEM_ACQUIRE_PERC=90

# ============================================================
# 日志与调试
# ============================================================
export TRANSFORMERS_VERBOSITY=info
export HABANA_PROFILE=0  # 设为1开启性能profiling
export LOG_LEVEL_ALL_HCL=3

# ============================================================
# 确认加载
# ============================================================
echo "✓ Gaudi2 训练环境变量已加载"
echo "  - PT_HPU_LAZY_MODE: $PT_HPU_LAZY_MODE"
echo "  - PT_HPU_ENABLE_LAZY_COLLECTIVES: $PT_HPU_ENABLE_LAZY_COLLECTIVES"
echo "  - HABANA_VISIBLE_DEVICES: $HABANA_VISIBLE_DEVICES"
