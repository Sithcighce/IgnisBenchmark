#!/usr/bin/env python3
"""
DeepSeek Detail Q Generator - CORRECTED ENGLISH VERSION
Uses proper English prompts from milestone1_detail_Q_generator.py
50 concurrent workers for faster processing
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from litellm import completion

from src.utils import setup_logging, load_env_variables

logger = logging.getLogger(__name__)

# DeepSeek配置
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_BASE = "https://api.deepseek.com"
MAX_RETRIES_PER_QUESTION = 3
MAX_CONCURRENT_FILES = 50  # 50并发


class DeepSeekEnglishQGenerator:
    """CORRECTED: Uses English prompts from milestone1_detail_Q_generator.py"""
    
    def __init__(self, output_dir: str = "question_english"):
        self.output_dir = Path(output_dir)
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        logger.info(f"Initialized DeepSeek ENGLISH Generator")
        logger.info(f"Model: {DEEPSEEK_MODEL}")
        logger.info(f"API Base: {DEEPSEEK_API_BASE}")
        logger.info(f"Concurrent workers: {MAX_CONCURRENT_FILES}")
        
        self.stats = {
            "total_files": 0,
            "completed": 0,
            "failed": 0,
            "total_questions": 0,
            "passed_questions": 0,
            "failed_questions": 0,
            "total_retries": 0
        }
    
    def call_deepseek(self, prompt: str, require_json: bool = False, timeout: int = 120) -> str:
        """调用DeepSeek API"""
        kwargs = {
            "model": "deepseek/" + DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "api_base": DEEPSEEK_API_BASE,
            "api_key": self.api_key,
            "timeout": timeout,
            "temperature": 0.7
        }
        
        if require_json:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = completion(**kwargs)
        return response.choices[0].message.content
    
    def build_generation_prompt(self, paper_text: str) -> str:
        """CORRECTED: English prompt from milestone1_detail_Q_generator.py"""
        
        prompt = f"""# ROLE
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
{{
  "questions": [
    {{
      "question_text": "Why does the negative temperature coefficient (NTC) region exist in low-temperature hydrocarbon oxidation, and what chain-branching/terminating reactions cause this phenomenon?",
      "standard_answer": "The NTC region arises from competing reaction pathways in the low-temperature oxidation of hydrocarbons (600-800K). At lower temperatures, alkyl radicals (R) react with O2 to form alkylperoxy radicals (ROO) which propagate chain-branching sequences through QOOH (hydroperoxyalkyl) intermediates, producing OH radicals and accelerating reactivity. However, as temperature increases within the NTC region, the ROO → R + O2 reverse reaction becomes thermodynamically favorable, diverting flux away from chain-branching pathways. Simultaneously, QOOH radicals can decompose to form olefins + HO2 (less reactive) rather than undergoing second O2 addition to form OOQOOH species (highly reactive chain-branching). This competition between chain-branching (QOOH + O2 → OOQOOH → 2OH + products) and chain-terminating (ROO → olefin + HO2) pathways creates a regime where increasing temperature paradoxically decreases reactivity, manifesting as negative ∂(ignition delay)/∂T.",
      "original_text": {{
        "1": "EXACT VERBATIM QUOTE FROM PAPER - at least 50 characters - supports the low-temperature chemistry",
        "2": "ANOTHER EXACT QUOTE - describes chain-branching or NTC mechanisms"
      }},
      "type": "reasoning",
      "difficulty": 5,
      "topic": "combustion_kinetics"
    }}
  ]
}}
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
"""
        return prompt
    
    def build_quality_check_prompt(self, question: Dict[str, Any], paper_excerpt: str) -> str:
        """CORRECTED: English quality check prompt"""
        
        original_text_str = "\n".join([f"[Citation {k}]: {v}" for k, v in question.get("original_text", {}).items()])
        
        prompt = f"""# ROLE
You are a strict question quality reviewer AND answer correctness verifier. You check if questions meet specifications AND if the standard answer is factually correct based on the paper.

---

## TASK 1: DOMAIN FOCUS CHECK

### ❌ REJECT if question is:
1. **Pure ML/CS/Statistics**: Questions that can be answered with general ML knowledge without domain context
   - ❌ "What is the advantage of Random Forest over Decision Trees?"
   - ❌ "How does cross-validation prevent overfitting?"
   
2. **Acceptable ML in Domain Context**: ML applied to combustion/CFD/energy
   - ✅ "Why does ANN struggle to predict cyclic variability in HCCI combustion compared to stochastic models?"
   - ✅ "How does physics-informed neural network improve CFD turbulence modeling accuracy?"

