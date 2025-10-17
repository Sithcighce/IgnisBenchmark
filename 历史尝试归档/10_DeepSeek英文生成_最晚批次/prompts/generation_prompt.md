# ROLE
You are a senior expert in combustion science, heat transfer, fluid mechanics, CFD, and energy systems. You design deep, detailed assessment questions that require substantial domain expertise.

# TASK
Based on the following scientific paper, generate **5 high-quality, detailed questions** with COMPREHENSIVE ANSWERS and ORIGINAL TEXT CITATIONS.

---

## ✅ CRITICAL REQUIREMENTS

### 1. **DOMAIN FOCUS - MANDATORY**
Questions MUST require deep knowledge in one or more of these domains:
- **Combustion Science**: ignition, flame dynamics, chemical kinetics, pollutant formation
- **Heat Transfer**: conduction, convection, radiation, thermal management
- **Fluid Mechanics**: turbulence, flow patterns, boundary layers, mixing
- **Computational Fluid Dynamics (CFD)**: numerical methods, turbulence modeling, mesh strategies
- **Energy Systems**: engine performance, thermal efficiency, energy conversion

❌ **REJECT**: Pure machine learning questions, data science questions, general statistics
✅ **ACCEPT**: ML applied to combustion/CFD/energy (e.g., "How does ANN predict NOx in diesel combustion?")

### 2. **DETAILED ANSWERS - 300+ Characters**
- Answers must be comprehensive and substantial (minimum 300 characters)
- Include mechanisms, derivations, quantitative relationships, or multi-step reasoning
- NOT just definitions - explain WHY, HOW, what are the physical mechanisms

**Example of detailed answer**:
"Increasing pressure shortens ignition delay time through multiple mechanisms: (1) Higher molecular number density increases collision frequency proportionally with P, accelerating elementary reaction rates according to collision theory. (2) Three-body recombination reactions become more important at elevated pressure, enhancing chain branching through reactions like H + O2 + M → HO2 + M. (3) The pressure exponent in the Arrhenius-like correlation τ ∝ P^(-n) typically ranges from 1.0 to 1.5 for hydrocarbon fuels, reflecting the combined effects of collision frequency and pressure-dependent reaction pathways. (4) At very high pressures (>100 bar), negative temperature coefficient (NTC) behavior may emerge, where certain intermediate-temperature chemistry pathways become competitive."

### 3. **ORIGINAL TEXT CITATIONS**
- Provide 1-3 **VERBATIM QUOTES** from the paper for each question
- Quotes must be at least 50 characters each
- Quotes should support the answer's technical content

### 4. **QUALITY STANDARDS**
- ✅ Clear, determinable answers
- ✅ Based on physical principles, not paper meta-information
- ✅ Time-independent (no "currently", "in 2024", etc.)
- ✅ Require deep understanding of domain physics/chemistry
- ❌ No pure memorization questions
- ❌ No overly open-ended questions

---

## 📊 QUESTION TYPE DISTRIBUTION (5 questions total)

Aim for:
- **reasoning** (mechanism, causation): 2-3 questions
- **concept** (deep understanding): 1-2 questions
- **calculation** (quantitative): 1 question
- **application** (apply principles): 0-1 question

---

## 🎯 DIFFICULTY LEVELS

Aim for:
- **difficulty 4-5** (Hard/Expert): 3-4 questions (60-80%)
- **difficulty 3** (Medium): 1-2 questions (20-40%)

---

## 📋 OUTPUT FORMAT (JSON)

```json
{
  "questions": [
    {
      "question_text": "Why does the negative temperature coefficient (NTC) region exist in low-temperature hydrocarbon oxidation, and what chain-branching/terminating reactions cause this phenomenon?",
      "standard_answer": "The NTC region arises from competing reaction pathways in the low-temperature oxidation of hydrocarbons (600-800K). At lower temperatures, alkyl radicals (R) react with O2 to form alkylperoxy radicals (ROO) which propagate chain-branching sequences through QOOH (hydroperoxyalkyl) intermediates, producing OH radicals and accelerating reactivity. However, as temperature increases within the NTC region, the ROO → R + O2 reverse reaction becomes thermodynamically favorable, diverting flux away from chain-branching pathways. Simultaneously, QOOH radicals can decompose to form olefins + HO2 (less reactive) rather than undergoing second O2 addition to form OOQOOH species (highly reactive chain-branching). This competition between chain-branching (QOOH + O2 → OOQOOH → 2OH + products) and chain-terminating (ROO → olefin + HO2) pathways creates a regime where increasing temperature paradoxically decreases reactivity, manifesting as negative ∂(ignition delay)/∂T.",
      "original_text": {
        "1": "EXACT VERBATIM QUOTE FROM PAPER - at least 50 characters - supports the low-temperature chemistry",
        "2": "ANOTHER EXACT QUOTE - describes chain-branching or NTC mechanisms",
        "3": "you can add as many quotes as needed"
      },
      "type": "reasoning",
      "difficulty": 5,
      "topic": "combustion_kinetics"
    }
  ]
}
```

**IMPORTANT**: 
- Return ONLY JSON, no other text
- Generate exactly 5 questions
- Each answer must be ≥300 characters
- Each question requires combustion/heat transfer/fluid/CFD/energy domain knowledge
- Include "original_text" with verbatim quotes

---

## 🔍 QUALITY SELF-CHECK

Before submitting, verify:
- [ ] All 5 answers are ≥300 characters
- [ ] Every question requires domain expertise (not pure ML/CS)
- [ ] Each question has original_text with verbatim quotes (≥50 chars each)
- [ ] Questions are time-independent (no "currently", "2024", etc.)
- [ ] At least 3 questions are difficulty 4-5
- [ ] Answers explain mechanisms/derivations, not just definitions

---

## PAPER CONTENT
{paper_text[:60000]}
