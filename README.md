# Gaudi2 多模态训练环境

Intel Gaudi2 + Qwen3.5 多模态模型训练环境，基于 LLaMA-Factory。

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd gaudi-training-base
```

### 2. 部署环境

在 Gaudi2 服务器上运行：

```bash
bash deploy.sh
```

这个脚本会：
- 构建 Docker 镜像 `gaudi-train-qwen35:v2`
- 启动容器 `gaudi-mutimodel-training`
- 挂载模型路径 `/data/models` 和工作空间 `/home/wzx/workspace`

### 3. 验证环境

进入容器并运行验证脚本：

```bash
docker exec -it gaudi-mutimodel-training bash
bash /workspace/verify_env.sh
```

验证脚本会：
- 检查 HPU 设备（应该显示 8 个 HPU）
- 验证模型路径 `/models/Qwen/`
- 安装 LLaMA-Factory
- 运行一个完整的训练测试

## 环境说明

### Docker 镜像

- **基础镜像**: `vault.habana.ai/gaudi-docker/1.24.1/ubuntu24.04/habanalabs/pytorch-installer-2.11.0:latest`
- **PyTorch**: 2.11.0a0 (Habana 定制版)
- **Transformers**: 5.8.0
- **关键依赖**: 
  - peft==0.18.1
  - trl==0.22.2
  - datasets==4.0.0
  - accelerate==1.7.0

### 容器配置

- **容器名**: `gaudi-mutimodel-training`
- **HPU 设备**: 8 个 Gaudi2 HPU
- **挂载路径**:
  - `/data/models` → `/models` (模型存储)
  - `/home/wzx/workspace` → `/workspace` (工作目录)
  - `/root/.cache/habana` → `/root/.cache/habana` (HPU 缓存)

### 环境变量

```bash
PT_HPU_LAZY_MODE=0                    # 使用 eager 模式
PT_HPU_RECIPE_CACHE_CONFIG=...        # Recipe 缓存配置
HABANA_VISIBLE_DEVICES=all            # 所有 HPU 可见
OMPI_MCA_btl_vader_single_copy_mechanism=none  # MPI 配置
```

## 训练配置

示例配置见 [LLaMA-Factory config.yaml](https://github.com/hiyouga/LLaMA-Factory)：

```yaml
model_name_or_path: /models/Qwen/Qwen3.5-0.8B
dataset: mllm_demo
template: qwen3_vl
output_dir: saves/qwen3.5-0.8b-v2
```

## 目录结构

```
gaudi-training-base/
├── Dockerfile           # Docker 镜像定义
├── deploy.sh            # 一键部署脚本
├── verify_env.sh        # 环境验证脚本
└── README.md            # 本文档
```

## 常见问题

### Q: 如何查看训练日志？

```bash
docker exec -it gaudi-mutimodel-training bash
cd /workspace/LLaMA-Factory
cat saves/qwen3.5-0.8b-v2/trainer_log.jsonl
```

### Q: 如何重启容器？

```bash
docker restart gaudi-mutimodel-training
```

### Q: 如何清理重新部署？

```bash
docker stop gaudi-mutimodel-training
docker rm gaudi-mutimodel-training
bash deploy.sh
```

### Q: 如何检查 HPU 状态？

```bash
docker exec -it gaudi-mutimodel-training python -c "import torch; print('HPU:', torch.hpu.is_available(), 'count:', torch.hpu.device_count())"
```

## 训练测试结果

验证脚本会运行一个完整的训练流程：
- 数据集: `mllm_demo` (6 样本)
- 训练 epoch: 1
- 输出目录: `saves/qwen3.5-0.8b-v2`
- 预期时长: ~50 秒

成功标志：
```
✓ 验证完成 - 训练已完成
```

## 技术栈

- **硬件**: Intel Gaudi2 (8 HPUs)
- **容器**: Docker + Habana 官方镜像
- **框架**: PyTorch 2.11.0 (Habana)
- **训练工具**: LLaMA-Factory
- **模型**: Qwen3.5 系列 (0.8B / 27B / 122B)

## 许可

根据 Habana Labs 和 Qwen 模型的许可协议使用。
