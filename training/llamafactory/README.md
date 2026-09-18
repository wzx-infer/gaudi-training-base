# LLaMA-Factory 训练方案

> 🎯 **适合人群**: 初学者、快速验证、标准训练场景

## 📖 什么是 LLaMA-Factory？

[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 是一个易用的大模型微调框架，支持：
- ✅ 100+ 开源模型（Qwen、LLaVA、InternVL等）
- ✅ 多种微调方法（全参、LoRA、QLoRA）
- ✅ Web UI 可视化界面
- ✅ 零代码配置（YAML文件）

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 LLaMA-Factory
pip install llmtuner[torch,metrics]

# 或者从源码安装（推荐）
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .[torch,metrics]
```

### 2. 准备数据

数据格式使用 ShareGPT 格式（已包含样例）：

```json
{
  "messages": [
    {"role": "user", "content": "<image>\n请分析这张CAD图纸的尺寸标注"},
    {"role": "assistant", "content": "<think>\n观察图纸结构...\n</think>\n该图纸标注了..."}
  ],
  "images": ["path/to/image.jpg"]
}
```

样例数据位置: `data/examples/train_cad.jsonl`

### 3. 一键训练

```bash
cd training/llamafactory
bash train.sh
```

就这么简单！✨

---

## 📝 配置说明

### 训练配置文件: `qwen2_vl_lora.yaml`

```yaml
### 模型
model_name_or_path: Qwen/Qwen2-VL-7B-Instruct

### 方法
finetuning_type: lora
lora_rank: 64           # LoRA秩
lora_alpha: 128         # LoRA缩放
lora_dropout: 0.05      # Dropout率

### 数据集
dataset: cad_multimodal  # 使用CAD数据集
template: qwen2_vl       # Qwen2-VL模板
cutoff_len: 8192         # 最大序列长度

### 训练超参
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
learning_rate: 5.0e-5
num_train_epochs: 3.0

### 输出
output_dir: ../../outputs/models/qwen2_vl_lora
```

### 数据集配置: `configs/llamafactory/dataset_info.json`

```json
{
  "cad_multimodal": {
    "file_name": "../../data/examples/train_cad.jsonl",
    "formatting": "sharegpt"
  }
}
```

---

## 🔧 自定义训练

### 修改训练参数

编辑 `qwen2_vl_lora.yaml`:

```yaml
# 调整 LoRA 参数
lora_rank: 128           # 增大秩提升能力
lora_alpha: 256          # 相应增大alpha

# 调整学习率
learning_rate: 1.0e-4    # 更大的学习率

# 调整训练轮数
num_train_epochs: 5.0    # 更多训练轮次
```

### 使用自己的数据集

1. **准备数据文件**: `data/my_data.jsonl`

```json
{"messages": [...], "images": [...]}
{"messages": [...], "images": [...]}
```

2. **注册数据集**: 编辑 `configs/llamafactory/dataset_info.json`

```json
{
  "my_dataset": {
    "file_name": "data/my_data.jsonl",
    "formatting": "sharegpt"
  }
}
```

3. **修改训练配置**: 编辑 `qwen2_vl_lora.yaml`

```yaml
dataset: my_dataset  # 改成你的数据集名
```

4. **开始训练**

```bash
bash train.sh
```

---

## 🎨 使用 Web UI (可选)

```bash
cd LLaMA-Factory
llamafactory-cli webui
```

在浏览器打开 http://localhost:7860，通过图形界面配置训练！

---

## 📊 训练监控

### 查看训练日志

```bash
# 实时监控
tail -f ../../outputs/models/qwen2_vl_lora/trainer_log.jsonl

# 查看损失曲线（需要安装 matplotlib）
python -m llmtuner.webui.runner --plot_loss ../../outputs/models/qwen2_vl_lora
```

### TensorBoard

```bash
tensorboard --logdir=../../outputs/models/qwen2_vl_lora
```

---

## 🔄 导出和合并模型

### 导出 LoRA 适配器

训练完成后，LoRA 权重自动保存在:
```
outputs/models/qwen2_vl_lora/
├── adapter_config.json
├── adapter_model.safetensors
└── trainer_log.jsonl
```

### 合并 LoRA 到基座模型

```bash
# 方法1: 使用 LLaMA-Factory
llamafactory-cli export \
    --model_name_or_path Qwen/Qwen2-VL-7B-Instruct \
    --adapter_name_or_path ../../outputs/models/qwen2_vl_lora \
    --template qwen2_vl \
    --finetuning_type lora \
    --export_dir ../../outputs/models/qwen2_vl_merged \
    --export_size 2 \
    --export_device cpu

# 方法2: 使用项目工具
cd ../../tools
python merge_lora.py \
    --base_model Qwen/Qwen2-VL-7B-Instruct \
    --lora_path ../outputs/models/qwen2_vl_lora \
    --output_path ../outputs/models/qwen2_vl_merged
```

---

## 🆚 LLaMA-Factory vs 原生训练

| 特性 | LLaMA-Factory | 原生训练 (Native) |
|------|---------------|-------------------|
| **学习曲线** | ⭐⭐⭐⭐⭐ 极易上手 | ⭐⭐⭐ 需要深度学习基础 |
| **配置方式** | YAML文件 | Python代码 |
| **灵活性** | ⭐⭐⭐ 预设方案 | ⭐⭐⭐⭐⭐ 完全自定义 |
| **调试难度** | ⭐⭐ 封装良好 | ⭐⭐⭐⭐ 需要手动调试 |
| **适合场景** | 快速验证、标准任务 | 定制需求、研究实验 |
| **模型支持** | 100+ 开源模型 | 自己实现 |
| **Web UI** | ✅ 内置 | ❌ 无 |

**推荐策略**:
- 🎯 **入门阶段**: 用 LLaMA-Factory 快速验证想法
- 🚀 **生产部署**: 用原生训练精细调优
- 🔬 **科研实验**: 用原生训练探索前沿

---

## 🐛 常见问题

### Q1: 如何切换模型？

编辑 `qwen2_vl_lora.yaml`:
```yaml
model_name_or_path: THUDM/cogvlm2-llama3-chat-19B
template: llama3  # 对应模板
```

### Q2: 显存不够怎么办？

```yaml
# 方法1: 减小batch size
per_device_train_batch_size: 1
gradient_accumulation_steps: 16  # 增大累积步数

# 方法2: 使用更小的LoRA秩
lora_rank: 32

# 方法3: 启用梯度检查点
gradient_checkpointing: true
```

### Q3: 训练速度慢？

```yaml
# 启用混合精度
bf16: true

# 增大batch size (如果显存允许)
per_device_train_batch_size: 2

# 减少评估频率
eval_steps: 1000
```

### Q4: 如何使用全参微调？

```yaml
finetuning_type: full  # 改成 full
# 移除 lora_* 相关配置
```

---

## 📚 进一步学习

- 📖 [LLaMA-Factory 官方文档](https://github.com/hiyouga/LLaMA-Factory)
- 🎥 [B站教程视频](https://space.bilibili.com/406315614)
- 💬 [Discord 社区](https://discord.gg/llamafactory)

---

## 🎓 进阶: 切换到原生训练

当你熟悉训练流程后，可以尝试原生训练方案获得更大灵活性：

```bash
cd ../native
bash train_stage1.sh  # 两阶段训练
```

参考文档: [docs/NATIVE_TRAINING.md](../../docs/NATIVE_TRAINING.md)

---

**Happy Training! 🎉**
