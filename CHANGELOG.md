# 更新日志

## [1.0.0] - 2026-09-17

### ✨ 初始发布

#### 核心功能
- 🎯 **两阶段训练**: 投影层预训练 + LoRA指令微调
- 🔧 **基座无关设计**: 以Qwen2.5-VL-7B为示例，支持替换其他多模态模型
- 🚀 **DeepSpeed ZeRO-2**: 8卡高效分布式训练
- 💡 **Lazy模式优化**: 图编译、算子融合、计算通信重叠
- 🧠 **think输出范式**: 强制模型输出推理过程+识别结果
- 📊 **TensorBoard监控**: 实时可视化训练指标

#### 训练脚本
- `train_qwen_multimodal.py`: 完整训练流程，支持两阶段切换
- `merge_lora.py`: LoRA权重合并工具

#### 自动化脚本
- `scripts/train_stage1.sh`: 阶段1一键启动
- `scripts/train_stage2.sh`: 阶段2一键启动
- `scripts/run_container.sh`: Docker容器快速启动
- `scripts/verify_env.sh`: 环境验证脚本
- `scripts/init_and_push.sh`: Git仓库初始化

#### 配置文件
- `ds_config_gaudi_z2.json`: DeepSpeed ZeRO-2配置
- `env.sh`: Gaudi2训练环境变量
- `Dockerfile`: 基于Habana 1.24.1官方镜像

#### 文档
- `README.md`: 完整使用文档（110+节）
- `QUICKSTART.md`: 快速启动指南
- `PROJECT_STRUCTURE.md`: 项目结构说明
- `FILE_MANIFEST.md`: 完整文件清单

#### 数据样例
- `data/train_cad.jsonl`: CAD图纸标注样例（3条）
- 支持Qwen多模态对话格式

### 🔧 技术栈

| 组件 | 版本 |
|-----|------|
| Synapse AI | 1.24.1 |
| Habana PyTorch | 2.11.0 |
| optimum-habana | 1.24.1 |
| transformers | 4.48.2 |
| peft | 0.11.1 |
| DeepSpeed | 1.24.1-habana |

### 📝 已知限制

- 仅支持Gaudi2训练，不支持推理部署
- 数据格式针对Qwen系列优化，其他基座需调整
- 需要手动准备训练数据集
- Lazy模式首次编译耗时30s-2min

### 🎯 适用场景

- CAD图纸识图任务
- 需要think推理链的多模态任务
- 需要替换不同多模态基座的场景
- Gaudi2 8卡集群训练

---

## 未来计划

### v1.1.0 (规划中)
- [ ] 支持更多基座模型的数据预处理适配
- [ ] 添加验证集评估脚本
- [ ] 支持多节点训练（16卡/32卡）
- [ ] 添加模型量化支持
- [ ] 提供推理示例代码

### v1.2.0 (规划中)
- [ ] 支持Gaudi3硬件
- [ ] 集成自动混合精度训练
- [ ] 添加模型评估指标
- [ ] 支持增量训练

---

## 版本说明

版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)：

- **主版本号（MAJOR）**: 不兼容的API修改
- **次版本号（MINOR）**: 向下兼容的功能新增
- **修订号（PATCH）**: 向下兼容的问题修正

---

**贡献者**: Claude Opus 5 (1M context)  
**协作**: @wangzhixiong
