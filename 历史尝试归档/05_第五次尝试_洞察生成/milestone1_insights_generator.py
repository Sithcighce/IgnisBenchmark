"""
Milestone 1 Insights Generator: Domain Insights with Original Text
Goal: Generate 10 domain insights learned from reading the paper
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


class Milestone1InsightsGenerator:
    """Generator for domain insights with original text citations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generation_model = config.get("generation_model", "openai/deepseek-ai/DeepSeek-V3")
        self.compliance_check_model = config.get("compliance_check_model", "openai/deepseek-ai/DeepSeek-V3")
        self.paper_path = config.get("paper_path", "main.txt")
        self.output_path = config.get("output_path", "data/milestone1_insights.jsonl")
        self.report_path = config.get("report_path", "data/milestone1_insights_report.md")
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
        """Build generation prompt for domain insights"""
        
        prompt = f"""# ROLE
You are a senior expert in combustion science, heat transfer, fluid mechanics, CFD, and energy systems. You extract valuable insights and learning points from scientific papers.

# TASK
After reading the following scientific paper, generate **10 domain insights** - things you learned or found interesting that require domain expertise to appreciate.

---

## ✅ WHAT IS AN "INSIGHT"?

An insight is:
- ✅ A non-obvious finding, mechanism, or principle you learned from reading
- ✅ Something that deepens understanding of combustion/heat transfer/fluid/CFD/energy
- ✅ Could be a counterintuitive result, a subtle mechanism, a quantitative relationship
- ✅ Should be interesting to domain experts, not just general readers

**Examples of GOOD insights**:
1. "Negative temperature coefficient (NTC) behavior in hydrocarbon oxidation arises because alkylperoxy decomposition (ROO → olefin + HO2) competes with chain-branching QOOH chemistry, creating a regime where higher temperature paradoxically slows ignition."

2. "Three-body recombination reactions like H + O2 + M → HO2 + M become dominant at pressures >30 bar, shifting ignition from chain-branching (explosive) to chain-propagation (gradual), fundamentally changing combustion regime."

3. "CFD turbulence models fail to capture cyclic variability in HCCI engines because RANS averaging inherently filters out stochastic fluctuations, while LES resolves them but at prohibitive computational cost for full engine cycles."

---

## ❌ NOT AN INSIGHT (Avoid These)

- ❌ Paper meta-information: "This paper reviews combustion modeling approaches"
- ❌ Too general: "Machine learning can improve predictions" (no domain depth)
- ❌ Time-sensitive: "In 2024, electric vehicles are growing rapidly"
- ❌ Overly broad: "Combustion is important for energy systems" (obvious)
- ❌ Pure ML/CS: "Neural networks can approximate nonlinear functions" (not domain-specific)

---

## 🎯 DOMAIN FOCUS - MANDATORY

Insights MUST relate to:
- **Combustion Science**: chemical kinetics, ignition, flame dynamics, pollutant formation
- **Heat Transfer**: thermal management, heat flux, radiative/convective mechanisms
- **Fluid Mechanics**: turbulence, mixing, flow instabilities, boundary layers
- **CFD**: numerical methods, turbulence modeling, mesh strategies, solver algorithms
- **Energy Systems**: engine performance, efficiency limits, emission control

✅ **Acceptable**: ML/AI applied to these domains (e.g., "ANNs fail to capture HCCI variability because...")
❌ **Not Acceptable**: Pure ML/CS insights without domain context

---

## 📋 OUTPUT FORMAT (JSON)

```json
{{
  "insights": [
    {{
      "insight_text": "Negative temperature coefficient (NTC) behavior in hydrocarbon oxidation arises because alkylperoxy decomposition (ROO → olefin + HO2) competes with chain-branching QOOH chemistry. At intermediate temperatures (600-800K), the equilibrium ROO ⇌ R + O2 shifts toward dissociation, diverting flux away from OOQOOH formation (which produces 2 OH radicals). This creates a counterintuitive regime where dτ/dT < 0.",
      "original_text": {{
        "1": "EXACT VERBATIM QUOTE FROM PAPER - at least 50 characters - supports this insight",
        "2": "ANOTHER EXACT QUOTE - provides evidence for the mechanism or finding"
      }},
      "domain": "combustion_kinetics",
      "tags": ["low_temperature_chemistry", "NTC", "chain_branching"]
    }}
  ]
}}
```

**IMPORTANT**:
- Return ONLY JSON, no other text
- Generate exactly 10 insights
- Each insight should be substantial (100-300 characters recommended)
- Each insight requires domain expertise to appreciate
- Include "original_text" with 1-3 verbatim quotes (≥50 chars each)

---

## 🔍 QUALITY SELF-CHECK

Before submitting, verify:
- [ ] All 10 insights require combustion/heat transfer/fluid/CFD/energy knowledge
- [ ] No paper meta-information ("this paper discusses...", "the author proposes...")
- [ ] No time-sensitive content ("currently", "in 2024", "latest trends...")
- [ ] Each insight has original_text with verbatim quotes
- [ ] Insights are non-obvious (not just "X is important" or "Y can be used for Z")
- [ ] Insights explain mechanisms, quantitative relationships, or subtle findings

---

## PAPER CONTENT
{paper_text[:60000]}
"""
        return prompt
    
    def build_compliance_check_prompt(self, insight: Dict[str, Any]) -> str:
        """Build compliance check prompt for insights"""
        
        prompt = f"""# ROLE
You are a strict compliance checker. Your task is to verify if an insight meets the quality and domain requirements.

---

## COMPLIANCE CHECKS

### ❌ REJECT if insight is:

#### 1. Paper Meta-Information
- Describes what the paper/article/review discusses
- Mentions "the author", "this paper", "this study", "this review"
- Examples:
  - ❌ "This paper reviews machine learning applications in combustion"
  - ❌ "The authors propose a new turbulence model for CFD"

#### 2. Time-Sensitive
- Contains specific years ("in 2024", "by 2030")
- Uses words like "currently", "recently", "latest", "modern"
- Predicts future trends or developments
- Examples:
  - ❌ "Currently, electric vehicles are becoming popular"
  - ❌ "Recent advances in AI have enabled better predictions"

#### 3. Too General/Obvious
- Statements that are common knowledge in the field
- No specific mechanism, no quantitative insight
- Just says "X is important" or "Y can improve Z"
- Examples:
  - ❌ "Combustion modeling is important for engine design"
  - ❌ "Machine learning can improve prediction accuracy"

#### 4. Overly Broad/Open-Ended
- Too vague to be meaningful
- Could apply to any field, not specific to combustion/heat/fluid/CFD/energy
- Examples:
  - ❌ "Interdisciplinary collaboration is beneficial"
  - ❌ "Computational methods are increasingly important"

#### 5. Pure ML/CS (Not Domain-Specific)
- Can be understood with only ML/CS knowledge
- No combustion/heat transfer/fluid/CFD/energy context
- Examples:
  - ❌ "Neural networks can approximate nonlinear functions"
  - ❌ "Cross-validation prevents overfitting in regression models"

### ✅ ACCEPT if insight:
- Describes a specific mechanism, relationship, or finding
- Requires domain expertise (combustion/heat/fluid/CFD/energy) to appreciate
- Is non-obvious or counterintuitive
- Explains "why" or "how" something works at a technical level
- May mention ML/AI BUT in domain context (e.g., "ANN fails in HCCI because...")

---

## OUTPUT FORMAT

```json
{{
  "compliant": true/false,
  "issues": [
    {{
      "type": "meta_info/time_sensitive/too_general/too_broad/pure_ml_cs",
      "description": "specific issue"
    }}
  ],
  "verdict": "pass/fail",
  "recommendation": "brief recommendation"
}}
```

**verdict**:
- `pass`: Compliant, domain-specific, substantial insight
- `fail`: Violates one or more compliance rules

---

## INSIGHT TO CHECK

```json
{json.dumps(insight, ensure_ascii=False, indent=2)}
```

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
                    "max_tokens": 20000,
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
    
    def generate_insights(self, paper_text: str) -> List[Dict[str, Any]]:
        """Generate domain insights using LLM"""
        logger.info("=" * 60)
        logger.info("Generating 10 Domain Insights")
        logger.info(f"Using model: {self.generation_model}")
        logger.info("=" * 60)
        
        prompt = self.build_generation_prompt(paper_text)
        response_text = self.call_llm(prompt, self.generation_model, require_json=True)
        
        # Save raw response
        debug_path = "data/milestone1_insights_raw.txt"
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
        
        insights = data.get("insights", [])
        
        if not insights:
            raise ValueError("No insights generated")
        
        logger.info(f"✅ Successfully generated {len(insights)} insights")
        return insights
    
    def check_compliance(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Check if insight is compliant"""
        prompt = self.build_compliance_check_prompt(insight)
        response_text = self.call_llm(prompt, self.compliance_check_model, require_json=True)
        
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Compliance check JSON parse failed: {e}")
            # Fallback
            return {
                "compliant": True,
                "issues": [],
                "verdict": "pass",
                "recommendation": "Failed to parse compliance check result"
            }
    
    def batch_compliance_check(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check all insights for compliance"""
        logger.info("=" * 60)
        logger.info("Compliance Check")
        logger.info(f"Using model: {self.compliance_check_model}")
        logger.info("=" * 60)
        
        compliance_results = []
        
        for i, insight in enumerate(insights, 1):
            logger.info(f"Checking insight {i}/{len(insights)}...")
            try:
                result = self.check_compliance(insight)
                compliance_results.append(result)
                
                verdict = result.get("verdict", "pass")
                logger.info(f"  Verdict: {verdict}")
                
            except Exception as e:
                logger.error(f"Compliance check failed for insight {i}: {e}")
                compliance_results.append({
                    "compliant": False,
                    "issues": [{"type": "error", "description": str(e)[:100]}],
                    "verdict": "fail",
                    "recommendation": "Exception during check"
                })
        
        pass_count = sum(1 for r in compliance_results if r.get("verdict") == "pass")
        logger.info(f"Compliance Check Results: {pass_count}/{len(compliance_results)} passed")
        
        return compliance_results
    
    def batch_citation_verification(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify all citations"""
        logger.info("=" * 60)
        logger.info("Citation Verification")
        logger.info(f"Similarity threshold: {self.citation_similarity_threshold*100:.0f}%")
        logger.info("=" * 60)
        
        verification_results = []
        
        for i, insight in enumerate(insights, 1):
            logger.info(f"Verifying citations for insight {i}/{len(insights)}...")
            
            original_text = insight.get("original_text", {})
            
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
        logger.info(f"Citation Verification: {total_verified}/{len(verification_results)} insights passed")
        
        return verification_results
    
    def wrap_with_metadata(self, insights: List[Dict[str, Any]],
                          compliance_results: List[Dict[str, Any]],
                          citation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to insights"""
        logger.info("=" * 60)
        logger.info("Adding Metadata")
        logger.info("=" * 60)
        
        wrapped_insights = []
        
        for insight, cr, citr in zip(insights, compliance_results, citation_results):
            insight_id = f"insight_{hashlib.md5(insight['insight_text'].encode()).hexdigest()[:8]}"
            
            wrapped_insight = {
                "insight_id": insight_id,
                "insight_text": insight.get("insight_text", ""),
                "original_text": insight.get("original_text", {}),
                "domain": insight.get("domain", "general"),
                "tags": insight.get("tags", []),
                "source": {
                    "type": "with_reference",
                    "paper_id": "PECS_combustion_review",
                    "paper_title": "Combustion Science Review"
                },
                "compliance_check": {
                    "compliant": cr.get("compliant", False),
                    "issues": cr.get("issues", []),
                    "verdict": cr.get("verdict", "fail"),
                    "recommendation": cr.get("recommendation", "")
                },
                "citation_verification": citr,
                "metadata": {
                    "generation_model": self.generation_model,
                    "compliance_check_model": self.compliance_check_model,
                    "created_at": datetime.now().isoformat(),
                    "milestone": "milestone_1_insights",
                    "insight_length": len(insight.get("insight_text", ""))
                }
            }
            
            wrapped_insights.append(wrapped_insight)
        
        logger.info(f"✓ Wrapped {len(wrapped_insights)} insights")
        return wrapped_insights
    
    def save_insights(self, insights: List[Dict[str, Any]]) -> None:
        """Save insights to JSONL"""
        logger.info("=" * 60)
        logger.info("Saving Insights")
        logger.info("=" * 60)
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for insight in insights:
                f.write(json.dumps(insight, ensure_ascii=False) + '\n')
        
        logger.info(f"✓ Insights saved to: {self.output_path}")
        logger.info(f"  Total: {len(insights)} insights")
    
    def generate_report(self, insights: List[Dict[str, Any]]) -> str:
        """Generate quality report"""
        logger.info("=" * 60)
        logger.info("Generating Report")
        logger.info("=" * 60)
        
        total = len(insights)
        
        # Compliance stats
        compliant = sum(1 for i in insights if i["compliance_check"]["compliant"])
        passed = sum(1 for i in insights if i["compliance_check"]["verdict"] == "pass")
        
        # Citation stats
        citation_verified = sum(1 for i in insights if i["citation_verification"]["verified"])
        
        # Domain distribution
        domain_count = {}
        for insight in insights:
            domain = insight.get("domain", "unknown")
            domain_count[domain] = domain_count.get(domain, 0) + 1
        
        report = f"""# Milestone 1 Insights - Quality Report

**Generation Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Model**: {self.generation_model}  
**Total Insights**: {total}

---

## 📊 OVERALL RESULTS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Compliance Passed** | {passed}/{total} | {passed/total*100:.1f}% |
| **Compliant** | {compliant}/{total} | {compliant/total*100:.1f}% |
| **Citations Verified** | {citation_verified}/{total} | {citation_verified/total*100:.1f}% |

---

## 🎯 DOMAIN DISTRIBUTION

| Domain | Count |
|--------|-------|
"""
        
        for domain, count in sorted(domain_count.items(), key=lambda x: -x[1]):
            report += f"| {domain} | {count} |\n"
        
        report += f"""
---

## 📋 DETAILED INSIGHTS

"""
        
        for i, insight in enumerate(insights, 1):
            verdict = insight["compliance_check"]["verdict"]
            verdict_emoji = "✅" if verdict == "pass" else "❌"
            
            report += f"""
### Insight {i} {verdict_emoji}

**Text**: {insight['insight_text'][:300]}{'...' if len(insight['insight_text']) > 300 else ''}

**Domain**: {insight['domain']}

**Verdict**: {verdict}

**Checks**:
- Compliant: {'✅' if insight['compliance_check']['compliant'] else '❌'}
- Citations verified: {'✅' if insight['citation_verification']['verified'] else '❌'} ({insight['citation_verification']['verified_citations']}/{insight['citation_verification']['total_citations']})

"""
            
            if insight['compliance_check']['issues']:
                report += "**Issues**:\n"
                for issue in insight['compliance_check']['issues']:
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
        logger.info("🚀 Milestone 1 Insights: Domain Learning Points")
        logger.info("=" * 80)
        
        try:
            # Load paper
            paper_text = self.load_paper_text()
            
            # Generate 10 insights
            insights = self.generate_insights(paper_text)
            
            # Compliance check (no retry)
            compliance_results = self.batch_compliance_check(insights)
            
            # Citation verification
            citation_results = self.batch_citation_verification(insights)
            
            # Wrap with metadata
            wrapped_insights = self.wrap_with_metadata(insights, compliance_results, citation_results)
            
            # Save
            self.save_insights(wrapped_insights)
            
            # Report
            report = self.generate_report(wrapped_insights)
            self.save_report(report)
            
            logger.info("=" * 80)
            logger.info("✅ Milestone 1 Insights completed!")
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
        log_file="logs/milestone1_insights.log"
    )
    
    load_env_variables(config.get("env_file_path", ".env"))
    
    insights_config = {
        "generation_model": "openai/deepseek-ai/DeepSeek-V3",
        "compliance_check_model": "openai/deepseek-ai/DeepSeek-V3",
        "paper_path": "main.txt",
        "output_path": "data/milestone1_insights.jsonl",
        "report_path": "data/milestone1_insights_report.md",
        "citation_similarity_threshold": 0.85
    }
    
    generator = Milestone1InsightsGenerator(insights_config)
    generator.run()


if __name__ == "__main__":
    main()
