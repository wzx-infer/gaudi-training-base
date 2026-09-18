#!/bin/bash

# 训练监控脚本 - 实时查看训练状态

set -e

LOG_DIR=${1:-"../outputs/logs"}
MODEL_DIR=${2:-"../outputs/models"}

echo "======================================"
echo "📊 训练监控"
echo "======================================"
echo "日志目录: $LOG_DIR"
echo "模型目录: $MODEL_DIR"
echo "======================================"
echo ""

# 检查是否有训练进程
if ! pgrep -f "train" > /dev/null; then
    echo "⚠️  没有检测到训练进程"
    echo ""
fi

# 显示最新的日志文件
if [ -d "$LOG_DIR" ]; then
    echo "📝 最新日志文件:"
    ls -lht "$LOG_DIR" | head -5
    echo ""

    LATEST_LOG=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "======================================"
        echo "📄 最新日志内容 (最后50行):"
        echo "======================================"
        tail -50 "$LATEST_LOG"
    fi
else
    echo "⚠️  日志目录不存在: $LOG_DIR"
fi

echo ""
echo "======================================"
echo "💾 已保存的checkpoint:"
echo "======================================"
if [ -d "$MODEL_DIR" ]; then
    find "$MODEL_DIR" -name "checkpoint-*" -o -name "adapter_model.*" | head -10
else
    echo "⚠️  模型目录不存在: $MODEL_DIR"
fi

echo ""
echo "======================================"
echo "💡 使用提示:"
echo "======================================"
echo "实时监控日志:"
echo "  tail -f $LOG_DIR/train_*.log"
echo ""
echo "查看GPU使用:"
echo "  hl-smi"
echo ""
echo "TensorBoard:"
echo "  tensorboard --logdir=$MODEL_DIR"
