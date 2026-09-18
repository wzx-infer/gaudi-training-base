# 暖通构件识别快速入门

本指南帮助你快速上手暖通构件识别任务的数据准备和训练流程。

## 🎯 任务说明

**输入**：工程图纸图像 + 文字prompt  
**输出**：`<think>推理过程</think>\n这是{构件类别}`

**支持的构件类别**：
- 风管三通
- 风管弯头
- 风管变径
- 风量调节阀
- 风管
- 风管法兰
- 防火阀
- 消声器

---

## 📋 数据准备流程

### 步骤1：准备图纸和标注

1. 收集暖通工程图纸（建议每类 ≥100张）
2. 将图纸放到 `data/images/hvac/` 目录
3. 创建CSV标注文件 `annotations.csv`：

```csv
image_name,component_type,description
hvac_tee_001.jpg,风管三通,三根管道交汇形成T型结构
hvac_elbow_001.jpg,风管弯头,管道90度转弯
hvac_reducer_001.jpg,风管变径,大小头渐变段
...
```

**CSV格式说明**：
- `image_name`: 图片文件名（相对于 `data/images/hvac/`）
- `component_type`: 构件类别（必须是上述8种之一）
- `description`: 构件描述（可选，用于生成更准确的think内容）

### 步骤2：批量生成训练数据

```bash
# 从CSV生成训练/验证数据集
python tools/build_hvac_dataset.py \
    --csv annotations.csv \
    --image_dir data/images/hvac \
    --output_dir data \
    --train_ratio 0.9

# 输出：
# - data/train/hvac_train.jsonl (训练集)
# - data/val/hvac_val.jsonl (验证集)
```

**工具会自动**：
- 验证图片是否存在
- 为每条数据生成think推理内容
- 按类别分层划分train/val
- 统计各类别分布

### 步骤3：验证数据格式

```bash
# 验证生成的数据格式
python tools/data_converter.py validate \
    --input data/train/hvac_train.jsonl

# 应该看到：
# ✅ 所有样本格式正确
# ✅ 图片路径有效
# ✅ 包含think标签
```

---

## 🚀 开始训练

### 方法1：LLaMA-Factory（推荐新手）

```bash
# 1. 环境准备
source configs/env.sh
bash scripts/verify_env.sh

# 2. 更新配置
# 编辑 configs/llamafactory/dataset_info.json
# 指向你的训练数据：data/train/hvac_train.jsonl

# 3. 一键训练
cd training/llamafactory
bash train.sh
```

### 方法2：原生训练（专业用户）

```bash
# 1. 环境准备
source configs/env.sh
bash scripts/verify_env.sh

# 2. 两阶段训练
cd training/native

# 阶段1：投影层预训练
bash train_stage1.sh

# 阶段2：LoRA指令微调
bash train_stage2.sh

# 3. 合并LoRA权重
cd ../../scripts
bash merge_lora.sh
```

---

## 📊 评估模型

训练完成后，评估模型在验证集上的表现：

```bash
python tools/evaluate_identification.py \
    --model_path outputs/models/qwen2_vl_merged \
    --val_data data/val/hvac_val.jsonl \
    --image_dir data/images/hvac \
    --output_file outputs/evaluation_results.json

# 输出：
# - 总体准确率
# - 各构件类别准确率
# - 混淆矩阵
# - 错误样本详情
```

---

## 🔍 单张推理测试

```bash
# 测试单张图片
python tools/inference_demo.py \
    --model_path outputs/models/qwen2_vl_merged \
    --image data/images/hvac/test_image.jpg \
    --prompt "请识别这个构件" \
    --parse

# 输出：
# 🧠 Think 推理:
# 观察标注位置，这是三根管道的交汇点...
#
# ✅ 识别结果:
# 这是风管三通
```

---

## 📈 数据规模建议

| 数据类型 | 最小规模 | 推荐规模 |
|---------|---------|---------|
| 总样本数 | 1000条 | 3000+条 |
| 每类样本数 | 100条 | 300+条 |
| 验证集比例 | 10% | 10-15% |

---

## ❓ 常见问题

### Q: CSV标注表示例在哪里？
A: 参考 `data/annotations_example.csv`

### Q: 如何确认图片路径正确？
A: `build_hvac_dataset.py` 会自动验证，缺失的图片会在日志中列出

### Q: 可以只训练部分构件类别吗？
A: 可以，CSV中只包含你需要的类别即可

### Q: think内容会自动生成吗？
A: 是的，工具根据构件类别自动生成think模板，也可以通过description字段定制

### Q: 训练需要多久？
A: 取决于数据量，1000条数据约2-3小时（Gaudi2 8卡）

---

## 📚 更多文档

- [数据格式详解](data/README.md)
- [完整README](README.md)
- [训练方案对比](docs/TRAINING_METHODS.md)
- [故障排查](docs/TROUBLESHOOTING.md)

---

**开始你的第一次训练吧！** 🚀
