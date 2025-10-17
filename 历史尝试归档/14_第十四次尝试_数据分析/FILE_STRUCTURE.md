# GPT-5验证结果分类目录说明

## 📂 目录结构

```
验证/gpt验证结果分类/
├── README.md                    # 总览文档
├── 1_答对的题目/
│   ├── correct.json             # 720题完整数据
│   └── correct_stats.json       # 统计和预览
├── 2_真实错误/
│   ├── real_errors.json         # 76题完整数据
│   └── real_errors_stats.json   # 统计和预览
├── 3_API失败_有分数/
│   ├── api_failures_with_score.json      # 69题完整数据
│   └── api_failures_with_score_stats.json # 统计和预览
├── 4_API失败_零分/
│   ├── api_failures_zero_score.json      # 7题完整数据
│   └── api_failures_zero_score_stats.json # 统计和预览
└── 5_未测试/
    ├── untested.json            # 112题完整数据
    └── untested_stats.json      # 统计和预览
```

---

## 📊 分类详情

### 1. ✅ 答对的题目 (720题)
- **文件**: `1_答对的题目/correct.json`
- **占比**: 73.17% (总题目) | 82.57% (已测试)
- **说明**: GPT-5正确回答的题目
- **数据包含**:
  - 完整题目文本和标准答案
  - GPT-5得分 (通常≥85分)
  - 题目难度、主题、类型

### 2. ❌ 真实错误 (76题)
- **文件**: `2_真实错误/real_errors.json`
- **占比**: 8.72% (已测试)
- **说明**: GPT-5给出实质性回答（≥500字符），但DeepSeek判定为错误
- **特征**:
  - 平均回答长度: 5,893字符
  - 分数范围: 0-80分
  - 主要错误领域: energy_systems (24题), combustion_kinetics (23题)
- **数据包含**:
  - 完整题目和标准答案
  - GPT-5回答长度
  - 得分详情

### 3. ⚠️ API失败（有分数） (69题)
- **文件**: `3_API失败_有分数/api_failures_with_score.json`
- **占比**: 7.91% (已测试)
- **分数范围**: 1-80分
- **说明**: 可能原因
  - 回答太短（<500字符）但有部分内容
  - API部分返回
  - 回答被截断
- **数据包含**:
  - 完整题目和标准答案
  - 得分 (1-80分)
  - answer_length标记

### 4. ⚠️ API失败（零分） (7题)
- **文件**: `4_API失败_零分/api_failures_zero_score.json`
- **占比**: 0.80% (已测试)
- **说明**: 很可能是完全API失败
- **可能原因**:
  - OpenRouter余额不足
  - API超时/错误
  - 无返回数据
- **题目ID示例**:
  - deepseek_q_0cac3a29
  - deepseek_q_3acd1555
  - deepseek_q_3fed5e25
  - deepseek_q_4e3a531c
  - deepseek_q_6f01d45d
  - deepseek_q_95b0e73e
  - deepseek_q_da3eb8f3

### 5. ⏭️ 未测试 (112题)
- **文件**: `5_未测试/untested.json`
- **占比**: 11.38% (总题目)
- **说明**: 脚本在第908题中断，剩余未测试
- **难度分布**:
  - 难度3: 5题
  - 难度4: 88题
  - 难度5: 19题
- **估算成本**: ~$7.96 (按平均$0.0711/题)

---

## 📋 文件格式说明

### 完整数据文件 (*.json)
每个题目包含：
```json
{
  "question_id": "deepseek_q_xxxxx",
  "question_text": "题目文本",
  "standard_answer": "标准答案",
  "original_text": {...},
  "type": "concept/reasoning/calculation/application",
  "difficulty": 3-5,
  "topic": "combustion_kinetics/energy_systems/...",
  "quality_check": {...},
  "category_info": {
    "question_id": "deepseek_q_xxxxx",
    "score": 0-100,           // 仅答对、真实错误、API失败有此字段
    "difficulty": 3-5,
    "topic": "...",
    "type": "...",
    "answer_length": 数字或"unknown"  // 仅真实错误、API失败有此字段
  }
}
```

### 统计文件 (*_stats.json)
包含：
```json
{
  "category": "分类名称",
  "total_count": 数量,
  "questions": [
    {
      "question_id": "deepseek_q_xxxxx",
      "difficulty": 3-5,
      "topic": "...",
      "type": "...",
      "score": 0-100或"N/A",
      "question_preview": "题目前100字..."
    }
  ]
}
```

---

## 🎯 使用建议

### 分析真实错误
```python
import json

# 加载真实错误题目
with open('2_真实错误/real_errors.json', 'r', encoding='utf-8') as f:
    real_errors = json.load(f)

# 找出最难的题目
difficult_errors = [q for q in real_errors if q['difficulty'] == 5]

# 按主题分组
from collections import defaultdict
by_topic = defaultdict(list)
for q in real_errors:
    by_topic[q['topic']].append(q)
```

### 检查API失败
```python
# 加载零分API失败
with open('4_API失败_零分/api_failures_zero_score.json', 'r', encoding='utf-8') as f:
    zero_score = json.load(f)

# 这些题目可能需要重新测试
print(f"需要重新测试的题目: {len(zero_score)}")
```

### 准备未测试题目
```python
# 加载未测试题目
with open('5_未测试/untested.json', 'r', encoding='utf-8') as f:
    untested = json.load(f)

# 按难度排序
untested_sorted = sorted(untested, key=lambda x: x['difficulty'])
```

---

## 📈 关键统计

| 分类 | 数量 | 占已测试 | 占总题目 |
|------|------|----------|----------|
| ✅ 答对 | 720 | 82.57% | 73.17% |
| ❌ 真实错误 | 76 | 8.72% | 7.72% |
| ⚠️ API失败（有分） | 69 | 7.91% | 7.01% |
| ⚠️ API失败（零分） | 7 | 0.80% | 0.71% |
| ⏭️ 未测试 | 112 | - | 11.38% |
| **总计** | **984** | **100%** | **100%** |

### 调整后性能指标
- **原始准确率**: 82.57% (720/872)
- **调整后准确率**: 90.45% (720/796，排除API失败)
- **真实错误率**: 9.55% (76/796)
- **API失败率**: 8.72% (76/872)

---

## 🔍 数据验证

验证脚本: `验证/save_categorized_questions.py`

验证结果:
- ✅ 总题目数: 984 (正确)
- ✅ 答对 + 真实错误 + API失败 + 未测试 = 984
- ✅ 所有题目ID唯一
- ✅ 每个分类文件完整性确认

---

生成时间: 2025-10-17
数据来源: `验证/complete_question_categorization.json`
