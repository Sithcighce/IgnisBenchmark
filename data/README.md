# 种子示例说明

本文件包含2道高质量种子题目，供新用户快速开始使用系统。

## 用途

1. **Few-shot示例**: 系统从benchmark错题库抽取题目作为Few-shot示例，帮助生成模型理解题目格式和质量要求
2. **初始化**: 新用户clone项目后可以立即运行，无需手动准备题目

## 数据格式

每行一个JSON对象，包含以下字段：
- `topic`: 主题
- `difficulty`: 难度 (1-5)
- `type`: 类型 (Logical Thinking / Knowledge-based)
- `question_text`: 题目文本
- `standard_answer`: 标准答案
- `generation_model`: 生成模型标识

## 使用方法

首次运行时，将本文件复制为 `benchmark_bank.jsonl`:

```powershell
Copy-Item data/seed_examples.jsonl data/benchmark_bank.jsonl
```

或者系统会自动使用这些示例初始化。

## 注意事项

- 这些题目经过测试，Qwen-8B模型答不对（因此放在benchmark集）
- 完整的5道高质量题目示例见 `docs/高质量题目示例.md`
- 运行系统后会自动积累更多题目到benchmark和validation集
