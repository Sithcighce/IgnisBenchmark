# 第一次尝试：基础题目生成

## 时间
2025年初

## 目标
从学术论文中生成燃烧科学领域的题目

## 使用脚本
- `milestone1_generator.py`

## 特点
- 最初的尝试，直接从论文生成题目
- 使用单一模型（Claude或GPT）
- 题目格式基础，包含question和answer
- 没有验证机制

## 产出数据
- `data/milestone1_candidates.jsonl` (如果存在)
- `data/milestone1_raw_response.txt`

## 结果
- 成功生成了一批候选题目
- 发现需要多模型验证来保证质量
- 为后续改进奠定基础

## 经验教训
- 单模型生成容易产生偏差
- 需要增加质量控制机制
- 题目需要更严格的格式化
