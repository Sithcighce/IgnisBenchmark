# 第十阶段：质量筛选

## 时间
验证系统建立后

## 目标
从通过验证的题目中筛选出最高质量的题目

## 使用脚本
- 数据分析脚本（在scripts/或tools/中）

## 特点
- 基于all_correct标记筛选
- 去除重复和低质量题目
- 分类整理

## 产出数据
- `验证/best.json` (984题，三模型一致通过)
- `验证/notpass.json` (88题，包含needs_review)

## 结果
- 得到984道高质量题目
- 这些是IgnisBenchmark的核心题库

## 经验教训
- 严格筛选保证了benchmark的价值
- needs_review机制允许人工复审边界情况
