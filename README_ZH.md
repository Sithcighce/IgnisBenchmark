# 🚀 智能题目生成系统

**流体力学、燃烧科学与航空航天工程专用**

[中文版](#中文版) | [English](README_EN.md)

---

## 🌟 项目概述

基于大语言模型的自动化题目生成与评估系统，专门针对**流体力学**、**燃烧科学**和**航空航天工程**领域设计。系统能够生成具有挑战性的题目，用于评估和提升AI模型在这些专业领域的能力。

> 💡 **其他领域适用**: 虽然专为流体/燃烧领域优化，但其他领域的研究者可以通过修改提示模板轻松适配，为自己的模型创建专业题集。

## ✨ 核心特性

- 🎯 **领域专业化**: 专注于流体力学、燃烧科学和航空航天工程
- 🤖 **多模型支持**: 集成Gemini、DeepSeek、Qwen、Yi、Llama模型，支持自动切换
- 🔄 **鲁棒性管道**: 自动模型切换确保生成任务的高可靠性
- 📊 **双重资产积累**: 正确答案（验证集）和挑战性题目（基准库）分别存储
- 🎨 **题目浏览器**: 交互式HTML查看器，方便审阅题目内容
- 🛠️ **完整工具链**: 数据清理、验证、分析和可视化工具
- 🌍 **多语言支持**: 支持英文和中文界面

## 🏗️ 系统架构

```
questions/
├── 📊 数据层
│   ├── data/                    # 数据文件
│   │   ├── benchmark_bank.jsonl # 挑战性题目（模型失败）
│   │   ├── validation_set.jsonl # 验证题目（模型成功）
│   │   └── seed_examples.jsonl  # 高质量种子样本
├── 🧠 核心模块
│   ├── src/                     # 源代码
│   │   ├── question_generator.py # 多模型切换的题目生成器
│   │   ├── answering_module.py   # 答案生成模块
│   │   ├── grading_module.py     # 自动判题系统
│   │   └── data_persistence.py   # 数据存储管理
├── 🎯 提示工程
│   ├── prompts/                 # 提示模板
│   │   ├── 生成题Prompt.md       # 题目生成提示
│   │   ├── 解题Prompt.md         # 问题求解提示
│   │   └── 判题Prompt.md         # 判题提示
├── 🛠️ 工具脚本
│   └── scripts/                 # 实用工具
│       ├── clean_benchmark.py   # 数据清理工具
│       ├── validate_system.py   # 系统验证
│       └── visualize_data.py    # 题目浏览器生成器
└── 🖥️ 用户界面
    ├── run.py                   # 主程序入口
    ├── app.py                   # 图形界面
    └── main.py                 # 命令行界面
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 大语言模型API密钥（Gemini、DeepSeek等）
- 支持的操作系统：Windows、macOS、Linux

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/Sithcighce/distillation_generation.git
cd questions

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.yaml.example config.yaml
# 编辑 config.yaml 添加您的API密钥
```

### 使用方法

**统一程序入口:**
```bash
# 图形界面（推荐）
python run.py --mode gui

# 命令行界面  
python run.py --mode cli

# 直接生成题目
python run.py --mode generate -n 20 -r 3

# 导出基准库为Markdown文件
python run.py --mode output

# 清理基准数据
python run.py --mode clean
```

## 系统支持根据不同难度或风格自定义Prompt模板。
你可以在 prompts 目录下添加如 生成题Prompt_higherlever.md、生成题Prompt_easy.md 等文件。

如何使用自定义Prompt：

在 prompts 目录下新建你的Prompt文件，例如：
生成题Prompt_higherlever.md
生成题Prompt_easy.md
在代码中手动读取对应Prompt文件：
（可选）你也可以在 prompt_manager.py 中根据难度参数选择不同Prompt。


## 📊 数据分析与可视化

导出基准库为Markdown文件以查看所有题目：

```bash
python run.py --mode output
```

这将在 `./output/all_by_score_asc_md` 下生成按分数排序的 Markdown 文件，包含：
- 📋 **选项卡界面**: 验证集、基准库和种子样本的分别显示
- 🔍 **详细视图**: 完整的题目文本、标准答案和模型回答
- 📊 **快速统计**: 成功率和题目数量
- 🎨 **简洁设计**: 易于阅读的格式，带有颜色编码的题目类型

## 🔧 系统维护

```bash
# 数据清理（移除判题系统错误）
python run.py --mode clean

# 系统验证（检查组件）
python run.py --mode validate

# 查看日志
cat logs/system.log
```

## 📈 当前性能

基于最新测试：
- 📊 **题目总数**: 100+
- 🎯 **成功率**: ~16%
- 🔬 **领域专注**: 流体力学、燃烧科学、航空航天
- 🤖 **模型数量**: 5个LLM提供商，支持自动切换

## 🛠️ 其他领域定制

要将此系统适配到您的研究领域：

1. **编辑提示模板**: 修改 `prompts/生成题Prompt.md`
   ```markdown
   # DISCIPLINES TO EXPLORE
   专注于您的特定领域:
   * **您的领域**: 具体主题和概念
   * **相关数学**: 相关数学基础
   * **应用**: 您领域中的实际应用
   ```

2. **更新示例**: 在提示中添加领域特定的示例
3. **调整难度**: 根据目标受众修改难度级别
4. **测试与迭代**: 运行小批量测试并根据结果优化

## 💡 使用场景

### 研究人员
- **模型评估**: 使用专业题库评估AI模型在流体力学领域的能力
- **弱点发现**: 通过错题分析发现模型的知识盲区
- **训练数据**: 将挑战性题目用于模型微调和改进

### 教育工作者
- **高级教学**: 将"AI也会答错的题目"用于研究生课程教学
- **前沿探讨**: 探讨AI认知边界，激发学生深度思考

### 工程师
- **技术评测**: 评估AI助手在实际工程问题上的可靠性
- **质量控制**: 建立专业领域的AI能力基准

## 🤝 贡献指南

欢迎贡献！请：
1. Fork 此仓库
2. 创建功能分支
3. 添加测试和文档
4. 提交 Pull Request

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

*为推进AI在流体力学和燃烧科学领域的能力而构建 ❤️*