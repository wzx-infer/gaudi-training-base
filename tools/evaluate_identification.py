#!/usr/bin/env python3
"""
暖通构件识别评估脚本
对验证集进行批量推理，统计整体和分类别准确率

用法:
    python evaluate_identification.py \
        --model_path outputs/models/qwen2_vl_merged \
        --val_data data/val/hvac_val.jsonl \
        --image_dir data/images/hvac \
        --output_file outputs/evaluation_results.json

输出:
    - 总体准确率
    - 各构件类别准确率
    - 混淆矩阵
    - 错误样本详情
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from tqdm import tqdm


def extract_component_type(text: str) -> str:
    """从模型输出中提取构件类型"""
    # 去除think标签
    if "<think>" in text:
        text = text.split("</think>")[-1]

    # 提取"这是XXX"中的XXX
    if "这是" in text:
        component = text.split("这是")[-1].split("（")[0].split("\n")[0].strip()
        return component

    return text.strip()


def load_validation_data(val_file: Path, image_dir: Path) -> List[Dict]:
    """加载验证集数据"""
    data = []
    with open(val_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line.strip())

            # 提取ground truth
            assistant_content = item["messages"][1]["content"]
            gt_component = extract_component_type(assistant_content)

            # 提取用户prompt和图像
            user_content = item["messages"][0]["content"]
            image_name = None
            user_text = ""

            for content in user_content:
                if content["type"] == "image":
                    image_name = content["image"]
                elif content["type"] == "text":
                    user_text = content["text"]

            if image_name:
                image_path = image_dir / image_name
                if image_path.exists():
                    data.append({
                        "image_path": str(image_path),
                        "image_name": image_name,
                        "user_prompt": user_text,
                        "ground_truth": gt_component,
                        "full_gt": assistant_content
                    })

    return data


def inference_single(model, processor, image_path: str, prompt: str, device: str = "hpu") -> str:
    """单张图片推理"""
    image = Image.open(image_path).convert("RGB")

    # 构造输入
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    # 应用chat template
    text = processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=True)

    # 处理输入
    inputs = processor(
        text=text,
        images=image,
        return_tensors="pt",
        padding=True
    ).to(device)

    # 生成
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
            temperature=1.0,
            top_p=1.0
        )

    # 解码
    generated_text = processor.batch_decode(
        output_ids[:, inputs['input_ids'].shape[1]:],
        skip_special_tokens=True
    )[0]

    return generated_text


def evaluate(model, processor, val_data: List[Dict], device: str = "hpu") -> Dict:
    """评估验证集"""
    results = {
        "total": len(val_data),
        "correct": 0,
        "accuracy": 0.0,
        "by_class": defaultdict(lambda: {"total": 0, "correct": 0, "accuracy": 0.0}),
        "confusion_matrix": defaultdict(lambda: defaultdict(int)),
        "errors": []
    }

    print(f"\n🔍 开始评估 {len(val_data)} 个样本...\n")

    for item in tqdm(val_data, desc="推理中"):
        # 推理
        try:
            pred_text = inference_single(
                model, processor,
                item["image_path"],
                item["user_prompt"],
                device
            )
            pred_component = extract_component_type(pred_text)
        except Exception as e:
            print(f"\n⚠️ 推理失败: {item['image_name']} - {e}")
            pred_text = ""
            pred_component = "ERROR"

        gt_component = item["ground_truth"]

        # 统计
        results["by_class"][gt_component]["total"] += 1
        results["confusion_matrix"][gt_component][pred_component] += 1

        is_correct = pred_component == gt_component

        if is_correct:
            results["correct"] += 1
            results["by_class"][gt_component]["correct"] += 1
        else:
            # 记录错误样本
            results["errors"].append({
                "image": item["image_name"],
                "prompt": item["user_prompt"],
                "ground_truth": gt_component,
                "prediction": pred_component,
                "full_output": pred_text
            })

    # 计算准确率
    results["accuracy"] = results["correct"] / results["total"] if results["total"] > 0 else 0.0

    for gt_class in results["by_class"]:
        class_stats = results["by_class"][gt_class]
        class_stats["accuracy"] = (
            class_stats["correct"] / class_stats["total"]
            if class_stats["total"] > 0 else 0.0
        )

    return results


def print_results(results: Dict):
    """打印评估结果"""
    print("\n" + "="*70)
    print("📊 评估结果")
    print("="*70)

    print(f"\n总体准确率: {results['accuracy']:.2%} ({results['correct']}/{results['total']})")

    print("\n各构件类别准确率:")
    print("-" * 70)
    print(f"{'构件类别':<20} {'样本数':>10} {'正确数':>10} {'准确率':>15}")
    print("-" * 70)

    for gt_class in sorted(results["by_class"].keys()):
        stats = results["by_class"][gt_class]
        print(f"{gt_class:<20} {stats['total']:>10} {stats['correct']:>10} {stats['accuracy']:>14.2%}")

    print("\n混淆矩阵:")
    print("-" * 70)

    # 获取所有类别
    all_classes = sorted(set(results["confusion_matrix"].keys()) |
                        set(c for row in results["confusion_matrix"].values() for c in row.keys()))

    # 打印表头
    print(f"{'真实\\预测':<15}", end="")
    for pred_class in all_classes:
        print(f"{pred_class[:10]:>12}", end="")
    print()
    print("-" * 70)

    # 打印矩阵
    for gt_class in all_classes:
        print(f"{gt_class:<15}", end="")
        for pred_class in all_classes:
            count = results["confusion_matrix"][gt_class][pred_class]
            print(f"{count:>12}", end="")
        print()

    if results["errors"]:
        print(f"\n错误样本数: {len(results['errors'])}")
        print("-" * 70)

        # 显示前10个错误
        for i, error in enumerate(results["errors"][:10], 1):
            print(f"\n错误 {i}:")
            print(f"  图像: {error['image']}")
            print(f"  真实类别: {error['ground_truth']}")
            print(f"  预测类别: {error['prediction']}")
            print(f"  完整输出: {error['full_output'][:100]}...")

        if len(results["errors"]) > 10:
            print(f"\n... 还有 {len(results['errors'])-10} 个错误样本")

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="暖通构件识别评估")
    parser.add_argument("--model_path", required=True, help="模型路径")
    parser.add_argument("--val_data", required=True, help="验证集JSONL文件")
    parser.add_argument("--image_dir", required=True, help="图像目录")
    parser.add_argument("--output_file", default="evaluation_results.json",
                       help="结果保存路径")
    parser.add_argument("--device", default="hpu", choices=["hpu", "cuda", "cpu"],
                       help="推理设备")
    parser.add_argument("--batch_size", type=int, default=1,
                       help="批次大小（暂不支持>1）")

    args = parser.parse_args()

    # 路径准备
    model_path = Path(args.model_path)
    val_file = Path(args.val_data)
    image_dir = Path(args.image_dir)
    output_file = Path(args.output_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("🎯 暖通构件识别评估")
    print("="*70)
    print(f"模型路径: {model_path}")
    print(f"验证集: {val_file}")
    print(f"图像目录: {image_dir}")
    print(f"设备: {args.device}")
    print("="*70)

    # 加载验证数据
    print("\n📂 加载验证集...")
    val_data = load_validation_data(val_file, image_dir)
    print(f"✓ 加载 {len(val_data)} 个验证样本")

    if not val_data:
        print("\n❌ 错误：验证集为空！")
        return

    # 加载模型
    print(f"\n🔧 加载模型: {model_path}")
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForVision2Seq.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    ).to(args.device)
    model.eval()
    print("✓ 模型加载完成")

    # 评估
    results = evaluate(model, processor, val_data, args.device)

    # 打印结果
    print_results(results)

    # 保存结果
    print(f"\n💾 保存结果到: {output_file}")

    # 转换defaultdict为普通dict用于JSON序列化
    json_results = {
        "total": results["total"],
        "correct": results["correct"],
        "accuracy": results["accuracy"],
        "by_class": dict(results["by_class"]),
        "confusion_matrix": {
            gt: dict(preds) for gt, preds in results["confusion_matrix"].items()
        },
        "errors": results["errors"]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, ensure_ascii=False, indent=2)

    print("✅ 评估完成！")


if __name__ == "__main__":
    main()
