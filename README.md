# 智能题库生成与评估系统

一个基于大模型的自动化题库生成系统，采用**双重资产积累**机制构建高质量题库。

## 核心特性

### 🎯 双重资产积累 (Dual Asset Accumulation)

系统采用创新的双数据库架构，实现题库资产的双向积累：

- **📚 错题库 (Benchmark Bank)**: 收集目标模型（如Qwen-8B）**答错**的题目，形成专门的挑战性benchmark
  - 文件: `data/benchmark_bank.jsonl`
  - 用途: 评估模型弱点、训练数据增强、能力边界测试
  - 包含: 题目数据 + 错误答案 + 判题结果

- **✅ 验证集 (Validation Set)**: 收集目标模型**答对**的题目，形成可靠的验证数据集
  - 文件: `data/validation_set.jsonl`
  - 用途: 模型性能验证、质量控制、Few-shot示例池
  - 包含: 高质量题目及标准答案

### � 自动化工作流

```
生成题目 (Gemini 2.5 Pro) 
    ↓
解答题目 (本地 Qwen-8B via LM Studio)
    ↓
智能判题 (Gemini 2.5 Flash)
    ↓
    ├─→ [答错] → 错题库 (含错误答案分析)
    └─→ [答对] → 验证集 (可用作Few-shot)
```

### 💡 核心优势

- **智能提示管理**: 所有Prompt独立存储在`docs/`目录，支持热更新无需改代码
- **成本可控**: API调用前预估成本，支持实时成本追踪
- **高质量保证**: 动态Few-shot策略，利用验证集中的优质题目提升生成质量
- **数据驱动**: 双向积累机制确保持续产出有价值的数据资产

## 快速开始

### 前提条件

✅ **已完成**:
- Python 3.13.4 虚拟环境
- 所有依赖包（litellm, flask等）
- Google API密钥配置
- LM Studio (qwen3-8b模型)
## 快速开始

### 环境准备

```powershell
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖（如未安装）
pip install -r requirements.txt

# 3. 配置环境变量
# 复制 .env.example 为 .env，填入 Google API Key
cp .env.example .env
```

### 启动 LM Studio

确保 LM Studio 已运行并加载 `qwen3-8b` 模型，监听 `http://localhost:1234`。

### 运行程序

```powershell
# 方式1: 单次运行（生成3题）
python main.py

# 方式2: 批量运行（5个周期，每周期3题）
python tools/batch_run.py --cycles 5 --questions 3

# 方式3: Web监控界面
python web_ui.py
# 访问 http://localhost:5000 查看实时状态
```

### 数据分析

```powershell
# 查看双数据库统计报告
python tools/analyze_data.py
```

## 项目结构

```
questions/
├── config.yaml                 # 系统配置
├── .env                        # API密钥（不提交Git）
├── requirements.txt            # Python依赖
├── main.py                     # 主程序（单次运行）
├── web_ui.py                   # Web监控界面
│
├── src/                        # 核心模块
│   ├── models.py               # 数据模型（QuestionUnit, BenchmarkEntry等）
│   ├── prompt_manager.py       # 提示词管理器
│   ├── question_generator.py   # 题目生成（Gemini 2.5 Pro）
│   ├── answering_module.py     # 解答模块（LM Studio）
│   ├── grading_module.py       # 判题模块（Gemini 2.5 Flash）
│   ├── data_persistence.py     # 双数据库持久化
│   ├── config_loader.py        # 配置加载
│   └── utils.py                # 工具函数
│
├── data/                       # 数据目录
│   ├── benchmark_bank.jsonl    # 错题库（含错误答案）
│   └── validation_set.jsonl    # 验证集（正确答案）
│
├── tools/                      # 工具脚本
│   ├── batch_run.py            # 批量运行
│   └── analyze_data.py         # 数据分析
│
├── testscript/                 # 测试脚本
│   └── test_setup.py           # 环境测试
│
├── docs/                       # 文档与提示词
│   ├── 宏观设计.md
│   ├── 实现细节.md
│   ├── 开发准则.md
│   ├── 生成题Prompt.md         # 题目生成提示词
│   ├── 判题Prompt.md           # 判题提示词
│   ├── 解题Prompt.md           # 解题提示词
│   └── 高质量题目示例.md
│
└── logs/                       # 日志目录
    └── system.log
```

