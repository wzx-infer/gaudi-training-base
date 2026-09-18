#!/usr/bin/env python3
"""
暖通构件数据集批量生成工具
从 CSV 标注表生成 ShareGPT 格式的训练数据，包含 think 推理过程

用法:
    python build_hvac_dataset.py \
        --csv annotations.csv \
        --image_dir data/images/hvac \
        --output_dir data \
        --train_ratio 0.9

CSV 格式要求:
    image_name,component_type,description
    hvac_001.jpg,风管三通,三根管道交汇形成T型结构
    hvac_002.jpg,风管弯头,管道90度转弯
"""

import os
import json
import csv
import random
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# 构件类别到think模板的映射
THINK_TEMPLATES = {
    "风管三通": "观察标注位置，这是三根管道的交汇点，其中两根管道在同一直线上，第三根管道垂直连接。从管道直径和连接方式判断，这是典型的风管三通接头。",
    "风管弯头": "图纸显示管道在此处改变方向，呈{angle}度转角。这是单根管道的方向改变，不涉及分支。从弯曲半径和管径一致性判断，这是标准的风管弯头。",
    "风管变径": "沿管道方向观察，管径从大端逐渐缩小到小端，两端直径不同。这是用于连接不同管径管道的过渡构件，渐变段确保气流平稳过渡。",
    "风量调节阀": "标注位置显示管道中有一个可调节装置，通常用虚线或特殊符号表示。从图例和位置判断，这是安装在风管内部用于调节风量的装置。",
    "风管": "观察线条特征：两条平行线表示管道边界，线条粗细均匀，中间无特殊标记或分支。这是标准的直管段表示方法，用于输送空气。",
    "风管法兰": "标注部位显示管道连接处有一圈凸出结构，带有螺栓孔位标注。这是用于连接两段管道的标准件，通过螺栓紧固实现密封连接。",
    "防火阀": "从图例符号判断，这是安装在风管内的防火安全装置。当温度超过设定值时，阀门自动关闭，阻止火势通过风管蔓延。",
    "消声器": "管道内部有特殊结构或填充物标注，用于降低气流噪音。从长度和结构判断，这是消声器装置。",
}

# 用户提示模板
USER_PROMPTS = [
    "请识别图纸中标注的构件类型",
    "这个构件是什么？",
    "请分析标注部位的构件",
    "图中标记处是什么设备？",
    "请识别这个暖通构件",
]


def generate_think_content(component_type: str, description: str = "") -> str:
    """生成think推理内容"""
    template = THINK_TEMPLATES.get(component_type,
        "观察图纸标注位置的结构特征，分析管道连接方式、几何形状和功能用途，综合判断构件类型。")

    # 如果是弯头且描述中有角度信息，替换角度
    if "弯头" in component_type and description:
        if "90" in description or "直角" in description:
            template = template.replace("{angle}", "90")
        elif "45" in description:
            template = template.replace("{angle}", "45")
        else:
            template = template.replace("{angle}", "")

    return template


def build_conversation(image_name: str, component_type: str, description: str = "") -> Dict:
    """构建单条对话数据"""
    user_prompt = random.choice(USER_PROMPTS)
    think_content = generate_think_content(component_type, description)

    # 构建assistant回复
    assistant_reply = f"<think>{think_content}</think>\n这是{component_type}"
    if description:
        assistant_reply += f"（{description}）"

    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_name},
                    {"type": "text", "text": user_prompt}
                ]
            },
            {
                "role": "assistant",
                "content": assistant_reply
            }
        ],
        "images": [image_name]
    }


def validate_images(data: List[Dict], image_dir: Path) -> Tuple[List[Dict], List[str]]:
    """验证图片文件是否存在"""
    valid_data = []
    missing_images = []

    for item in data:
        image_name = item["images"][0]
        image_path = image_dir / image_name

        if image_path.exists():
            valid_data.append(item)
        else:
            missing_images.append(str(image_path))

    return valid_data, missing_images


