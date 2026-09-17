# 📚 文档导航指南

## 🎯 我应该看哪个文档？

根据你的需求，快速找到对应的文档：

---

## 🚀 我想快速开始训练
→ **阅读**: [QUICKSTART.md](QUICKSTART.md)

**包含内容**:
- 一键启动训练的3步流程
- 数据格式说明
- 训练参数配置
- 常见问题解决

**适合**: 已经了解基本概念，想立即开始训练

---

## 📖 我想全面了解项目
→ **阅读**: [README.md](README.md)

**包含内容**:
- 完整的项目介绍（8000+字）
- 两阶段训练详细说明
- 硬件要求与环境配置
- 性能调优建议
- 基座模型替换指南
- 完整的常见问题排查

**适合**: 首次使用，想深入理解项目

---

## 🏗️ 我想了解项目结构
→ **阅读**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

**包含内容**:
- 项目目录树
- 各模块功能说明
- 文件依赖关系
- 数据流程图

**适合**: 想修改代码或扩展功能

---

## 📋 我想查看所有文件
→ **阅读**: [FILE_MANIFEST.md](FILE_MANIFEST.md)

**包含内容**:
- 完整文件清单
- 每个文件的作用
- 文件是否需要修改
- 文件依赖关系

**适合**: 想了解项目完整性，检查缺失文件

---

## 📊 我想了解项目概况
→ **阅读**: [SUMMARY.md](SUMMARY.md)

**包含内容**:
- 项目完成清单
- 核心特性总结
- 技术栈说明
- 适用场景分析
- 项目亮点

**适合**: 快速了解项目能做什么，有什么特点

---

## ✅ 我想查看交付物
→ **阅读**: [DELIVERY_REPORT.md](DELIVERY_REPORT.md)

**包含内容**:
- 交付物统计
- 质量检查清单
- 使用流程总结
- 性能指标
- 后续扩展计划

**适合**: 项目验收，确认完整性

---

## 📅 我想查看版本历史
→ **阅读**: [CHANGELOG.md](CHANGELOG.md)

**包含内容**:
- 版本更新记录
- 新增功能列表
- 已知限制
- 未来计划

**适合**: 了解项目演进历史

---

## 🧭 推荐阅读顺序

### 新手用户
1. **QUICKSTART.md** - 快速上手
2. **README.md** - 深入理解
3. **PROJECT_STRUCTURE.md** - 了解结构

### 高级用户
1. **SUMMARY.md** - 快速了解全貌
2. **FILE_MANIFEST.md** - 查看文件清单
3. **README.md** - 查询特定问题

### 开发者
1. **PROJECT_STRUCTURE.md** - 了解架构
2. **README.md** - 查看API和参数
3. **FILE_MANIFEST.md** - 确认依赖关系

---

## 📑 文档矩阵

| 文档 | 长度 | 详细度 | 适合场景 |
|-----|------|--------|---------|
| QUICKSTART.md | 短 | ⭐⭐ | 快速启动 |
| README.md | 长 | ⭐⭐⭐⭐⭐ | 完整参考 |
| PROJECT_STRUCTURE.md | 中 | ⭐⭐⭐ | 架构理解 |
| FILE_MANIFEST.md | 中 | ⭐⭐⭐⭐ | 文件查询 |
| SUMMARY.md | 中 | ⭐⭐⭐⭐ | 功能概览 |
| DELIVERY_REPORT.md | 长 | ⭐⭐⭐⭐⭐ | 交付验收 |
| CHANGELOG.md | 短 | ⭐⭐ | 版本历史 |

---

## 🔍 按问题查找文档

### 环境相关
**Q: 如何配置环境？**  
→ [README.md § 环境准备](README.md#环境准备)

**Q: 如何验证环境？**  
→ [QUICKSTART.md § 环境准备](QUICKSTART.md#环境准备)

### 训练相关
**Q: 如何开始训练？**  
→ [QUICKSTART.md § 开始训练](QUICKSTART.md#开始训练)

**Q: 如何调整超参数？**  
→ [QUICKSTART.md § 自定义配置](QUICKSTART.md#自定义配置)

**Q: 两阶段训练的原理？**  
→ [README.md § 两阶段训练详解](README.md#两阶段训练详解)

### 数据相关
**Q: 数据格式是什么？**  
→ [QUICKSTART.md § 数据准备](QUICKSTART.md#数据准备)

**Q: 如何准备自己的数据？**  
→ [README.md § 数据准备](README.md#数据准备)

### 模型相关
**Q: 如何替换基座模型？**  
→ [README.md § 基座模型替换](README.md#基座模型替换)

**Q: 如何合并LoRA权重？**  
→ [QUICKSTART.md § 合并权重](QUICKSTART.md#合并权重)

### 问题排查
**Q: 训练遇到错误怎么办？**  
→ [README.md § 常见问题排查](README.md#常见问题排查)

**Q: 性能不理想怎么优化？**  
→ [README.md § 性能调优](README.md#性能调优)

### 架构理解
**Q: 项目文件有哪些？**  
→ [FILE_MANIFEST.md](FILE_MANIFEST.md)

**Q: 各模块的作用是什么？**  
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 💡 快速命令

```bash
# 查看快速启动指南
cat QUICKSTART.md

# 查看完整文档
cat README.md

# 查看项目结构
cat PROJECT_STRUCTURE.md

# 查看文件清单
cat FILE_MANIFEST.md

# 查看项目总结
cat SUMMARY.md

# 查看交付报告
cat DELIVERY_REPORT.md
```

---

## 🎯 使用建议

### 首次使用
1. 先看 **SUMMARY.md** 了解全貌（5分钟）
2. 再看 **QUICKSTART.md** 快速上手（10分钟）
3. 遇到问题查 **README.md** 对应章节

### 日常使用
- 有疑问 → 搜索 **README.md**
- 改代码 → 查看 **PROJECT_STRUCTURE.md**
- 报错了 → 查看 **README.md § 常见问题**

### 项目交接
1. **DELIVERY_REPORT.md** - 交付物确认
2. **SUMMARY.md** - 功能清单
3. **README.md** - 使用手册

---

## 📞 还是找不到答案？

1. **搜索文档**: 使用 `grep "关键词" *.md` 搜索所有文档
2. **查看代码注释**: 核心脚本都有详细注释
3. **运行验证脚本**: `bash scripts/verify_env.sh`
4. **查看官方文档**: https://docs.habana.ai/

---

**提示**: 所有Markdown文档都支持GitHub渲染，推送后在网页查看体验更佳！
