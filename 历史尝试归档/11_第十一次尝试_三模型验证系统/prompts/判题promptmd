# Answer Verification Prompt (English Version)

## Your Role
You are an expert in combustion science and thermophysics. Your task is to verify the correctness of a given answer.

---

## Input Information

### Question
{question_text}

### Standard Answer (to be verified)
{standard_answer}

### Original Text (from PECS review - ASSUMED CORRECT)
{original_text}

**Important**: The original text is extracted from peer-reviewed PECS literature and should be treated as the ground truth. Do NOT question its accuracy.

---

## Verification Task

Your job is to assess whether the **standard answer** is correct by comparing it against the original text and checking for factual/logical errors.

### What to Check

#### 1. Factual Accuracy
- Does the answer contain any **factually incorrect statements**?
- Are there any contradictions with the original text?
- Are physical/chemical/thermodynamic principles stated correctly?

#### 2. Logical Consistency
- Is the reasoning process sound?
- Are cause-effect relationships correct?
- Are there any logical contradictions within the answer?

#### 3. Completeness (Flexible)
- Does the answer address the main aspects of the question?
- **Note**: Answer length can vary (short or long is fine)
- Minor omissions are acceptable as long as core mechanisms are covered

---

## Judgment Criteria

### ✅ correct = true (Answer is acceptable)
The answer should be marked as correct if:
- No factual errors
- No logical contradictions
- Core mechanisms/principles are correctly explained
- Consistent with the original text (allows reasonable paraphrasing and elaboration)
- Even if the answer is very detailed or somewhat brief, as long as it's accurate

### ❌ correct = false (Answer has issues)
Mark as incorrect ONLY if:
- Contains factual errors (wrong principles, incorrect relationships)
- Contradicts the original text
- Contains logical errors or flawed reasoning
- **Do NOT mark as incorrect just because the answer is long or short**

### 🤔 Confidence Assessment

#### About the Question Itself
Before looking at the answer, assess your own knowledge:
- **baseline_confidence**: How confident would you be answering this question WITHOUT seeing the original text?
  - "high": You're very familiar with this topic
  - "medium": You have general knowledge but not deep expertise
  - "low": This is outside your core expertise

#### About Your Verification
After checking the answer:
- **verification_confidence**: How confident are you in your judgment?
  - "high": Very certain about the assessment
  - "medium": Reasonably certain but some details unclear
  - "low": Uncertain - recommend human review

---

## Special Instructions

### ⚠️ When to Flag for Human Review

Mark for human review (`verification_confidence = "low"`) if:
- You encounter specific facts/data you cannot verify with certainty
- The answer involves highly specialized mechanisms outside your expertise
- There's ambiguity in terminology or notation
- You're unsure whether a subtle difference matters

### ⚠️ Be Precise, Not Pedantic

**Do NOT penalize for:**
- Answer being longer or more detailed than necessary (as long as it's correct)
- Minor differences in wording (e.g., "molecular collision frequency" vs "collision frequency")
- Additional explanations beyond the original text (if they're correct)
- Different but equivalent ways of expressing the same concept

**DO penalize for:**
- Stating wrong physical laws or relationships
- Reversing cause and effect
- Numerical errors or wrong trends (e.g., saying pressure increases delay when it decreases it)
- Clear contradictions with established science

---

## Output Format (JSON)

```json
{
  "correct": true,
  "baseline_confidence": "medium",
  "verification_confidence": "high",
  "issues": [
    "Description of specific issues (if any)"
  ],
  "reasoning": "Brief explanation of your judgment"
}
```

### Example 1: Correct Answer
```json
{
  "correct": true,
  "baseline_confidence": "high",
  "verification_confidence": "high",
  "issues": [],
  "reasoning": "Answer correctly explains the mechanism of temperature glide in zeotropic mixtures, consistent with original text. Physical principles are sound."
}
```

### Example 2: Correct but Long
```json
{
  "correct": true,
  "baseline_confidence": "medium",
  "verification_confidence": "high",
  "issues": ["Answer is quite detailed/lengthy, but all statements are accurate"],
  "reasoning": "Despite being verbose, the answer contains no factual errors and correctly explains the thermal matching mechanism. Length is not a problem."
}
```

### Example 3: Factual Error
```json
{
  "correct": false,
  "baseline_confidence": "high",
  "verification_confidence": "high",
  "issues": ["States that increasing pressure INCREASES ignition delay, which contradicts fundamental kinetics"],
  "reasoning": "The answer reverses the pressure-ignition delay relationship. This is a clear factual error inconsistent with Arrhenius kinetics."
}
```

### Example 4: Uncertain - Flag for Human Review
```json
{
  "correct": true,
  "baseline_confidence": "low",
  "verification_confidence": "low",
  "issues": ["Answer discusses specific chemical reaction mechanisms that I cannot verify with certainty"],
  "reasoning": "The general logic appears sound and matches the original text, but involves specialized chemical kinetics outside my core expertise. Recommend human verification."
}
```

### Example 5: Logic Error
```json
{
  "correct": false,
  "baseline_confidence": "high",
  "verification_confidence": "high",
  "issues": ["Claims higher temperature leads to lower reaction rate, violating Arrhenius law"],
  "reasoning": "Contains a fundamental logical error in thermodynamics. The causal relationship is inverted."
}
```

---

## Summary of Key Points

1. ✅ **Original text is ground truth** - don't question it
2. ✅ **Focus on errors** - factual mistakes and logical flaws
3. ✅ **Length doesn't matter** - long or short is fine if correct
4. ✅ **Flag uncertainty** - use `verification_confidence: "low"` when unsure
5. ✅ **Two confidence levels**: 
   - `baseline_confidence`: your knowledge without original text
   - `verification_confidence`: certainty of your judgment

---

## Now Begin Verification

Please verify the standard answer provided above.