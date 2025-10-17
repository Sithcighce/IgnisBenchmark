# 第一次尝试：基础生成

**时间**: 2024年初  
**脚本**: milestone1_generator.py  
**策略**: 基础prompt生成问题  

## 目标
从学术论文生成高质量的燃烧科学问题，每篇论文5题。

## 方法
- 使用基础生成prompt
- 直接从论文内容提取关键信息
- 简单的质量检查

## 数据文件
- `milestone1_candidates.jsonl`: 候选题目
- `milestone1_raw_response.txt`: 原始API响应
- `milestone1_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 基础生成prompt

## 结果
生成了第一批候选题目，但质量不够稳定。

## 经验教训
- ✅ 证明了可行性
- ❌ 需要更详细的prompt指导
- ❌ 需要多次迭代改进
