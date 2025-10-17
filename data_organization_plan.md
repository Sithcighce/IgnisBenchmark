# Data 文件夹整理分析

## milestone1 系列文件分析

### 1. milestone1 基础版 (第一次尝试)
```
milestone1_candidates.jsonl  → 01_第一次尝试_基础生成/data/
milestone1_raw_response.txt → 01_第一次尝试_基础生成/data/
milestone1_report.md → 01_第一次尝试_基础生成/data/
```

### 2. milestone1_compare (第二次尝试 - 对比生成)
```
milestone1_compare.jsonl → 02_第二次尝试_对比生成/data/
milestone1_compare_raw_iter1.txt → 02_第二次尝试_对比生成/data/
milestone1_compare_report.md → 02_第二次尝试_对比生成/data/
```

### 3. milestone1_withtext (第三次尝试 - 保留原文)
```
milestone1_withtext.jsonl → 03_第三次尝试_保留原文/data/
milestone1_withtext_raw_iter1.txt → 03_第三次尝试_保留原文/data/
milestone1_withtext_raw_iter2.txt → 03_第三次尝试_保留原文/data/
milestone1_withtext_raw_iter3.txt → 03_第三次尝试_保留原文/data/
milestone1_withtext_report.md → 03_第三次尝试_保留原文/data/
```

### 4. milestone1_detail_Q (第四次尝试 - 详细问题)
```
milestone1_detail_Q.jsonl → 04_第四次尝试_详细问题/data/
milestone1_detail_Q_raw.txt → 04_第四次尝试_详细问题/data/
milestone1_detail_Q_report.md → 04_第四次尝试_详细问题/data/
```

### 5. milestone1_insights (第五次尝试 - 洞察生成)
```
milestone1_insights.jsonl → 05_第五次尝试_洞察生成/data/
milestone1_insights_raw.txt → 05_第五次尝试_洞察生成/data/
milestone1_insights_report.md → 05_第五次尝试_洞察生成/data/
```

### 6. milestone1_insights_pro (第五次尝试专业版 - 洞察生成专业版)
```
milestone1_insights_pro.jsonl → 06_第五次尝试_洞察生成专业版/data/
milestone1_insights_pro_report.md → 06_第五次尝试_洞察生成专业版/data/
```

## 其他文件分析

### seed_examples.jsonl
- 这是种子示例,所有尝试都用到
- **决定**: 保留在 data/ ,因为是基础数据

### grading_errors.jsonl, removed_grading_errors.jsonl
- 这些是判题错误相关
- **决定**: 保留在 data/ ,因为是通用数据

### sample_questions.json, main.txt
- 这些是通用示例
- **决定**: 保留在 data/ ,因为是辅助文件

### README.md
- data 文件夹的说明文档
- **决定**: 保留在 data/

## 总结

**需要移动的文件** (19个):
1-3. milestone1 基础版 (3个) → 01_第一次尝试_基础生成/data/
4-6. milestone1_compare (3个) → 02_第二次尝试_对比生成/data/
7-11. milestone1_withtext (5个) → 03_第三次尝试_保留原文/data/
12-14. milestone1_detail_Q (3个) → 04_第四次尝试_详细问题/data/
15-17. milestone1_insights (3个) → 05_第五次尝试_洞察生成/data/
18-19. milestone1_insights_pro (2个) → 06_第五次尝试_洞察生成专业版/data/

**保留在 data/ 的文件** (6个):
- seed_examples.jsonl (种子示例,基础数据)
- grading_errors.jsonl (通用错误数据)
- removed_grading_errors.jsonl (通用错误数据)
- sample_questions.json (通用示例)
- main.txt (通用文本)
- README.md (说明文档)
