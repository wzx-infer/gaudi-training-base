#!/bin/bash
# 远程 Gaudi2 训练修复和重新测试脚本
# 使用方法：在远程服务器上运行 bash remote_fix_and_test.sh

set -e

echo "============================================"
echo "Gaudi2 训练修复和测试"
echo "============================================"
echo ""

# 查找项目目录
if [ -d ~/gaudi-training-base ]; then
    PROJECT_DIR=~/gaudi-training-base
elif [ -d /workspace/gaudi-training-base ]; then
    PROJECT_DIR=/workspace/gaudi-training-base
else
    PROJECT_DIR=$(find ~ -name "gaudi-training-base" -type d 2>/dev/null | head -1)
fi

if [ -z "$PROJECT_DIR" ]; then
    echo "❌ 错误：未找到项目目录"
    exit 1
fi

cd "$PROJECT_DIR"
echo "工作目录: $PROJECT_DIR"
echo ""

# 1. 清理旧容器
echo "=== 1. 清理旧容器 ==="
OLD_CONTAINERS=$(docker ps -a -q --filter "ancestor=gaudi-training-base:latest")
if [ -n "$OLD_CONTAINERS" ]; then
    echo "停止并删除旧容器..."
    docker stop $OLD_CONTAINERS 2>/dev/null || true
    docker rm $OLD_CONTAINERS 2>/dev/null || true
    echo "✓ 清理完成"
else
    echo "没有旧容器需要清理"
fi
echo ""

# 2. 创建必要的目录
echo "=== 2. 创建输出目录 ==="
mkdir -p outputs/models outputs/logs outputs/checkpoints
mkdir -p data/images/hvac
echo "✓ 目录创建完成"
echo ""

# 3. 验证数据集
echo "=== 3. 验证训练数据集 ==="
if [ ! -f data/examples/train_cad.jsonl ]; then
    echo "❌ 数据集不存在，创建示例数据..."
    mkdir -p data/examples
    cat > data/examples/train_cad.jsonl << 'EOF'
{"messages": [{"role": "user", "content": [{"type": "text", "text": "请识别这个暖通构件"}]}, {"role": "assistant", "content": "<think>根据图纸特征分析，这是一个标准的风管三通接头。</think>\n这是风管三通"}]}
{"messages": [{"role": "user", "content": [{"type": "text", "text": "这个构件是什么？"}]}, {"role": "assistant", "content": "<think>观察管道弯曲特征，这是90度弯头。</think>\n这是风管弯头（90度）"}]}
{"messages": [{"role": "user", "content": [{"type": "text", "text": "请分析这段管道"}]}, {"role": "assistant", "content": "<think>管径从大端逐渐缩小到小端，这是变径管。</think>\n这是风管变径（大小头）"}]}
EOF
    echo "✓ 创建了简单的测试数据集"
else
    LINES=$(wc -l < data/examples/train_cad.jsonl)
    echo "✓ 数据集存在，包含 $LINES 条数据"
fi
echo ""

# 4. 检查并修复配置文件
echo "=== 4. 检查配置文件 ==="

# 检查 dataset_info.json
if [ ! -f configs/llamafactory/dataset_info.json ]; then
    echo "创建 dataset_info.json..."
    mkdir -p configs/llamafactory
    cat > configs/llamafactory/dataset_info.json << 'EOF'
{
  "cad_multimodal": {
    "file_name": "data/examples/train_cad.jsonl",
    "formatting": "sharegpt",
    "columns": {
      "messages": "messages",
      "images": "images"
    },
    "tags": {
      "role_tag": "role",
      "content_tag": "content",
      "user_tag": "user",
      "assistant_tag": "assistant"
    }
  }
}
EOF
fi

# 检查 DeepSpeed 配置
if [ ! -f configs/deepspeed_z2.json ]; then
    echo "创建 deepspeed_z2.json..."
    cat > configs/deepspeed_z2.json << 'EOF'
{
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto",
  "gradient_accumulation_steps": "auto",
  "gradient_clipping": 1.0,
  "zero_optimization": {
    "stage": 2,
    "allgather_partitions": true,
    "reduce_scatter": true,
    "overlap_comm": true,
    "contiguous_gradients": true
  },
  "bf16": {
    "enabled": true
  },
  "steps_per_print": 10
}
EOF
fi

echo "✓ 配置文件检查完成"
echo ""

# 5. 启动训练容器（测试模式）
echo "=== 5. 启动训练容器（测试模式） ==="
echo "使用简化配置进行测试..."

# 创建测试训练脚本
cat > test_train_in_container.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

echo "容器内环境测试"
cd /workspace/gaudi-training-base

# 加载环境变量
source configs/env.sh

# 检查 Habana 设备
echo "检查 Habana 设备..."
python3 -c "import habana_frameworks.torch as ht; print(f'Habana devices: {ht.hpu.device_count()}')" || echo "警告：Habana PyTorch 未正确加载"

# 检查数据集
echo "检查数据集..."
python3 << 'EOFPY'
import json
with open('data/examples/train_cad.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"数据集行数: {len(lines)}")
    print(f"第一条: {json.loads(lines[0])}")
EOFPY

# 安装 LLaMA-Factory（如果需要）
if ! python3 -c "import llmtuner" 2>/dev/null; then
    echo "安装 LLaMA-Factory..."
    pip install llmtuner[torch,metrics] -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
fi

# 测试训练命令（dry-run）
echo "测试训练配置..."
cd training/llamafactory
export DATASET_DIR=../../configs/llamafactory

# 创建最小化测试配置
cat > test_config.yaml << 'EOFYAML'
model_name_or_path: Qwen/Qwen2-VL-7B-Instruct
stage: sft
do_train: true
finetuning_type: lora
lora_target: all
lora_rank: 8
lora_alpha: 16
dataset: cad_multimodal
template: qwen2_vl
cutoff_len: 2048
max_samples: 2
output_dir: ../../outputs/models/test_output
logging_steps: 1
save_steps: 10
per_device_train_batch_size: 1
gradient_accumulation_steps: 1
learning_rate: 5.0e-5
num_train_epochs: 1
bf16: true
use_habana: true
use_lazy_mode: true
overwrite_output_dir: true
EOFYAML

echo "运行最小化训练测试（2个样本，1个epoch）..."
llamafactory-cli train test_config.yaml 2>&1 | tee ../../outputs/logs/test_train.log

echo "✓ 训练测试完成"
EOFSCRIPT

chmod +x test_train_in_container.sh

echo "启动 Docker 容器进行测试..."
docker run -it --rm \
    --runtime=habana \
    -e HABANA_VISIBLE_DEVICES=all \
    -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
    --cap-add=sys_nice \
    --net=host \
    --ipc=host \
    -v $(pwd):/workspace/gaudi-training-base \
    gaudi-training-base:latest \
    bash /workspace/gaudi-training-base/test_train_in_container.sh

echo ""
echo "============================================"
echo "测试完成！"
echo "============================================"
echo ""
echo "如果测试成功，可以运行完整训练："
echo "  cd training/llamafactory"
echo "  bash train.sh"
echo ""
echo "查看日志："
echo "  tail -f outputs/logs/test_train.log"
