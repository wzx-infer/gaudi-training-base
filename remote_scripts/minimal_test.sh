#!/bin/bash
# Minimal training test - fixes common issues and runs a tiny test
set -e
cd ~/gaudi-training-base

echo "=== Minimal Training Test ==="
echo ""

# 1. Create minimal test data if needed
mkdir -p data/examples
if [ ! -f data/examples/train_cad.jsonl ] || [ $(wc -l < data/examples/train_cad.jsonl) -lt 2 ]; then
    echo "Creating test dataset..."
    cat > data/examples/train_cad.jsonl << 'EOF'
{"messages":[{"role":"user","content":[{"type":"text","text":"这是什么构件？"}]},{"role":"assistant","content":"<think>根据特征分析</think>\n这是风管三通"}]}
{"messages":[{"role":"user","content":[{"type":"text","text":"识别构件类型"}]},{"role":"assistant","content":"<think>观察弯曲角度</think>\n这是风管弯头"}]}
{"messages":[{"role":"user","content":[{"type":"text","text":"分析管道"}]},{"role":"assistant","content":"<think>管径变化明显</think>\n这是变径管"}]}
EOF
fi

# 2. Ensure configs exist
mkdir -p configs/llamafactory
cat > configs/llamafactory/dataset_info.json << 'EOF'
{"cad_multimodal":{"file_name":"data/examples/train_cad.jsonl","formatting":"sharegpt","columns":{"messages":"messages"},"tags":{"role_tag":"role","content_tag":"content","user_tag":"user","assistant_tag":"assistant"}}}
EOF

# 3. Create minimal training config
mkdir -p training/llamafactory
cat > training/llamafactory/minimal_test.yaml << 'EOF'
model_name_or_path: Qwen/Qwen2-VL-7B-Instruct
stage: sft
do_train: true
finetuning_type: lora
lora_target: all
lora_rank: 8
dataset: cad_multimodal
template: qwen2_vl
cutoff_len: 1024
max_samples: 3
output_dir: ../../outputs/test_minimal
logging_steps: 1
save_steps: 100
per_device_train_batch_size: 1
gradient_accumulation_steps: 1
num_train_epochs: 1
learning_rate: 5.0e-5
bf16: true
use_habana: true
use_lazy_mode: true
overwrite_output_dir: true
EOF

# 4. Run in container
echo "Starting Docker container for minimal test..."
docker run --rm \
    --runtime=habana \
    -e HABANA_VISIBLE_DEVICES=all \
    -e PT_HPU_LAZY_MODE=1 \
    -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
    --cap-add=sys_nice \
    --net=host \
    --ipc=host \
    -v $(pwd):/workspace/gaudi-training-base \
    gaudi-training-base:latest \
    bash -c '
cd /workspace/gaudi-training-base
source configs/env.sh
cd training/llamafactory
export DATASET_DIR=../../configs/llamafactory

# Install llama-factory if needed
if ! python3 -c "import llmtuner" 2>/dev/null; then
    echo "Installing LLaMA-Factory..."
    pip install -q llmtuner[torch,metrics]
fi

echo "Running minimal training test..."
llamafactory-cli train minimal_test.yaml
'

echo ""
echo "✓ Test complete! Check outputs/test_minimal/ for results"