def split_train_val(data: List[Dict], train_ratio: float = 0.9,
                    min_per_class: int = 5) -> Tuple[List[Dict], List[Dict]]:
    """
    按类别分层划分训练集和验证集
    确保每个类别至少有 min_per_class 个样本在验证集
    """
    # 按构件类别分组
    by_class = {}
    for item in data:
        component_type = item["messages"][1]["content"].split("这是")[-1].split("（")[0]
        if component_type not in by_class:
            by_class[component_type] = []
        by_class[component_type].append(item)

    train_data = []
    val_data = []

    for component_type, items in by_class.items():
        random.shuffle(items)
        total = len(items)

        # 确保验证集至少有min_per_class个样本，或者该类别的10%
        val_count = max(min_per_class, int(total * (1 - train_ratio)))
        val_count = min(val_count, total // 2)  # 验证集不超过50%

        val_data.extend(items[:val_count])
        train_data.extend(items[val_count:])

        print(f"  {component_type}: {len(items)} 总计 -> {len(items[val_count:])} 训练 + {val_count} 验证")

    return train_data, val_data


def main():
    parser = argparse.ArgumentParser(description="批量生成暖通构件训练数据集")
    parser.add_argument("--csv", required=True, help="CSV标注文件路径")
    parser.add_argument("--image_dir", required=True, help="图像文件夹路径")
    parser.add_argument("--output_dir", default="data", help="输出目录")
    parser.add_argument("--train_ratio", type=float, default=0.9, help="训练集比例")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--min_val_per_class", type=int, default=5,
                       help="每个类别最少验证样本数")

    args = parser.parse_args()

    random.seed(args.seed)

    # 路径准备
    csv_path = Path(args.csv)
    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    train_dir = output_dir / "train"
    val_dir = output_dir / "val"
    train_dir.mkdir(exist_ok=True)
    val_dir.mkdir(exist_ok=True)

    print("="*60)
    print("📊 暖通构件数据集生成工具")
    print("="*60)
    print(f"输入CSV: {csv_path}")
    print(f"图像目录: {image_dir}")
    print(f"输出目录: {output_dir}")
    print(f"训练比例: {args.train_ratio:.1%}")
    print("="*60)

    # 读取CSV标注
    print("\n📝 读取CSV标注...")
    all_data = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_name = row['image_name']
            component_type = row['component_type']
            description = row.get('description', '')

            conversation = build_conversation(image_name, component_type, description)
            all_data.append(conversation)

    print(f"✓ 读取 {len(all_data)} 条标注")

    # 验证图片存在性
    print("\n🔍 验证图片文件...")
    valid_data, missing_images = validate_images(all_data, image_dir)

    if missing_images:
        print(f"⚠️  警告：{len(missing_images)} 张图片不存在:")
        for img in missing_images[:10]:  # 只显示前10个
            print(f"    - {img}")
        if len(missing_images) > 10:
            print(f"    ... 还有 {len(missing_images)-10} 张")

    print(f"✓ 有效数据: {len(valid_data)} 条")

    if not valid_data:
        print("\n❌ 错误：没有有效数据！请检查图片路径")
        return

    # 划分训练集和验证集
    print("\n📂 划分训练集和验证集...")
    train_data, val_data = split_train_val(
        valid_data,
        train_ratio=args.train_ratio,
        min_per_class=args.min_val_per_class
    )

    # 保存数据集
    print("\n💾 保存数据集...")

    train_file = train_dir / "hvac_train.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✓ 训练集: {train_file} ({len(train_data)} 条)")

    val_file = val_dir / "hvac_val.jsonl"
    with open(val_file, 'w', encoding='utf-8') as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✓ 验证集: {val_file} ({len(val_data)} 条)")

    # 统计信息
    print("\n"+"="*60)
    print("📊 数据集统计")
    print("="*60)
    print(f"总样本数: {len(valid_data)}")
    print(f"训练集: {len(train_data)} ({len(train_data)/len(valid_data)*100:.1f}%)")
    print(f"验证集: {len(val_data)} ({len(val_data)/len(valid_data)*100:.1f}%)")

    # 统计各类别分布
    print("\n各类别分布:")
    component_counts = {}
    for item in valid_data:
        component_type = item["messages"][1]["content"].split("这是")[-1].split("（")[0]
        component_counts[component_type] = component_counts.get(component_type, 0) + 1

    for comp_type, count in sorted(component_counts.items(), key=lambda x: -x[1]):
        print(f"  {comp_type}: {count} 条")

    print("\n"+"="*60)
    print("✅ 数据集生成完成！")
    print("="*60)

    # 检查是否满足最小数量要求
    if len(train_data) < 1000:
        print(f"\n⚠️  建议：训练集样本数 ({len(train_data)}) 少于推荐的1000条")

    for comp_type, count in component_counts.items():
        if count < 100:
            print(f"⚠️  建议：{comp_type} 样本数 ({count}) 少于推荐的100条")


if __name__ == "__main__":
    main()
