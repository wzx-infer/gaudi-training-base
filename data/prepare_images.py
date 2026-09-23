#!/usr/bin/env python
"""
MechVQA 图片下载脚本

由于 ModelScope 数据集图片需要单独处理，这个脚本提供两个方案：
1. 从 ModelScope git repo 克隆（推荐）
2. 生成占位图片用于测试流程
"""

import os
import json
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import subprocess


def create_placeholder_images(data_dir="data/mechvqa"):
    """创建占位图片用于测试训练流程"""
    print("\n" + "="*60)
    print("创建占位图片（用于测试训练流程）")
    print("="*60)

    # 读取数据获取所有图片路径
    all_images = set()

    for split in ['train', 'val']:
        json_path = Path(data_dir) / 'converted' / f'{split}.json'
        with open(json_path, 'r') as f:
            data = json.load(f)

        for item in data:
            for img_path in item['images']:
                # data/mechvqa/images/xx/xxx.png
                all_images.add(img_path)

    print(f"总共需要 {len(all_images)} 张图片")

    # 创建占位图片（300x300 灰色）
    placeholder = Image.new('RGB', (300, 300), color=(128, 128, 128))

    created = 0
    for img_path in tqdm(list(all_images), desc="创建占位图"):
        full_path = Path(img_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_path.exists():
            placeholder.save(full_path)
            created += 1

    print(f"\n✓ 创建了 {created} 张占位图片")
    print(f"⚠️  注意：这些是占位图片，仅用于测试训练流程")
    print(f"   实际训练需要真实图片！")


def download_from_git(data_dir="data/mechvqa"):
    """从 ModelScope Git 仓库下载图片"""
    print("\n" + "="*60)
    print("从 ModelScope Git 下载图片")
    print("="*60)

    repo_url = "https://www.modelscope.cn/datasets/xiaofengalg/MechVQA.git"
    images_dir = Path(data_dir) / "images"

    print(f"仓库: {repo_url}")
    print(f"目标: {images_dir}")
    print("\n提示：这可能需要较长时间，图片数据较大")
    print("如果失败，可以手动从网页端下载图片压缩包")

    # 使用 git sparse-checkout 只下载 images 目录
    temp_dir = Path(data_dir) / "temp_clone"
    temp_dir.mkdir(exist_ok=True)

    commands = [
        f"cd {temp_dir} && git init",
        f"cd {temp_dir} && git remote add origin {repo_url}",
        f"cd {temp_dir} && git config core.sparseCheckout true",
        f"cd {temp_dir} && echo 'images/*' > .git/info/sparse-checkout",
        f"cd {temp_dir} && git pull origin master",
    ]

    print("\n执行 Git 命令...")
    for cmd in commands:
        print(f"  $ {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ 失败: {result.stderr}")
            return False

    # 移动图片到目标目录
    import shutil
    if (temp_dir / "images").exists():
        if images_dir.exists():
            shutil.rmtree(images_dir)
        shutil.move(str(temp_dir / "images"), str(images_dir))
        print(f"\n✓ 图片已下载到: {images_dir}")

        # 清理临时目录
        shutil.rmtree(temp_dir)
        return True
    else:
        print("\n✗ 下载失败：未找到 images 目录")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MechVQA 图片准备")
    parser.add_argument('--mode', choices=['placeholder', 'git'], default='placeholder',
                        help='placeholder: 创建占位图用于测试; git: 从Git下载真实图片')
    parser.add_argument('--data_dir', default='data/mechvqa', help='数据目录')

    args = parser.parse_args()

    print("="*60)
    print("MechVQA 图片准备")
    print("="*60)
    print(f"模式: {args.mode}")
    print(f"目录: {args.data_dir}")

    if args.mode == 'placeholder':
        create_placeholder_images(args.data_dir)
        print("\n下一步：")
        print("  1. 运行测试训练验证流程")
        print("  2. 使用 --mode git 下载真实图片进行正式训练")
    else:
        success = download_from_git(args.data_dir)
        if success:
            print("\n下一步：")
            print("  启动训练: bash training/llamafactory/train_sft.sh")
        else:
            print("\n失败处理：")
            print("  1. 手动从网页端下载: https://modelscope.cn/datasets/xiaofengalg/MechVQA")
            print("  2. 或使用占位图测试: python data/prepare_images.py --mode placeholder")


if __name__ == "__main__":
    main()
