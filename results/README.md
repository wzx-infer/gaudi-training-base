# 训练结果

本目录用于存放训练和评估的结果记录。

## 目录结构

```
results/
├── training_logs/          # 训练日志和指标
├── evaluation_results/     # 模型评估结果
├── visualizations/         # 可视化图表（loss曲线等）
└── benchmarks/            # 性能基准测试结果
```

## 结果记录

### 训练记录

每次训练完成后，建议记录以下信息：

```json
{
  "experiment_id": "qwen3.5-0.8b-cad-v1",
  "model": "Qwen3.5-0.8B",
  "dataset": "cad_drawings_1000",
  "training_time": "2024-09-23",
  "hardware": "Gaudi2 8卡",
  "stages": {
    "stage1": {
      "epochs": 3,
      "final_loss": 0.85,
      "duration": "2h15m"
    },
    "stage2": {
      "epochs": 5,
      "final_loss": 0.42,
      "duration": "4h30m"
    }
  }
}
```

### 评估结果

```json
{
  "model": "qwen3.5-0.8b-cad-v1",
  "test_set": "cad_test_100",
  "metrics": {
    "accuracy": 0.92,
    "think_quality_score": 0.88,
    "avg_inference_time_ms": 1250
  }
}
```

## 可视化

使用 TensorBoard 或 matplotlib 生成训练曲线，保存到 `visualizations/` 子目录。

## 版本管理

建议为每次重要实验创建结果记录文件，便于对比和追溯。
