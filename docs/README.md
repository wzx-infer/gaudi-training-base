# Gaudi2 8卡多模态大模型训练底座

面向CAD图纸识图的多模态大模型训练工程，支持图像+文本输入，输出think思维链+识别结果。

## 硬件环境

- **硬件**: Intel Gaudi2 8卡集群
- **基础镜像**: `vault.habana.ai/gaudi-docker/1.24.1/ubuntu24.04/habanalabs/pytorch-installer-2.11.0:latest`
  - Synapse AI 1.24.1
  - Habana PyTorch 2.11.0（Lazy模式训练专用）
- **通信链路**: HCCL多卡通信已验证

## 核心特性

✅ **基座无关设计**: 以Qwen2.5-VL-7B为示例，预留替换入口，支持其他多模态大模型  
✅ **两阶段训练**: 投影层预训练 + LoRA指令微调  
✅ **think输出范式**: 强制模型输出推理过程+识别结果  
✅ **Lazy模式优化**: 图编译、算子融合、计算通信重叠  
✅ **DeepSpeed ZeRO-2**: 8卡高效分布式训练  
✅ **CPU侧预处理**: 图像处理不占用HPU算力  

---

## 快速开始

### 1. 构建Docker镜像

```bash
cd gaudi-training-base
docker build -t gaudi-multimodal-train:1.24.1 .
```

### 2. 启动容器

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

**目录挂载说明**:
- `/workspace/gaudi-training-base`: 工程代码目录
- `/models`: 预下载的基座模型权重
- `/data`: 训练数据集（包含图像和JSONL标注）
- `/output`: 训练输出（checkpoints、日志、TensorBoard）

### 3. 加载环境变量

```bash
source env.sh
```

输出确认：
```
✓ Gaudi2 训练环境变量已加载
  - PT_HPU_LAZY_MODE: 1
  - PT_HPU_ENABLE_LAZY_COLLECTIVES: true
  - HABANA_VISIBLE_DEVICES: all
```

---

## 数据准备

### 数据集格式

将训练数据放置在 `data/` 目录：

```
data/
├── train_cad.jsonl          # 标注文件
└── images/                  # 图像文件夹
    ├── cad_drawing_001.jpg
    ├── cad_drawing_002.jpg
    └── ...
```

### JSONL格式示例

遵循Qwen多模态对话格式，固化think输出范式：

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "cad_drawing_001.jpg"},
        {"type": "text", "text": "这张CAD图纸展示了什么机械部件？"}
      ]
    },
    {
      "role": "assistant",
      "content": "<think>首先观察图纸整体布局，识别视图类型...</think>\n\n这是一个法兰盘零件，外径Φ120mm..."
    }
  ]
}
```

**关键要求**:
- assistant回复必须以 `<think>...</think>` 开头，包含推理过程
- think标签后跟识别结果

---

## 训练方式

### 方式A：optimum-habana指令化训练（快速验证）

适用于快速验证训练链路，最小化自定义代码。

#### 阶段1：投影层预训练

```bash
deepspeed --num_gpus 8 --num_nodes 1 \
  --use_hpu \
  --hostfile /tmp/hostfile \
  $(which gaudi_spawn) \
  --world_size 8 \
  --use_deepspeed \
  $(python -c "from optimum.habana.transformers import GaudiTrainer; print(GaudiTrainer.__file__.replace('__init__.py', 'training_args.py'))") \
  --model_name_or_path Qwen/Qwen2.5-VL-7B-Instruct \
  --data_path data/train_cad.jsonl \
  --image_folder data/images \
  --output_dir output/stage1_projector \
  --num_train_epochs 3 \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 4 \
  --learning_rate 1e-3 \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 10 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --bf16 true \
  --deepspeed ds_config_gaudi_z2.json \
  --use_lazy_mode true \
  --use_hpu_graphs true
```

#### 阶段2：LoRA指令微调

```bash
deepspeed --num_gpus 8 --num_nodes 1 \
  --use_hpu \
  --use_deepspeed \
  $(which gaudi_spawn) \
  --world_size 8 \
  <训练脚本> \
  --model_name_or_path Qwen/Qwen2.5-VL-7B-Instruct \
  --data_path data/train_cad.jsonl \
  --image_folder data/images \
  --output_dir output/stage2_lora \
  --num_train_epochs 5 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 10 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --bf16 true \
  --deepspeed ds_config_gaudi_z2.json \
  --use_lazy_mode true \
  --lora_r 64 \
  --lora_alpha 128
```

---

### 方式B：Python训练脚本（完整可控）

使用 `train_qwen_multimodal.py` 进行两阶段训练。

#### 阶段1：投影层预训练

```bash
deepspeed --num_gpus 8 --num_nodes 1 \
  --hostfile /tmp/hostfile \
  train_qwen_multimodal.py \
  --model_name_or_path Qwen/Qwen2.5-VL-7B-Instruct \
  --data_path data/train_cad.jsonl \
  --image_folder data/images \
  --stage 1 \
  --output_dir output/stage1_projector \
  --num_train_epochs 3 \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 4 \
  --learning_rate 1e-3 \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 10 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --bf16 true \
  --deepspeed ds_config_gaudi_z2.json \
  --ddp_timeout 3600 \
  --dataloader_num_workers 4 \
  --remove_unused_columns false \
  --report_to tensorboard
