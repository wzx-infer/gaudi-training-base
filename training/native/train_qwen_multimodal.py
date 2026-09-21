#!/usr/bin/env python3
"""
Gaudi2 8卡多模态大模型训练脚本
示例基座：Qwen2.5-VL-7B-Instruct（可替换为其他多模态模型）

训练分两阶段：
  阶段1：冻结LLM+视觉编码器，仅训练图像投影层
  阶段2：冻结视觉编码器，LoRA微调LLM主干

设计原则：基座无关，便于替换其他多模态大模型
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import torch
from torch.utils.data import Dataset
from PIL import Image
from transformers import (
    AutoProcessor,
    Qwen2VLForConditionalGeneration,
    TrainingArguments,
    Trainer,
    HfArgumentParser,
)
from peft import LoraConfig, get_peft_model, TaskType
import habana_frameworks.torch.core as htcore
import habana_frameworks.torch.distributed.hccl as hccl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# 模型配置（基座替换入口）
# ============================================================
@dataclass
class ModelArguments:
    model_name_or_path: str = field(
        default="Qwen/Qwen2.5-VL-7B-Instruct",
        metadata={"help": "多模态基座模型路径，可替换为其他模型"}
    )
    vision_encoder_name: Optional[str] = field(
        default=None,
        metadata={"help": "视觉编码器路径（若模型内置则无需指定）"}
    )
    cache_dir: Optional[str] = field(default=None)
    trust_remote_code: bool = field(default=True)


@dataclass
class DataArguments:
    data_path: str = field(
        default="data/train_cad.jsonl",
        metadata={"help": "训练数据路径"}
    )
    image_folder: str = field(
        default="data/images",
        metadata={"help": "图像文件夹路径"}
    )
    max_length: int = field(default=2048)


@dataclass
class TrainingStage:
    stage: int = field(
        default=1,
        metadata={"help": "训练阶段：1=投影层预训练，2=LoRA指令微调"}
    )
    lora_r: int = field(default=64)
    lora_alpha: int = field(default=128)
    lora_dropout: float = field(default=0.05)
    lora_target_modules: str = field(
        default="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj",
        metadata={"help": "LoRA目标模块，逗号分隔"}
    )


# ============================================================
# 数据集（支持Qwen多模态格式，可扩展到其他格式）
# ============================================================
class MultimodalCADDataset(Dataset):
    """CAD图纸识图数据集，遵循Qwen对话格式"""

    def __init__(
        self,
        data_path: str,
        processor: Any,
        image_folder: str,
        max_length: int = 2048,
    ):
        self.processor = processor
        self.image_folder = image_folder
        self.max_length = max_length

        # 加载JSONL数据
        self.data = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                self.data.append(json.loads(line.strip()))

        logger.info(f"✓ 加载 {len(self.data)} 条训练样本")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        messages = item["messages"]

        # 提取用户输入（图像+文本）
        user_message = messages[0]["content"]
        assistant_message = messages[1]["content"]

        # 解析图像路径
        image_path = None
        text_prompt = ""
        for content in user_message:
            if content["type"] == "image":
                image_path = os.path.join(self.image_folder, content["image"])
            elif content["type"] == "text":
                text_prompt = content["text"]

        # 加载图像（CPU侧预处理）
        image = Image.open(image_path).convert("RGB") if image_path else None

        # 构造对话格式（适配Qwen，可根据其他模型调整）
        conversation = [
            {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": text_prompt}]},
            {"role": "assistant", "content": assistant_message}
        ]

        # Processor编码
        text = self.processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=False)
        inputs = self.processor(
            text=text,
            images=image,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
        )

        # 准备训练标签
        labels = inputs["input_ids"].clone()
        # 找到assistant回复起始位置，之前的部分mask掉
        assistant_start = text.find("<|im_start|>assistant")
        if assistant_start != -1:
            tokenized_prefix = self.processor.tokenizer(
                text[:assistant_start],
                add_special_tokens=False
            )["input_ids"]
            labels[0, :len(tokenized_prefix)] = -100

        return {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "pixel_values": inputs.get("pixel_values", torch.zeros(1, 3, 224, 224)).squeeze(0),
            "labels": labels.squeeze(0),
        }


# ============================================================
# 模型冻结策略
# ============================================================
def freeze_model_components(model, stage: int):
    """
    阶段1：冻结LLM+视觉编码器，仅训练投影层
    阶段2：冻结视觉编码器，LoRA微调LLM
    """
    trainable_modules = []

    if stage == 1:
        logger.info("🔒 阶段1：冻结LLM主干和视觉编码器，训练投影层")
        for name, param in model.named_parameters():
            param.requires_grad = False
            # 解冻投影层（通常命名为visual_projection, mm_projector, merger等）
            if any(key in name.lower() for key in ["projector", "projection", "adapter", "merger"]):
                param.requires_grad = True
                trainable_modules.append(name)

    elif stage == 2:
        logger.info("🔒 阶段2：冻结视觉编码器，LoRA微调LLM主干")
        for name, param in model.named_parameters():
            # 冻结视觉编码器
            if any(key in name.lower() for key in ["visual", "vision", "vit"]):
                param.requires_grad = False
            # 收集可训练模块（LoRA层）
            elif param.requires_grad:
                trainable_modules.append(name)

    # 统计参数
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())

    logger.info(f"📊 可训练参数: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")

    # 打印可训练模块清单
    if trainable_modules:
        logger.info(f"✅ 可训练模块清单 ({len(trainable_modules)} 个):")
        for module in trainable_modules[:20]:  # 最多显示前20个
            logger.info(f"  - {module}")
        if len(trainable_modules) > 20:
            logger.info(f"  ... 还有 {len(trainable_modules)-20} 个模块")
    else:
        logger.warning("⚠️ 警告：没有找到可训练模块！请检查freeze策略")

    return trainable_modules


# ============================================================
# 主训练流程
# ============================================================
def main():
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingStage, TrainingArguments))
    model_args, data_args, stage_args, training_args = parser.parse_args_into_dataclasses()

    # 验证Lazy模式
    assert os.environ.get("PT_HPU_LAZY_MODE") == "1", "❌ 必须设置 PT_HPU_LAZY_MODE=1"
    logger.info("✓ 检测到Lazy模式启用")

    # 加载processor和模型
    logger.info(f"🔧 加载基座模型: {model_args.model_name_or_path}")
    processor = AutoProcessor.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        cache_dir=model_args.cache_dir,
    )

    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        cache_dir=model_args.cache_dir,
        torch_dtype=torch.bfloat16,
    )

    # 应用训练策略
    if stage_args.stage == 1:
        freeze_model_components(model, stage=1)
    elif stage_args.stage == 2:
        freeze_model_components(model, stage=2)
        # 应用LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=stage_args.lora_r,
            lora_alpha=stage_args.lora_alpha,
            lora_dropout=stage_args.lora_dropout,
            target_modules=stage_args.lora_target_modules.split(","),
            bias="none",
        )
        model = get_peft_model(model, lora_config)
        logger.info("✓ 已应用LoRA配置")

    # 移动到HPU
    model = model.to("hpu")

    # 加载数据集
    train_dataset = MultimodalCADDataset(
        data_path=data_args.data_path,
        processor=processor,
        image_folder=data_args.image_folder,
        max_length=data_args.max_length,
    )

    # 自定义Trainer（适配Gaudi）
    class GaudiMultimodalTrainer(Trainer):
        def training_step(self, model, inputs):
            model.train()
            inputs = self._prepare_inputs(inputs)

            with torch.autocast(device_type="hpu", dtype=torch.bfloat16):
                outputs = model(**inputs)
                loss = outputs.loss

            if self.args.gradient_accumulation_steps > 1:
                loss = loss / self.args.gradient_accumulation_steps

            self.accelerator.backward(loss)
            htcore.mark_step()  # Lazy模式同步点

            return loss.detach()

    # 开始训练
    trainer = GaudiMultimodalTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=processor.tokenizer,
    )

    logger.info(f"🚀 开始阶段{stage_args.stage}训练")
    trainer.train()

    # 保存模型
    trainer.save_model(training_args.output_dir)
    processor.save_pretrained(training_args.output_dir)
    logger.info(f"✅ 训练完成，权重保存至: {training_args.output_dir}")


if __name__ == "__main__":
    main()
