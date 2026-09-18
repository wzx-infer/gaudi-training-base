# 快速启动指南

## 一键启动训练

### 1. 环境准备

```bash
# 加载环境变量
source env.sh

# 验证环境（可选但推荐）
bash scripts/verify_env.sh
```

### 2. 数据准备

将你的CAD图纸数据按以下格式组织：

```
data/
├── train_cad.jsonl    # 标注文件
└── images/            # 图像文件夹
    ├── drawing_001.jpg
    ├── drawing_002.jpg
    └── ...
```

**JSONL格式示例**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "drawing_001.jpg"},
        {"type": "text", "text": "识别这张CAD图纸"}
      ]
    },
    {
      "role": "assistant",
      "content": "<think>观察图纸布局，这是三视图...</think>\n\n这是一个轴类零件..."
    }
  ]
}
```

### 3. 开始训练

**阶段1：投影层预训练（3 epochs，~2-4小时）**
```bash
bash scripts/train_stage1.sh
```

训练参数：
- Batch size: 2 × 4梯度累积 = 8 effective batch
- Learning rate: 1e-3
- 训练目标：对齐视觉特征与LLM空间

**阶段2：LoRA指令微调（5 epochs，~4-8小时）**
```bash
bash scripts/train_stage2.sh
```

训练参数：
- Batch size: 1 × 8梯度累积 = 8 effective batch
- Learning rate: 2e-4
- LoRA秩: 64
- 训练目标：学习think推理+识别能力

### 4. 合并权重

```bash
python merge_lora.py \
  --base_model Qwen/Qwen2.5-VL-7B-Instruct \
  --lora_adapter output/stage2_lora/checkpoint-final \
  --output output/merged_model
```

### 5. 监控训练

**终端1：实时硬件监控**
```bash
watch -n 1 hl-smi
```

**终端2：TensorBoard可视化**
```bash
tensorboard --logdir output/stage2_lora/logs --port 6006 --bind_all
```

访问: `http://<服务器IP>:6006`

---

## 自定义配置

### 调整训练超参数

编辑 `scripts/train_stage1.sh` 或 `scripts/train_stage2.sh`:

```bash
# 修改epoch数
--num_train_epochs 5

# 调整batch size（显存不足时减小）
--per_device_train_batch_size 1
--gradient_accumulation_steps 16

# 调整学习率
--learning_rate 5e-4

# 启用梯度检查点（节省显存）
--gradient_checkpointing true
```

### 切换基座模型

修改脚本中的 `MODEL_PATH`:

```bash
# 使用LLaVA
MODEL_PATH="liuhaotian/llava-v1.6-vicuna-7b"

# 使用InternVL
MODEL_PATH="OpenGVLab/InternVL2-8B"

# 使用Qwen2-VL
MODEL_PATH="Qwen/Qwen2-VL-7B-Instruct"
```

⚠️ **注意**: 不同模型可能需要调整数据预处理格式。

### 调整LoRA配置

在 `scripts/train_stage2.sh` 中修改：

```bash
# 增加LoRA秩（更强表达能力，更多显存）
LORA_R=128
LORA_ALPHA=256

# 调整目标模块（根据模型架构）
LORA_TARGET_MODULES="q_proj,k_proj,v_proj,o_proj"
```

---

## Docker使用

### 构建镜像

```bash
docker build -t gaudi-multimodal-train:1.24.1 .
```

### 启动容器

```bash
bash scripts/run_container.sh
```

或手动启动：

```bash
docker run -it --rm \
  --runtime=habana \
  -e HABANA_VISIBLE_DEVICES=all \
  -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
  --cap-add=sys_nice \
  --net=host \
  --ipc=host \
  -v $(pwd):/workspace/gaudi-training-base \
  -v /path/to/models:/models \
  -v /path/to/data:/data \
  -v /path/to/output:/output \
  gaudi-multimodal-train:1.24.1
```

进入容器后：

```bash
cd /workspace/gaudi-training-base
source env.sh
bash scripts/verify_env.sh
bash scripts/train_stage1.sh
```

---

## 常见问题

### Q1: 训练卡在"Compiling graph"

**原因**: 首次训练会编译计算图，耗时30s-2min

**解决**: 等待编译完成，后续step会复用缓存

### Q2: HCCL通信超时

```bash
# 增加超时时间
export HCCL_TIMEOUT=3600

# 检查网络
ibstat
ifconfig
```

### Q3: HPU显存不足

```bash
# 减小batch size
--per_device_train_batch_size 1
--gradient_accumulation_steps 16

# 启用梯度检查点
--gradient_checkpointing true

# 降低序列长度
--max_length 1024
```

### Q4: 训练loss不下降

- 检查数据格式是否正确
- 确认think标签完整闭合
- 尝试降低学习率
- 增加warmup比例

### Q5: 输出没有think标签

- 检查训练数据中所有assistant回复是否都包含 `<think>...</think>`
- 确认tokenizer没有过滤特殊标签
- 增加训练epoch数

---

## 训练时间估算

基于8卡Gaudi2，1000条样本：

| 阶段 | Epochs | Batch Size | 预计时长 |
|-----|--------|-----------|---------|
| 阶段1 | 3 | 2×4 | 2-4小时 |
| 阶段2 | 5 | 1×8 | 4-8小时 |

实际时间取决于：
- 图像分辨率
- 序列长度
- 网络延迟
- 首次图编译（一次性开销）

---

## 下一步

✅ 训练完成后，你可以：

1. **模型评估**: 编写推理脚本验证think输出质量
2. **部署推理**: 使用vLLM/TGI在GPU上部署（Gaudi推理待支持）
3. **继续训练**: 基于merged_model继续微调更多数据
4. **模型量化**: 转换为INT8/FP8降低推理成本

---

**🎯 目标**: 让模型像工程师一样先思考（think）再输出结果！
