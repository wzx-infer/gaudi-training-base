# Gaudi2 8卡多模态大模型训练底座 - 完整文件清单

## 📁 项目文件树

```
gaudi-training-base/
│
├── 📖 文档
│   ├── README.md                       # 完整使用文档（训练流程、监控、排错）
│   ├── QUICKSTART.md                   # 快速启动指南（一键训练）
│   ├── PROJECT_STRUCTURE.md            # 项目结构说明
│   └── FILE_MANIFEST.md                # 本文件（完整清单）
│
├── 🐳 Docker环境
│   ├── Dockerfile                      # 基于Habana 1.24.1镜像
│   └── env.sh                          # 训练环境变量（Lazy模式等）
│
├── ⚙️ 训练配置
│   └── ds_config_gaudi_z2.json         # DeepSpeed ZeRO Stage2配置
│
├── 🎯 核心训练脚本
│   ├── train_qwen_multimodal.py        # 两阶段训练主脚本
│   └── merge_lora.py                   # LoRA权重合并工具
│
├── 📊 数据集
│   └── data/
│       ├── train_cad.jsonl             # CAD图纸标注样例（think范式）
│       └── images/                     # 图像文件夹（需自行准备）
│
├── 🚀 自动化脚本
│   └── scripts/
│       ├── train_stage1.sh             # 阶段1训练启动脚本
│       ├── train_stage2.sh             # 阶段2训练启动脚本
│       ├── run_container.sh            # Docker容器启动脚本
│       ├── verify_env.sh               # 环境验证脚本
│       └── init_and_push.sh            # Git初始化与推送脚本
│
├── 📂 输出目录
│   └── outputs/                        # 训练输出（需手动创建或训练时自动创建）
│       ├── stage1_projector/           # 阶段1 checkpoints
│       ├── stage2_lora/                # 阶段2 checkpoints + logs
│       └── merged_model/               # 合并后的完整模型
│
└── 🚫 .gitignore                       # Git忽略规则
```

---

## 📄 核心文件说明

### 1. 训练脚本

| 文件 | 大小 | 功能 |
|-----|------|-----|
| `train_qwen_multimodal.py` | ~600行 | 两阶段训练逻辑，支持基座替换 |
| `merge_lora.py` | ~100行 | LoRA适配器合并回基座模型 |

### 2. 配置文件

| 文件 | 功能 |
|-----|------|
| `env.sh` | 设置PT_HPU_LAZY_MODE、HCCL等环境变量 |
| `ds_config_gaudi_z2.json` | DeepSpeed ZeRO-2配置（优化器分片、通信重叠） |
| `Dockerfile` | 基于Habana 1.24.1官方镜像构建 |

### 3. 数据文件

| 文件 | 格式 | 说明 |
|-----|------|-----|
| `data/train_cad.jsonl` | JSONL | 样例数据（3条），展示think范式 |
| `data/images/` | JPG/PNG | 图像文件夹（需自行准备实际数据） |

### 4. 自动化脚本

| 脚本 | 用途 |
|-----|------|
| `scripts/train_stage1.sh` | 一键启动阶段1训练 |
| `scripts/train_stage2.sh` | 一键启动阶段2训练 |
| `scripts/run_container.sh` | 快速启动Docker容器 |
| `scripts/verify_env.sh` | 验证HPU设备、环境变量、Python包 |
| `scripts/init_and_push.sh` | Git初始化并推送到GitHub |

---

## 🎯 文件用途速查

### 想快速启动训练？
→ 阅读 `QUICKSTART.md`，然后执行：
```bash
source env.sh
bash scripts/train_stage1.sh
bash scripts/train_stage2.sh
```

### 想了解项目架构？
→ 阅读 `PROJECT_STRUCTURE.md`

### 遇到问题需要排错？
→ 查看 `README.md` 的"常见问题排查"章节