## 配置说明

### config.yaml 关键参数

```yaml
# API模型配置
generation_model: "gemini/gemini-2.5-pro-latest"  # 生成题目
grading_model: "gemini/gemini-2.5-flash-latest"   # 判题

# 本地模型配置
lm_studio_base_url: "http://localhost:1234/v1"
lm_studio_model_name: "qwen3-8b"

# 数据路径（双数据库）
benchmark_bank_path: "data/benchmark_bank.jsonl"  # 错题库
validation_set_path: "data/validation_set.jsonl"  # 验证集

# 提示词目录
prompts_dir: "docs"

# Few-shot配置
few_shot_count: 2                    # 使用验证集中的示例数
few_shot_source: "validation_set"    # 从验证集抽取
```

## 使用示例

### 示例1: 初次运行

```powershell
# 运行主程序（使用种子题目作为Few-shot）
python main.py

# 输出示例：
# 生成了 3 个题目
# 题目已解答
# 判题完成
# 错题库新增: 2 题
# 验证集新增: 1 题
```

### 示例2: 批量生成

```powershell
# 批量运行10个周期，每周期5题
python tools/batch_run.py --cycles 10 --questions 5

# 查看统计
python tools/analyze_data.py
```

### 示例3: Web监控

```powershell
# 启动监控服务
python web_ui.py

# 浏览器访问 http://localhost:5000
# 实时查看：
# - 错题库数量: 47
# - 验证集数量: 23
# - API累计成本: $1.23
```

## 技术架构

### API 调用链

```
用户 → main.py
         ↓
    [生成题目]
    QuestionGenerator → Gemini 2.5 Pro (via LiteLLM)
         ↓
    [解答题目]
    AnsweringModule → LM Studio (qwen3-8b)
         ↓
    [智能判题]
    GradingModule → Gemini 2.5 Flash (via LiteLLM)
         ↓
    [分类保存]
    DataPersistence → benchmark_bank.jsonl / validation_set.jsonl
```

### 数据流

```
Few-shot示例 (从validation_set抽取)
    ↓
生成新题目 (topic, difficulty, type, question_text, standard_answer)
    ↓
本地模型解答
    ↓
判题 (is_correct, score, reasoning)
    ↓
    ├─ [不正确] → BenchmarkEntry {question_data, failed_attempt, grading_result}
    │                  ↓
    │            benchmark_bank.jsonl
    │
    └─ [正确] → QuestionUnit → validation_set.jsonl
```

## 开发准则

本项目严格遵循以下开发准则：

1. **文档管理**: 所有 `.md` 文档统一放置在 `docs/` 目录
2. **代码组织**: 核心代码在 `src/`，工具脚本在 `tools/`，测试在 `testscript/`
3. **提示词分离**: 所有 Prompt 独立存储为 `.md` 文件，由 `PromptManager` 动态加载
4. **双数据库**: 错题库和验证集分别管理，实现双重资产积累
5. **成本控制**: API 调用前估算成本（使用 LiteLLM 的成本追踪）
6. **Git 管理**: 及时提交到 `git@github.com:Sithcighce/distillation_generation.git`

详见 `docs/开发准则.md`。

## 常见问题

### Q: 如何更新提示词？
A: 直接编辑 `docs/` 目录下的对应 `.md` 文件（如 `生成题Prompt.md`），无需修改代码。

### Q: 如何切换生成模型？
A: 修改 `config.yaml` 中的 `generation_model` 参数。

### Q: 错题库和验证集的区别？
A: 
- **错题库**: 目标模型答错的题，用于构建 benchmark 和分析弱点
- **验证集**: 目标模型答对的题，用于 Few-shot 示例和质量验证

### Q: 如何查看 API 成本？
A: 运行 `python web_ui.py`，访问 http://localhost:5000 查看实时成本。

## 贡献与维护

- **项目维护**: 遵循开发准则，保持代码整洁
- **数据备份**: 定期备份 `data/` 目录
- **Git 提交**: 使用清晰的 commit message

## 许可证

MIT License

---

**系统版本**: v2.0 (双重资产积累架构)  
**最后更新**: 2025年

