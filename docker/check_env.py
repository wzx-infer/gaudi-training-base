#!/usr/bin/env python3
"""
Gaudi2 训练环境依赖版本检查脚本
用于验证容器内依赖是否符合版本锁定要求
"""

import sys

def check_version(package_name, expected_version, allow_dev=False):
    """检查单个包的版本"""
    try:
        if package_name == "torch":
            import torch
            actual_version = torch.__version__
        elif package_name == "transformers":
            import transformers
            actual_version = transformers.__version__
        elif package_name == "accelerate":
            import accelerate
            actual_version = accelerate.__version__
        elif package_name == "peft":
            import peft
            actual_version = peft.__version__
        elif package_name == "tokenizers":
            import tokenizers
            actual_version = tokenizers.__version__
        elif package_name == "optimum-habana":
            import optimum.habana
            # optimum-habana 版本可能在 optimum 包中
            try:
                actual_version = optimum.habana.__version__
            except:
                import optimum
                actual_version = optimum.__version__
        elif package_name == "datasets":
            import datasets
            actual_version = datasets.__version__
        elif package_name == "deepspeed":
            import deepspeed
            actual_version = deepspeed.__version__
        else:
            return None, "未知包"

        # 开发版本处理 (例如 2.11.0a0+git009b5f6)
        if allow_dev and "+" in actual_version:
            actual_version = actual_version.split("+")[0]

        # 版本比对
        match = actual_version.startswith(expected_version)
        return actual_version, "✓" if match else "✗"

    except ImportError:
        return None, "未安装"
    except Exception as e:
        return None, f"错误: {e}"


def main():
    print("=" * 60)
    print("Gaudi2 训练环境依赖版本检查")
    print("=" * 60)
    print()

    # 定义期望的版本
    requirements = [
        ("torch", "2.11.0", True),                    # 允许开发版本
        ("transformers", "4.48.3", False),            # 必须严格匹配
        ("tokenizers", "0.19.1", False),
        ("accelerate", "0.31.0", False),              # LLaMA-Factory 关键依赖
        ("peft", "0.11.1", False),
        ("optimum-habana", "1.24.1", False),
        ("datasets", "2.20.0", False),
        ("deepspeed", "0.", True),                    # DeepSpeed 版本不严格要求
    ]

    all_pass = True

    for package, expected, allow_dev in requirements:
        actual, status = check_version(package, expected, allow_dev)

        if actual:
            print(f"{package:20s} | 期望: {expected:10s} | 实际: {actual:20s} | {status}")
        else:
            print(f"{package:20s} | 期望: {expected:10s} | {status}")
            all_pass = False

    print()
    print("=" * 60)

    # 关键检查：AutoModelForVision2Seq 是否存在
    print("\n关键功能检查:")
    try:
        from transformers import AutoModelForVision2Seq
        print("✓ AutoModelForVision2Seq 可导入 (Qwen2-VL 支持)")
    except ImportError:
        print("✗ AutoModelForVision2Seq 不可导入 - transformers 版本过高!")
        all_pass = False

    # HPU 环境检查
    print("\nHPU 环境变量:")
    import os
    hpu_vars = [
        "PT_HPU_LAZY_MODE",
        "PT_HPU_ENABLE_LAZY_COLLECTIVES",
        "HABANA_VISIBLE_DEVICES"
    ]
    for var in hpu_vars:
        value = os.environ.get(var, "未设置")
        print(f"  {var}: {value}")

    print()
    if all_pass:
        print("✓ 所有依赖版本检查通过")
        return 0
    else:
        print("✗ 存在版本冲突，请检查 Dockerfile")
        return 1


if __name__ == "__main__":
    sys.exit(main())
