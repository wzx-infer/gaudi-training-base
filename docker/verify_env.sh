#!/bin/bash
# Gaudi2 训练环境验证脚本
# 在容器内运行，验证 HPU、模型、LLaMA-Factory 是否正常
# 使用 Qwen3.8-27B 模型进行训练测试

set -e

echo "=========================================="
echo "Gaudi2 训练环境验证 - Qwen3.8-27B"
echo "=========================================="

# 1. 验证 HPU 设备
echo ""
echo ">>> 1. 验证 HPU 设备..."
python -c "import torch; print('HPU 可用:', torch.hpu.is_available()); print('HPU 数量:', torch.hpu.device_count())"

# 2. 验证模型路径
echo ""
echo ">>> 2. 验证模型路径..."
echo "检查 Qwen3.8-27B 模型..."
ls -lh /models/Qwen/Qwen3.8-27B/ | head -10

# 3. 安装 LLaMA-Factory
echo ""
echo ">>> 3. 安装 LLaMA-Factory..."
cd /workspace/LLaMA-Factory
pip install -e . --no-deps -q

# 4. 验证 LLaMA-Factory
echo ""
echo ">>> 4. 验证 LLaMA-Factory..."
python -c "import llamafactory; print('LLaMA-Factory 版本:', llamafactory.__version__)"

# 5. 验证核心依赖版本
echo ""
echo ">>> 5. 验证核心依赖版本..."
python -c "
import transformers, peft, trl, datasets, accelerate
print(f'transformers: {transformers.__version__}')
print(f'peft: {peft.__version__}')
print(f'trl: {trl.__version__}')
print(f'datasets: {datasets.__version__}')
print(f'accelerate: {accelerate.__version__}')
"

# 6. 启动训练测试
echo ""
echo ">>> 6. 启动训练测试..."
echo "模型: Qwen3.8-27B"
echo "训练配置: config-27b.yaml"
echo "输出目录: saves/qwen3.8-27b-lora"
echo ""

cd /workspace/LLaMA-Factory
llamafactory-cli train config-27b.yaml

echo ""
echo "=========================================="
echo "✓ 验证完成 - 训练已完成"
echo "=========================================="
echo ""
echo "检查训练输出:"
echo "  - checkpoint: ls -lh saves/qwen3.8-27b-lora/"
echo "  - 日志: cat saves/qwen3.8-27b-lora/trainer_log.jsonl"
echo ""
