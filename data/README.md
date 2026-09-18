# 数据说明

**任务场景**：暖通/机电工程图构件识别，识别输出为构件类别（风管三通、弯头、变径、阀门等）

## 📁 目录结构

```
data/
├── examples/           # 样例数据（暖通构件识别）
│   └── train_cad.jsonl
├── train/             # 训练数据 (使用工具生成)
├── val/               # 验证数据 (使用工具生成)
├── images/            # 图像文件
│   └── hvac/         # 暖通工程图纸
└── README.md          # 本文件
```

## 📝 数据格式

本项目支持 **ShareGPT 格式**的多模态数据，专注于**暖通构件识别任务**：

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "hvac_tee_001.jpg"},
        {"type": "text", "text": "请识别图纸中红圈标注的构件类型"}
      ]
    },
    {
      "role": "assistant",
      "content": "<think>观察红圈位置，这是三根管道的交汇点，其中两根管道在同一直线上，第三根管道垂直连接。从管道直径和连接方式判断，这是典型的风管三通接头。</think>\n这是风管三通"
    }
  ],
  "images": ["hvac_tee_001.jpg"]
}
```

### 暖通构件类别

本项目支持的暖通构件类别：

| 构件类别 | 说明 | 示例图纸特征 |
|---------|------|-------------|
| 风管三通 | 三根管道交汇，支管垂直连接主管 | T型结构，90度分支 |
| 风管弯头 | 管道方向改变 | 90度/45度转角 |
| 风管变径 | 连接不同管径的过渡段 | 大小头，渐变段 |
| 风量调节阀 | 调节风量的装置 | 管道中虚线标注 |
| 风管 | 直管段 | 平行双线 |
| 风管法兰 | 管道连接件 | 凸出结构+螺栓孔 |
| 防火阀 | 防火安全装置 | 特殊图例符号 |
| 消声器 | 降噪装置 | 内部填充结构 |
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `messages` | List | ✅ | 对话消息列表 |
| `messages[].role` | String | ✅ | 角色: `user` / `assistant` / `system` |
| `messages[].content` | String | ✅ | 消息内容，用户消息中用 `<image>` 标记图片位置 |
| `images` | List | ⚠️ | 图片路径列表（多模态必需） |

### Think 范式

推荐在 assistant 回复中加入 `<think>...</think>` 标签，训练模型的推理能力：

```json
{
  "role": "assistant",
  "content": "<think>\n让我分析一下这个问题：\n1. 观察图纸整体布局\n2. 识别关键尺寸\n3. 理解标注含义\n</think>\n\n根据分析，这张图纸..."
}
```

## 🔧 数据准备工具

### 1. 批量生成数据集（推荐）

使用批量生成工具从CSV标注表生成训练数据：

```bash
# 准备CSV标注文件 annotations.csv，格式如下：
# image_name,component_type,description
# hvac_001.jpg,风管三通,三根管道交汇形成T型结构
# hvac_002.jpg,风管弯头,管道90度转弯
# ...

# 批量生成数据集
python tools/build_hvac_dataset.py \
    --csv annotations.csv \
    --image_dir data/images/hvac \
    --output_dir data \
    --train_ratio 0.9

# 自动生成：
# - data/train/hvac_train.jsonl (训练集)
# - data/val/hvac_val.jsonl (验证集)
# - 自动验证图片存在性
# - 自动添加think推理内容
# - 按类别分层划分train/val
```

**CSV文件示例**：
```csv
image_name,component_type,description
hvac_tee_001.jpg,风管三通,三根管道交汇
hvac_elbow_001.jpg,风管弯头,90度转角
hvac_reducer_001.jpg,风管变径,大小头连接
hvac_damper_001.jpg,风量调节阀,可调节风量
```

### 2. 格式转换

如果你的数据是其他格式（如 Alpaca），可以使用转换工具：

```bash
# Alpaca 格式转换为 ShareGPT
python tools/data_converter.py convert \
    --input your_alpaca_data.jsonl \
    --output train/converted_data.jsonl \
    --format alpaca
