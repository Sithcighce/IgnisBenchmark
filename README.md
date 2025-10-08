# 🚀 Intelligent Question Generation System

**Specialized for Fluid Mechanics, Combustion Science & Aerospace Engineering**

[English](#english) | [中文版](#中文版)

---

## English

### 🌟 Overview

An automated question generation and evaluation system powered by large language models, specifically designed for **fluid mechanics**, **combustion science**, and **aerospace engineering** research. The system generates challenging questions to evaluate and improve AI model capabilities in these specialized domains.

> 💡 **For Other Domains**: While optimized for fluid/combustion fields, researchers in other domains can easily adapt the system by modifying the prompt templates to create specialized question sets for their own models.

### ✨ Key Features

- 🎯 **Domain-Specialized**: Focused on fluid mechanics, combustion, and aerospace engineering
- 🤖 **Multi-Model Support**: Integrated Gemini, DeepSeek, Qwen, Yi, Llama models with automatic fallback
- 🔄 **Robust Pipeline**: Automatic model switching ensures high reliability in generation tasks
- 📊 **Dual Asset Accumulation**: Separate storage for correct answers (validation set) and challenging questions (benchmark)
- 🎨 **Question Browser**: Interactive HTML viewer for easy question content review
- 🛠️ **Complete Toolchain**: Data cleaning, validation, analysis, and visualization tools
- 🌍 **Multilingual**: Support for English and Chinese interfaces

### 🏗️ System Architecture

```
questions/
├── 📊 Data Layer
│   ├── data/                    # Data files
│   │   ├── benchmark_bank.jsonl # Challenging questions (model failed)
│   │   ├── validation_set.jsonl # Validation questions (model passed)
│   │   └── seed_examples.jsonl  # High-quality seed examples
├── 🧠 Core Modules
│   ├── src/                     # Source code
│   │   ├── question_generator.py # Question generator with multi-model fallback
│   │   ├── answering_module.py   # Answer generation module
│   │   ├── grading_module.py     # Automated grading system
│   │   └── data_persistence.py   # Data storage and management
├── 🎯 Prompt Engineering
│   ├── prompts/                 # Prompt templates
│   │   ├── 生成题Prompt.md       # Question generation prompts
│   │   ├── 解题Prompt.md         # Problem solving prompts
│   │   └── 判题Prompt.md         # Grading prompts
├── 🛠️ Tools & Scripts
│   └── scripts/                 # Utility scripts
│       ├── clean_benchmark.py   # Data cleaning utilities
│       ├── validate_system.py   # System validation
│       └── visualize_data.py    # Question browser generator
└── 🖥️ User Interfaces
    ├── run.py                   # Main entry point
    ├── app.py                   # GUI interface
    └── main.py                 # CLI interface
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- API keys for LLM services (Gemini, DeepSeek, etc.)
- Supported OS: Windows, macOS, Linux

#### Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/questions
cd questions

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config.yaml.example config.yaml
# Edit config.yaml to add your API keys
```

#### Usage

**Single Entry Point:**
```bash
# GUI Application (Recommended)
python run.py --mode gui

# Command Line Interface
python run.py --mode cli

# Generate questions directly
python run.py --mode generate -n 20 -r 3

# Generate question browser
python run.py --mode visualize

# Clean benchmark data
python run.py --mode clean
```

### 📊 Data Analysis & Visualization

Generate an interactive HTML browser to review all questions:

```bash
python run.py --mode visualize
```

This creates `question_browser.html` with:
- 📋 **Tabbed Interface**: Separate tabs for validation set, benchmark, and seed examples
- 🔍 **Detailed View**: Complete question text, standard answers, and model responses
- 📊 **Quick Stats**: Success rates and question counts
- 🎨 **Clean Design**: Easy-to-read formatting with color-coded question types

### 🔧 System Maintenance

```bash
# Data cleaning (remove grading system errors)
python run.py --mode clean

# System validation (check components)
python run.py --mode validate

# View logs
cat logs/system.log
```

### 📈 Current Performance

Based on latest testing:
- 📊 **Total Questions**: 100+
- 🎯 **Success Rate**: ~16%
- 🔬 **Domain Focus**: Fluid mechanics, combustion, aerospace
- 🤖 **Models**: 5 LLM providers with automatic fallback

### 🛠️ Customization for Other Domains

To adapt this system for your research domain:

1. **Edit Prompt Templates**: Modify `prompts/生成题Prompt.md`
   ```markdown
   # DISCIPLINES TO EXPLORE
   Focus on your specific domain:
   * **Your Field**: Specific topics and concepts
   * **Related Math**: Relevant mathematical foundations
   * **Applications**: Real-world applications in your domain
   ```

2. **Update Examples**: Add domain-specific examples in the prompt
3. **Adjust Difficulty**: Modify difficulty levels for your target audience
4. **Test & Iterate**: Run small batches and refine based on results

### 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests and documentation
4. Submit a pull request

### 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 中文版

### 🌟 项目概述

基于大语言模型的自动化题目生成与评估系统，专门针对**流体力学**、**燃烧科学**和**航空航天工程**领域设计。系统能够生成具有挑战性的题目，用于评估和提升AI模型在这些专业领域的能力。

> 💡 **其他领域适用**: 虽然专为流体/燃烧领域优化，但其他领域的研究者可以通过修改提示模板轻松适配，为自己的模型创建专业题集。

### ✨ 核心特性

- 🎯 **领域专业化**: 专注于流体力学、燃烧科学和航空航天工程
- 🤖 **多模型支持**: 集成Gemini、DeepSeek、Qwen、Yi、Llama模型，支持自动切换
- 🔄 **鲁棒性管道**: 自动模型切换确保生成任务的高可靠性
- 📊 **双重资产积累**: 正确答案（验证集）和挑战性题目（基准库）分别存储
- 🎨 **题目浏览器**: 交互式HTML查看器，方便审阅题目内容
- 🛠️ **完整工具链**: 数据清理、验证、分析和可视化工具
- 🌍 **多语言支持**: 支持英文和中文界面

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- 大语言模型API密钥（Gemini、DeepSeek等）
- 支持的操作系统：Windows、macOS、Linux

#### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/your-repo/questions
cd questions

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.yaml.example config.yaml
# 编辑 config.yaml 添加您的API密钥
```

#### 使用方法

**统一程序入口:**
```bash
# 图形界面（推荐）
python run.py --mode gui

# 命令行界面  
python run.py --mode cli

# 直接生成题目
python run.py --mode generate -n 20 -r 3

# 生成题目浏览器
python run.py --mode visualize

# 清理基准数据
python run.py --mode clean
```

### 📊 数据分析与可视化

生成交互式HTML浏览器来查看所有题目：

```bash
python run.py --mode visualize
```

这将创建 `question_browser.html` 文件，包含：
- 📋 **选项卡界面**: 验证集、基准库和种子样本的分别显示
- 🔍 **详细视图**: 完整的题目文本、标准答案和模型回答
- 📊 **快速统计**: 成功率和题目数量
- 🎨 **简洁设计**: 易于阅读的格式，带有颜色编码的题目类型

### 🔧 系统维护

```bash
# 数据清理（移除判题系统错误）
python run.py --mode clean

# 系统验证（检查组件）
python run.py --mode validate

# 查看日志
cat logs/system.log
```

### 📈 当前性能

基于最新测试：
- 📊 **题目总数**: 100+
- 🎯 **成功率**: ~16%
- 🔬 **领域专注**: 流体力学、燃烧科学、航空航天
- 🤖 **模型数量**: 5个LLM提供商，支持自动切换

### 🛠️ 其他领域定制

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

### 🤝 贡献指南

欢迎贡献！请：
1. Fork 此仓库
2. 创建功能分支
3. 添加测试和文档
4. 提交 Pull Request

### 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

*Built with ❤️ for advancing AI capabilities in fluid mechanics and combustion science*

*为推进AI在流体力学和燃烧科学领域的能力而构建 ❤️*