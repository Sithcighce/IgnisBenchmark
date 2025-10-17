"""
Milestone 1 Compare Generator: Improved Quality with Iterative Validation
Goal: Generate 20 high-quality questions with ≥90% acceptance rate
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from litellm import completion

from src.utils import load_config, setup_logging, load_env_variables

logger = logging.getLogger(__name__)


class Milestone1CompareGenerator:
    """Improved generator with quality checking loop"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generation_model = config.get("generation_model", "gemini/gemini-2.0-flash-exp")
        self.quality_check_model = config.get("quality_check_model", "gemini/gemini-2.0-flash-exp")
        self.paper_path = config.get("paper_path", "main.txt")
        self.output_path = config.get("output_path", "data/milestone1_compare.jsonl")
        self.report_path = config.get("report_path", "data/milestone1_compare_report.md")
        self.max_iterations = config.get("max_iterations", 3)
        self.acceptance_threshold = config.get("acceptance_threshold", 0.90)
        
    def load_paper_text(self) -> str:
        """Load paper text"""
        logger.info(f"Loading paper from: {self.paper_path}")
        
        if not os.path.exists(self.paper_path):
            raise FileNotFoundError(f"Paper file not found: {self.paper_path}")
        
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"Paper loaded successfully: {len(text)} characters")
        return text
    
    def build_generation_prompt(self, paper_text: str, iteration: int = 1, 
                                feedback: str = "") -> str:
        """Build English generation prompt (translated from 新prompt.md)"""
        
        feedback_section = ""
        if iteration > 1 and feedback:
            feedback_section = f"""
---

## 🔄 FEEDBACK FROM PREVIOUS ITERATION

**Issues found in previous generation:**
{feedback}

**Please address these issues in the new generation.**

---
"""
        
        prompt = f"""# ROLE
You are a senior expert in combustion science and engineering thermophysics, skilled at designing high-quality assessment questions based on scientific literature.

# TASK
Based on the following PECS (Progress in Energy and Combustion Science) review paper, generate **20 high-quality questions**.

{feedback_section}

---

## ✅ REQUIREMENTS FOR QUESTIONS

### 1. Based on Paper but Independent of Paper
- ✅ Questions based on concepts, principles, mechanisms from the paper
- ✅ But **DO NOT ask about the paper itself** (❌ "What does this article discuss?" "What views did the author propose?")
- ✅ Questions should test **domain knowledge**, not "reading comprehension"

### 2. Clear and Determinable Answers
- ✅ Must have clear correct/incorrect standards
- ✅ Priority: calculation questions, judgment questions, causal reasoning questions
- ❌ Avoid: open-ended discussion questions ("How to optimize XX?"), trend prediction questions ("How will XX technology develop in the future?")

### 3. Time-Independent
- ✅ Based on physical principles, chemical mechanisms, mathematical relationships
- ❌ Avoid: specific year technology applications, latest developments, industrial status ("Applications of XX technology in XX field in 2024")

### 4. Depth First
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
{{
  "questions": [
    {{
      "question_text": "Why does increasing pressure shorten ignition delay time? Explain from molecular collision and chemical kinetics perspectives.",
      "standard_answer": "Increased pressure raises molecular number density, causing collision frequency to increase proportionally with P. According to Arrhenius law, reaction rate k is proportional to collision frequency and activation energy exponential term. At high pressure, elementary reaction rates accelerate, chain reactions progress faster, leading to shortened ignition delay time τ. The quantitative relationship is τ ∝ P^(-n), where n depends on reaction mechanism, typically between 1-2. Additionally, at high pressure, three-body reaction contributions are enhanced, further accelerating the ignition process.",
      "type": "reasoning",
      "difficulty": 3,
      "topic": "ignition_kinetics"
    }}
  ]
}}
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

---

## PAPER CONTENT
{paper_text[:50000]}
"""
        return prompt
    
    def build_quality_check_prompt(self, question: Dict[str, Any]) -> str:
        """Build English quality check prompt (translated from 质量检查prompt.md)"""
        
        prompt = f"""# ROLE
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
{{
  "compliant": true/false,
  "issues": [
    {{
      "type": "meta_question/time_sensitive/too_open/shallow_definition",
      "description": "specific issue description"
    }}
  ],
  "severity": "reject/review/pass",
  "recommendation": "recommendation"
}}
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
"""
        return prompt
    
    def call_llm(self, prompt: str, model: str, require_json: bool = True) -> str:
        """Call LLM with fallback mechanism"""
        model_fallbacks = [
            {'model': model},
            {'model': 'openai/deepseek-ai/DeepSeek-V3', 
             'api_base': 'https://api.siliconflow.cn/v1', 
             'api_key': os.environ.get('SILICONFLOW_API_KEY')}
        ]
        
        for attempt in range(2):
            for model_index, m in enumerate(model_fallbacks):
                try:
                    if attempt > 0 or model_index > 0:
                        logger.info(f"Attempt {attempt+1}, trying model: {m['model']}")
                    
                    completion_kwargs = {
                        "model": m['model'],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8 if "generation" in prompt else 0.3,
                        "max_tokens": 8000,
                        "timeout": 180
                    }
                    
                    if require_json and ("gemini" in m['model'].lower() or "openai" in m['model']):
                        completion_kwargs["response_format"] = {"type": "json_object"}
                    
                    if 'api_base' in m and m['api_base']:
                        completion_kwargs['api_base'] = m['api_base']
                    if 'api_key' in m and m['api_key']:
                        completion_kwargs['api_key'] = m['api_key']
                    
                    response = completion(**completion_kwargs)
                    
                    if not response or not response.choices:
                        logger.warning(f"Model {m['model']} returned empty response")
                        continue
                    
                    message = response.choices[0].message
                    if not message.content:
                        logger.warning(f"Model {m['model']} returned empty content")
                        continue
                    
                    response_text = message.content.strip()
                    
                    # Remove possible markdown code block markers
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.startswith("```"):
                        response_text = response_text[3:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    return response_text.strip()
                    
                except Exception as e:
                    logger.warning(f"❌ Model {m['model']} attempt {attempt+1} failed: {e}")
                    continue
        
        raise RuntimeError("All models and retries failed")
    
    def generate_questions(self, paper_text: str, iteration: int = 1, 
                          feedback: str = "") -> List[Dict[str, Any]]:
        """Generate questions using LLM"""
        logger.info("=" * 60)
        logger.info(f"ITERATION {iteration}: Generating Questions")
        logger.info(f"Using model: {self.generation_model}")
        logger.info("=" * 60)
        
        prompt = self.build_generation_prompt(paper_text, iteration, feedback)
        response_text = self.call_llm(prompt, self.generation_model, require_json=True)
        
        # Save raw response for debugging
        debug_path = f"data/milestone1_compare_raw_iter{iteration}.txt"
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info(f"Raw response saved to: {debug_path}")
        
        # Parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")
            # Try to fix common JSON issues
            import re
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            data = json.loads(response_text)
        
        questions = data.get("questions", [])
        
        if not questions:
            raise ValueError("No questions generated")
        
        logger.info(f"✅ Successfully generated {len(questions)} questions")
        return questions
    
    def check_question_quality(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality of a single question"""
        prompt = self.build_quality_check_prompt(question)
        response_text = self.call_llm(prompt, self.quality_check_model, require_json=True)
        
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Quality check JSON parse failed: {e}")
            # Fallback: assume it passes review
            return {
                "compliant": True,
                "issues": [],
                "severity": "review",
                "recommendation": "Failed to parse quality check result"
            }
    
    def batch_quality_check(self, questions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float, str]:
        """
        Perform quality check on all questions
        Returns: (quality_results, acceptance_rate, feedback)
        """
        logger.info("=" * 60)
        logger.info("Performing Quality Check on All Questions")
        logger.info(f"Using model: {self.quality_check_model}")
        logger.info("=" * 60)
        
        quality_results = []
        
        for i, q in enumerate(questions, 1):
            logger.info(f"Checking question {i}/{len(questions)}...")
            try:
                result = self.check_question_quality(q)
                quality_results.append(result)
            except Exception as e:
                logger.warning(f"Quality check failed for question {i}: {e}")
                quality_results.append({
                    "compliant": True,
                    "issues": [],
                    "severity": "review",
                    "recommendation": f"Quality check error: {e}"
                })
        
        # Calculate acceptance rate
        pass_count = sum(1 for r in quality_results if r.get("severity") == "pass")
        review_count = sum(1 for r in quality_results if r.get("severity") == "review")
        reject_count = sum(1 for r in quality_results if r.get("severity") == "reject")
        
        acceptance_rate = (pass_count + review_count) / len(quality_results) if quality_results else 0
        
        logger.info(f"Quality Check Results:")
        logger.info(f"  Pass: {pass_count}/{len(quality_results)}")
        logger.info(f"  Review: {review_count}/{len(quality_results)}")
        logger.info(f"  Reject: {reject_count}/{len(quality_results)}")
        logger.info(f"  Acceptance Rate: {acceptance_rate*100:.1f}%")
        
        # Generate feedback for next iteration
        feedback = self._generate_feedback(quality_results, questions)
        
        return quality_results, acceptance_rate, feedback
    
    def _generate_feedback(self, quality_results: List[Dict[str, Any]], 
                          questions: List[Dict[str, Any]]) -> str:
        """Generate feedback based on quality check results"""
        issue_types = {}
        
        for i, (result, question) in enumerate(zip(quality_results, questions), 1):
            if result.get("severity") == "reject":
                for issue in result.get("issues", []):
                    issue_type = issue.get("type", "unknown")
                    if issue_type not in issue_types:
                        issue_types[issue_type] = []
                    issue_types[issue_type].append({
                        "question_num": i,
                        "question_text": question.get("question_text", "")[:100],
                        "description": issue.get("description", "")
                    })
        
        if not issue_types:
            return ""
        
        feedback = "Common issues found:\n\n"
        for issue_type, examples in issue_types.items():
            feedback += f"**{issue_type}** ({len(examples)} questions):\n"
            for ex in examples[:3]:  # Show first 3 examples
                feedback += f"  - Q{ex['question_num']}: {ex['question_text']}...\n"
                feedback += f"    Issue: {ex['description']}\n"
            feedback += "\n"
        
        return feedback
    
    def wrap_with_metadata(self, questions: List[Dict[str, Any]], 
                          quality_results: List[Dict[str, Any]],
                          paper_id: str = "PECS_2020_Vol85_p1", 
                          paper_title: str = "Combustion Theory Review") -> List[Dict[str, Any]]:
        """Add system metadata fields"""
        logger.info("=" * 60)
        logger.info("Adding System Metadata")
        logger.info("=" * 60)
        
        wrapped_questions = []
        
        for q, qr in zip(questions, quality_results):
            wrapped = {
                # System generated fields
                "question_id": f"comb_qa_{str(uuid.uuid4())[:8]}",
                
                # AI generated fields
                "question_text": q.get("question_text", ""),
                "standard_answer": q.get("standard_answer", ""),
                "type": q.get("type", "reasoning"),
                "difficulty": q.get("difficulty", 3),
                "topic": q.get("topic", "general_combustion"),
                
                # Source information
                "source": {
                    "type": "with_reference",
                    "paper_id": paper_id,
                    "paper_title": paper_title
                },
                
                # Quality check result
                "quality_check": {
                    "severity": qr.get("severity", "review"),
                    "compliant": qr.get("compliant", True),
                    "issues": qr.get("issues", []),
                    "recommendation": qr.get("recommendation", "")
                },
                
                # Metadata
                "metadata": {
                    "generation_model": self.generation_model,
                    "quality_check_model": self.quality_check_model,
                    "created_at": datetime.now().isoformat(),
                    "milestone": "milestone_1_compare"
                }
            }
            wrapped_questions.append(wrapped)
        
        logger.info(f"✓ Successfully wrapped {len(wrapped_questions)} questions")
        return wrapped_questions
    
    def save_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Save questions to JSONL file"""
        logger.info("=" * 60)
        logger.info("Saving Questions")
        logger.info("=" * 60)
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        
        logger.info(f"✓ Questions saved to: {self.output_path}")
        logger.info(f"  Total: {len(questions)} questions")
    
    def generate_final_report(self, questions: List[Dict[str, Any]], 
                            quality_results: List[Dict[str, Any]],
                            acceptance_rate: float,
                            iterations: int) -> str:
        """Generate final quality assessment report"""
        logger.info("=" * 60)
        logger.info("Generating Final Report")
        logger.info("=" * 60)
        
        total = len(questions)
        
        # Type distribution
        type_count = {}
        for q in questions:
            qtype = q.get("type", "unknown")
            type_count[qtype] = type_count.get(qtype, 0) + 1
        
        # Difficulty distribution
        difficulty_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for q in questions:
            diff = q.get("difficulty", 3)
            if diff in difficulty_count:
                difficulty_count[diff] += 1
        
        # Topic distribution
        topic_count = {}
        for q in questions:
            topic = q.get("topic", "unknown")
            topic_count[topic] = topic_count.get(topic, 0) + 1
        
        # Quality distribution
        pass_count = sum(1 for r in quality_results if r.get("severity") == "pass")
        review_count = sum(1 for r in quality_results if r.get("severity") == "review")
        reject_count = sum(1 for r in quality_results if r.get("severity") == "reject")
        
        # Answer length analysis
        answer_lengths = [len(q.get("standard_answer", "")) for q in questions]
        avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        
        report = f"""# Milestone 1 Compare - Quality Assessment Report

**Generation Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Generation Model**: {self.generation_model}  
**Quality Check Model**: {self.quality_check_model}  
**Data Source**: {self.paper_path}  
**Iterations**: {iterations}  
**Acceptance Threshold**: {self.acceptance_threshold*100:.0f}%

---

## 🎯 QUALITY CHECK RESULTS

### Overall Acceptance Rate: **{acceptance_rate*100:.1f}%** {'✅ PASSED' if acceptance_rate >= self.acceptance_threshold else '❌ FAILED'}

| Severity | Count | Percentage |
|----------|-------|------------|
| ✅ Pass | {pass_count} | {pass_count/total*100:.1f}% |
| ⚠️ Review | {review_count} | {review_count/total*100:.1f}% |
| ❌ Reject | {reject_count} | {reject_count/total*100:.1f}% |
| **Total Acceptable** | **{pass_count + review_count}** | **{acceptance_rate*100:.1f}%** |

---

## 📊 OVERALL STATISTICS

- **Total Questions**: {total}
- **Target**: 20 questions
- **Completion Rate**: {total/20*100:.1f}%

---

## 🎯 QUESTION TYPE DISTRIBUTION

| Type | Count | Percentage | Target |
|------|-------|------------|--------|
"""
        
        type_targets = {"reasoning": 50, "concept": 25, "calculation": 15, "application": 10}
        for qtype in sorted(type_count.keys()):
            count = type_count[qtype]
            percentage = count / total * 100
            target = type_targets.get(qtype, 0)
            status = "✅" if abs(percentage - target) <= 10 else "⚠️"
            report += f"| {qtype} | {count} | {percentage:.1f}% | {target}% {status} |\n"
        
        report += f"""
---

## 📈 DIFFICULTY DISTRIBUTION

| Difficulty | Count | Percentage | Target | Status |
|------------|-------|------------|--------|--------|
| 1 (Basic) | {difficulty_count[1]} | {difficulty_count[1]/total*100:.1f}% | 5% | {'✅' if difficulty_count[1]/total <= 0.15 else '⚠️'} |
| 2 (Easy) | {difficulty_count[2]} | {difficulty_count[2]/total*100:.1f}% | 5% | {'✅' if difficulty_count[2]/total <= 0.15 else '⚠️'} |
| 3 (Medium) | {difficulty_count[3]} | {difficulty_count[3]/total*100:.1f}% | 35% | {'✅' if 0.25 <= difficulty_count[3]/total <= 0.45 else '⚠️'} |
| 4 (Hard) | {difficulty_count[4]} | {difficulty_count[4]/total*100:.1f}% | 35% | {'✅' if 0.25 <= difficulty_count[4]/total <= 0.45 else '⚠️'} |
| 5 (Expert) | {difficulty_count[5]} | {difficulty_count[5]/total*100:.1f}% | 20% | {'✅' if 0.10 <= difficulty_count[5]/total <= 0.30 else '⚠️'} |

---

## 🔬 TOPIC DISTRIBUTION

"""
        for topic, count in sorted(topic_count.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total * 100
            report += f"- **{topic}**: {count} questions ({percentage:.1f}%)\n"
        
        report += f"""
---

## 📝 ANSWER QUALITY ANALYSIS

- **Average Answer Length**: {avg_length:.0f} characters
- **Questions with adequate answers** (≥100 chars): {sum(1 for l in answer_lengths if l >= 100)} / {total}

---

## ⚠️ REJECTED QUESTIONS ANALYSIS

"""
        
        rejected_questions = [(i+1, q, r) for i, (q, r) in enumerate(zip(questions, quality_results)) 
                             if r.get("severity") == "reject"]
        
        if rejected_questions:
            report += f"Total rejected: {len(rejected_questions)}\n\n"
            for i, (qnum, q, r) in enumerate(rejected_questions[:5], 1):
                report += f"### Rejected Question {i} (Q{qnum})\n\n"
                report += f"**Question**: {q.get('question_text', '')[:200]}...\n\n"
                report += f"**Issues**:\n"
                for issue in r.get("issues", []):
                    report += f"- **{issue.get('type')}**: {issue.get('description')}\n"
                report += f"\n**Recommendation**: {r.get('recommendation', 'N/A')}\n\n"
                report += "---\n\n"
        else:
            report += "No questions were rejected! ✅\n\n"
        
        report += f"""
---

## ✅ ACCEPTANCE CRITERIA

- [{'x' if total == 20 else ' '}] Generated exactly 20 complete Q&A pairs
- [{'x' if acceptance_rate >= self.acceptance_threshold else ' '}] Acceptance rate ≥ {self.acceptance_threshold*100:.0f}%
- [{'x' if sum(1 for l in answer_lengths if l >= 100) >= 18 else ' '}] At least 18 questions with adequate answers (≥100 chars)
- [x] Output in standard JSON format

---

## 💡 RECOMMENDATIONS

"""
        if acceptance_rate >= 0.95:
            report += "✨ **Excellent Quality**! Almost all questions meet standards. Ready for next milestone.\n"
        elif acceptance_rate >= self.acceptance_threshold:
            report += "✓ **Good Quality**. Acceptance rate meets threshold. Recommend manual review of questions marked for review.\n"
        else:
            report += f"⚠️ **Needs Improvement**. Acceptance rate {acceptance_rate*100:.1f}% is below threshold {self.acceptance_threshold*100:.0f}%.\n"
        
        report += f"""
---

## 📋 SAMPLE QUESTIONS

### Top 3 Passed Questions

"""
        
        passed_questions = [(i+1, q) for i, (q, r) in enumerate(zip(questions, quality_results)) 
                           if r.get("severity") == "pass"]
        
        for i, (qnum, q) in enumerate(passed_questions[:3], 1):
            report += f"""
#### Question {i} (Q{qnum})

- **Type**: {q.get('type')}
- **Difficulty**: {q.get('difficulty')}/5
- **Topic**: {q.get('topic')}

**Question**:  
{q.get('question_text', '')}

**Answer**:  
{q.get('standard_answer', '')[:300]}{'...' if len(q.get('standard_answer', '')) > 300 else ''}

---
"""
        
        return report
    
    def save_report(self, report: str) -> None:
        """Save assessment report"""
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to: {self.report_path}")
    
    def run(self) -> None:
        """Run complete iterative generation and quality check process"""
        logger.info("=" * 80)
        logger.info("🚀 Milestone 1 Compare: Iterative Generation with Quality Check")
        logger.info("=" * 80)
        
        try:
            # Load paper
            paper_text = self.load_paper_text()
            
            # Iterative generation
            iteration = 1
            feedback = ""
            
            while iteration <= self.max_iterations:
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"ITERATION {iteration}/{self.max_iterations}")
                logger.info("=" * 80)
                
                # Generate questions
                ai_questions = self.generate_questions(paper_text, iteration, feedback)
                
                # Quality check
                quality_results, acceptance_rate, feedback = self.batch_quality_check(ai_questions)
                
                # Check if acceptance threshold met
                if acceptance_rate >= self.acceptance_threshold:
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info(f"✅ ACCEPTANCE THRESHOLD MET: {acceptance_rate*100:.1f}% >= {self.acceptance_threshold*100:.0f}%")
                    logger.info("=" * 80)
                    
                    # Wrap with metadata
                    full_questions = self.wrap_with_metadata(
                        ai_questions,
                        quality_results,
                        paper_id="PECS_combustion_review",
                        paper_title="Combustion Science Review"
                    )
                    
                    # Save questions
                    self.save_questions(full_questions)
                    
                    # Generate and save report
                    report = self.generate_final_report(ai_questions, quality_results, 
                                                       acceptance_rate, iteration)
                    self.save_report(report)
                    
                    # Print report to console
                    print("\n" + report)
                    
                    logger.info("=" * 80)
                    logger.info("✅ MILESTONE 1 COMPARE COMPLETED SUCCESSFULLY!")
                    logger.info("=" * 80)
                    logger.info(f"📄 Questions file: {self.output_path}")
                    logger.info(f"📊 Report file: {self.report_path}")
                    logger.info(f"🎯 Final acceptance rate: {acceptance_rate*100:.1f}%")
                    logger.info(f"🔄 Iterations used: {iteration}/{self.max_iterations}")
                    
                    return
                
                else:
                    logger.warning("")
                    logger.warning("=" * 80)
                    logger.warning(f"⚠️ Acceptance rate {acceptance_rate*100:.1f}% < threshold {self.acceptance_threshold*100:.0f}%")
                    logger.warning(f"Will retry with iteration {iteration + 1}")
                    logger.warning("=" * 80)
                    iteration += 1
            
            # Max iterations reached without meeting threshold
            logger.error("")
            logger.error("=" * 80)
            logger.error(f"❌ FAILED: Maximum iterations ({self.max_iterations}) reached")
            logger.error(f"Final acceptance rate: {acceptance_rate*100:.1f}% < threshold {self.acceptance_threshold*100:.0f}%")
            logger.error("=" * 80)
            
            # Still save the best attempt
            full_questions = self.wrap_with_metadata(
                ai_questions,
                quality_results,
                paper_id="PECS_combustion_review",
                paper_title="Combustion Science Review"
            )
            self.save_questions(full_questions)
            
            report = self.generate_final_report(ai_questions, quality_results, 
                                               acceptance_rate, self.max_iterations)
            self.save_report(report)
            
            logger.info(f"Best attempt saved to: {self.output_path}")
            
        except Exception as e:
            logger.error(f"❌ Milestone 1 Compare execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


def main():
    """Main function"""
    # Load config
    config = load_config()
    
    # Setup logging
    setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file="logs/milestone1_compare.log"
    )
    
    # Load environment variables
    load_env_variables(config.get("env_file_path", ".env"))
    
    # Milestone 1 Compare configuration
    m1_compare_config = {
        "generation_model": config.get("generation_model", "gemini/gemini-2.0-flash-exp"),
        "quality_check_model": config.get("quality_check_model", "gemini/gemini-2.0-flash-exp"),
        "paper_path": "main.txt",
        "output_path": "data/milestone1_compare.jsonl",
        "report_path": "data/milestone1_compare_report.md",
        "max_iterations": 3,
        "acceptance_threshold": 0.90
    }
    
    # Run
    generator = Milestone1CompareGenerator(m1_compare_config)
    generator.run()


if __name__ == "__main__":
    main()
