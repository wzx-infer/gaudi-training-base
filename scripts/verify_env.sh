#!/bin/bash
# 训练环境验证脚本
# 用法: bash scripts/verify_env.sh

set -e

echo "================================================"
echo "🔍 Gaudi2训练环境验证"
echo "================================================"

# 1. 检查HPU设备
echo ""
echo "1️⃣ 检查HPU设备..."
if command -v hl-smi &> /dev/null; then
    hl-smi -L
    echo "✓ HPU设备检测正常"
else
    echo "❌ 未找到hl-smi命令，请确认Habana驱动已安装"
    exit 1
fi

# 2. 检查环境变量
echo ""
echo "2️⃣ 检查环境变量..."
REQUIRED_VARS=(
    "PT_HPU_LAZY_MODE"
    "PT_HPU_ENABLE_LAZY_COLLECTIVES"
    "HABANA_VISIBLE_DEVICES"
    "DS_ACCELERATOR"
)

ALL_OK=true
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 缺少环境变量: $var"
        ALL_OK=false
    else
        echo "✓ $var=${!var}"
    fi
done

if [ "$ALL_OK" = false ]; then
    echo ""
    echo "⚠️ 请先执行: source env.sh"
    exit 1
fi

# 3. 检查Python包
echo ""
echo "3️⃣ 检查Python依赖..."
REQUIRED_PACKAGES=(
    "habana_frameworks"
    "transformers"
    "peft"
    "deepspeed"
    "optimum.habana"
)

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import ${pkg}" 2>/dev/null; then
        VERSION=$(python -c "import ${pkg}; print(getattr(${pkg}, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "✓ ${pkg} ${VERSION}"
    else
        echo "❌ 缺少Python包: ${pkg}"
        ALL_OK=false
    fi
done

# 4. 检查PyTorch HPU支持
echo ""
echo "4️⃣ 检查PyTorch HPU支持..."
python -c "
import torch
import habana_frameworks.torch.core as htcore

print(f'✓ PyTorch版本: {torch.__version__}')

if torch.hpu.is_available():
    print(f'✓ HPU可用，设备数: {torch.hpu.device_count()}')
    print(f'✓ 当前设备: {torch.hpu.current_device()}')
else:
    print('❌ HPU不可用')
    exit(1)
"

# 5. 检查HCCL多卡通信
echo ""
echo "5️⃣ 检查HCCL配置..."
HCCL_VARS=(
    "HCCL_OVER_TCP"
    "HCCL_SOCKET_IFNAME"
)

for var in "${HCCL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️ 建议设置: $var"
    else
        echo "✓ $var=${!var}"
    fi
done

# 6. 检查数据目录
echo ""
echo "6️⃣ 检查数据目录..."
if [ -f "data/train_cad.jsonl" ]; then
    LINE_COUNT=$(wc -l < data/train_cad.jsonl)
    echo "✓ 训练数据: data/train_cad.jsonl ($LINE_COUNT 条样本)"
else
    echo "⚠️ 未找到训练数据: data/train_cad.jsonl"
fi

if [ -d "data/images" ]; then
    IMAGE_COUNT=$(find data/images -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l)
    echo "✓ 图像目录: data/images ($IMAGE_COUNT 个文件)"
else
    echo "⚠️ 未找到图像目录: data/images"
fi

# 7. 检查DeepSpeed配置
echo ""
echo "7️⃣ 检查DeepSpeed配置..."
if [ -f "ds_config_gaudi_z2.json" ]; then
    echo "✓ DeepSpeed配置: ds_config_gaudi_z2.json"
    python -c "import json; config=json.load(open('ds_config_gaudi_z2.json')); print(f'  ZeRO Stage: {config[\"zero_optimization\"][\"stage\"]}'); print(f'  FP16: {config[\"fp16\"][\"enabled\"]}')"
else
    echo "❌ 缺少DeepSpeed配置文件"
    exit 1
fi

# 8. 验证Lazy模式
echo ""
echo "8️⃣ 验证Lazy模式..."
python -c "
import os
import torch
import habana_frameworks.torch.core as htcore

lazy_mode = os.environ.get('PT_HPU_LAZY_MODE', '0')
if lazy_mode == '1':
    print('✓ Lazy模式已启用')
    x = torch.randn(10, 10, device='hpu')
    y = x * 2
    htcore.mark_step()
    print('✓ Lazy图编译测试通过')
else:
    print('❌ Lazy模式未启用，请设置 PT_HPU_LAZY_MODE=1')
    exit(1)
"

echo ""
echo "================================================"
echo "✅ 环境验证完成！"
echo "================================================"
echo ""
echo "🚀 可以开始训练："
echo "   阶段1: bash scripts/train_stage1.sh"
echo "   阶段2: bash scripts/train_stage2.sh"
