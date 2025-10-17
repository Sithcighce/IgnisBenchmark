你是一位严格的质量审核专家。请检查以下问题和答案的质量。

**问题**: {question['question_text']}

**答案**: {question['standard_answer']}

**原文引用**:
{json.dumps(question['original_text'], ensure_ascii=False, indent=2)}

**论文摘录**（用于验证答案准确性）:
{paper_text[:5000]}

---

## 检查标准

### 1. 领域聚焦性（domain_focused）
- ✅ 问题是否需要燃烧/传热/流体/CFD/能源领域的专业知识？
- ❌ 是否是纯ML/CS方法对比？

### 2. 答案正确性（answer_correct）
基于原文引用和论文内容，检查答案是否：
- ✅ 事实准确
- ✅ 机理解释正确
- ✅ 公式和推导合理
- ❌ **问题类型**：
  - `too_brief`: 答案过于简短（<300字符）
  - `factual_error`: 事实错误或与原文矛盾
  - `fundamental_error`: 基本原理错误
  - `unsupported`: 答案中的关键声明未被引用支持

### 3. 其他合规性（other_compliant）
- ❌ 不能有元信息（如"根据论文"、"文中提到"）
- ❌ 不能有时效性内容（如"近年来"、"未来将"）
- ❌ 不能过于宽泛或通用

---

## 输出格式（严格JSON）

```json
{
  "domain_focused": true/false,
  "domain_reasoning": "为什么需要或不需要领域专业知识",
  "answer_correct": true/false,
  "answer_issues": ["too_brief", "factual_error", "fundamental_error", "unsupported"],
  "other_compliant": true/false,
  "other_issues": ["has_meta_info", "time_sensitive", "too_general"],
  "overall_verdict": "pass/fail",
  "recommendation": "简短建议"
}
```
