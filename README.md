# Gaudi2 多模态大模型训练底座

<div align="center">

**🚀 两阶段训练框架 | 🎯 双训练方案 | 📦 开箱即用**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Gaudi](https://img.shields.io/badge/Gaudi2-8%20Cards-orange.svg)](https://habana.ai/)

[快速开始](#-快速开始) • [文档导航](#-文档导航) • [训练方案](#-训练方案) • [项目结构](#-项目结构)

</div>

---

## 📖 项目简介

基于 **Intel Gaudi2 8卡**的多模态大模型训练底座工程，支持 Qwen2-VL、LLaVA、InternVL 等主流多模态模型的高效训练。

### ✨ 核心特性

- **🎯 双训练方案**
  - **LLaMA-Factory**: 小白友好，开箱即用，3行命令启动训练
  - **原生训练**: 专业可控，两阶段训练，支持深度定制

- **⚡ Gaudi2 优化**
  - DeepSpeed ZeRO-2 优化，支持8卡分布式
  - Lazy模式 + 算子融合 + 通信重叠
  - 混合精度训练 (BF16)

- **🧠 Think 范式**
  - 训练可解释 AI，让模型学会推理
  - 支持 `<think>` 标签的思维链训练

- **🛠️ 工程化完备**
  - Docker 容器化部署
  - 一键训练脚本
  - 自动化监控和日志

---

## 🚀 快速开始

### 方法1: LLaMA-Factory (推荐新手)

```bash
# 1. 环境准备
source configs/env.sh
bash scripts/verify_env.sh

# 2. 准备数据 (使用样例数据测试)
# 数据已在 data/examples/train_cad.jsonl

# 3. 一键训练
cd training/llamafactory
bash train.sh
```

**就这么简单！** ✨ 训练会自动开始，模型保存在 `outputs/models/`

### 方法2: 原生训练 (专业用户)

```bash
# 1. 环境准备
source configs/env.sh
bash scripts/verify_env.sh

# 2. 两阶段训练
cd training/native

# 阶段1: 投影层预训练
bash train_stage1.sh

# 阶段2: LoRA 指令微调
bash train_stage2.sh

# 3. 合并 LoRA 权重
cd ../../scripts
bash merge_lora.sh
```

---

## 📚 文档导航

### 🎯 我该看哪个文档？

| 你的情况 | 推荐文档 | 说明 |
|---------|---------|------|
| **第一次使用** | [快速开始](docs/QUICKSTART.md) | 3分钟上手 |
| **小白用户** | [LLaMA-Factory教程](training/llamafactory/README.md) | 零代码训练 |
| **专业用户** | [原生训练指南](docs/NATIVE_TRAINING.md) | 深度定制 |
| **准备数据** | [数据准备指南](data/README.md) | 格式转换和验证 |
| **项目总览** | [项目总结](docs/SUMMARY.md) | 5分钟了解全貌 |
| **完整手册** | [完整文档](docs/README.md) | 详细说明 |

### 📂 所有文档

```
docs/
├── README.md                   # 完整使用手册
├── QUICKSTART.md              # 快速开始指南
├── SUMMARY.md                 # 项目总结
├── NATIVE_TRAINING.md         # 原生训练详解
├── README_NAVIGATION.md       # 文档导航
└── ...                        # 其他文档

training/
├── llamafactory/README.md     # LLaMA-Factory 教程
└── native/                    # 原生训练代码

data/README.md                 # 数据准备指南
```

---

## 🎯 训练方案

### 方案对比

| 特性 | LLaMA-Factory | 原生训练 |
|------|---------------|----------|
| **学习曲线** | ⭐⭐⭐⭐⭐ 极易上手 | ⭐⭐⭐ 需要基础 |
| **配置方式** | YAML 文件 | Python 代码 |
| **灵活性** | ⭐⭐⭐ 预设方案 | ⭐⭐⭐⭐⭐ 完全自定义 |
| **模型支持** | 100+ 开源模型 | 自己实现 |
| **Web UI** | ✅ 内置 | ❌ 无 |
| **适合场景** | 快速验证、标准任务 | 定制需求、研究实验 |

### 推荐策略

- 🎯 **入门阶段**: LLaMA-Factory 快速验证
- 🚀 **生产部署**: 原生训练精细调优
- 🔬 **科研实验**: 原生训练探索前沿

---

## 📁 项目结构

```
gaudi-training-base/
├── training/                    # 训练核心
│   ├── llamafactory/           # LLaMA-Factory 方案
│   │   ├── qwen2_vl_lora.yaml # 训练配置
│   │   ├── train.sh           # 一键训练
│   │   └── README.md          # 详细教程
│   └── native/                 # 原生训练方案
│       ├── train_qwen_multimodal.py
│       ├── train_stage1.sh
│       └── train_stage2.sh
├── configs/                     # 配置文件
│   ├── deepspeed_z2.json       # DeepSpeed 配置
│   ├── env.sh                  # 环境变量
│   └── llamafactory/
│       └── dataset_info.json   # 数据集配置
├── docker/                      # Docker 相关
│   ├── Dockerfile
│   ├── build.sh
│   └── run.sh
├── scripts/                     # 自动化脚本
│   ├── verify_env.sh           # 环境检查
│   ├── merge_lora.sh           # 权重合并
│   └── monitor.sh              # 训练监控
├── tools/                       # 工具脚本
│   ├── merge_lora.py           # LoRA 合并工具
│   └── data_converter.py       # 数据格式转换
├── data/                        # 数据目录
│   ├── examples/               # 样例数据
│   │   └── train_cad.jsonl
│   └── README.md               # 数据准备指南
├── outputs/                     # 训练输出 (gitignore)
│   ├── models/                 # 模型权重
│   ├── logs/                   # 训练日志
│   └── checkpoints/            # 检查点
└── docs/                        # 文档
    ├── README.md               # 完整手册
    ├── QUICKSTART.md
    └── ...
```

---

## 🔧 环境要求

### 硬件
- **Intel Gaudi2** 8卡
- **内存**: 512GB+ 推荐
- **存储**: 500GB+ SSD

### 软件
- **OS**: Ubuntu 20.04/22.04
- **Python**: 3.10+
- **Habana SDK**: 1.17.0+
- **PyTorch**: 2.3.0+

### 依赖安装

```bash
# 安装 Habana SDK (如果还没安装)
# 参考: https://docs.habana.ai/

# 安装 Python 依赖
pip install -r requirements.txt

# LLaMA-Factory (可选)
pip install llmtuner[torch,metrics]
```

---

## 📊 训练监控

### 实时监控

```bash
# 查看训练状态
bash scripts/monitor.sh

# 实时日志
tail -f outputs/logs/train_*.log

# Gaudi 状态
hl-smi

# TensorBoard
tensorboard --logdir=outputs/models
```

### Web UI (LLaMA-Factory)

```bash
llamafactory-cli webui
# 访问 http://localhost:7860
```

---

## 🎓 使用教程

### 1. 准备你的数据

参考 [data/README.md](data/README.md) 准备 ShareGPT 格式数据：

```json
{
  "messages": [
    {"role": "user", "content": "<image>\n你的问题"},
    {"role": "assistant", "content": "<think>\n推理过程\n</think>\n答案"}
  ],
  "images": ["path/to/image.jpg"]
}
```

### 2. 选择训练方案

**新手?** → [LLaMA-Factory 教程](training/llamafactory/README.md)

**专业用户?** → [原生训练指南](docs/NATIVE_TRAINING.md)

### 3. 开始训练

```bash
# LLaMA-Factory
cd training/llamafactory && bash train.sh

# 或原生训练
cd training/native && bash train_stage1.sh
```

### 4. 评估和部署

```bash
# 合并 LoRA 权重
bash scripts/merge_lora.sh

# 模型推理测试
python tools/inference_test.py
```

---

## 🐛 故障排查

### 常见问题

**Q: 训练启动失败？**
```bash
# 检查环境
bash scripts/verify_env.sh

# 查看日志
cat outputs/logs/latest.log
```

**Q: 显存不足？**
```yaml
# 减小 batch size
per_device_train_batch_size: 1
gradient_accumulation_steps: 16
```

**Q: 数据格式错误？**
```bash
# 验证数据
python tools/data_converter.py validate --input your_data.jsonl
```

更多问题参考: [FAQ文档](docs/FAQ.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发规范
- 遵循 PEP 8 代码风格
- 添加单元测试
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Intel Habana](https://habana.ai/) - Gaudi2 硬件支持
- [Qwen Team](https://github.com/QwenLM/Qwen2-VL) - 多模态基座模型
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) - 训练框架
- [DeepSpeed](https://www.deepspeed.ai/) - 分布式训练优化

---

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/wzx-infer/gaudi-training-base/issues)
- **讨论**: [GitHub Discussions](https://github.com/wzx-infer/gaudi-training-base/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ for Gaudi2 Community

</div>
