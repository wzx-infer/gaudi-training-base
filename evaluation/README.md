# 模型评估

本目录用于存放模型评估相关的脚本和结果。

## 评估流程

训练完成后，可以通过以下方式评估模型：

### 1. 推理测试

```bash
# 使用训练后的模型进行推理测试
python tools/inference_demo.py \
  --model_path outputs/models/merged_model \
  --image_path data/test/sample.jpg \
  --prompt "请分析这张CAD图纸"
```

### 2. 批量评估

```bash
# 对测试集进行批量评估
python tools/evaluate_identification.py \
  --model_path outputs/models/merged_model \
  --test_data data/val/ \
  --output_file results/evaluation_results.json
```

### 3. 评估指标

- **准确率**: 识别结果与标注的匹配度
- **Think质量**: 推理过程的完整性和合理性
- **响应时间**: 单张图片的推理耗时

## 评估数据集

将测试数据放置在 `data/val/` 目录下，格式与训练数据相同。

## 注意事项

- 评估需要在 CPU 或 GPU 环境进行（Gaudi2 推理支持待完善）
- 确保测试数据与训练数据格式一致
- 记录评估结果到 `results/` 目录
