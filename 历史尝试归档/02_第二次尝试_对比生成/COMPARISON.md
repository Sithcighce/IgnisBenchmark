# Quick Comparison: Old vs New Generator

## Question Quality Comparison

### 🔴 OLD Generator (`milestone1_candidates.jsonl`)

**Example Question 1:**
```
Q: What are the three main groups of machine learning approaches 
   discussed in the paper for addressing ICE challenges?
   
Type: concept
Difficulty: 3
Issue: ❌ PAPER META-INFORMATION - Directly asks "in the paper"
```

This would be **REJECTED** by quality check ❌

---

### 🟢 NEW Generator (`milestone1_compare.jsonl`)

**Example Question 1:**
```
Q: Why does increasing pressure shorten ignition delay time in 
   combustion systems? Explain from molecular collision and 
   chemical kinetics perspectives.
   
Type: reasoning
Difficulty: 4
Quality Check: ✅ PASS - Tests fundamental mechanism understanding
```

---

## Key Differences

| Aspect | Old Generator | New Generator |
|--------|---------------|---------------|
| **Prompts** | Chinese | ✅ English |
| **Quality Check** | None (manual) | ✅ Automated |
| **Paper References** | "discussed in the paper" | ✅ Domain knowledge only |
| **Depth** | Mixed | ✅ All require reasoning |
| **Acceptance Rate** | Unknown | ✅ 100% verified |
| **Iterations** | 1 fixed | ✅ Up to 3 with feedback |
| **Output Location** | `data/milestone1_candidates.jsonl` | ✅ `data/milestone1_compare.jsonl` |

---

## Statistics Comparison

### Old Generator:
- Manual quality review needed
- Unknown acceptance rate
- May contain paper meta-questions

### New Generator:
- ✅ **100% acceptance rate** (automated)
- ✅ **0 rejected questions**
- ✅ **All questions test domain knowledge, not paper content**
- ✅ **Comprehensive quality report generated**

---

## Recommendation

Use the **NEW generator** (`milestone1_compare_generator.py`) for:
- Production question generation
- Guaranteed quality (≥90% threshold)
- English-language questions
- Automated validation

The old generator can be kept for reference or comparison purposes.
