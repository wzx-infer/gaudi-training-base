#!/usr/bin/env python
"""
MechVQA 评估脚本

功能：
1. 加载训练后的模型（或baseline模型）
2. 在验证集上推理
3. 计算评估指标：Accuracy, F1, BLEU
4. 保存结果和预测
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from tqdm import tqdm
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
from peft import PeftModel


def extract_answer(text: str) -> str:
    """从模型输出中提取answer部分"""
    # 匹配 <answer>...</answer>
    match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 如果没有answer标签，返回think之后的内容或全部内容
    match = re.search(r'</think>\s*(.*)', text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def calculate_metrics(predictions: List[str], references: List[str]) -> Dict:
    """计算评估指标"""
    from collections import Counter

    # Exact Match Accuracy
    exact_matches = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
    accuracy = exact_matches / len(predictions)

    # Token-level F1
    f1_scores = []
    for pred, ref in zip(predictions, references):
        pred_tokens = set(pred.split())
        ref_tokens = set(ref.split())

        if len(pred_tokens) == 0 and len(ref_tokens) == 0:
            f1_scores.append(1.0)
        elif len(pred_tokens) == 0 or len(ref_tokens) == 0:
            f1_scores.append(0.0)
        else:
            common = pred_tokens & ref_tokens
            precision = len(common) / len(pred_tokens)
            recall = len(common) / len(ref_tokens)
            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0.0
            f1_scores.append(f1)

    avg_f1 = sum(f1_scores) / len(f1_scores)

    # BLEU-4 (simple implementation)
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        bleu_scores = []
        smoothing = SmoothingFunction().method1
        for pred, ref in zip(predictions, references):
            score = sentence_bleu([ref.split()], pred.split(), smoothing_function=smoothing)
            bleu_scores.append(score)
        avg_bleu = sum(bleu_scores) / len(bleu_scores)
    except ImportError:
        print("Warning: NLTK not installed, skipping BLEU calculation")
        avg_bleu = 0.0

    return {
        'accuracy': accuracy,
        'f1': avg_f1,
        'bleu': avg_bleu,
        'total_samples': len(predictions),
        'exact_matches': exact_matches
    }


def load_model(model_path: str, base_model: str = None):
    """加载模型和tokenizer"""
    print(f"Loading model from: {model_path}")

    # 判断是否是LoRA checkpoint
    is_lora = os.path.exists(os.path.join(model_path, "adapter_config.json"))

    if is_lora:
        if base_model is None:
            base_model = "/models/Qwen/Qwen3.8-27B"
        print(f"  Loading base model: {base_model}")
        print(f"  Loading LoRA adapter: {model_path}")

        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        model = PeftModel.from_pretrained(model, model_path)
        model = model.merge_and_unload()

        processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=True)
    else:
        print(f"  Loading full model: {model_path}")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

    model.eval()
    return model, processor


def inference_on_dataset(model, processor, data_path: str, images_dir: str, max_samples: int = None):
    """在数据集上推理"""
    print(f"\nRunning inference on: {data_path}")

    # 加载数据
    with open(data_path, 'r') as f:
        data = json.load(f)

    if max_samples:
        data = data[:max_samples]
        print(f"  Limited to first {max_samples} samples")

    predictions = []
    references = []

    for item in tqdm(data, desc="Inference"):
        # 提取问题和参考答案
        messages = item['messages']
        question = messages[0]['content']
        reference = extract_answer(messages[1]['content'])

        # TODO: 加载图片并推理
        # 这里需要实现实际的推理逻辑
        # pred = model.generate(...)

        # 临时：使用参考答案作为预测（用于测试）
        pred = f"[Placeholder prediction for: {question[:50]}...]"

        predictions.append(pred)
        references.append(reference)

    return predictions, references


def main():
    parser = argparse.ArgumentParser(description="Evaluate MechVQA model")
    parser.add_argument('--model_path', type=str, required=True, help='Path to model or LoRA adapter')
    parser.add_argument('--base_model', type=str, default='/models/Qwen/Qwen3.8-27B', help='Base model for LoRA')
    parser.add_argument('--data_path', type=str, default='data/mechvqa/converted/val.json', help='Validation data')
    parser.add_argument('--images_dir', type=str, default='data/mechvqa/images', help='Images directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Output directory for results')
    parser.add_argument('--max_samples', type=int, default=None, help='Max samples to evaluate')
    parser.add_argument('--baseline', action='store_true', help='Evaluate baseline (no training)')

    args = parser.parse_args()

    print("="*60)
    print("MechVQA Model Evaluation")
    print("="*60)
    print(f"Model: {args.model_path}")
    print(f"Data: {args.data_path}")
    print(f"Mode: {'Baseline' if args.baseline else 'Fine-tuned'}")

    # 加载模型
    # model, processor = load_model(args.model_path, args.base_model)

    # 推理
    # predictions, references = inference_on_dataset(
    #     model, processor, args.data_path, args.images_dir, args.max_samples
    # )

    # 临时：生成模拟数据用于测试流程
    print("\n⚠️  Using placeholder predictions for testing pipeline")
    predictions = [f"pred_{i}" for i in range(10)]
    references = [f"ref_{i}" for i in range(10)]

    # 计算指标
    print("\nCalculating metrics...")
    metrics = calculate_metrics(predictions, references)

    # 保存结果
    os.makedirs(args.output_dir, exist_ok=True)

    results = {
        'model_path': args.model_path,
        'data_path': args.data_path,
        'baseline': args.baseline,
        'metrics': metrics
    }

    results_path = Path(args.output_dir) / 'metrics.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    predictions_path = Path(args.output_dir) / 'predictions.json'
    with open(predictions_path, 'w') as f:
        json.dump({
            'predictions': predictions,
            'references': references
        }, f, ensure_ascii=False, indent=2)

    # 打印结果
    print("\n" + "="*60)
    print("Evaluation Results")
    print("="*60)
    print(f"Accuracy: {metrics['accuracy']:.4f} ({metrics['exact_matches']}/{metrics['total_samples']})")
    print(f"F1 Score: {metrics['f1']:.4f}")
    print(f"BLEU-4:   {metrics['bleu']:.4f}")
    print(f"\nResults saved to: {args.output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
