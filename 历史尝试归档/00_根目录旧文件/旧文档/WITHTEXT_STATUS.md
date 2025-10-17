# Milestone 1 WithText Generator - 状态报告

## 🔄 当前状态：正在运行

**启动时间**: 2025-10-14 18:52:04  
**当前阶段**: ITERATION 1 - 生成带原文引用的题目  
**使用模型**: DeepSeek-V3 (生成) + Gemini 2.0 Flash (质检)

---

## 📋 设计特点

### 1. **原文引用要求**
每道题必须包含 `original_text` 字段：
```json
{
  "question_text": "问题...",
  "standard_answer": "答案...",
  "original_text": {
    "1": "论文中的原文片段1（逐字引用）",
    "2": "论文中的原文片段2（逐字引用）"
  }
}
```

### 2. **双重验证机制**
- **步骤1**: 内容质量检查（不传入original_text）
  - 检查是否有论文元信息题
  - 检查是否有时效性问题
  - 检查是否过于开放
  
- **步骤2**: 原文验证
  - 使用模糊匹配算法
  - 忽略标点、空格、换行
  - 要求至少85%相似度
  - 使用`SequenceMatcher`滑动窗口查找

### 3. **综合通过标准**
题目必须同时满足：
- 内容质量检查 ≥ 90% (pass + review)
- 原文验证 ≥ 90% (所有引用都验证通过)
- 综合通过率 ≥ 90%

### 4. **迭代改进**
- 最多3次迭代
- 失败时提供反馈并重新生成
- 引用验证失败时提示"使用原文逐字引用"

---

## 🎯 预期输出

### 文件：
1. `data/milestone1_withtext.jsonl` - 20道带原文引用的题目
2. `data/milestone1_withtext_report.md` - 详细质量报告

### 每道题包含：
- 所有标准字段 (question_text, standard_answer, type, difficulty, topic)
- **新增**: `original_text` 字典
- **新增**: `citation_verification` 验证结果
- 质量检查结果
- 完整元数据

---

## ⚙️ 技术亮点

### 原文验证算法
```python
def verify_citations(citations, paper_text):
    for each citation:
        1. normalize_text() - 去除标点、小写化、统一空格
        2. sliding_window() - 在论文中滑动窗口搜索
        3. SequenceMatcher.ratio() - 计算相似度
        4. threshold_check() - 检查是否 ≥ 85%
    return verification_result
```

### 滑动窗口策略
- 窗口大小: 引用长度的 80%-120%
- 允许轻微的格式差异
- 忽略所有非字母数字字符

---

## 📊 质量指标

将在报告中包含：
- 内容质量分布 (pass/review/reject)
- 引用验证成功率
- 每道题的引用数量统计
- 引用相似度分布
- 综合通过率

---

**当前状态**: ⏳ 等待DeepSeek生成20道题目...

**预计时间**: 3-5分钟（取决于API响应速度）
