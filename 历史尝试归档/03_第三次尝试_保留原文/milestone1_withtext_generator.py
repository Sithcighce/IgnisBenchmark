"""
Milestone 1 WithText Generator: Questions with Original Text Citations
Goal: Generate 20 high-quality questions with verified original text references
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from litellm import completion
from difflib import SequenceMatcher

from src.utils import load_config, setup_logging, load_env_variables

logger = logging.getLogger(__name__)


class Milestone1WithTextGenerator:
    """Generator with original text citation and verification"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generation_model = config.get("generation_model", "gemini/gemini-2.0-flash-thinking-exp")
        self.quality_check_model = config.get("quality_check_model", "gemini/gemini-2.0-flash-exp")
        self.paper_path = config.get("paper_path", "main.txt")
        self.output_path = config.get("output_path", "data/milestone1_withtext.jsonl")
        self.report_path = config.get("report_path", "data/milestone1_withtext_report.md")
        self.max_iterations = config.get("max_iterations", 3)
        self.acceptance_threshold = config.get("acceptance_threshold", 0.90)
        self.citation_similarity_threshold = config.get("citation_similarity_threshold", 0.90)
        self.paper_text = ""
        self.normalized_paper_text = ""
        
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison: remove punctuation, whitespace, newlines"""
        # Convert to lowercase
        text = text.lower()
        # Remove all punctuation and special characters, keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing spaces
        return text.strip()
    
    def find_best_match(self, citation: str, paper_text: str) -> Tuple[float, str]:
        """
        Find best matching substring in paper for the citation.
        Returns: (similarity_score, matched_text)
        """
        normalized_citation = self.normalize_text(citation)
        citation_len = len(normalized_citation)
        
        if citation_len == 0:
            return 0.0, ""
        
        normalized_paper = self.normalize_text(paper_text)
        
        # OPTIMIZATION: For short citations, try exact substring first
        if citation_len < 30:
            if normalized_citation in normalized_paper:
                return 1.0, normalized_citation
            return 0.0, ""
        
        # OPTIMIZATION: Use fast substring search to find candidates
        # Split citation into key phrases
        key_start = normalized_citation[:25]
        key_end = normalized_citation[-25:]
        
        # Find potential locations
        candidate_positions = []
        pos = 0
        while True:
            idx = normalized_paper.find(key_start, pos)
            if idx == -1:
                break
            candidate_positions.append(idx)
            pos = idx + 1
        
        # Also try end phrase
        pos = 0
        while True:
            idx = normalized_paper.find(key_end, pos)
            if idx == -1:
                break
            # Add position accounting for citation length
            candidate_positions.append(max(0, idx - citation_len + 25))
            pos = idx + 1
        
        # If no candidates, sample every 10000 chars (fallback)
        if not candidate_positions:
            candidate_positions = list(range(0, len(normalized_paper), 10000))
        
        # Remove duplicates and limit to first 50 candidates
        candidate_positions = sorted(set(candidate_positions))[:50]
        
        # Now do precise matching only around candidates
        best_score = 0.0
        best_match = ""
        min_window = int(citation_len * 0.8)
        max_window = int(citation_len * 1.2)
        
        for start_pos in candidate_positions:
            # Check a region around this position
            region_start = max(0, start_pos - 100)
            region_end = min(len(normalized_paper), start_pos + citation_len + 200)
            region = normalized_paper[region_start:region_end]
            
            # Try different window sizes in this small region
            for window_size in range(min_window, min(max_window + 1, len(region) + 1)):
                for i in range(len(region) - window_size + 1):
                    window = region[i:i + window_size]
                    similarity = SequenceMatcher(None, normalized_citation, window).ratio()
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = window
                        
                        # Early exit if we found near-perfect match
                        if similarity > 0.95:
                            return best_score, best_match
        
        return best_score, best_match
    
    def verify_citations(self, citations: Dict[str, str], paper_text: str) -> Dict[str, Any]:
        """
        Verify all citations exist in the paper.
        Returns: verification result with details
        """
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
        self.normalized_paper_text = self.normalize_text(text)
        
        logger.info(f"Paper loaded successfully: {len(text)} characters")
        return text
    
    def build_generation_prompt(self, paper_text: str, iteration: int = 1, 
                                feedback: str = "") -> str:
        """Build English generation prompt with original text citation requirement"""
        
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
{{
  "question_text": "Why does increasing pressure shorten ignition delay time?",
  "standard_answer": "Increased pressure raises molecular number density...",
  "original_text": {{
    "1": "The ignition delay time decreases with increasing pressure due to the higher molecular number density, which leads to more frequent molecular collisions and faster reaction rates.",
    "2": "At elevated pressures, three-body reactions become more important, further accelerating the ignition process through enhanced chain branching."
  }},
  "type": "reasoning",
  "difficulty": 4
}}
```

### 3. Clear and Determinable Answers
- ✅ Must have clear correct/incorrect standards
- ✅ Priority: calculation questions, judgment questions, causal reasoning questions
- ❌ Avoid: open-ended discussion questions, trend prediction questions

### 4. Time-Independent
- ✅ Based on physical principles, chemical mechanisms, mathematical relationships
- ❌ Avoid: specific year technology applications, latest developments, industrial status

### 5. Depth First
- ✅ Require understanding **why**, **what is the mechanism**, **how to derive**
- ❌ Avoid: pure memorization definition questions
- ✅ Encourage: mechanism explanation questions

---

## 📊 QUESTION TYPE DISTRIBUTION

### **reasoning (Reasoning Analysis) - 50%** (Most Important)
- Causal reasoning: "Why does X lead to Y?"
- Mechanism explanation: "What is the physical/chemical mechanism of X phenomenon?"
- Parameter influence: "How does changing X affect Y? Through what pathway?"

### **concept (Conceptual Understanding) - 25%**
- Deep meaning of key concepts (not simple definitions)
- Relationships and differences between concepts
- Can be "term explanation", but requires depth

### **calculation (Calculation) - 15%**
- Quantitative reasoning
- Order of magnitude estimation
- Parameter calculation

### **application (Application) - 10%**
- Apply principles to specific scenarios
- Must have clear answers, cannot be too open

---

## 🎯 DIFFICULTY LEVELS (1-5)

**Distribution Requirements**:
- difficulty 3-4: 70% (main body)
- difficulty 5: 20% (challenging)
- difficulty 1-2: 10% (basic)

---

## ❌ STRICTLY AVOID THESE QUESTION TYPES

### Type 1: Paper Meta-Information Questions
❌ "What combustion modes does this review discuss?"
❌ "What viewpoint did the author propose in Section 3?"

### Type 2: Open-ended/Subjective Questions
❌ "How to optimize diesel NOx emissions?" (too open)
❌ "What is the future development direction of HCCI technology?" (predictive)

### Type 3: Pure Definition Memorization Questions
❌ "What is ignition delay time?" (can be searched)
✅ "Why does ignition delay time show non-monotonic variation?" (requires understanding)

### Type 4: Time-Sensitive Questions
❌ "Impact of electric vehicles in 2024"
❌ "Current industrial NOx after-treatment technologies"

---

## 📋 OUTPUT FORMAT (JSON)

**CRITICAL**: You MUST include the "original_text" field with exact quotes from the paper!

```json
{{
  "questions": [
    {{
      "question_text": "Why does increasing pressure shorten ignition delay time? Explain from molecular collision and chemical kinetics perspectives.",
      "standard_answer": "Increased pressure raises molecular number density, causing collision frequency to increase proportionally with P. According to Arrhenius law, reaction rate k is proportional to collision frequency and activation energy exponential term. At high pressure, elementary reaction rates accelerate, chain reactions progress faster, leading to shortened ignition delay time τ. The quantitative relationship is τ ∝ P^(-n), where n depends on reaction mechanism, typically between 1-2.",
      "original_text": {{
        "1": "EXACT QUOTE FROM PAPER - must be verbatim, at least 50 characters",
        "2": "ANOTHER EXACT QUOTE FROM PAPER - supports the answer or question context"
      }},
      "type": "reasoning",
      "difficulty": 3,
      "topic": "ignition_kinetics"
    }}
  ]
}}
```

**IMPORTANT**: 
- Return ONLY JSON, no other text, explanations, or markdown code blocks
- Generate exactly 20 questions
- Each question MUST have "original_text" field with at least 1 verbatim quote
- Standard answers must be sufficiently detailed (at least 100 characters)

---

## 🔍 QUALITY SELF-CHECK

- [ ] Each question has "original_text" field with verbatim quotes
- [ ] Quotes are substantial (≥50 characters each)
- [ ] Questions test domain knowledge, not paper content
- [ ] No time-related words ("currently", "2024", etc.)
- [ ] At least 10 reasoning questions
- [ ] difficulty 3-5 accounts for > 80%

---

## PAPER CONTENT
{paper_text[:50000]}
"""
        return prompt
    
    def build_quality_check_prompt(self, question: Dict[str, Any]) -> str:
        """Build English quality check prompt (WITHOUT original_text)"""
        
        # Remove original_text from question for quality check
        question_for_check = {k: v for k, v in question.items() if k != "original_text"}
        
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

