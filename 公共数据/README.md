# 公共数据文件夹

本文件夹存放项目的公共基础数据,供所有生成尝试和实验使用。

## 📁 文件夹内容

### 1. compliant/ - 原文语料库
- **内容**: 328篇来自Progress in Energy and Combustion Science期刊的学术论文原文
- **用途**: 作为题目生成的原文引用来源
- **格式**: TXT文本文件
- **特点**: 高质量学术文献,覆盖燃烧、能源、传热、流体力学等领域

### 2. main.txt - 合并语料库
- **内容**: 所有328篇论文合并成的单一文本文件
- **用途**: 某些早期实验使用单文件输入
- **大小**: 约数百MB
- **说明**: 当前系统已改用compliant/分文件方式,此文件主要用于历史兼容

### 3. seed_examples.jsonl - 种子示例题目
- **内容**: 2道高质量种子题目
- **用途**: 
  - Few-shot学习示例
  - 新用户初始化系统
  - 帮助生成模型理解题目格式和质量要求
- **格式**: JSONL(每行一个JSON对象)
- **字段**: topic, difficulty, type, question_text, standard_answer, generation_model

### 4. sample_questions.json - 样例问题集
- **内容**: 多个示例问题
- **用途**: 测试和验证用途
- **格式**: JSON数组

## 🔗 使用说明

### 原文语料库使用
```python
# 读取单篇原文
with open('公共数据/compliant/paper_filename.txt', 'r', encoding='utf-8') as f:
    original_text = f.read()

# 或使用索引文件
import pandas as pd
index = pd.read_csv('公共数据/compliant/compliant_index.csv')
```

### 种子示例使用
```python
import json

# 读取种子示例
with open('公共数据/seed_examples.jsonl', 'r', encoding='utf-8') as f:
    seeds = [json.loads(line) for line in f]

# 用作Few-shot示例
few_shot_examples = seeds[:2]
```

## 📊 数据统计

- **论文总数**: 328篇
- **语料总大小**: ~500MB
- **时间跨度**: 2015-2025年
- **领域覆盖**: 燃烧科学、能源系统、传热、流体力学、CFD、化学反应等

## 🔍 数据来源

- **期刊**: Progress in Energy and Combustion Science
- **影响因子**: 高影响力国际期刊
- **质量**: 同行评审的高质量学术文献

## ⚠️ 注意事项

1. **版权**: 这些原文仅用于学术研究和题目生成,不得用于商业用途
2. **编码**: 所有文件使用UTF-8编码
3. **完整性**: 请勿删除或修改原文文件,保持数据完整性
4. **引用**: 生成题目时会自动引用原文片段,标注来源

## 📝 历史说明

- **创建时间**: 项目初期
- **最后更新**: 2025-10-17
- **维护状态**: 稳定,无需频繁更新
- **用途演变**: 
  - 早期: 使用main.txt单文件
  - 当前: 使用compliant/分文件结构,支持并发访问和精确引用

---

**相关文档**:
- [来时路](../最终交付/来时路/README.md) - 了解项目整体历程
- [历史尝试归档](../历史尝试归档/README.md) - 查看各次尝试如何使用这些数据
