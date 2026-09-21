#!/bin/bash
# 远程 Gaudi2 训练完整诊断和测试脚本
# 使用方法：在远程服务器上运行 bash remote_full_test.sh

set -e

echo "============================================"
echo "Gaudi2 训练环境完整诊断和测试"
echo "============================================"
echo ""

# 1. 检查 Gaudi 硬件
echo "=== 1. 检查 Gaudi2 硬件状态 ==="
hl-smi
echo ""

# 2. 检查 Docker 镜像
echo "=== 2. 检查 Docker 镜像 ==="
docker images | grep -E "gaudi|habana|REPOSITORY"
echo ""

# 3. 查找项目目录
echo "=== 3. 查找项目目录 ==="
if [ -d ~/gaudi-training-base ]; then
    PROJECT_DIR=~/gaudi-training-base
elif [ -d /workspace/gaudi-training-base ]; then
    PROJECT_DIR=/workspace/gaudi-training-base
else
    echo "未找到项目目录，搜索中..."
    PROJECT_DIR=$(find ~ -name "gaudi-training-base" -type d 2>/dev/null | head -1)
fi

if [ -z "$PROJECT_DIR" ]; then
    echo "❌ 错误：未找到 gaudi-training-base 目录"
    echo "请先将项目代码同步到远程服务器"
    exit 1
fi

echo "✓ 找到项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR"
echo ""

# 4. 检查最近的训练日志
echo "=== 4. 检查最近的训练日志/错误 ==="
if [ -d outputs/logs ]; then
    echo "训练日志目录存在"
    LATEST_LOG=$(find outputs/logs -name "*.log" -type f 2>/dev/null | sort -r | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "最新日志文件: $LATEST_LOG"
        echo "--- 最后50行 ---"
        tail -50 "$LATEST_LOG"
    else
        echo "未找到日志文件"
    fi
else
    echo "输出目录不存在，这是首次运行"
fi
echo ""

# 5. 检查 Docker 容器状态
echo "=== 5. 检查 Docker 容器状态 ==="
echo "运行中的容器："
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
echo ""
echo "最近的容器（包括已停止）："
docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}" | head -10

# 检查是否有失败的容器
FAILED_CONTAINER=$(docker ps -a --filter "status=exited" --filter "ancestor=gaudi-training-base:latest" --format "{{.ID}}" | head -1)
if [ -n "$FAILED_CONTAINER" ]; then
    echo ""
    echo "=== 6. 检查失败容器的日志 ==="
    echo "容器ID: $FAILED_CONTAINER"
    echo "--- 最后100行日志 ---"
    docker logs --tail 100 "$FAILED_CONTAINER"
fi
echo ""

# 7. 检查数据集
echo "=== 7. 检查训练数据集 ==="
if [ -f data/examples/train_cad.jsonl ]; then
    echo "✓ 示例数据集存在"
    LINES=$(wc -l < data/examples/train_cad.jsonl)
    echo "  数据条数: $LINES"
    echo "  第一条数据:"
    head -1 data/examples/train_cad.jsonl | python3 -m json.tool 2>/dev/null || head -1 data/examples/train_cad.jsonl
else
    echo "❌ 示例数据集不存在"
fi
echo ""

# 8. 检查镜像构建
echo "=== 8. 检查 Docker 镜像是否存在 ==="
if docker images | grep -q "gaudi-training-base"; then
    echo "✓ Docker 镜像存在"
    docker images gaudi-training-base:latest
else
    echo "❌ Docker 镜像不存在，需要构建"
    echo "运行: cd docker && bash build.sh"
fi
echo ""

echo "============================================"
echo "诊断完成！"
echo "============================================"
