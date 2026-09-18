#!/usr/bin/env python3
"""
暖通构件识别推理演示
单张图纸 → 输出 think 推理 + 识别结果

用法:
    # 单张图片推理
    python inference_demo.py \
        --model_path outputs/models/qwen2_vl_merged \
        --image path/to/hvac_drawing.jpg \
        --prompt "请识别这个构件"

    # 批量推理
    python inference_demo.py \
        --model_path outputs/models/qwen2_vl_merged \
        --image_dir data/images/hvac \
        --output_file results.jsonl
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Optional

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq


def inference(
    model,
    processor,
    image_path: str,
    prompt: str = "请识别图纸中的构件类型",
    device: str = "hpu",
    max_new_tokens: int = 512
) -> str:
    """
    单张图片推理

    Args:
        model: 加载的模型
        processor: 加载的processor
        image_path: 图片路径
        prompt: 用户提示
        device: 推理设备
        max_new_tokens: 最大生成token数

    Returns:
        模型生成的文本（包含think推理）
    """
    # 加载图像
    image = Image.open(image_path).convert("RGB")

    # 构造对话
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
    text = processor.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=True
    )

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
            max_new_tokens=max_new_tokens,
            do_sample=False,  # 确定性输出
            temperature=1.0,
            top_p=1.0
        )

    # 解码（只取生成的部分）
    generated_text = processor.batch_decode(
        output_ids[:, inputs['input_ids'].shape[1]:],
        skip_special_tokens=True
    )[0]

    return generated_text


def batch_inference(
    model,
    processor,
    image_dir: Path,
    prompt: str,
    device: str,
    extensions: List[str] = ['.jpg', '.jpeg', '.png']
) -> List[dict]:
    """
    批量推理目录下所有图片

    Returns:
        推理结果列表
    """
    results = []

    # 收集所有图片
    image_files = []
    for ext in extensions:
        image_files.extend(image_dir.glob(f"*{ext}"))
        image_files.extend(image_dir.glob(f"*{ext.upper()}"))

    print(f"\n找到 {len(image_files)} 张图片")
    print("="*70)

    for img_path in image_files:
        print(f"\n处理: {img_path.name}")

        try:
            output = inference(model, processor, str(img_path), prompt, device)

            result = {
                "image": img_path.name,
                "prompt": prompt,
                "output": output
            }

            results.append(result)

            # 打印结果
            print(f"结果: {output}")

        except Exception as e:
            print(f"⚠️ 推理失败: {e}")
            results.append({
                "image": img_path.name,
                "prompt": prompt,
                "output": f"ERROR: {str(e)}"
            })

    return results


def parse_output(text: str) -> dict:
    """
    解析模型输出，提取think和识别结果

    Returns:
        {
            "think": "推理过程",
            "result": "识别结果"
        }
    """
    think = ""
    result = text

    # 提取think内容
    if "<think>" in text and "</think>" in text:
        think_start = text.find("<think>") + 7
        think_end = text.find("</think>")
        think = text[think_start:think_end].strip()

        # 剩余部分是识别结果
        result = text[think_end + 8:].strip()

    return {
        "think": think,
        "result": result
    }


def main():
    parser = argparse.ArgumentParser(description="暖通构件识别推理演示")

    # 模型参数
    parser.add_argument("--model_path", required=True, help="模型路径")
    parser.add_argument("--device", default="hpu", choices=["hpu", "cuda", "cpu"],
                       help="推理设备")

    # 输入参数（二选一）
    parser.add_argument("--image", help="单张图片路径")
    parser.add_argument("--image_dir", help="图片目录（批量推理）")

    # 推理参数
    parser.add_argument("--prompt", default="请识别图纸中的构件类型",
                       help="用户提示")
    parser.add_argument("--max_new_tokens", type=int, default=512,
                       help="最大生成token数")

    # 输出参数
    parser.add_argument("--output_file", help="结果保存路径（JSONL格式）")
    parser.add_argument("--parse", action="store_true",
                       help="解析输出，分离think和结果")

    args = parser.parse_args()

    if not args.image and not args.image_dir:
        parser.error("必须指定 --image 或 --image_dir")

    # 加载模型
    print("="*70)
    print("🎯 暖通构件识别推理")
    print("="*70)
    print(f"模型路径: {args.model_path}")
    print(f"设备: {args.device}")
    print("="*70)

    print("\n🔧 加载模型...")
    processor = AutoProcessor.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForVision2Seq.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    ).to(args.device)
    model.eval()
    print("✓ 模型加载完成\n")

    # 推理
    if args.image:
        # 单张图片推理
        print("="*70)
        print(f"📷 图片: {args.image}")
        print(f"💬 提示: {args.prompt}")
        print("="*70)

        output = inference(
            model, processor,
            args.image,
            args.prompt,
            args.device,
            args.max_new_tokens
        )

        if args.parse:
            parsed = parse_output(output)
            print("\n🧠 Think 推理:")
            print("-"*70)
            print(parsed["think"])
            print("\n✅ 识别结果:")
            print("-"*70)
            print(parsed["result"])
        else:
            print("\n📝 模型输出:")
            print("-"*70)
            print(output)

        print("\n" + "="*70)

        # 保存结果
        if args.output_file:
            result = {
                "image": args.image,
                "prompt": args.prompt,
                "output": output
            }
            if args.parse:
                result.update(parse_output(output))

            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✓ 结果已保存到: {args.output_file}")

    else:
        # 批量推理
        image_dir = Path(args.image_dir)
        results = batch_inference(
            model, processor,
            image_dir,
            args.prompt,
            args.device
        )

        print("\n" + "="*70)
        print(f"✅ 批量推理完成，处理了 {len(results)} 张图片")
        print("="*70)

        # 保存结果
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    if args.parse:
                        result.update(parse_output(result["output"]))
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')
            print(f"✓ 结果已保存到: {args.output_file}")


if __name__ == "__main__":
    main()