### ✅ ACCEPT if question requires:
- Combustion science knowledge (kinetics, flames, ignition, emissions)
- Heat transfer principles (conduction, convection, radiation)
- Fluid mechanics concepts (turbulence, flow, boundary layers)
- CFD expertise (numerical methods, modeling, mesh)
- Energy systems understanding (engines, efficiency, thermal management)

---

## TASK 2: ANSWER CORRECTNESS VERIFICATION

Based on the **original_text citations** and **paper content**, verify if the standard answer is:

### ✅ CORRECT if:
- Facts align with citations and paper content
- Mechanisms/principles are accurately described
- Quantitative relationships are correct
- No contradictions with paper

### ❌ INCORRECT if:
- **Too Brief**: Answer < 300 characters (insufficient detail)
- **Factual Errors**: Contradicts citations or known physics
- **Fundamental Errors**: Wrong mechanisms, incorrect principles, logical flaws
- **Unsupported Claims**: Answer makes claims not backed by citations

---

## TASK 3: OTHER QUALITY CHECKS

❌ REJECT if:
- Paper meta-information ("this paper discusses...", "the author proposes...")
- Time-sensitive ("currently", "in 2024", "latest trends...")
- Overly open-ended (no determinable answer)
- Pure memorization (just definition, no depth)

---

## OUTPUT FORMAT

```json
{{
  "domain_focused": true/false,
  "domain_reasoning": "explanation why it requires or doesn't require domain expertise",
  
  "answer_correct": true/false,
  "answer_issues": [
    {{
      "type": "too_brief/factual_error/fundamental_error/unsupported",
      "description": "specific issue"
    }}
  ],
  
  "other_compliant": true/false,
  "other_issues": [
    {{
      "type": "meta_question/time_sensitive/too_open/shallow",
      "description": "specific issue"
    }}
  ],
  
  "overall_verdict": "pass/fail",
  "recommendation": "brief recommendation"
}}
```

**overall_verdict**:
- `pass`: Domain-focused + answer correct + no other issues
- `fail`: Any check fails

---

## QUESTION TO CHECK

```json
{json.dumps(question, ensure_ascii=False, indent=2)}
```

## ORIGINAL TEXT CITATIONS

{original_text_str}

## PAPER EXCERPT (for answer verification)

{paper_excerpt[:20000]}

**IMPORTANT**: Return ONLY the JSON result, no other text.
"""
        return prompt
    
    def build_retry_prompt(self, question: Dict[str, Any], quality_result: Dict[str, Any], paper_text: str) -> str:
        """CORRECTED: English retry prompt with feedback"""
        
        prompt = f"""# ROLE
You are a senior expert in combustion science, heat transfer, fluid mechanics, CFD, and energy systems.

Your previous question did NOT pass quality review. Please revise it based on the reviewer's feedback.

---

## ORIGINAL QUESTION

**Question**: {question['question_text']}

**Answer**: {question['standard_answer']}

**Citations**: {json.dumps(question['original_text'], ensure_ascii=False, indent=2)}

---

## QUALITY REVIEW FEEDBACK

**Domain Focused**: {"✅ Pass" if quality_result.get('domain_focused') else "❌ FAIL - " + quality_result.get('domain_reasoning', '')}

**Answer Correct**: {"✅ Pass" if quality_result.get('answer_correct') else "❌ FAIL - Issues: " + str(quality_result.get('answer_issues', []))}

**Other Compliant**: {"✅ Pass" if quality_result.get('other_compliant') else "❌ FAIL - Issues: " + str(quality_result.get('other_issues', []))}

**Recommendation**: {quality_result.get('recommendation', 'Please improve the question')}

---

## YOUR TASK

Revise the question to address ALL issues mentioned above:

1. **Ensure Domain Focus**: Must require combustion/heat transfer/fluid/CFD/energy expertise
2. **Detailed Answer**: ≥300 characters with mechanisms, derivations, or multi-step reasoning
3. **Accurate Content**: Facts must align with paper citations
4. **Proper Citations**: 1-3 verbatim quotes from paper (≥50 chars each)
5. **Fix ALL Issues**: Address every point in the recommendation

---

## PAPER CONTENT

{paper_text[:60000]}

---

## OUTPUT FORMAT (JSON ONLY)

```json
{{
  "question_text": "REVISED question text",
  "standard_answer": "REVISED detailed answer (≥300 characters)",
  "original_text": {{
    "1": "EXACT quote from paper",
    "2": "ANOTHER exact quote"
  }},
  "type": "reasoning|calculation|concept",
  "difficulty": 3-5,
  "topic": "combustion_kinetics|heat_transfer|fluid_mechanics|CFD_modeling|energy_systems"
}}
```

