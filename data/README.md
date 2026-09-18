# 数据说明

## 📁 目录结构

```
data/
├── examples/           # 样例数据
│   └── train_cad.jsonl
├── train/             # 训练数据 (自己准备)
├── val/               # 验证数据 (自己准备)
└── README.md          # 本文件
```

## 📝 数据格式

本项目支持 **ShareGPT 格式**的多模态数据：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "<image>\n请分析这张CAD图纸的尺寸标注"
    },
    {
      "role": "assistant",
      "content": "<think>\n我需要仔细观察图纸的各个部分...\n1. 首先识别主要的尺寸标注\n2. 然后分析标注的位置和含义\n</think>\n\n该CAD图纸包含以下尺寸标注：..."
    }
  ],
  "images": ["path/to/cad_image.jpg"]
}
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

### 1. 格式转换

如果你的数据是其他格式（如 Alpaca），可以使用转换工具：

```bash
# Alpaca 格式转换为 ShareGPT
python ../tools/data_converter.py convert \
    --input your_alpaca_data.jsonl \
    --output train/converted_data.jsonl \
    --format alpaca

# 自动检测格式
python ../tools/data_converter.py convert \
    --input your_data.jsonl \
    --output train/converted_data.jsonl \
    --format auto
```

### 2. 格式验证

验证你的数据格式是否正确：

```bash
python ../tools/data_converter.py validate \
    --input train/your_data.jsonl
```

### 3. 添加 Think 标签

为现有数据添加 think 标签：

```bash
python ../tools/data_converter.py add-think \
    --input train/data.jsonl \
    --output train/data_with_think.jsonl
```

## 📊 数据组织建议

### 目录结构示例

```
data/
├── examples/
│   └── train_cad.jsonl          # 样例数据
├── train/
│   ├── cad_analysis.jsonl       # CAD图纸分析数据
│   ├── ocr_recognition.jsonl    # OCR识别数据
│   └── qa_pairs.jsonl           # 问答对数据
├── val/
│   └── validation.jsonl         # 验证集
└── images/
    ├── cad/                     # CAD图纸
    ├── diagrams/                # 示意图
    └── photos/                  # 照片
```

### 图片路径

图片路径可以是：
- **相对路径**: `images/cad/drawing001.jpg`
- **绝对路径**: `/data/images/drawing001.jpg`
- **URL**: `http://example.com/image.jpg` (如果模型支持)

## 🎯 数据质量建议

### 1. 数据量
- **最小**: 1000条对话（快速验证）
- **推荐**: 10000+条对话（良好性能）
- **理想**: 100000+条对话（最佳性能）

### 2. 数据多样性
- ✅ 覆盖不同类型的CAD图纸
- ✅ 包含不同难度的问题
- ✅ 多样化的问答风格
- ✅ 平衡的对话长度

### 3. 数据清洗
- ✅ 移除重复数据
- ✅ 检查图片是否存在
- ✅ 验证JSON格式正确
- ✅ 统一图片尺寸和格式

### 4. Think 质量
- ✅ 思考过程要具体，不要泛泛而谈
- ✅ 步骤要清晰，便于模型学习
- ✅ 长度适中，通常3-5个推理步骤
- ❌ 避免"让我想想"这种无信息量的内容

## 📝 数据标注示例

### 好的标注 ✅

```json
{
  "messages": [
    {
      "role": "user", 
      "content": "<image>\n这个零件的总长度是多少？"
    },
    {
      "role": "assistant",
      "content": "<think>\n1. 观察图纸，找到表示总长度的尺寸标注\n2. 识别标注数值：左端到右端标注为120mm\n3. 验证：各段尺寸相加 = 30+60+30 = 120mm，一致\n</think>\n\n根据图纸标注，这个零件的总长度是 120mm。"
    }
  ],
  "images": ["data/images/cad/part_001.jpg"]
}
```

### 不好的标注 ❌

```json
{
  "messages": [
    {
      "role": "user",
      "content": "总长度？"  // ❌ 太简短，缺少上下文
    },
    {
      "role": "assistant", 
      "content": "120mm"  // ❌ 没有推理过程，没有think标签
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