### 想替换其他多模态基座？
→ 修改 `scripts/train_stage*.sh` 中的 `MODEL_PATH`  
→ 参考 `README.md` 的"基座模型替换"章节

### 想调整训练超参数？
→ 编辑 `scripts/train_stage*.sh` 中的参数  
→ 或修改 `ds_config_gaudi_z2.json`

### 想验证环境是否正常？
→ 执行 `bash scripts/verify_env.sh`

---

## 📦 文件依赖关系

```
env.sh
  ↓ 被加载
scripts/train_stage*.sh
  ↓ 调用
train_qwen_multimodal.py
  ↓ 读取
ds_config_gaudi_z2.json + data/train_cad.jsonl + data/images/
  ↓ 输出
outputs/stage1_projector/ 或 outputs/stage2_lora/
  ↓ 合并
merge_lora.py
  ↓ 输出
outputs/merged_model/
```

---

## 🔧 各文件是否需要修改？

| 文件 | 是否需要修改 | 说明 |
|-----|------------|-----|
| `README.md` | ❌ 不需要 | 文档，直接阅读 |
| `QUICKSTART.md` | ❌ 不需要 | 快速指南 |
| `Dockerfile` | ⚠️ 可选 | 需要额外依赖时修改 |
| `env.sh` | ⚠️ 可选 | 需要调整HCCL参数时修改 |
| `ds_config_gaudi_z2.json` | ⚠️ 可选 | 高级调优时修改 |
| `train_qwen_multimodal.py` | ⚠️ 可选 | 替换基座时可能需要调整数据格式 |
| `merge_lora.py` | ❌ 不需要 | 通用工具 |
| `data/train_cad.jsonl` | ✅ 必须 | 替换为实际训练数据 |
| `data/images/` | ✅ 必须 | 放入实际图像文件 |
| `scripts/*.sh` | ⚠️ 可选 | 需要调整超参数时修改 |

---

## 📊 文件大小估算

| 类型 | 文件 | 大小 |
|-----|------|-----|
| 文档 | README.md 等 | ~50KB |
| 脚本 | *.sh + *.py | ~80KB |
| 配置 | *.json | ~2KB |
| 数据 | train_cad.jsonl（样例） | ~1KB |
| 数据 | images/（实际数据） | **用户自行准备** |
| 输出 | checkpoints | **训练时生成，~14GB×2** |

---

## 🚀 工作流程对应文件

1. **环境准备** → `Dockerfile` + `env.sh`
2. **数据准备** → `data/train_cad.jsonl` + `data/images/`
3. **环境验证** → `scripts/verify_env.sh`
4. **阶段1训练** → `scripts/train_stage1.sh` + `train_qwen_multimodal.py`
5. **阶段2训练** → `scripts/train_stage2.sh` + `train_qwen_multimodal.py`
6. **权重合并** → `merge_lora.py`
7. **推送GitHub** → `scripts/init_and_push.sh`

---

## ⚠️ 不包含的文件

本工程**不提供**以下内容（需用户自行准备）：

- ❌ 预训练模型权重（需从Hugging Face下载）
- ❌ 实际训练数据集（仅提供3条样例）
- ❌ 推理服务代码（工程仅用于训练）
- ❌ 模型评估脚本（需根据任务自行编写）

---

## 📝 缺失文件检查

在开始训练前，确认以下文件存在：

```bash
# 核心文件
ls train_qwen_multimodal.py
ls ds_config_gaudi_z2.json
ls env.sh

# 训练脚本
ls scripts/train_stage1.sh
ls scripts/train_stage2.sh

# 数据文件（需自行准备）
ls data/train_cad.jsonl
ls data/images/*.jpg  # 应该有实际图像
```

如果缺少任何核心文件，请检查项目完整性或重新克隆仓库。

---

**📌 提示**: 所有 `.sh` 脚本已设置为可执行权限，可直接运行 `bash scripts/xxx.sh`