```

#### 阶段2：LoRA指令微调

```bash
deepspeed --num_gpus 8 --num_nodes 1 \
  --hostfile /tmp/hostfile \
  train_qwen_multimodal.py \
  --model_name_or_path Qwen/Qwen2.5-VL-7B-Instruct \
  --data_path data/train_cad.jsonl \
  --image_folder data/images \
  --stage 2 \
  --output_dir output/stage2_lora \
  --num_train_epochs 5 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --learning_rate 2e-4 \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 10 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --bf16 true \
  --deepspeed ds_config_gaudi_z2.json \
  --ddp_timeout 3600 \
  --dataloader_num_workers 4 \
  --remove_unused_columns false \
  --lora_r 64 \
  --lora_alpha 128 \
  --lora_dropout 0.05 \
  --lora_target_modules q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj \
  --report_to tensorboard
```

---

## 训练监控

### 硬件监控

实时查看8卡HPU利用率：

```bash
watch -n 1 hl-smi
```

输出示例：
```
+-----------------------------------------------------------------------------+
| HL-SMI Version:                              hl-1.24.1-fw-51.5.0           |
| Driver Version:                                     1.24.1-3bf9e81          |
|-------------------------------+----------------------+----------------------+
| AIP  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | AIP-Util  Compute M. |
|===============================+======================+======================|
|   0  HL-225              N/A  | 0000:12:00.0     N/A |                   0 |
| N/A   45C   N/A    85W / 600W |  78000MiB / 98304MiB |     95%      Default |
|-------------------------------+----------------------+----------------------+
...
```

### TensorBoard可视化

```bash
tensorboard --logdir output/stage2_lora/runs --port 6006 --bind_all
```

浏览器访问: `http://<节点IP>:6006`

监控指标：
- `train/loss`: 训练损失曲线
- `train/learning_rate`: 学习率调度
- `train/grad_norm`: 梯度范数
- `train/epoch`: 训练进度

---

## 权重合并

训练完成后，将LoRA适配器合并回基座模型：

```bash
python merge_lora.py \
  --base_model Qwen/Qwen2.5-VL-7B-Instruct \
  --lora_adapter output/stage2_lora/checkpoint-final \
  --output output/merged_model
```

输出：
```
✅ LoRA权重合并完成！
   完整模型路径: output/merged_model
   可直接用于推理或继续训练
```

---

## 基座模型替换

工程设计为基座无关，替换其他多模态大模型只需修改以下参数：

### 1. 修改模型路径

在训练命令中替换 `--model_name_or_path`:

```bash
# 示例：替换为LLaVA
--model_name_or_path liuhaotian/llava-v1.6-vicuna-7b

# 示例：替换为Qwen2-VL
--model_name_or_path Qwen/Qwen2-VL-7B-Instruct

# 示例：替换为InternVL
--model_name_or_path OpenGVLab/InternVL2-8B
```

### 2. 调整数据格式

不同模型的对话格式可能不同，需修改 `train_qwen_multimodal.py` 中的：

```python
# 第85-95行：MultimodalCADDataset.__getitem__
# 根据目标模型的prompt template调整
conversation = [
    {"role": "user", "content": [...]},
    {"role": "assistant", "content": assistant_message}
]
text = self.processor.apply_chat_template(conversation, ...)
```

### 3. 调整LoRA目标模块

不同架构的注意力层命名不同：

```bash
# Qwen系列
--lora_target_modules q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj

# LLaMA系列
--lora_target_modules q_proj,k_proj,v_proj,o_proj

# Mistral系列
--lora_target_modules q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj
```

### 4. 调整超参数

根据模型规模调整batch size和学习率：

| 模型规模 | batch_size | grad_accum | learning_rate |
|---------|-----------|-----------|--------------|
| 7B      | 2         | 4         | 1e-3 / 2e-4  |
| 13B     | 1         | 8         | 8e-4 / 1e-4  |
| 27B+    | 1         | 16        | 5e-4 / 5e-5  |

---

## Lazy模式说明

### 为什么必须使用Lazy模式？

Gaudi2的Lazy模式是大模型分布式训练的核心优化：

1. **图编译优化**: 将整个计算图编译后整体下发硬件，实现算子融合、显存布局优化
2. **计算通信重叠**: 启用 `PT_HPU_ENABLE_LAZY_COLLECTIVES=true` 后，HCCL通信与计算并行执行
3. **显存高效**: 静态图分析减少中间Tensor生命周期，相比Eager模式节省30%+显存

### Eager模式的局限

- **仅用于单卡调试**: 动态图逐算子执行，方便断点调试
- **多卡训练吞吐低**: 无法重叠通信，8卡加速比<4x
- **不推荐正式训练**: 显存占用高，训练速度慢

### Lazy模式关键点

```bash
# env.sh中已配置
export PT_HPU_LAZY_MODE=1                    # 启用Lazy图模式
export PT_HPU_ENABLE_LAZY_COLLECTIVES=true   # 通信计算重叠
```

