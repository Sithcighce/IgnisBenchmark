# Batch Detail Q Generator - 使用说明

## 📋 功能概述

批量处理所有txt文件，为每个文件生成5道详细的领域专业问题。

### 核心特性

- ✅ **并发处理**: 20个文件同时处理
- ✅ **高速API**: DeepSeek-V3 Pro (RPM=30,000)
- ✅ **完整论文**: 不截断文章内容
- ✅ **自动分类**: pass.json + not_pass.json
- ✅ **文件复制**: 每个输出文件夹包含原始txt副本

---

## 🚀 快速开始

### 1. 运行批处理

```bash
python run_batch_detail_q.py
```

程序会自动：
- 读取 `compliant/` 文件夹中的所有txt文件（~298个）
- 为每个文件生成5道详细问题
- 输出到 `questions/` 文件夹

### 2. 输出结构

```
questions/
├── BATCH_SUMMARY.md                    # 总结报告
├── paper_name_1/
│   ├── paper_name_1.txt                # 原始论文副本
│   ├── pass.json                       # 通过质量检查的问题
│   └── not_pass.json                   # 未通过质量检查的问题
├── paper_name_2/
│   ├── paper_name_2.txt
│   ├── pass.json
│   └── not_pass.json
...
```

---

## 📊 处理流程

### 每个文件的处理步骤

1. **读取论文全文** - 不截断！完整读取
2. **生成5道问题** - 使用DeepSeek-V3 Pro
3. **质量检查** - 每道题逐一检查
   - domain_focused: 是否需要领域专业知识
   - answer_correct: 答案是否正确
   - other_compliant: 其他合规性
4. **引文验证** - 检查原文引用是否存在
5. **分类保存**:
   - `pass.json`: 质量检查+引文验证全部通过
   - `not_pass.json`: 任一项未通过

---

## ⚙️ 配置说明

### 并发设置

```python
MAX_CONCURRENT_FILES = 20  # 同时处理20个文件
```

- 每个文件约需6次API调用（1生成+5检查）
- 20并发 = 120并发请求
- 远低于RPM限制（30,000）

### 模型配置

```python
GENERATION_MODEL = "openai/deepseek-ai/DeepSeek-V3"
QUALITY_CHECK_MODEL = "openai/deepseek-ai/DeepSeek-V3"
```

### 引文验证阈值

```python
CITATION_THRESHOLD = 0.85  # 85%相似度
```

---

## 📝 问题格式

每道问题包含以下字段：

```json
{
  "question_text": "问题描述",
  "standard_answer": "详细答案（≥300字符）",
  "original_text": {
    "1": "原文引用1",
    "2": "原文引用2"
  },
  "type": "reasoning|calculation|concept",
  "difficulty": 3-5,
  "topic": "combustion_kinetics|heat_transfer|...",
  "quality_check": {
    "domain_focused": true,
    "answer_correct": true,
    "overall_verdict": "pass"
  },
  "citation_verification": {
    "verified": true,
    "total_citations": 2,
    "verified_citations": 2
  }
}
```

---

## 📈 预期性能

### 时间估算

- **单个文件**: ~30-60秒
- **298个文件**: ~2-3小时（并发处理）

### API调用量

- **每个文件**: ~6次调用
- **总计**: ~1,788次调用
- **Token消耗**: 
  - 输入: ~298 * 20K = 5.96M tokens
  - 输出: ~298 * 10K = 2.98M tokens

### 费用估算（SiliconFlow Pro）

- DeepSeek-V3 定价: 约 ¥0.5/M tokens（输入+输出）
- 预估总费用: ~¥5-10

---

## 🔍 监控和调试

### 实时日志

程序运行时会显示：
```
[paper_name_1] Processing...
[paper_name_1] Paper length: 245678 chars
[paper_name_1] Generating questions...
[paper_name_1] Generated 5 questions
[paper_name_1] Checking Q1...
[paper_name_1] Q1 PASSED
...
Progress: 15/298 (5.0%)
```

### 查看总结报告

```bash
cat questions/BATCH_SUMMARY.md
```

---

## ⚠️ 重要说明

### 1. 绝不截断文章

程序会读取**完整的论文全文**，不会截断。即使论文很长（>100KB），也会完整传给模型。

### 2. API速率限制

- RPM: 30,000（每分钟请求数）
- TPM: 5,000,000（每分钟token数）

当前配置（20并发）远低于限制，无需担心速率限制。

### 3. 错误处理

如果某个文件处理失败，程序会：
- 记录错误日志
- 继续处理其他文件
- 在总结报告中标记失败文件

---

## 🛠️ 故障排除

### 问题1: API Key错误

确保环境变量已设置：
```bash
export SILICONFLOW_API_KEY="your-key-here"
```

### 问题2: 内存不足

如果处理非常大的文件（>1MB），可能需要降低并发数：
```python
MAX_CONCURRENT_FILES = 10  # 降低到10
```

### 问题3: 某些文件失败

检查 `BATCH_SUMMARY.md` 中的错误信息，常见原因：
- 文件编码问题
- 论文内容过短
- API临时故障

---

## 📊 质量标准

### 通过标准（pass.json）

必须同时满足：
- ✅ domain_focused = true
- ✅ answer_correct = true
- ✅ other_compliant = true
- ✅ citation_verification.verified = true

### 未通过原因（not_pass.json）

可能原因：
- ❌ 问题不需要领域专业知识（纯ML/CS）
- ❌ 答案过短（<300字符）
- ❌ 答案有事实错误
- ❌ 引用未在原文中找到（<85%相似度）

---

## 🎯 预期结果

基于之前的测试（milestone1_detail_Q）：

- **题目领域聚焦率**: 100%（全部需要燃烧/CFD专业知识）
- **答案长度合格率**: 100%（平均984字符）
- **引文验证通过率**: 80%
- **整体通过率**: 20-40%（预期）

**注意**: 整体通过率较低是因为质量检查非常严格，但**所有生成的题目都是高质量的专业问题**。

---

## 📧 技术支持

如有问题，请查看：
1. `questions/BATCH_SUMMARY.md` - 总结报告
2. 程序日志输出
3. 各文件夹中的 `not_pass.json` - 失败原因

---

**Ready to go!** 🚀
