#!/bin/bash
# Gaudi2 训练环境变量配置（版本锁定方案）
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
# HCCL 多卡通信
# ============================================================
export HCCL_COMM_ID=127.0.0.1:5555
export HCCL_SOCKET_IFNAME=eth0

# ============================================================
# 优化配置
# ============================================================
export PT_HPU_MAX_COMPOUND_OP_SIZE=1024
export PT_HPU_ENABLE_REFINE_DYNAMIC_SHAPES=0

# ============================================================
# Python / 训练配置
# ============================================================
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8

# ============================================================
# 版本检查禁用（固定版本后不需要运行时检查）
# ============================================================
export DISABLE_VERSION_CHECK=0

echo "✓ Gaudi2 训练环境变量已加载（版本锁定方案）"
echo "  - PT_HPU_LAZY_MODE: $PT_HPU_LAZY_MODE"
echo "  - PT_HPU_ENABLE_LAZY_COLLECTIVES: $PT_HPU_ENABLE_LAZY_COLLECTIVES"
echo "  - HABANA_VISIBLE_DEVICES: $HABANA_VISIBLE_DEVICES"
echo ""
echo "依赖版本锁定："
echo "  - transformers==4.48.3 (支持 AutoModelForVision2Seq)"
echo "  - accelerate==0.31.0 (LLaMA-Factory 兼容)"
echo "  - peft==0.11.1"
echo "  - optimum-habana==1.24.1"
