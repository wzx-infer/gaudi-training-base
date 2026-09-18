# 项目重构日志

## v2.0.0 - 重大更新 (2026-09-17)

### 🎉 主要变化

#### 1. 目录结构重构
- ✅ **清晰分类**: 按功能模块组织目录
  - `training/` - 训练核心代码
  - `configs/` - 配置文件集中管理
  - `docker/` - Docker相关文件
  - `scripts/` - 自动化脚本
  - `tools/` - 工具脚本
  - `data/` - 数据管理
  - `outputs/` - 训练输出
  - `docs/` - 文档集中

#### 2. 新增 LLaMA-Factory 训练方案 ⭐
- ✅ 零代码训练：YAML配置即可
- ✅ 3行命令启动：`source env.sh && cd training/llamafactory && bash train.sh`
- ✅ 100+模型支持：Qwen、LLaVA、InternVL等
- ✅ Web UI：可视化配置和监控
- ✅ 小白友好：完整中文教程

#### 3. 双训练方案架构
- **LLaMA-Factory** (`training/llamafactory/`)
  - 适合：新手、快速验证、标准任务
  - 特点：开箱即用，零代码配置
  
- **原生训练** (`training/native/`)
  - 适合：专业用户、定制需求、研究实验
  - 特点：完全可控，深度定制

#### 4. 新增工具脚本
- ✅ `tools/data_converter.py` - 数据格式转换
  - 支持 Alpaca → ShareGPT
  - 自动格式检测
  - 数据格式验证
  - 批量添加 think 标签

- ✅ `scripts/monitor.sh` - 训练监控
  - 实时查看训练状态
  - 日志自动聚合
  - checkpoint 管理

- ✅ `scripts/merge_lora.sh` - 权重合并
  - 一键合并 LoRA
  - 自动验证

#### 5. 文档优化
- ✅ 新增 `training/llamafactory/README.md` - LLaMA-Factory 完整教程
- ✅ 新增 `data/README.md` - 数据准备详细指南
- ✅ 重写 `README.md` - 更专业的项目主页
- ✅ 所有文档移至 `docs/` 目录

#### 6. Docker 优化
- ✅ `docker/build.sh` - 一键构建镜像
- ✅ `docker/run.sh` - 简化容器启动
- ✅ 统一 Docker 相关文件

---

## 🔄 文件迁移对照表

### 旧结构 → 新结构

| 旧路径 | 新路径 |
|--------|--------|
| `train_qwen_multimodal.py` | `training/native/train_qwen_multimodal.py` |
| `merge_lora.py` | `tools/merge_lora.py` |
| `scripts/train_stage1.sh` | `training/native/train_stage1.sh` |
| `scripts/train_stage2.sh` | `training/native/train_stage2.sh` |
| `ds_config_gaudi_z2.json` | `configs/deepspeed_z2.json` |
| `env.sh` | `configs/env.sh` |
| `Dockerfile` | `docker/Dockerfile` |
| `scripts/run_container.sh` | `docker/run.sh` |
| `scripts/verify_env.sh` | `scripts/verify_env.sh` (保留) |
| `data/train_cad.jsonl` | `data/examples/train_cad.jsonl` |
| `*.md` (根目录) | `docs/*.md` |

### 新增文件

```
training/llamafactory/
├── qwen2_vl_lora.yaml       # LLaMA-Factory 训练配置
├── train.sh                  # 一键训练脚本
└── README.md                 # 完整教程

configs/llamafactory/
└── dataset_info.json         # 数据集配置

docker/
└── build.sh                  # 镜像构建脚本

scripts/
├── merge_lora.sh             # LoRA 合并脚本
└── monitor.sh                # 训练监控脚本

tools/
└── data_converter.py         # 数据格式转换工具

data/
└── README.md                 # 数据准备指南

outputs/                      # 新增输出目录
├── models/
├── logs/
└── checkpoints/

README.md                     # 重写的项目主页
```

---

## 📊 重构统计

### 目录结构
- 旧结构: 根目录20个文件，1个scripts目录
- 新结构: 8个顶层目录，清晰分类

### 文件数量
- 核心代码: 12个文件
- 配置文件: 4个文件
- 文档: 8个文件
- 工具脚本: 7个文件
- **总计**: 31个文件 (+11个新增)

### 新增功能
- LLaMA-Factory 完整集成
- 数据转换工具
- 训练监控工具
- Docker 自动化脚本

---

## 🎯 使用变化

### 环境加载
```bash
# 旧方式
source env.sh

# 新方式 (路径变化)
source configs/env.sh
```

### 训练启动

**LLaMA-Factory (新增)**
```bash
cd training/llamafactory
bash train.sh
```

**原生训练**
```bash
# 旧方式
bash scripts/train_stage1.sh

# 新方式
cd training/native
bash train_stage1.sh
```

### 权重合并
```bash
# 旧方式
python merge_lora.py --args...

# 新方式
bash scripts/merge_lora.sh [args...]
```

---

## 🚀 升级指南

如果你已经克隆了旧版本：

### 1. 备份你的修改
```bash
git stash
```

### 2. 拉取最新代码
```bash
git pull origin main
```

### 3. 更新环境变量引用
```bash
# 修改你的脚本中的路径
sed -i 's|source env.sh|source configs/env.sh|g' your_script.sh
```

### 4. 迁移你的数据
```bash
# 移动自定义数据到新目录
mv data/your_data.jsonl data/train/
```

### 5. 测试环境
```bash
source configs/env.sh
bash scripts/verify_env.sh
```

---

## 💡 设计理念

### 模块化
- 每个目录职责单一
- 配置与代码分离
- 输出与源码分离

### 用户友好
- 双训练方案，满足不同用户
- 完善的文档和教程
- 自动化脚本减少手工操作

### 可扩展性
- 清晰的目录结构便于扩展
- 工具脚本模块化设计
- 配置文件集中管理

### 专业化
- 符合开源项目标准结构
- Docker/scripts/tools 分离
- 完整的测试和监控工具

---

## 📝 破坏性变化

### 路径变化
- ⚠️ 所有根目录脚本已迁移
- ⚠️ 环境变量文件路径变化
- ⚠️ 文档路径变化

### 兼容性
- ✅ 训练数据格式：兼容
- ✅ 模型权重：兼容
- ✅ 配置文件：兼容
- ⚠️ 自定义脚本：需要更新路径

---

## 🎉 下一步

### 推荐操作
1. 尝试 LLaMA-Factory 训练：`cd training/llamafactory && bash train.sh`
2. 查看新文档：`cat training/llamafactory/README.md`
3. 转换你的数据：`python tools/data_converter.py --help`
4. 监控训练：`bash scripts/monitor.sh`

### 反馈
- 遇到问题？提交 Issue
- 有建议？发起 Discussion
- 喜欢？给个 Star ⭐

---

**v2.0.0 带来全新体验，让训练更简单！** 🚀
