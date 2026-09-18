#!/bin/bash

# 数据格式转换工具
# 将其他格式转换为 LLaMA-Factory 支持的 ShareGPT 格式

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def convert_to_sharegpt(input_file: str, output_file: str, format_type: str = "auto"):
    """
    转换数据格式为 ShareGPT 格式

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        format_type: 输入格式类型 (auto/alpaca/belle/...)
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    converted_data = []

    for item in data:
        # 自动检测格式
        if format_type == "auto":
            if "conversations" in item:
                format_type = "sharegpt"
            elif "instruction" in item:
                format_type = "alpaca"
            else:
                format_type = "custom"

        # 转换逻辑
        if format_type == "sharegpt":
            # 已经是 ShareGPT 格式
            converted_item = {
                "messages": item.get("conversations", item.get("messages", [])),
                "images": item.get("images", [])
            }

        elif format_type == "alpaca":
            # Alpaca 格式转换
            messages = []
            if item.get("instruction"):
                user_content = item["instruction"]
                if item.get("input"):
                    user_content += f"\n{item['input']}"

                messages.append({
                    "role": "user",
                    "content": user_content
                })

            if item.get("output"):
                messages.append({
                    "role": "assistant",
                    "content": item["output"]
                })

            converted_item = {
                "messages": messages,
                "images": item.get("images", [])
            }

        else:
            # 自定义格式
            print(f"⚠️  未知格式，跳过: {item}")
            continue

        converted_data.append(converted_item)

    # 保存转换结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 转换完成！")
    print(f"   输入: {input_file} ({len(data)} 条)")
    print(f"   输出: {output_file} ({len(converted_data)} 条)")


def validate_sharegpt(file_path: str):
    """验证 ShareGPT 格式数据"""

    with open(file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    errors = []

    for idx, item in enumerate(data):
        # 检查必需字段
        if "messages" not in item:
            errors.append(f"行 {idx+1}: 缺少 'messages' 字段")
            continue

        messages = item["messages"]
        if not isinstance(messages, list):
            errors.append(f"行 {idx+1}: 'messages' 应该是列表")
            continue

        # 检查对话格式
        for msg_idx, msg in enumerate(messages):
            if "role" not in msg:
                errors.append(f"行 {idx+1}, 消息 {msg_idx+1}: 缺少 'role' 字段")
            if "content" not in msg:
                errors.append(f"行 {idx+1}, 消息 {msg_idx+1}: 缺少 'content' 字段")

            if msg.get("role") not in ["user", "assistant", "system"]:
                errors.append(f"行 {idx+1}, 消息 {msg_idx+1}: 无效的 role '{msg.get('role')}'")

    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for error in errors[:10]:  # 只显示前10个
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... 还有 {len(errors)-10} 个错误")
        return False
    else:
        print(f"✅ 验证通过！共 {len(data)} 条数据")
        return True


def add_think_tags(input_file: str, output_file: str):
    """为数据添加 <think> 标签（用于训练思考能力）"""

    with open(input_file, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    modified_count = 0

    for item in data:
        for msg in item.get("messages", []):
            if msg.get("role") == "assistant":
                content = msg["content"]
                # 如果还没有 think 标签，添加一个模板
                if "<think>" not in content:
                    msg["content"] = "<think>\n让我分析一下这个问题...\n</think>\n" + content
                    modified_count += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 添加 think 标签完成！修改了 {modified_count} 条数据")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据格式转换工具")
    parser.add_argument("command", choices=["convert", "validate", "add-think"],
                       help="操作类型")
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--format", default="auto",
                       help="输入格式 (auto/alpaca/sharegpt)")

    args = parser.parse_args()

    if args.command == "convert":
        if not args.output:
            print("❌ convert 命令需要 --output 参数")
            sys.exit(1)
        convert_to_sharegpt(args.input, args.output, args.format)

    elif args.command == "validate":
        validate_sharegpt(args.input)

    elif args.command == "add-think":
        if not args.output:
            print("❌ add-think 命令需要 --output 参数")
            sys.exit(1)
        add_think_tags(args.input, args.output)
