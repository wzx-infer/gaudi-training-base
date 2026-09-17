#!/bin/bash
# Git仓库初始化与推送脚本
# 用法: bash scripts/init_and_push.sh

set -e

REPO_NAME="gaudi-training-base"
REPO_DESC="Gaudi2 8-Card Multimodal LLM Training Base for CAD Drawing Recognition"

echo "================================================"
echo "🚀 初始化Git仓库并推送到GitHub"
echo "================================================"

# 检查gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 未检测到 gh CLI，请先安装："
    echo "   Ubuntu/Debian: sudo apt install gh"
    echo "   或访问: https://cli.github.com/"
    exit 1
fi

# 检查登录状态
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录GitHub，请先执行: gh auth login"
    exit 1
fi

echo "✓ gh CLI已就绪"

# 初始化Git仓库
echo "📦 初始化本地Git仓库..."
git init

# 添加所有文件
echo "📝 添加文件到Git..."
git add .

# 提交
echo "💾 创建首次提交..."
git commit -m "feat: Gaudi2 8卡多模态大模型训练底座

- 支持Qwen2.5-VL-7B作为示例基座，可替换其他多模态模型
- 两阶段训练：投影层预训练 + LoRA指令微调
- DeepSpeed ZeRO-2 8卡分布式训练
- Lazy模式优化：图编译、算子融合、计算通信重叠
- CAD图纸识图任务，强制think思维链输出
- 提供完整训练脚本、环境配置、数据样例
- 支持权重合并、TensorBoard可视化、硬件监控

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"

# 创建GitHub仓库
echo "🌐 创建GitHub远程仓库..."
gh repo create $REPO_NAME \
  --public \
  --source=. \
  --description="$REPO_DESC" \
  --remote=origin

# 推送到远程
echo "⬆️ 推送代码到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "================================================"
echo "✅ 完成！"
echo "================================================"
echo "📦 仓库地址:"
gh repo view --web

echo ""
echo "🎯 后续操作:"
echo "   1. 准备数据集: data/train_cad.jsonl + data/images/"
echo "   2. 构建镜像: docker build -t gaudi-multimodal-train:1.24.1 ."
echo "   3. 启动容器: bash scripts/run_container.sh"
echo "   4. 开始训练: bash scripts/train_stage1.sh"