Return ONLY the JSON, no other text.
"""
        return prompt
    
    def retry_question(self, question: Dict[str, Any], quality_result: Dict[str, Any], 
                      paper_text: str, paper_excerpt: str, retry_count: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """重试生成单个问题"""
        logger.info(f"  Retry #{retry_count}: Regenerating question...")
        
        retry_prompt = self.build_retry_prompt(question, quality_result, paper_text)
        response = self.call_deepseek(retry_prompt, require_json=True)
        new_question = json.loads(response)
        
        check_prompt = self.build_quality_check_prompt(new_question, paper_excerpt)
        check_response = self.call_deepseek(check_prompt, require_json=True)
        new_quality_result = json.loads(check_response)
        
        self.stats["total_retries"] += 1
        
        return new_question, new_quality_result
    
    def process_single_question(self, question: Dict[str, Any], paper_text: str, 
                                paper_excerpt: str, q_index: int) -> Dict[str, Any]:
        """处理单个问题（含智能重试）"""
        logger.info(f"  Processing Q{q_index}...")
        
        check_prompt = self.build_quality_check_prompt(question, paper_excerpt)
        check_response = self.call_deepseek(check_prompt, require_json=True)
        quality_result = json.loads(check_response)
        
        current_question = question
        retry_count = 0
        
        while quality_result.get("overall_verdict") != "pass" and retry_count < MAX_RETRIES_PER_QUESTION:
            retry_count += 1
            logger.info(f"  Q{q_index} FAILED - Retrying ({retry_count}/{MAX_RETRIES_PER_QUESTION})...")
            
            current_question, quality_result = self.retry_question(
                current_question, quality_result, paper_text, paper_excerpt, retry_count
            )
        
        current_question["quality_check"] = quality_result
        current_question["retry_count"] = retry_count
        
        if quality_result.get("overall_verdict") == "pass":
            logger.info(f"  Q{q_index} PASSED (after {retry_count} retries)")
            return {"status": "pass", "question": current_question}
        else:
            logger.warning(f"  Q{q_index} FAILED (exhausted {MAX_RETRIES_PER_QUESTION} retries)")
            return {"status": "fail", "question": current_question}
    
    def process_single_file(self, txt_file: Path) -> Dict[str, Any]:
        """处理单个txt文件"""
        file_name = txt_file.stem
        logger.info(f"[{file_name}] Processing...")
        
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                paper_text = f.read()
            
            logger.info(f"[{file_name}] Paper length: {len(paper_text)} chars")
            
            output_folder = self.output_dir / file_name
            output_folder.mkdir(parents=True, exist_ok=True)
            
            shutil.copy(txt_file, output_folder / f"{file_name}.txt")
            
            logger.info(f"[{file_name}] Generating 5 questions...")
            gen_prompt = self.build_generation_prompt(paper_text)
            response = self.call_deepseek(gen_prompt, require_json=True, timeout=180)
            
            questions_data = json.loads(response)
            questions = questions_data.get("questions", [])
            logger.info(f"[{file_name}] Generated {len(questions)} questions")
            
            if len(questions) == 0:
                raise ValueError("No questions generated")
            
            paper_excerpt = paper_text[:8000]
            
            passed_questions = []
            failed_questions = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.process_single_question, q, paper_text, paper_excerpt, i): i
                    for i, q in enumerate(questions, 1)
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    
                    question = result["question"]
                    import hashlib
                    q_hash = hashlib.md5(question['question_text'].encode()).hexdigest()[:8]
                    question['question_id'] = f"deepseek_q_{q_hash}"
                    question['source'] = {
                        "type": "deepseek_generation",
                        "paper_file": file_name,
                        "paper_title": file_name
                    }
                    question['metadata'] = {
                        "generation_model": DEEPSEEK_MODEL,
                        "created_at": datetime.now().isoformat(),
                        "answer_length": len(question.get('standard_answer', ''))
                    }
                    
                    if result["status"] == "pass":
                        passed_questions.append(question)
                    else:
                        failed_questions.append(question)
            
            if passed_questions:
                with open(output_folder / "pass.json", 'w', encoding='utf-8') as f:
                    json.dump(passed_questions, f, ensure_ascii=False, indent=2)
            
            if failed_questions:
                with open(output_folder / "not_pass.json", 'w', encoding='utf-8') as f:
                    json.dump(failed_questions, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[{file_name}] ✅ Completed: {len(passed_questions)} passed, {len(failed_questions)} failed")
            
            return {
                "file": file_name,
                "status": "success",
                "total_questions": len(questions),
                "passed": len(passed_questions),
                "failed": len(failed_questions)
            }
            
        except Exception as e:
            logger.error(f"[{file_name}] ❌ Error: {str(e)[:500]}")
            return {
                "file": file_name,
                "status": "failed",
                "error": str(e)[:500]
            }
    
    def process_all_files(self):
        """批量处理所有文件（50并发）"""
        logger.info("=" * 80)
        logger.info("BATCH PROCESSING - 50 CONCURRENT WORKERS")
        logger.info("=" * 80)
        
        compliant_dir = Path("compliant")
        txt_files = sorted(list(compliant_dir.glob("*.txt")))
        
        logger.info(f"Found {len(txt_files)} txt files")
        logger.info(f"Concurrent workers: {MAX_CONCURRENT_FILES}")
        
        self.stats["total_files"] = len(txt_files)
        
        results = []
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_FILES) as executor:
            futures = {executor.submit(self.process_single_file, f): f for f in txt_files}
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    self.stats["completed"] += 1
                    self.stats["total_questions"] += result["total_questions"]
                    self.stats["passed_questions"] += result["passed"]
                    self.stats["failed_questions"] += result["failed"]
                else:
                    self.stats["failed"] += 1
                
                progress = len(results) / len(txt_files) * 100
                logger.info(f"Progress: {len(results)}/{len(txt_files)} ({progress:.1f}%)")
        
        self.generate_summary_report(results)
        
        logger.info("=" * 80)
        logger.info("✅ Batch processing completed!")
        logger.info(f"   Files: {self.stats['completed']}/{self.stats['total_files']}")
        logger.info(f"   Questions: {self.stats['passed_questions']}/{self.stats['total_questions']} passed")
        logger.info(f"   Total retries: {self.stats['total_retries']}")
        logger.info("=" * 80)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成总结报告"""
        report_file = self.output_dir / "BATCH_SUMMARY.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# DeepSeek English Q Generation - Summary Report

**Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model**: {DEEPSEEK_MODEL}  
**API Base**: {DEEPSEEK_API_BASE}  
**Processing Mode**: CORRECTED English Prompts + Intelligent Retry (Max 3)  
**Concurrent Workers**: {MAX_CONCURRENT_FILES}

---

## 📊 OVERALL STATISTICS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Files Completed** | {self.stats['completed']}/{self.stats['total_files']} | {self.stats['completed']/max(1,self.stats['total_files'])*100:.1f}% |
| **Total Questions** | {self.stats['total_questions']} | - |
| **Questions Passed** | {self.stats['passed_questions']} | {self.stats['passed_questions']/max(1,self.stats['total_questions'])*100:.1f}% |
| **Questions Failed** | {self.stats['failed_questions']} | {self.stats['failed_questions']/max(1,self.stats['total_questions'])*100:.1f}% |
| **Total Retries** | {self.stats['total_retries']} | - |

---

## 📋 DETAILED RESULTS

| File | Status | Total Q | Passed | Failed |
|------|--------|---------|--------|--------|
""")
            
            for result in sorted(results, key=lambda x: x["file"]):
                status_icon = "✅" if result["status"] == "success" else "❌"
                if result["status"] == "success":
                    f.write(f"| {result['file']} | {status_icon} | {result['total_questions']} | {result['passed']} | {result['failed']} |\n")
                else:
                    error_msg = result.get('error', 'Unknown')[:50]
                    f.write(f"| {result['file']} | {status_icon} | - | - | Error: {error_msg} |\n")
        
        logger.info(f"Summary report saved to: {report_file}")


def main():
    """主函数"""
    setup_logging()
    load_env_variables()
    
    print("=" * 80)
    print("DeepSeek CORRECTED English Q Generator")
    print("=" * 80)
    print(f"Model: {DEEPSEEK_MODEL}")
    print(f"API: {DEEPSEEK_API_BASE}")
    print(f"Concurrent workers: {MAX_CONCURRENT_FILES}")
    print(f"Max retries: {MAX_RETRIES_PER_QUESTION}")
    print("=" * 80)
    print("\n⚠️  CORRECTED VERSION - Using proper English prompts!")
    print("    Output: question_english/\n")
    
    generator = DeepSeekEnglishQGenerator("question_english")
    generator.process_all_files()
    
    print("\n✅ ALL DONE!")
    print(f"Check: question_english/BATCH_SUMMARY.md")


if __name__ == "__main__":
    main()
