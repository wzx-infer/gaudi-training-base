# MechVQA 多模态训练项目计划

## 📊 数据集信息

**MechVQA Dataset** - 机械工程图纸视觉问答数据集
- **训练集**: 12,749 样本
- **验证集**: 766 样本
- **任务类型**: 机械图纸理解 + VQA
- **数据格式**: 
  ```json
  {
    "images": ["images/xxx.png"],
    "messages": [
      {"role": "user", "content": "<image>问题..."},
      {"role": "assistant", "content": "<think>推理...</think><answer>答案</answer>"}
    ],
    "metadata": {
      "capability": "Recognition/Judging",
      "difficulty": "Easy/Medium/Hard",
      "question_type": "VQA",
      "subcategory": "Dimension & Annotation/Consistency Judgment/..."
    }
  }
  ```

## 🎯 任务目标

### 任务1: 双训练方案验证 ✅
- [x] LLaMA-Factory CLI 训练（已在demo上验证通过）
- [ ] DeepSpeed 手写代码训练（待实现）

### 任务2: MechVQA SFT 训练
**对比目标**: [MechVL-4B-SFT](https://modelscope.cn/models/xiaofengalg/MechVL-4B-SFT)

#### 2.1 Baseline评估（不训练）
- [ ] 使用 Qwen3.8-27B 原始模型直接推理验证集
- [ ] 计算基准指标：Accuracy, F1, BLEU等
- [ ] 保存baseline结果

#### 2.2 SFT训练
- [ ] 转换MechVQA数据为LLaMA-Factory格式
- [ ] 配置训练参数（LoRA + DeepSpeed ZeRO-2）
- [ ] 训练Qwen3.8-27B（12749样本）
- [ ] 保存checkpoint和LoRA权重

#### 2.3 SFT评估
- [ ] 推理验证集（766样本）
- [ ] 计算训练后指标
- [ ] 对比 Baseline vs SFT vs MechVL-4B-SFT

#### 2.4 可视化展示
- [ ] Loss曲线（training loss + validation loss）
- [ ] 评估指标曲线（Accuracy, F1等）
- [ ] 样例对比（Before/After训练）
- [ ] 更新README展示结果

### 任务3: 全链路打通
```
data/ (MechVQA)
  ↓
training/ (LLaMA-Factory + Native)
  ↓
evaluation/ (推理 + 指标计算)
  ↓
results/ (训练日志 + 可视化)
```

- [ ] training/: 两种训练方案
- [ ] evaluation/: 自动评估脚本
- [ ] results/: 结构化结果记录
- [ ] README.md: 完整文档更新

### 任务4: RL训练（可选）
**对比目标**: [MechVL-4B-RL](https://modelscope.cn/models/xiaofengalg/MechVL-4B-RL)
- [ ] 基于SFT模型做强化学习
- [ ] 对比 SFT vs RL vs MechVL-4B-RL

---

## 📁 项目结构设计

```
gaudi-training-base/
├── docker/                     # ✅ 已完成
│   ├── Dockerfile
│   ├── deploy.sh
│   └── verify_env.sh
│
├── data/                       # 数据准备
│   ├── mechvqa/
│   │   ├── raw/               # 原始数据
│   │   │   ├── train.jsonl    # 12749
│   │   │   └── val.jsonl      # 766
│   │   ├── converted/         # LLaMA-Factory格式
│   │   │   ├── train.json
│   │   │   └── val.json
│   │   └── images/            # 图片（从modelscope下载）
│   └── download_mechvqa.py    # 数据下载脚本
│
├── training/                   # 训练模块
│   ├── llamafactory/
│   │   ├── configs/
│   │   │   ├── mechvqa_sft.yaml      # SFT训练配置
│   │   │   └── mechvqa_rl.yaml       # RL训练配置
│   │   ├── train_sft.sh
│   │   └── train_rl.sh
│   │
│   └── native/                # DeepSpeed原生训练
│       ├── train_mechvqa.py
│       ├── train_mechvqa.sh
│       └── deepspeed_config.json
│
├── evaluation/                 # 评估模块
│   ├── evaluate_mechvqa.py    # 主评估脚本
│   ├── metrics/
│   │   ├── accuracy.py
│   │   ├── bleu.py
│   │   └── f1.py
│   ├── inference.py           # 批量推理
│   └── visualize.py           # 可视化工具
│
├── results/                    # 结果记录
│   ├── baseline/              # Baseline结果
│   │   ├── predictions.json
│   │   └── metrics.json
│   ├── sft/                   # SFT结果
│   │   ├── training_logs/
│   │   ├── checkpoints/
│   │   ├── predictions.json
│   │   ├── metrics.json
│   │   └── visualizations/    # Loss曲线图等
│   └── rl/                    # RL结果（可选）
│
└── README.md                   # 更新完整文档
```

---

## 🚀 实施步骤

### Step 1: 数据准备（今天）
1. 下载MechVQA图片
2. 转换数据格式为LLaMA-Factory兼容
3. 验证数据加载

### Step 2: Baseline评估（今天）
1. 实现评估脚本
2. Qwen3.8-27B直接推理验证集
3. 保存baseline结果

### Step 3: SFT训练（明天）
1. 配置LLaMA-Factory训练参数
2. 启动SFT训练（~2-4小时）
3. 监控训练过程

### Step 4: SFT评估与可视化（明天）
1. 评估训练后模型
2. 生成对比结果
3. 可视化展示

### Step 5: Native训练方案（明天）
1. 实现DeepSpeed原生训练脚本
2. 验证训练效果

### Step 6: 文档更新（明天）
1. 更新README
2. 添加结果展示
3. 完整流程文档

---

## 📈 评估指标

### 主要指标
- **Accuracy**: 答案完全匹配比例
- **BLEU**: 答案文本相似度
- **F1 Score**: Token级别F1
- **Think Chain Quality**: 推理链完整性

### 分类指标
- 按难度分层：Easy/Medium/Hard
- 按能力分类：Recognition/Judging
- 按子类别：Dimension & Annotation/Consistency Judgment等

---

## ⏱️ 时间估算

- **数据准备**: 1-2小时
- **Baseline评估**: 1小时（766样本推理）
- **SFT训练**: 2-4小时（12749样本，8卡Gaudi2）
- **SFT评估**: 1小时
- **可视化与文档**: 2小时
- **Native训练方案**: 3-4小时

**总计**: 1-2天完成核心任务

---

## 🎯 成功标准

1. ✅ 双训练方案都能正常运行
2. ✅ Baseline和SFT结果对比清晰
3. ✅ 训练曲线完整记录
4. ✅ README展示图文并茂的结果
5. ✅ 训练→评估→结果全链路打通
