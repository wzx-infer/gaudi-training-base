#!/usr/bin/env python3
"""
LoRA权重合并脚本
将训练完成的LoRA适配器合并回基座模型，导出完整权重
"""

import argparse
import logging
from pathlib import Path

import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
from peft import PeftModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def merge_lora_weights(
    base_model_path: str,
    lora_adapter_path: str,
    output_path: str,
    trust_remote_code: bool = True,
):
    """
    合并LoRA适配器到基座模型

    Args:
        base_model_path: 原始基座模型路径
        lora_adapter_path: LoRA适配器路径（训练输出目录）
        output_path: 合并后模型保存路径
        trust_remote_code: 是否信任远程代码
    """
    logger.info(f"🔧 加载基座模型: {base_model_path}")
    base_model = AutoModelForVision2Seq.from_pretrained(
        base_model_path,
        trust_remote_code=trust_remote_code,
        torch_dtype=torch.bfloat16,
        device_map="cpu",  # 合并在CPU进行，避免HPU显存占用
    )

    logger.info(f"🔧 加载LoRA适配器: {lora_adapter_path}")
    model = PeftModel.from_pretrained(
        base_model,
        lora_adapter_path,
        torch_dtype=torch.bfloat16,
    )

    logger.info("🔄 合并LoRA权重到基座模型...")
    merged_model = model.merge_and_unload()

    logger.info(f"💾 保存合并后的模型到: {output_path}")
    Path(output_path).mkdir(parents=True, exist_ok=True)
    merged_model.save_pretrained(
        output_path,
        safe_serialization=True,  # 使用safetensors格式
        max_shard_size="5GB",
    )

    # 保存processor配置
    logger.info("💾 保存processor配置")
    processor = AutoProcessor.from_pretrained(
        base_model_path,
        trust_remote_code=trust_remote_code,
    )
    processor.save_pretrained(output_path)

    logger.info("✅ LoRA权重合并完成！")
    logger.info(f"   完整模型路径: {output_path}")
    logger.info(f"   可直接用于推理或继续训练")


def main():
    parser = argparse.ArgumentParser(description="合并LoRA适配器到基座模型")
    parser.add_argument(
        "--base_model",
        type=str,
        required=True,
        help="原始基座模型路径",
    )
    parser.add_argument(
        "--lora_adapter",
        type=str,
        required=True,
        help="LoRA适配器路径（训练输出目录）",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="合并后模型保存路径",
    )
    parser.add_argument(
        "--trust_remote_code",
        action="store_true",
        default=True,
        help="是否信任远程代码",
    )

    args = parser.parse_args()

    merge_lora_weights(
        base_model_path=args.base_model,
        lora_adapter_path=args.lora_adapter,
        output_path=args.output,
        trust_remote_code=args.trust_remote_code,
    )


if __name__ == "__main__":
    main()
