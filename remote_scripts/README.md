# 远程 Gaudi2 训练调试指南

## 步骤 1: 上传脚本到远程服务器

在你的本地 PowerShell 中执行：

```powershell
# 使用 scp 上传脚本到远程服务器
scp -r remote_scripts wzx@10.89.83.84:~/
```

或者手动复制文件内容到远程服务器。

## 步骤 2: 连接到远程服务器

```bash
ssh wzx@10.89.83.84
# 密码: qwerty
```

## 步骤 3: 运行诊断脚本

```bash
cd ~/remote_scripts
chmod +x *.sh
bash remote_full_test.sh
```

这个脚本会：
- 检查 8 张 Gaudi2 卡状态
- 检查 Docker 镜像
- 查找项目目录
- 检查训练日志和错误
- 检查数据集
- 显示失败容器的日志

## 步骤 4: 运行修复和测试脚本

根据诊断结果，运行修复脚本：

```bash
bash remote_fix_and_test.sh
```

这个脚本会：
- 清理旧的 Docker 容器
- 创建必要的目录结构
- 验证并创建测试数据集（如果不存在）
- 检查并修复配置文件
- 启动 Docker 容器进行最小化训练测试（2个样本，1个epoch）

## 步骤 5: 查看测试结果

```bash
# 查看训练日志
cat ~/gaudi-training-base/outputs/logs/test_train.log

# 如果测试成功，运行完整训练
cd ~/gaudi-training-base/training/llamafactory
source ../../configs/env.sh
bash train.sh
```

## 常见问题和解决方案

### 问题 1: Docker 镜像不存在

```bash
cd ~/gaudi-training-base/docker
bash build.sh
```

### 问题 2: 项目代码未同步到远程服务器

从本地上传项目代码：

```powershell
# 在本地 PowerShell 中执行
cd C:\Users\wangzhixiong\gaudi-training-base
scp -r * wzx@10.89.83.84:~/gaudi-training-base/
```

或使用 git：

```bash
# 在远程服务器上
cd ~
git clone https://github.com/wzx-infer/gaudi-training-base.git
cd gaudi-training-base
```

### 问题 3: 模型下载失败

容器内需要访问 Hugging Face 下载模型。可以：

1. 预先下载模型到本地
2. 配置 HF_ENDPOINT 镜像
3. 使用本地模型路径

```bash
# 设置 HF 镜像（在容器内）
export HF_ENDPOINT=https://hf-mirror.com
```

### 问题 4: 权限问题

```bash
# 修复目录权限
sudo chown -R wzx:wzx ~/gaudi-training-base
```

### 问题 5: 显存不足

编辑 `training/llamafactory/qwen2_vl_lora.yaml`：

```yaml
per_device_train_batch_size: 1  # 减小 batch size
gradient_accumulation_steps: 16  # 增加梯度累积
lora_rank: 32  # 减小 LoRA rank
```

## 调试技巧

### 查看 Gaudi 设备状态
```bash
hl-smi
watch -n 1 hl-smi  # 实时监控
```

### 查看 Docker 容器日志
```bash
docker ps -a  # 查看所有容器
docker logs <container_id>  # 查看特定容器日志
docker logs -f <container_id>  # 实时查看日志
```

### 进入运行中的容器
```bash
docker exec -it <container_id> /bin/bash
```

### 测试 Habana 环境
```bash
# 在容器内
python3 -c "import habana_frameworks.torch as ht; print(ht.hpu.device_count())"
```

## 预期输出

成功运行后，你应该看到：

1. ✓ 8 张 Gaudi2 卡正常识别
2. ✓ Docker 镜像存在
3. ✓ 训练容器成功启动
4. ✓ 数据集加载正常
5. ✓ 训练开始并输出 loss

训练日志应该包含：
```
Habana devices: 8
数据集行数: 3
训练开始...
{'loss': 2.xxx, 'learning_rate': xxx, 'epoch': 0.xx}
```

## 下一步

测试成功后，可以：

1. 运行完整训练（多个 epoch，完整数据集）
2. 调整超参数优化性能
3. 监控训练指标
4. 定期保存 checkpoint
