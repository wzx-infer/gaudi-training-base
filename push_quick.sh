#!/bin/bash
# 快速推送脚本

cd /home/wzx/gaudi-training-base

echo "=== 当前提交 ==="
git log --oneline -1
echo ""

echo "=== 远程仓库 ==="
git remote -v
echo ""

echo "=== 准备推送 ==="
echo "远程分支: origin/main"
echo "本地分支: master"
echo ""

# 推送到远程main分支
git push origin master:main

echo ""
echo "✓ 推送完成！"
echo "查看: https://github.com/wzx-infer/gaudi-training-base"