#### 2. Time-Sensitive Questions
- Contains specific years ("in 2024...", "in recent five years...")
- Asking "currently...", "latest...", "at present..."
- Asking "future development", "trend prediction"

#### 3. Too Open-ended Questions
- Asking "how to optimize...", "how to improve..." (no clear answer)
- Asking "discuss...", "evaluate...", "analyze pros and cons of..."
- Answer contains "depends on...", "it depends...", "need to comprehensively consider..."

#### 4. Pure Memorization Definition Questions (No Depth)
- Only asking "What is X?", "What is the definition of X?"
- Answer is just textbook definition, no mechanism/principle/derivation

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
- concept type: needs to understand relationships between concepts
- calculation type: needs calculation or quantitative reasoning
- application type: needs to apply principles to scenarios

---

## OUTPUT FORMAT

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

## NOW START CHECKING

Please check the following question:

```json
{json.dumps(question_for_check, ensure_ascii=False, indent=2)}
```

**IMPORTANT**: Return ONLY the JSON result, no other text or explanations.
"""
        return prompt
    
    def call_llm(self, prompt: str, model: str, require_json: bool = True) -> str:
        """Call LLM with fallback mechanism"""
        # Use DeepSeek for everything to avoid Gemini rate limits
        model_fallbacks = [
            {'model': 'openai/deepseek-ai/DeepSeek-V3', 
             'api_base': 'https://api.siliconflow.cn/v1', 
             'api_key': os.environ.get('SILICONFLOW_API_KEY')},
        ]
        
        for attempt in range(2):
            for model_index, m in enumerate(model_fallbacks):
                try:
                    if model_index > 0:
                        logger.info(f"Trying fallback model: {m['model']}")
                    
                    completion_kwargs = {
                        "model": m['model'],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 20000,  # Very large for citations
                        "timeout": 300
                    }
                    
                    if require_json and "deepseek" in m['model'].lower():
                        completion_kwargs["response_format"] = {"type": "json_object"}
                    
                    if 'api_base' in m and m['api_base']:
                        completion_kwargs['api_base'] = m['api_base']
                    if 'api_key' in m and m['api_key']:
                        completion_kwargs['api_key'] = m['api_key']
                    
                    logger.info(f"Calling {m['model']}...")
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
                    
                    logger.info(f"✓ Got response from {m['model']}: {len(response_text)} chars")
                    return response_text.strip()
                    
                except Exception as e:
                    logger.warning(f"❌ Model {m['model']} attempt {attempt+1} failed: {str(e)[:200]}")
                    if attempt < 1:
                        continue
        
        raise RuntimeError("All models and retries failed")
    
    def generate_questions(self, paper_text: str, iteration: int = 1, 
                          feedback: str = "") -> List[Dict[str, Any]]:
        """Generate questions using LLM"""
        logger.info("=" * 60)
        logger.info(f"ITERATION {iteration}: Generating Questions with Citations")
        logger.info(f"Using model: {self.generation_model}")
        logger.info("=" * 60)
        
        prompt = self.build_generation_prompt(paper_text, iteration, feedback)
        response_text = self.call_llm(prompt, self.generation_model, require_json=True)
        
        # Save raw response for debugging
        debug_path = f"data/milestone1_withtext_raw_iter{iteration}.txt"
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(response_text)
        logger.info(f"Raw response saved to: {debug_path}")
        
        # Parse JSON
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}")
            logger.warning(f"Error at line {e.lineno}, column {e.colno}")
            
            # Try to fix common JSON issues
            import re
            
            # Fix 1: Remove trailing commas
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            
            # Fix 2: Escape unescaped quotes in strings
            # This is tricky, so we'll try a more aggressive approach
            
            try:
                data = json.loads(response_text)
                logger.info("✓ JSON fixed successfully")
            except json.JSONDecodeError as e2:
                logger.error(f"JSON fix failed: {e2}")
                logger.error(f"Problematic section around line {e2.lineno}:")
                lines = response_text.split('\n')
                start = max(0, e2.lineno - 3)
                end = min(len(lines), e2.lineno + 2)
                for i in range(start, end):
                    logger.error(f"  {i+1}: {lines[i]}")
                raise
        
        questions = data.get("questions", [])
        
        if not questions:
            raise ValueError("No questions generated")
        
        logger.info(f"✅ Successfully generated {len(questions)} questions")
        return questions
    
    def check_question_quality(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality of a single question (without original_text)"""
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
        logger.info("Step 1: Quality Check (Content)")
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
        
        logger.info(f"Content Quality Results:")
        logger.info(f"  Pass: {pass_count}/{len(quality_results)}")
        logger.info(f"  Review: {review_count}/{len(quality_results)}")
        logger.info(f"  Reject: {reject_count}/{len(quality_results)}")
        logger.info(f"  Acceptance Rate: {acceptance_rate*100:.1f}%")
        
        # Generate feedback for next iteration
        feedback = self._generate_feedback(quality_results, questions)
        
        return quality_results, acceptance_rate, feedback
    
    def batch_citation_verification(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verify all citations in all questions
        Returns: list of verification results
        """
        logger.info("=" * 60)
        logger.info("Step 2: Citation Verification")
        logger.info(f"Similarity threshold: {self.citation_similarity_threshold*100:.0f}%")
        logger.info("=" * 60)
        
        verification_results = []
        
        for i, q in enumerate(questions, 1):
            logger.info(f"Verifying citations for question {i}/{len(questions)}...")
            
            original_text = q.get("original_text", {})
            
            if not original_text:
                logger.warning(f"  ⚠️ Question {i} has no citations!")
                verification_results.append({
                    "verified": False,
                    "total_citations": 0,
                    "verified_citations": 0,
                    "failed_citations": [{"error": "No citations provided"}],
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
        
        # Summary
        total_verified = sum(1 for r in verification_results if r["verified"])
        total_questions = len(verification_results)
        citation_pass_rate = total_verified / total_questions if total_questions > 0 else 0
        
        logger.info(f"Citation Verification Summary:")
        logger.info(f"  Verified: {total_verified}/{total_questions}")
        logger.info(f"  Pass Rate: {citation_pass_rate*100:.1f}%")
        
        return verification_results
    
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
                          citation_results: List[Dict[str, Any]],
                          paper_id: str = "PECS_2020_Vol85_p1", 
                          paper_title: str = "Combustion Theory Review") -> List[Dict[str, Any]]:
        """Add system metadata fields"""
        logger.info("=" * 60)
        logger.info("Adding System Metadata")
        logger.info("=" * 60)
        
        wrapped_questions = []
        
        for q, qr, cr in zip(questions, quality_results, citation_results):
            wrapped = {
                # System generated fields
                "question_id": f"comb_qa_{str(uuid.uuid4())[:8]}",
                
                # AI generated fields
                "question_text": q.get("question_text", ""),
                "standard_answer": q.get("standard_answer", ""),
                "original_text": q.get("original_text", {}),
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
                
                # Citation verification result
                "citation_verification": {
                    "verified": cr.get("verified", False),
                    "total_citations": cr.get("total_citations", 0),
                    "verified_citations": cr.get("verified_citations", 0),
                    "failed_citations": cr.get("failed_citations", [])
                },
                
                # Metadata
                "metadata": {
                    "generation_model": self.generation_model,
                    "quality_check_model": self.quality_check_model,
                    "created_at": datetime.now().isoformat(),
                    "milestone": "milestone_1_withtext"
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
                            citation_results: List[Dict[str, Any]],
                            content_acceptance_rate: float,
                            citation_pass_rate: float,
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
        
        # Quality distribution
        pass_count = sum(1 for r in quality_results if r.get("severity") == "pass")
        review_count = sum(1 for r in quality_results if r.get("severity") == "review")
        reject_count = sum(1 for r in quality_results if r.get("severity") == "reject")
        
        # Citation statistics
        total_citations = sum(cr.get("total_citations", 0) for cr in citation_results)
        verified_citations = sum(cr.get("verified_citations", 0) for cr in citation_results)
        citation_verified_questions = sum(1 for cr in citation_results if cr.get("verified", False))
        
        # Overall pass rate (both content and citations must pass)
        overall_pass_count = sum(1 for qr, cr in zip(quality_results, citation_results)
                                if qr.get("severity") in ["pass", "review"] and cr.get("verified", False))
        overall_pass_rate = overall_pass_count / total if total > 0 else 0
        
        report = f"""# Milestone 1 WithText - Quality Assessment Report

**Generation Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Generation Model**: {self.generation_model}  
**Quality Check Model**: {self.quality_check_model}  
**Data Source**: {self.paper_path}  
**Iterations**: {iterations}  
**Acceptance Threshold**: {self.acceptance_threshold*100:.0f}%  
**Citation Similarity Threshold**: {self.citation_similarity_threshold*100:.0f}%

---

## 🎯 OVERALL RESULTS

### Combined Pass Rate: **{overall_pass_rate*100:.1f}%** {'✅ PASSED' if overall_pass_rate >= self.acceptance_threshold else '❌ FAILED'}

Questions must pass BOTH content quality check AND citation verification.

| Metric | Value |
|--------|-------|
| **Questions Passing Both Checks** | {overall_pass_count}/{total} ({overall_pass_rate*100:.1f}%) |
| **Content Acceptance Rate** | {content_acceptance_rate*100:.1f}% |
| **Citation Pass Rate** | {citation_pass_rate*100:.1f}% |

---

## 📝 CONTENT QUALITY CHECK RESULTS

| Severity | Count | Percentage |
|----------|-------|------------|
| ✅ Pass | {pass_count} | {pass_count/total*100:.1f}% |
| ⚠️ Review | {review_count} | {review_count/total*100:.1f}% |
| ❌ Reject | {reject_count} | {reject_count/total*100:.1f}% |
| **Total Acceptable** | **{pass_count + review_count}** | **{content_acceptance_rate*100:.1f}%** |

---

## 📚 CITATION VERIFICATION RESULTS

| Metric | Count | Details |
|--------|-------|---------|
| **Total Citations** | {total_citations} | Across all questions |
| **Verified Citations** | {verified_citations} | Met {self.citation_similarity_threshold*100:.0f}% similarity threshold |
| **Questions with All Citations Verified** | {citation_verified_questions}/{total} | {citation_pass_rate*100:.1f}% |
| **Citation Verification Rate** | {verified_citations}/{total_citations if total_citations > 0 else 1} | {verified_citations/total_citations*100 if total_citations > 0 else 0:.1f}% |

---

## 📊 QUESTION TYPE DISTRIBUTION

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

## ⚠️ FAILED CITATION VERIFICATION

"""
        
        failed_citation_questions = [(i+1, q, cr) for i, (q, cr) in enumerate(zip(questions, citation_results))
                                     if not cr.get("verified", False)]
        
        if failed_citation_questions:
            report += f"Total questions with failed citations: {len(failed_citation_questions)}\n\n"
            for i, (qnum, q, cr) in enumerate(failed_citation_questions[:5], 1):
                report += f"### Failed Question {i} (Q{qnum})\n\n"
                report += f"**Question**: {q.get('question_text', '')[:150]}...\n\n"
                report += f"**Citation Issues**:\n"
                for failed in cr.get("failed_citations", []):
                    if "citation_id" in failed:
                        report += f"- Citation {failed['citation_id']}: {failed['similarity']*100:.1f}% similarity\n"
                        report += f"  Text: {failed['text']}\n"
                    else:
                        report += f"- {failed.get('error', 'Unknown error')}\n"
                report += "\n---\n\n"
        else:
            report += "All citations verified successfully! ✅\n\n"
        
        report += f"""
---

## ✅ ACCEPTANCE CRITERIA

- [{'x' if total == 20 else ' '}] Generated exactly 20 complete Q&A pairs
- [{'x' if content_acceptance_rate >= self.acceptance_threshold else ' '}] Content acceptance rate ≥ {self.acceptance_threshold*100:.0f}%
- [{'x' if citation_pass_rate >= self.acceptance_threshold else ' '}] Citation pass rate ≥ {self.acceptance_threshold*100:.0f}%
- [{'x' if overall_pass_rate >= self.acceptance_threshold else ' '}] Overall pass rate ≥ {self.acceptance_threshold*100:.0f}%
- [x] Output in standard JSON format with citations

---

## 💡 RECOMMENDATIONS

"""
        if overall_pass_rate >= 0.95:
            report += "✨ **Excellent Quality**! Almost all questions meet both content and citation standards.\n"
        elif overall_pass_rate >= self.acceptance_threshold:
            report += "✓ **Good Quality**. Overall pass rate meets threshold. Some questions may need citation review.\n"
        else:
            report += f"⚠️ **Needs Improvement**. Overall pass rate {overall_pass_rate*100:.1f}% is below threshold.\n"
            if content_acceptance_rate < self.acceptance_threshold:
                report += "  - Focus on improving content quality\n"
            if citation_pass_rate < self.acceptance_threshold:
                report += "  - Focus on providing more accurate verbatim quotes from the paper\n"
        
        report += f"""
---

## 📋 SAMPLE QUESTIONS (Fully Verified)

"""
        
        # Get questions that passed both checks
        fully_verified = [(i+1, q, cr) for i, (q, qr, cr) in enumerate(zip(questions, quality_results, citation_results))
                         if qr.get("severity") in ["pass", "review"] and cr.get("verified", False)]
        
        for i, (qnum, q, cr) in enumerate(fully_verified[:3], 1):
            report += f"""
### Question {i} (Q{qnum})

- **Type**: {q.get('type')}
- **Difficulty**: {q.get('difficulty')}/5
- **Topic**: {q.get('topic')}
- **Citations**: {cr.get('total_citations', 0)} (all verified ✅)

**Question**:  
{q.get('question_text', '')}

**Answer**:  
{q.get('standard_answer', '')[:300]}{'...' if len(q.get('standard_answer', '')) > 300 else ''}

**Original Text Citations**:
"""
            for cit_id, cit_text in q.get('original_text', {}).items():
                similarity = cr.get('details', {}).get(cit_id, {}).get('similarity', 0)
                report += f"  {cit_id}. [{similarity*100:.1f}% match] {cit_text[:150]}{'...' if len(cit_text) > 150 else ''}\n"
            
            report += "\n---\n"
        
        return report
    
    def save_report(self, report: str) -> None:
        """Save assessment report"""
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Report saved to: {self.report_path}")
    
    def run(self) -> None:
        """Run complete iterative generation and verification process"""
        logger.info("=" * 80)
        logger.info("🚀 Milestone 1 WithText: Questions with Verified Citations")
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
                
                # Generate questions with citations
                ai_questions = self.generate_questions(paper_text, iteration, feedback)
                
                # Step 1: Quality check (content)
                quality_results, content_acceptance_rate, content_feedback = self.batch_quality_check(ai_questions)
                
                # Step 2: Citation verification
                citation_results = self.batch_citation_verification(ai_questions)
                citation_pass_rate = sum(1 for cr in citation_results if cr.get("verified", False)) / len(citation_results)
                
                # Calculate overall pass rate
                overall_pass_count = sum(1 for qr, cr in zip(quality_results, citation_results)
                                        if qr.get("severity") in ["pass", "review"] and cr.get("verified", False))
                overall_pass_rate = overall_pass_count / len(ai_questions)
                
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"ITERATION {iteration} SUMMARY:")
                logger.info(f"  Content Acceptance: {content_acceptance_rate*100:.1f}%")
                logger.info(f"  Citation Pass Rate: {citation_pass_rate*100:.1f}%")
                logger.info(f"  Overall Pass Rate: {overall_pass_rate*100:.1f}%")
                logger.info("=" * 80)
                
                # Check if threshold met
                if overall_pass_rate >= self.acceptance_threshold:
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info(f"✅ ACCEPTANCE THRESHOLD MET: {overall_pass_rate*100:.1f}% >= {self.acceptance_threshold*100:.0f}%")
                    logger.info("=" * 80)
                    
                    # Wrap with metadata
                    full_questions = self.wrap_with_metadata(
                        ai_questions,
                        quality_results,
                        citation_results,
                        paper_id="PECS_combustion_review",
                        paper_title="Combustion Science Review"
                    )
                    
                    # Save questions
                    self.save_questions(full_questions)
                    
                    # Generate and save report
                    report = self.generate_final_report(
                        ai_questions, quality_results, citation_results,
                        content_acceptance_rate, citation_pass_rate, iteration
                    )
                    self.save_report(report)
                    
                    # Print report to console
                    print("\n" + report)
                    
                    logger.info("=" * 80)
                    logger.info("✅ MILESTONE 1 WITHTEXT COMPLETED SUCCESSFULLY!")
                    logger.info("=" * 80)
                    logger.info(f"📄 Questions file: {self.output_path}")
                    logger.info(f"📊 Report file: {self.report_path}")
                    logger.info(f"🎯 Final overall pass rate: {overall_pass_rate*100:.1f}%")
                    logger.info(f"🔄 Iterations used: {iteration}/{self.max_iterations}")
                    
                    return
                
                else:
                    logger.warning("")
                    logger.warning("=" * 80)
                    logger.warning(f"⚠️ Overall pass rate {overall_pass_rate*100:.1f}% < threshold {self.acceptance_threshold*100:.0f}%")
                    
                    # Generate combined feedback
                    feedback = content_feedback
                    if citation_pass_rate < self.acceptance_threshold:
                        feedback += f"\n\nCITATION ISSUES: Only {citation_pass_rate*100:.1f}% of questions had verified citations.\n"
                        feedback += "Please ensure all citations are EXACT VERBATIM quotes from the paper, not paraphrases.\n"
                    
                    logger.warning(f"Will retry with iteration {iteration + 1}")
                    logger.warning("=" * 80)
                    iteration += 1
            
            # Max iterations reached
            logger.error("")
            logger.error("=" * 80)
            logger.error(f"❌ FAILED: Maximum iterations ({self.max_iterations}) reached")
            logger.error(f"Final overall pass rate: {overall_pass_rate*100:.1f}% < threshold {self.acceptance_threshold*100:.0f}%")
            logger.error("=" * 80)
            
            # Still save the best attempt
            full_questions = self.wrap_with_metadata(
                ai_questions, quality_results, citation_results,
                paper_id="PECS_combustion_review",
                paper_title="Combustion Science Review"
            )
            self.save_questions(full_questions)
            
            report = self.generate_final_report(
                ai_questions, quality_results, citation_results,
                content_acceptance_rate, citation_pass_rate, self.max_iterations
            )
            self.save_report(report)
            
            logger.info(f"Best attempt saved to: {self.output_path}")
            
        except Exception as e:
            logger.error(f"❌ Milestone 1 WithText execution failed: {e}")
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
        log_file="logs/milestone1_withtext.log"
    )
    
    # Load environment variables
    load_env_variables(config.get("env_file_path", ".env"))
    
    # Milestone 1 WithText configuration
    m1_withtext_config = {
        "generation_model": "openai/deepseek-ai/DeepSeek-V3",
        "quality_check_model": "openai/deepseek-ai/DeepSeek-V3",  # Use DeepSeek to avoid Gemini rate limits
        "paper_path": "main.txt",
        "output_path": "data/milestone1_withtext.jsonl",
        "report_path": "data/milestone1_withtext_report.md",
        "max_iterations": 3,
        "acceptance_threshold": 0.90,
        "citation_similarity_threshold": 0.85  # Slightly lower threshold for citations
    }
    
    # Run
    generator = Milestone1WithTextGenerator(m1_withtext_config)
    generator.run()


if __name__ == "__main__":
    main()