训练代码中需在每个step后调用：

```python
import habana_frameworks.torch.core as htcore

# 前向+反向传播后
loss.backward()
htcore.mark_step()  # 标记图边界，触发编译下发
```

---

## 常见问题排查

### 1. HCCL通信超时

**现象**:
```
RuntimeError: HCCL_TIMEOUT: Communication timeout after 1800000ms
```

**解决**:
```bash
# 增加超时时间
export HCCL_TIMEOUT=3600

# 检查网络连通性
ibstat
ifconfig

# 确认HCCL环境变量
export HCCL_OVER_TCP=1
export HCCL_SOCKET_IFNAME=eth0  # 替换为实际网卡名
```

### 2. Lazy图重复编译

**现象**:
```
[Warning] Dynamic shape detected, recompiling graph...
```

**原因**: 输入shape变化导致图重新编译（首次编译耗时30s-2min）

**解决**:
```bash
# 固定输入shape
--max_length 2048  # 统一padding长度
--dataloader_drop_last true  # 丢弃不足batch

# 减少shape变化
export PT_HPU_ENABLE_REFINE_DYNAMIC_SHAPES=0
```

### 3. HPU显存OOM

**现象**:
```
RuntimeError: HabanaOutOfMemoryError: Device out of memory
```

**解决**:
```bash
# 减小batch size
--per_device_train_batch_size 1
--gradient_accumulation_steps 16

# 启用梯度检查点
--gradient_checkpointing true

# 降低序列长度
--max_length 1024
```

### 4. DeepSpeed初始化失败

**现象**:
```
AssertionError: [deepspeed] 'ds_accelerator' not found
```

**解决**:
```bash
# 确认环境变量
export DS_ACCELERATOR=hpu

# 验证DeepSpeed版本
pip show deepspeed | grep habana
```

### 5. 图像加载错误

**现象**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/images/xxx.jpg'
```

**解决**:
```bash
# 检查图像路径
ls data/images/*.jpg

# 验证JSONL中的image字段路径
cat data/train_cad.jsonl | jq '.messages[0].content[] | select(.type=="image") | .image'

# 确保相对路径正确
--image_folder data/images  # 相对于工程根目录
```

---

## 项目结构

```
gaudi-training-base/
├── Dockerfile                    # Docker镜像构建文件
├── env.sh                        # 训练环境变量脚本
├── ds_config_gaudi_z2.json       # DeepSpeed ZeRO-2配置
├── train_qwen_multimodal.py      # Python训练脚本（方式B）
├── merge_lora.py                 # LoRA权重合并脚本
├── data/
│   ├── train_cad.jsonl           # 样例数据集
│   └── images/                   # 图像文件夹
├── output/                       # 训练输出目录
│   ├── stage1_projector/         # 阶段1 checkpoints
│   ├── stage2_lora/              # 阶段2 checkpoints
│   └── merged_model/             # 合并后的完整模型
└── README.md                     # 本文档
```

---

## 依赖版本

| 组件 | 版本 | 说明 |
|-----|------|-----|
| Synapse AI | 1.24.1 | Gaudi硬件驱动 |
| Habana PyTorch | 2.11.0 | Lazy模式训练专用 |
| optimum-habana | 1.24.1 | Hugging Face Gaudi适配 |
| transformers | 4.48.2 | 模型库 |
| peft | 0.11.1 | LoRA库 |
| accelerate | 0.31.0 | 分布式训练 |
| DeepSpeed | @1.24.1 | Habana分支 |

---

## 手动Git操作脚本

训练完成后，可使用以下脚本初始化Git仓库并推送到GitHub：

```bash
#!/bin/bash
# save as: init_and_push.sh

set -e

echo "🚀 初始化Git仓库..."
git init
git add .
git commit -m "feat: Gaudi2 8卡多模态大模型训练底座

- 支持Qwen2.5-VL-7B作为示例基座
- 两阶段训练：投影层预训练 + LoRA指令微调
- DeepSpeed ZeRO-2 分布式训练
- Lazy模式优化，计算通信重叠
- CAD图纸识图任务，think输出范式

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"

echo "📦 创建GitHub仓库..."
gh repo create gaudi-training-base \
  --public \
  --source=. \
  --description="Gaudi2 8-Card Multimodal LLM Training Base for CAD Drawing Recognition" \
  --remote=origin

echo "⬆️ 推送代码到GitHub..."
git branch -M main
git push -u origin main

echo "✅ 完成！仓库地址："
gh repo view --web
```

**使用方法**:

```bash
chmod +x init_and_push.sh
./init_and_push.sh
```

**前置要求**:
- 已安装 `gh` CLI: `sudo apt install gh` 或从 https://cli.github.com/ 下载
- 已登录GitHub: `gh auth login`

---

## 许可证

MIT License

---

## 联系方式

- 问题反馈: 在GitHub仓库提Issue
- 技术交流: 参考Habana官方文档 https://docs.habana.ai/

---

**🎯 训练目标**: 让模型学会像工程师一样思考，先推理（think）再输出识别结果！
