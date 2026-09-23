#!/usr/bin/env python
"""
MechVQA 数据集下载和准备脚本

功能：
1. 从ModelScope下载MechVQA数据集
2. 转换为LLaMA-Factory格式
3. 下载所有图片到本地
"""

import json
import os
import sys
from pathlib import Path
from tqdm import tqdm
import requests
from urllib.parse import urljoin


def load_raw_data(cache_dir="/root/.cache/modelscope/hub/datasets/downloads"):
    """加载原始数据"""
    train_file = Path(cache_dir) / "1ef998c728a2fbc77c2ea8d5c8f95f358cc3acbdf5c5f4dc39d4bb8f94659eb5"
    val_file = Path(cache_dir) / "b366f97c8b4c01763ca40bce58acddc0a10f60bc3a04a9c3b97d7de504d83629"

    print("Loading train data...")
    with open(train_file, 'r', encoding='utf-8') as f:
        train_data = [json.loads(line) for line in f]

    print("Loading validation data...")
    with open(val_file, 'r', encoding='utf-8') as f:
        val_data = [json.loads(line) for line in f]

    print(f"✓ Train: {len(train_data)} samples")
    print(f"✓ Val: {len(val_data)} samples")

    return train_data, val_data


def save_raw_data(train_data, val_data, output_dir="data/mechvqa/raw"):
    """保存原始数据到项目目录"""
    os.makedirs(output_dir, exist_ok=True)

    train_path = Path(output_dir) / "train.jsonl"
    val_path = Path(output_dir) / "val.jsonl"

    print(f"\nSaving to {output_dir}...")

    with open(train_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    with open(val_path, 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✓ Saved: {train_path}")
    print(f"✓ Saved: {val_path}")


def convert_to_llamafactory(data, split_name):
    """
    转换为LLaMA-Factory格式

    原始格式:
    {
      "images": ["images/xxx.png"],
      "messages": [
        {"role": "user", "content": "<image>问题..."},
        {"role": "assistant", "content": "<think>...</think><answer>...</answer>"}
      ],
      "metadata": {...}
    }

    LLaMA-Factory格式:
    {
      "messages": [
        {"role": "user", "content": "<image>问题..."},
        {"role": "assistant", "content": "<think>...</think><answer>...</answer>"}
      ],
      "images": ["data/mechvqa/images/xxx.png"]
    }
    """
    converted = []

    for item in tqdm(data, desc=f"Converting {split_name}"):
        # 更新图片路径为本地路径
        local_images = []
        for img_path in item["images"]:
            # images/xx/xxx.png -> data/mechvqa/images/xx/xxx.png
            local_path = f"data/mechvqa/images/{img_path.replace('images/', '')}"
            local_images.append(local_path)

        converted_item = {
            "messages": item["messages"],
            "images": local_images
        }
        converted.append(converted_item)

    return converted


def save_llamafactory_format(train_data, val_data, output_dir="data/mechvqa/converted"):
    """保存为LLaMA-Factory格式"""
    os.makedirs(output_dir, exist_ok=True)

    train_converted = convert_to_llamafactory(train_data, "train")
    val_converted = convert_to_llamafactory(val_data, "val")

    train_path = Path(output_dir) / "train.json"
    val_path = Path(output_dir) / "val.json"

    print(f"\nSaving LLaMA-Factory format to {output_dir}...")

    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_converted, f, ensure_ascii=False, indent=2)

    with open(val_path, 'w', encoding='utf-8') as f:
        json.dump(val_converted, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved: {train_path} ({len(train_converted)} samples)")
    print(f"✓ Saved: {val_path} ({len(val_converted)} samples)")


def download_images(data, base_url, output_dir="data/mechvqa/images"):
    """
    下载图片到本地

    注意：MechVQA图片托管在ModelScope，需要构造正确的下载URL
    """
    os.makedirs(output_dir, exist_ok=True)

    # 收集所有图片路径
    all_images = set()
    for item in data:
        for img_path in item["images"]:
            all_images.add(img_path)

    print(f"\nTotal unique images: {len(all_images)}")
    print("Note: Images are on ModelScope CDN. Manual download may be needed.")
    print(f"Image directory: {output_dir}")

    # 创建图片子目录结构
    for img_path in tqdm(list(all_images)[:5], desc="Creating directories"):
        local_path = Path(output_dir) / img_path.replace('images/', '')
        local_path.parent.mkdir(parents=True, exist_ok=True)

    print("\n⚠️  Image download requires ModelScope dataset access.")
    print("Please manually copy images from ModelScope cache or download via modelscope SDK:")
    print(f"  from modelscope.msdatasets import MsDataset")
    print(f"  ds = MsDataset.load('xiaofengalg/MechVQA')")


def create_dataset_info():
    """创建dataset_info.json for LLaMA-Factory"""
    dataset_info = {
        "mechvqa_train": {
            "file_name": "data/mechvqa/converted/train.json",
            "formatting": "sharegpt",
            "columns": {
                "messages": "messages",
                "images": "images"
            },
            "tags": {
                "role_tag": "role",
                "content_tag": "content",
                "user_tag": "user",
                "assistant_tag": "assistant"
            }
        },
        "mechvqa_val": {
            "file_name": "data/mechvqa/converted/val.json",
            "formatting": "sharegpt",
            "columns": {
                "messages": "messages",
                "images": "images"
            },
            "tags": {
                "role_tag": "role",
                "content_tag": "content",
                "user_tag": "user",
                "assistant_tag": "assistant"
            }
        }
    }

    output_path = "data/mechvqa/dataset_info.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Created: {output_path}")
    print("Add this to LLaMA-Factory's dataset_info.json to use the dataset.")


def main():
    print("="*60)
    print("MechVQA Dataset Preparation")
    print("="*60)

    # 1. 加载原始数据
    train_data, val_data = load_raw_data()

    # 2. 保存原始数据到项目目录
    save_raw_data(train_data, val_data)

    # 3. 转换为LLaMA-Factory格式
    save_llamafactory_format(train_data, val_data)

    # 4. 创建dataset_info.json
    create_dataset_info()

    # 5. 提示图片下载
    download_images(train_data + val_data, base_url="https://modelscope.cn")

    print("\n" + "="*60)
    print("✓ Data preparation completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Copy images from ModelScope cache to data/mechvqa/images/")
    print("2. Verify data with: python -c 'import json; print(json.load(open(\"data/mechvqa/converted/train.json\"))[0])'")
    print("3. Start training with: cd training/llamafactory && bash train_sft.sh")


if __name__ == "__main__":
    main()
