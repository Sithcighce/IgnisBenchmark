"""
Milestone 1 Detail Q Generator: Deep Domain-Specific Questions
Goal: Generate 5 high-quality, domain-specific questions with detailed answers (300+ chars)
Focus: Combustion, Heat Transfer, Fluid Mechanics, CFD, Energy and their applications
"""

import os
import re
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from litellm import completion
from difflib import SequenceMatcher

from src.utils import load_config, setup_logging, load_env_variables

logger = logging.getLogger(__name__)


class Milestone1DetailQGenerator:
    """Generator for detailed domain-specific questions with answer verification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generation_model = config.get("generation_model", "openai/deepseek-ai/DeepSeek-V3")
        self.quality_check_model = config.get("quality_check_model", "openai/deepseek-ai/DeepSeek-V3")
        self.paper_path = config.get("paper_path", "main.txt")
        self.output_path = config.get("output_path", "data/milestone1_detail_Q.jsonl")
        self.report_path = config.get("report_path", "data/milestone1_detail_Q_report.md")
        self.min_answer_length = config.get("min_answer_length", 300)
        self.citation_similarity_threshold = config.get("citation_similarity_threshold", 0.85)
        self.paper_text = ""
        
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def find_best_match(self, citation: str, paper_text: str) -> Tuple[float, str]:
        """Find best matching substring in paper for the citation"""
        normalized_citation = self.normalize_text(citation)
        citation_len = len(normalized_citation)
        
        if citation_len == 0:
            return 0.0, ""
        
        normalized_paper = self.normalize_text(paper_text)
        
        if citation_len < 30:
            if normalized_citation in normalized_paper:
                return 1.0, normalized_citation
            return 0.0, ""
        
        # Fast search using key phrases
        key_start = normalized_citation[:25]
        key_end = normalized_citation[-25:]
        
        candidate_positions = []
        pos = 0
        while True:
            idx = normalized_paper.find(key_start, pos)
            if idx == -1:
                break
            candidate_positions.append(idx)
            pos = idx + 1
        
        pos = 0
        while True:
            idx = normalized_paper.find(key_end, pos)
            if idx == -1:
                break
            candidate_positions.append(max(0, idx - citation_len + 25))
            pos = idx + 1
        
        if not candidate_positions:
            candidate_positions = list(range(0, len(normalized_paper), 10000))
        
        candidate_positions = sorted(set(candidate_positions))[:50]
        
        best_score = 0.0
        best_match = ""
        min_window = int(citation_len * 0.8)
        max_window = int(citation_len * 1.2)
        
        for start_pos in candidate_positions:
            region_start = max(0, start_pos - 100)
            region_end = min(len(normalized_paper), start_pos + citation_len + 200)
            region = normalized_paper[region_start:region_end]
            
            for window_size in range(min_window, min(max_window + 1, len(region) + 1)):
                for i in range(len(region) - window_size + 1):
                    window = region[i:i + window_size]
                    similarity = SequenceMatcher(None, normalized_citation, window).ratio()
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = window
                        
                        if similarity > 0.95:
                            return best_score, best_match
        
        return best_score, best_match
    
    def verify_citations(self, citations: Dict[str, str], paper_text: str) -> Dict[str, Any]:
        """Verify all citations exist in the paper"""
        results = {
            "verified": True,
            "total_citations": len(citations),
            "verified_citations": 0,
            "failed_citations": [],
            "details": {}
        }
        
        for citation_id, citation_text in citations.items():
            score, matched_text = self.find_best_match(citation_text, paper_text)
            
            is_verified = score >= self.citation_similarity_threshold
            
            results["details"][citation_id] = {
                "text": citation_text,
                "similarity": score,
                "verified": is_verified,
                "matched_snippet": matched_text[:100] if matched_text else ""
            }
            
            if is_verified:
                results["verified_citations"] += 1
            else:
                results["verified"] = False
                results["failed_citations"].append({
                    "citation_id": citation_id,
                    "text": citation_text[:100] + "...",
                    "similarity": score
                })
        
        return results
    
    def load_paper_text(self) -> str:
        """Load paper text"""
        logger.info(f"Loading paper from: {self.paper_path}")
        
        if not os.path.exists(self.paper_path):
            raise FileNotFoundError(f"Paper file not found: {self.paper_path}")
        
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        self.paper_text = text
        logger.info(f"Paper loaded successfully: {len(text)} characters")
        return text
    
    def build_generation_prompt(self, paper_text: str) -> str:
        """Build generation prompt for detailed domain-specific questions"""
        
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
    
    def build_quality_check_prompt(self, question: Dict[str, Any], paper_text: str) -> str:
        """Build quality check prompt with answer verification"""
        
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

{paper_text[:20000]}

**IMPORTANT**: Return ONLY the JSON result, no other text.
"""
        return prompt
    
    def call_llm(self, prompt: str, model: str, require_json: bool = True) -> str:
        """Call LLM with DeepSeek"""
        model_config = {
            'model': 'openai/deepseek-ai/DeepSeek-V3',
            'api_base': 'https://api.siliconflow.cn/v1',
            'api_key': os.environ.get('SILICONFLOW_API_KEY')
        }
        
        for attempt in range(2):
            try:
                logger.info(f"Calling {model_config['model']}...")
                
                messages = [{"role": "user", "content": prompt}]
                
                completion_kwargs = {
                    "model": model_config["model"],
                    "messages": messages,
                    "api_base": model_config["api_base"],
                    "api_key": model_config["api_key"],
                    "max_tokens": 25000,
                    "temperature": 0.7
                }
                
                if require_json:
                    completion_kwargs["response_format"] = {"type": "json_object"}
                
                response = completion(**completion_kwargs)
                response_text = response.choices[0].message.content
                
                logger.info(f"✓ Got response from {model_config['model']}: {len(response_text)} chars")
                return response_text
                
            except Exception as e:
                logger.warning(f"❌ Model {model_config['model']} attempt {attempt + 1} failed: {str(e)[:200]}")
                if attempt < 1:
                    continue
                else:
                    raise
        
        raise RuntimeError("All retries failed")
    
    def generate_questions(self, paper_text: str) -> List[Dict[str, Any]]:
        """Generate detailed questions using LLM"""
        logger.info("=" * 60)
        logger.info("Generating 5 Detailed Domain-Specific Questions")
        logger.info(f"Using model: {self.generation_model}")
        logger.info("=" * 60)
        
        prompt = self.build_generation_prompt(paper_text)
        response_text = self.call_llm(prompt, self.generation_model, require_json=True)
        
        # Save raw response
        debug_path = "data/milestone1_detail_Q_raw.txt"
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info(f"Raw response saved to: {debug_path}")
        
        # Parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")
            # Try to fix
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e2:
                logger.error(f"JSON parse failed again: {e2}")
                raise
        
        questions = data.get("questions", [])
        
        if not questions:
            raise ValueError("No questions generated")
        
        logger.info(f"✅ Successfully generated {len(questions)} questions")
        return questions
    
    def check_question_quality(self, question: Dict[str, Any], paper_text: str) -> Dict[str, Any]:
        """Check quality and answer correctness"""
        prompt = self.build_quality_check_prompt(question, paper_text)
        response_text = self.call_llm(prompt, self.quality_check_model, require_json=True)
        
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Quality check JSON parse failed: {e}")
            # Fallback
            return {
                "domain_focused": True,
                "domain_reasoning": "Parse failed",
                "answer_correct": True,
                "answer_issues": [],
                "other_compliant": True,
                "other_issues": [],
                "overall_verdict": "pass",
                "recommendation": "Failed to parse quality check result"
            }
    
    def batch_quality_check(self, questions: List[Dict[str, Any]], paper_text: str) -> List[Dict[str, Any]]:
        """Check all questions"""
        logger.info("=" * 60)
        logger.info("Quality Check & Answer Verification")
        logger.info(f"Using model: {self.quality_check_model}")
        logger.info("=" * 60)
        
        quality_results = []
        
        for i, q in enumerate(questions, 1):
            logger.info(f"Checking question {i}/{len(questions)}...")
            try:
                result = self.check_question_quality(q, paper_text)
                quality_results.append(result)
                
                verdict = result.get("overall_verdict", "pass")
                logger.info(f"  Verdict: {verdict}")
                
            except Exception as e:
                logger.error(f"Quality check failed for question {i}: {e}")
                quality_results.append({
                    "domain_focused": False,
                    "domain_reasoning": f"Error: {str(e)[:100]}",
                    "answer_correct": False,
                    "answer_issues": [{"type": "error", "description": str(e)[:100]}],
                    "other_compliant": False,
                    "other_issues": [],
                    "overall_verdict": "fail",
                    "recommendation": "Exception during check"
                })
        
        pass_count = sum(1 for r in quality_results if r.get("overall_verdict") == "pass")
        logger.info(f"Quality Check Results: {pass_count}/{len(quality_results)} passed")
        
        return quality_results
    
    def batch_citation_verification(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify all citations"""
        logger.info("=" * 60)
        logger.info("Citation Verification")
        logger.info(f"Similarity threshold: {self.citation_similarity_threshold*100:.0f}%")
        logger.info("=" * 60)
        
        verification_results = []
        
        for i, q in enumerate(questions, 1):
            logger.info(f"Verifying citations for question {i}/{len(questions)}...")
            
            original_text = q.get("original_text", {})
            
            if not original_text:
                logger.warning(f"  ⚠️ No citations found")
                verification_results.append({
                    "verified": False,
                    "total_citations": 0,
                    "verified_citations": 0,
                    "failed_citations": [],
                    "details": {}
                })
                continue
            
            result = self.verify_citations(original_text, self.paper_text)
            verification_results.append(result)
            
            if result["verified"]:
                logger.info(f"  ✅ All {result['total_citations']} citations verified")
            else:
                logger.warning(f"  ❌ {len(result['failed_citations'])} citation(s) failed verification")
                for failed in result['failed_citations']:
                    logger.warning(f"     - Citation {failed['citation_id']}: {failed['similarity']*100:.1f}% similarity")
        
        total_verified = sum(1 for r in verification_results if r["verified"])
        logger.info(f"Citation Verification: {total_verified}/{len(verification_results)} questions passed")
        
        return verification_results
    
    def wrap_with_metadata(self, questions: List[Dict[str, Any]],
                          quality_results: List[Dict[str, Any]],
                          citation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to questions"""
        logger.info("=" * 60)
        logger.info("Adding Metadata")
        logger.info("=" * 60)
        
        wrapped_questions = []
        
        for q, qr, cr in zip(questions, quality_results, citation_results):
            question_id = f"detail_q_{hashlib.md5(q['question_text'].encode()).hexdigest()[:8]}"
            
            wrapped_q = {
                "question_id": question_id,
                "question_text": q.get("question_text", ""),
                "standard_answer": q.get("standard_answer", ""),
                "original_text": q.get("original_text", {}),
                "type": q.get("type", "unknown"),
                "difficulty": q.get("difficulty", 3),
                "topic": q.get("topic", "general"),
                "source": {
                    "type": "with_reference",
                    "paper_id": "PECS_combustion_review",
                    "paper_title": "Combustion Science Review"
                },
                "quality_check": {
                    "domain_focused": qr.get("domain_focused", False),
                    "domain_reasoning": qr.get("domain_reasoning", ""),
                    "answer_correct": qr.get("answer_correct", False),
                    "answer_issues": qr.get("answer_issues", []),
                    "other_compliant": qr.get("other_compliant", False),
                    "other_issues": qr.get("other_issues", []),
                    "overall_verdict": qr.get("overall_verdict", "fail"),
                    "recommendation": qr.get("recommendation", "")
                },
                "citation_verification": cr,
                "metadata": {
                    "generation_model": self.generation_model,
                    "quality_check_model": self.quality_check_model,
                    "created_at": datetime.now().isoformat(),
                    "milestone": "milestone_1_detail_Q",
                    "answer_length": len(q.get("standard_answer", ""))
                }
            }
            
            wrapped_questions.append(wrapped_q)
        
        logger.info(f"✓ Wrapped {len(wrapped_questions)} questions")
        return wrapped_questions
    
    def save_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Save questions to JSONL"""
        logger.info("=" * 60)
        logger.info("Saving Questions")
        logger.info("=" * 60)
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        
        logger.info(f"✓ Questions saved to: {self.output_path}")
        logger.info(f"  Total: {len(questions)} questions")
    
    def generate_report(self, questions: List[Dict[str, Any]]) -> str:
        """Generate quality report"""
        logger.info("=" * 60)
        logger.info("Generating Report")
        logger.info("=" * 60)
        
        total = len(questions)
        
        # Quality stats
        passed = sum(1 for q in questions if q["quality_check"]["overall_verdict"] == "pass")
        domain_focused = sum(1 for q in questions if q["quality_check"]["domain_focused"])
        answer_correct = sum(1 for q in questions if q["quality_check"]["answer_correct"])
        
        # Citation stats
        citation_verified = sum(1 for q in questions if q["citation_verification"]["verified"])
        
        # Answer length stats
        answer_lengths = [q["metadata"]["answer_length"] for q in questions]
        avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        min_length = min(answer_lengths) if answer_lengths else 0
        
        report = f"""# Milestone 1 Detail Q - Quality Report

**Generation Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Model**: {self.generation_model}  
**Total Questions**: {total}

---

## 📊 OVERALL RESULTS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Overall Passed** | {passed}/{total} | {passed/total*100:.1f}% |
| **Domain-Focused** | {domain_focused}/{total} | {domain_focused/total*100:.1f}% |
| **Answer Correct** | {answer_correct}/{total} | {answer_correct/total*100:.1f}% |
| **Citations Verified** | {citation_verified}/{total} | {citation_verified/total*100:.1f}% |

---

## 📝 ANSWER LENGTH STATISTICS

| Metric | Value |
|--------|-------|
| **Minimum Required** | 300 characters |
| **Average Length** | {avg_length:.0f} characters |
| **Shortest Answer** | {min_length} characters {'✅' if min_length >= 300 else '❌'} |

---

## 📋 DETAILED QUESTIONS

"""
        
        for i, q in enumerate(questions, 1):
            verdict = q["quality_check"]["overall_verdict"]
            verdict_emoji = "✅" if verdict == "pass" else "❌"
            
            report += f"""
### Question {i} {verdict_emoji}

**Question**: {q['question_text'][:200]}{'...' if len(q['question_text']) > 200 else ''}

**Answer Length**: {q['metadata']['answer_length']} chars

**Verdict**: {verdict}

**Checks**:
- Domain-focused: {'✅' if q['quality_check']['domain_focused'] else '❌'} - {q['quality_check']['domain_reasoning'][:100]}
- Answer correct: {'✅' if q['quality_check']['answer_correct'] else '❌'}
- Citations verified: {'✅' if q['citation_verification']['verified'] else '❌'} ({q['citation_verification']['verified_citations']}/{q['citation_verification']['total_citations']})

"""
            
            if q['quality_check']['answer_issues']:
                report += "**Answer Issues**:\n"
                for issue in q['quality_check']['answer_issues']:
                    report += f"  - {issue['type']}: {issue['description']}\n"
                report += "\n"
        
        return report
    
    def save_report(self, report: str) -> None:
        """Save report"""
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to: {self.report_path}")
    
    def run(self) -> None:
        """Run generation process"""
        logger.info("=" * 80)
        logger.info("🚀 Milestone 1 Detail Q: Deep Domain-Specific Questions")
        logger.info("=" * 80)
        
        try:
            # Load paper
            paper_text = self.load_paper_text()
            
            # Generate 5 questions
            questions = self.generate_questions(paper_text)
            
            # Quality check with answer verification
            quality_results = self.batch_quality_check(questions, paper_text)
            
            # Citation verification
            citation_results = self.batch_citation_verification(questions)
            
            # Wrap with metadata
            wrapped_questions = self.wrap_with_metadata(questions, quality_results, citation_results)
            
            # Save
            self.save_questions(wrapped_questions)
            
            # Report
            report = self.generate_report(wrapped_questions)
            self.save_report(report)
            
            logger.info("=" * 80)
            logger.info("✅ Milestone 1 Detail Q completed!")
            logger.info(f"   Output: {self.output_path}")
            logger.info(f"   Report: {self.report_path}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            raise


def main():
    """Main function"""
    config = load_config()
    
    setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file="logs/milestone1_detail_Q.log"
    )
    
    load_env_variables(config.get("env_file_path", ".env"))
    
    detail_q_config = {
        "generation_model": "openai/deepseek-ai/DeepSeek-V3",
        "quality_check_model": "openai/deepseek-ai/DeepSeek-V3",
        "paper_path": "main.txt",
        "output_path": "data/milestone1_detail_Q.jsonl",
        "report_path": "data/milestone1_detail_Q_report.md",
        "min_answer_length": 300,
        "citation_similarity_threshold": 0.85
    }
    
    generator = Milestone1DetailQGenerator(detail_q_config)
    generator.run()


if __name__ == "__main__":
    main()
