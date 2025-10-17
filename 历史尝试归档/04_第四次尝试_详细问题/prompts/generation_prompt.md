# ROLE
You are a senior expert in combustion science and engineering thermophysics, skilled at designing high-quality assessment questions based on scientific literature.

# TASK
Based on the following PECS (Progress in Energy and Combustion Science) review paper, generate **20 high-quality questions** WITH ORIGINAL TEXT CITATIONS.

{feedback_section}

---

## ✅ REQUIREMENTS FOR QUESTIONS

### 1. Based on Paper but Independent of Paper
- ✅ Questions based on concepts, principles, mechanisms from the paper
- ✅ But **DO NOT ask about the paper itself** (❌ "What does this article discuss?" "What views did the author propose?")
- ✅ Questions should test **domain knowledge**, not "reading comprehension"

### 2. **CRITICAL: Include Original Text Citations**
- ✅ For EACH question, provide 1-3 **EXACT QUOTES** from the paper that support the question/answer
- ✅ Quotes must be **VERBATIM** (word-for-word) from the paper, NOT paraphrased or summarized
- ✅ Quotes should be substantial (at least 50 characters each)
- ✅ Quotes must be directly relevant to the question's scientific content

**Example**:
```json
{
  "question_text": "Why does increasing pressure shorten ignition delay time?",
  "standard_answer": "Increased pressure raises molecular number density...",
  "original_text": {
    "1": "The ignition delay time decreases with increasing pressure due to the higher molecular number density, which leads to more frequent molecular collisions and faster reaction rates.",
    "2": "At elevated pressures, three-body reactions become more important, further accelerating the ignition process through enhanced chain branching."
  },
  "type": "reasoning",
  "difficulty": 3,
  "topic": "ignition_kinetics"
}
```

### 3. Clear and Determinable Answers
- ✅ Must have clear correct/incorrect standards
- ✅ Priority: calculation questions, judgment questions, causal reasoning questions
- ❌ Avoid: open-ended discussion questions ("How to optimize XX?"), trend prediction questions ("How will XX technology develop in the future?")

### 4. Time-Independent
- ✅ Based on physical principles, chemical mechanisms, mathematical relationships
- ❌ Avoid: specific year technology applications, latest developments, industrial status ("Applications of XX technology in XX field in 2024")

### 5. Depth First
- ✅ Require understanding **why**, **what is the mechanism**, **how to derive**
- ❌ Avoid: pure memorization definition questions ("What is ignition delay?")
- ✅ Encourage: mechanism explanation questions ("Why does increased pressure shorten ignition delay?")

---

## 📊 QUESTION TYPE DISTRIBUTION

### **reasoning (Reasoning Analysis) - 50%** (Most Important)
- Causal reasoning: "Why does X lead to Y?"
- Mechanism explanation: "What is the physical/chemical mechanism of X phenomenon?"
- Parameter influence: "How does changing X affect Y? Through what pathway?"

**Example**:
```
Q: Why does increasing pressure shorten ignition delay time? Explain from the molecular collision perspective.
A: Increased pressure raises molecular number density, leading to increased collision frequency. According to the Arrhenius law,
   reaction rate is proportional to collision frequency, so chemical reactions accelerate and ignition delay time shortens.
   Quantitatively, ignition delay τ ∝ P^(-n), where n is typically 1-2.
```

### **concept (Conceptual Understanding) - 25%**
- Deep meaning of key concepts (not simple definitions)
- Relationships and differences between concepts
- Can be "term explanation", but requires depth

**Example**:
```
Q: What is the difference between laminar flame speed and flame propagation speed?
   Which is more relevant in turbulent combustion?
A: Laminar flame speed is the normal velocity of unburned mixture relative to the flame front, a thermochemical property.
   Flame propagation speed is the spatial movement velocity of the flame front, affected by turbulence and stretch.
   In turbulent combustion, flame propagation speed is more relevant because turbulence significantly enhances propagation,
   but laminar flame speed remains the fundamental parameter.
```

### **calculation (Calculation) - 15%**
- Quantitative reasoning
- Order of magnitude estimation
- Parameter calculation

