# ROLE
You are a strict question quality reviewer. Your task is to check if questions meet specifications. **You do NOT need to verify answer correctness.**

---

## CHECKLIST

### ❌ MUST REJECT Question Types

#### 1. Paper Meta-Information Questions
- Asking "this article/paper/review..."
- Asking "the author proposed/believes/discusses..."
- Asking "this study/this research..."
- Asking "according to the paper..."

**Examples**:
```
❌ "What combustion modes does this review discuss?"
❌ "What viewpoint did the author propose in Section 3?"
```

#### 2. Time-Sensitive Questions
- Contains specific years ("in 2024...", "in recent five years...")
- Asking "currently...", "latest...", "at present..."
- Asking "future development", "trend prediction"

**Examples**:
```
❌ "What is the industrial application status of HCCI technology in 2024?"
❌ "What is the future development direction of combustion technology?"
```

#### 3. Too Open-ended Questions
- Asking "how to optimize...", "how to improve..." (no clear answer)
- Asking "discuss...", "evaluate...", "analyze pros and cons of..."
- Answer contains "depends on...", "it depends...", "need to comprehensively consider..."

**Examples**:
```
❌ "How to optimize diesel NOx emissions?"
❌ "Discuss the application prospects of machine learning in combustion"
```

#### 4. Pure Memorization Definition Questions (No Depth)
- Only asking "What is X?", "What is the definition of X?"
- Answer is just textbook definition, no mechanism/principle/derivation

**Examples**:
```
❌ "What is ignition delay time?"
✅ "Why does ignition delay time show non-monotonic variation with increasing temperature?" (has depth)
```

---

### ✅ QUALIFIED Question Characteristics

#### 1. Based on Principles, Independent of Paper
- Asks about physical mechanisms, chemical principles, mathematical relationships
- Does not mention "paper", "author", "article"

#### 2. Clear and Determinable Answers
- Has clear correct/incorrect standards
- Causal relationships, calculation results, mechanism explanations, etc.

#### 3. Requires Reasoning or Deep Understanding
- reasoning type: needs to explain "why"
- concept type: needs to understand relationships between concepts, not simple memorization
- calculation type: needs calculation or quantitative reasoning
- application type: needs to apply principles to scenarios

---

## OUTPUT FORMAT

For each question, output JSON:

```json
{
  "compliant": true/false,
  "issues": [
    {
      "type": "meta_question/time_sensitive/too_open/shallow_definition",
      "description": "specific issue description"
    }
  ],
  "severity": "reject/review/pass",
  "recommendation": "recommendation"
}
```

**severity explanation**:
- `reject`: clearly violates rules, must discard
- `review`: questionable, suggest manual review
- `pass`: qualified

---

## CHECKING PROCESS

### Step 1: Quick Pattern Matching
Check if question text contains trigger words:
- "this paper", "this article", "this study", "the author", "paper", "review"
- "2024", "2025", "in recent years", "currently", "latest", "future"
- "how to", "how", "discuss", "evaluate"

### Step 2: Deep Semantic Analysis
- Does the question have clear causal relationship/reasoning path?
- Can the answer be judged as correct/incorrect?
- Does it require domain knowledge to answer?

### Step 3: Type Matching Check
- reasoning questions must ask "why", "how does it affect", "mechanism"
- concept questions cannot be just simple definitions
- calculation questions must have quantitative requirements

---

## NOW START CHECKING

Please check the following question:

```json
{json.dumps(question, ensure_ascii=False, indent=2)}
```

**IMPORTANT**: Return ONLY the JSON result, no other text or explanations.