```

### 3. 格式验证

验证你的数据格式是否正确：

```bash
python tools/data_converter.py validate \
    --input train/hvac_train.jsonl
```

## 📊 数据组织建议

### 推荐数据规模

| 数据集 | 最小规模 | 推荐规模 | 说明 |
|--------|---------|---------|------|
| **总样本数** | 1000条 | 3000+条 | 快速验证 → 良好性能 |
| **每类样本数** | 100条 | 300+条 | 保证每类均衡 |
| **验证集比例** | 10% | 10-15% | 按类别分层划分 |

### 构件类别分布示例

```
总计: 3000 条
├── 风管三通: 500 条 (16.7%)
├── 风管弯头: 500 条 (16.7%)
├── 风管变径: 400 条 (13.3%)
├── 风量调节阀: 300 条 (10.0%)
├── 风管: 600 条 (20.0%)
├── 风管法兰: 300 条 (10.0%)
├── 防火阀: 200 条 (6.7%)
└── 消声器: 200 条 (6.7%)
```

### 目录结构示例

```
data/
├── examples/
│   └── train_cad.jsonl          # 6个暖通构件样例
├── train/
│   └── hvac_train.jsonl         # 训练集（工具生成）
├── val/
│   └── hvac_val.jsonl           # 验证集（工具生成）
└── images/
    └── hvac/                    # 暖通工程图纸
        ├── hvac_tee_001.jpg
        ├── hvac_elbow_001.jpg
        ├── hvac_reducer_001.jpg
        └── ...
```

## 📝 数据标注示例

### 好的标注 ✅

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "image", "image": "hvac_tee_001.jpg"},
        {"type": "text", "text": "请识别图纸中红圈标注的构件类型"}
      ]
    },
    {
      "role": "assistant",
      "content": "<think>观察红圈位置，这是三根管道的交汇点，其中两根管道在同一直线上，第三根管道垂直连接。从管道直径和连接方式判断，这是典型的风管三通接头。</think>\n这是风管三通"
    }
  ],
  "images": ["hvac_tee_001.jpg"]
}
```

**要点**：
- ✅ Think推理过程具体，描述了观察到的特征
- ✅ 识别结果简洁明确："这是{构件类别}"
- ✅ 图像路径清晰
- ✅ 用户prompt自然

### 不好的标注 ❌

```json
{
  "messages": [
    {
      "role": "user",
      "content": "这是什么？"  // ❌ 太简短，缺少上下文
    },
    {
      "role": "assistant",
      "content": "三通"  // ❌ 没有think推理，没有"这是"格式
    }
  ],
  "images": []  // ❌ 缺少图片
}
```

## 🔍 检查清单

准备好数据后，检查以下内容：

- [ ] JSON 格式正确（可用工具验证）
- [ ] 所有图片文件存在且可访问
- [ ] messages 包含完整对话（至少一轮问答）
- [ ] assistant 回复包含 `<think>` 标签
- [ ] user 消息包含 `<image>` 标记
- [ ] 图片路径正确
- [ ] 数据量充足（建议 >1000 条）
- [ ] 没有重复数据

## 🚀 开始训练

数据准备好后，更新训练配置：

### LLaMA-Factory 方式

编辑 `configs/llamafactory/dataset_info.json`:
```json
{
  "my_dataset": {
    "file_name": "data/train/your_data.jsonl",
    "formatting": "sharegpt"
  }
}
```

编辑 `training/llamafactory/qwen2_vl_lora.yaml`:
```yaml
dataset: my_dataset
```

然后开始训练：
```bash
cd training/llamafactory
bash train.sh
```

### 原生训练方式

编辑 `training/native/train_qwen_multimodal.py`:
```python
TRAIN_DATA = "data/train/your_data.jsonl"
VAL_DATA = "data/val/your_val.jsonl"
```

然后开始训练：
```bash
cd training/native
bash train_stage1.sh
```

---

**数据准备完成后，就可以开始训练了！** 🎉