**Example**:
```
Q: A methane-air mixture (φ=1.0) has a laminar flame speed of about 0.4 m/s at 300K, 1atm.
   If pressure increases to 10 atm and temperature rises to 600K, estimate the new flame speed (given SL ∝ T^α P^β,
   α≈2, β≈-0.5).
A: SL,new = SL,ref × (T_new/T_ref)^α × (P_new/P_ref)^β
         = 0.4 × (600/300)^2 × (10/1)^(-0.5)
         = 0.4 × 4 × 0.316 ≈ 0.5 m/s
```

### **application (Application) - 10%**
- Apply principles to specific scenarios
- Must have clear answers, cannot be too open

**Example**:
```
Q: In HCCI engine design, why is precise intake temperature control necessary?
   (Answer from ignition mechanism perspective)
A: HCCI relies on auto-ignition, where ignition timing is determined by mixture chemical kinetics. Intake temperature directly affects
   end-of-compression temperature, which affects ignition delay. Temperature deviation of 5-10K may cause ignition timing to advance/delay
   by several crank angles, affecting combustion phasing and performance. Therefore precise control is needed (typically within ±2K).
```

---

## 🎯 DIFFICULTY LEVELS (1-5)

**Distribution Requirements**:
- difficulty 3-4: 70% (main body)
- difficulty 5: 20% (challenging)
- difficulty 1-2: 10% (basic)

**Difficulty Definitions**:
- **3**: Requires understanding mechanism of a single concept
- **4**: Requires integrating multiple concepts or involves quantitative reasoning
- **5**: Requires deep analysis, interdisciplinary knowledge, or complex derivation

---

## ❌ STRICTLY AVOID THESE QUESTION TYPES

### Type 1: Paper Meta-Information Questions
```
❌ "What combustion modes does this review discuss?"
❌ "What viewpoint did the author propose in Section 3?"
❌ "Which classical models did the paper cite?"
```

### Type 2: Open-ended/Subjective Questions
```
❌ "How to optimize diesel NOx emissions?" (too open, non-unique answer)
❌ "What is the future development direction of HCCI technology?" (predictive, will become outdated)
❌ "Discuss the potential of machine learning in combustion" (too broad)
```

### Type 3: Pure Definition Memorization Questions
```
❌ "What is ignition delay time?" (can be searched on Google)
✅ "Why does ignition delay time show non-monotonic variation with increasing temperature?" (requires understanding NTC region)
```

### Type 4: Time-Sensitive Questions
```
❌ "Impact of electric vehicles on internal combustion engines in 2024"
❌ "Current industrial NOx after-treatment technologies"
```

---

## 📋 OUTPUT FORMAT (JSON)

```json
{
  "questions": [
    {
      "question_text": "Why does increasing pressure shorten ignition delay time? Explain from molecular collision and chemical kinetics perspectives.",
      "standard_answer": "Increased pressure raises molecular number density, causing collision frequency to increase proportionally with P. According to Arrhenius law, reaction rate k is proportional to collision frequency and activation energy exponential term. At high pressure, elementary reaction rates accelerate, chain reactions progress faster, leading to shortened ignition delay time τ. The quantitative relationship is τ ∝ P^(-n), where n depends on reaction mechanism, typically between 1-2. Additionally, at high pressure, three-body reaction contributions are enhanced, further accelerating the ignition process.",
      "original_text": {
        "1": "EXACT VERBATIM QUOTE FROM PAPER - at least 50 characters - supports pressure effect on ignition",
        "2": "ANOTHER EXACT QUOTE - describes molecular collision or reaction rate mechanisms"
      },
      "type": "reasoning",
      "difficulty": 3,
      "topic": "ignition_kinetics"
    }
  ]
}
```

**CRITICAL**: 
- Return ONLY JSON, no other text, explanations, or markdown code blocks
- Generate exactly 20 questions
- Standard answers must be sufficiently detailed (at least 100 characters)

---

## 🔍 QUALITY SELF-CHECK (Confirm After Generation)

- [ ] Each question passes the "why" test (has clear physical/chemical mechanism)
- [ ] Answers have uniqueness or determinability (not "it depends")
- [ ] No mention of "this paper", "the author", "the review"
- [ ] No time-related words ("in recent years", "currently", "2024")
- [ ] At least 10 reasoning questions (require reasoning mechanisms)
- [ ] difficulty 3-5 accounts for > 80%
- [ ] **EVERY question has original_text with 1-3 verbatim quotes (≥50 chars each)**

---

## PAPER CONTENT
{paper_text[:50000]}
