#!/usr/bin/env python3
"""
Milestone 1 Insights Pro Generator
生成高质量的领域洞察，强调理解过程而非简单陈述事实
每篇论文生成5条深度洞察
"""

import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import difflib
from litellm import completion

# 导入已有模块
from src.utils import setup_logging, load_env_variables

# 配置日志
logger = logging.getLogger(__name__)

# 文件路径
PAPER_FILE = Path("main.txt")
OUTPUT_FILE = Path("data/milestone1_insights_pro.jsonl")
REPORT_FILE = Path("data/milestone1_insights_pro_report.md")

# 模型配置
GENERATION_MODEL = "openai/deepseek-ai/DeepSeek-V3"
CITATION_THRESHOLD = 0.85


def load_paper_data() -> Dict[str, Any]:
    """加载论文全文"""
    logger.info(f"Loading paper from: {PAPER_FILE}")
    with open(PAPER_FILE, 'r', encoding='utf-8') as f:
        entire_text = f.read()
    logger.info(f"  Text length: {len(entire_text)} chars")
    return {
        "title": "Combustion Science Review",
        "entire_text": entire_text
    }


def build_generation_prompt(seed_data: Dict[str, Any]) -> str:
    """
    构建生成洞察的prompt
    强调理解过程：为什么→怎么样→意味着什么
    """
    # 截取前50000字符以避免超长context
    text_excerpt = seed_data['entire_text'][:50000]
    
    prompt = f"""你是一位燃烧科学和CFD领域的资深专家。你刚刚仔细阅读了这篇论文的核心内容，并从中获得了深刻的领域理解。

**论文标题**: {seed_data['title']}

**论文内容摘录** (前50000字符):
{text_excerpt}

---

## 任务要求

请生成 **5条高质量的领域洞察**，每条洞察必须：

### 1. 内容要求
- **聚焦领域**: 必须关于燃烧、传热、流体力学、CFD、能源应用（不要纯ML/CS方法对比）
- **展示理解过程**（重要！）：
  - ❌ 错误示例（仅陈述事实）："灰盒模型结合物理和数据驱动方法"
  - ✅ 正确示例（展示理解）："灰盒模型的关键创新在于**在物理约束下学习数据模式**，这解决了纯ML模型在小样本燃烧数据上的过拟合问题，同时避免了CFD的计算瓶颈"

### 2. 洞察结构（三段式）
每条洞察应包含：
1. **核心发现**（What）：这个领域知识的本质是什么
2. **理解过程**（Why/How）：为什么这很重要？它如何解决问题？背后的机理是什么？
3. **领域意义**（Impact）：对燃烧/CFD/能源领域意味着什么

示例格式：
"[核心发现]。这是因为[理解过程/机理解释]，从而[领域意义/解决的问题]。"

### 3. 引用要求
- 每条洞察必须引用论文原文中的 **2段具体文字**
- 引用文字必须是原文的**精确片段**（不要改写）
- 引用长度：每段50-200字符

### 4. 禁止内容
- ❌ 简单罗列事实（如"XX方法比YY快"）
- ❌ 纯ML方法对比（如"SVM vs ANN"）
- ❌ 缺少机理解释的陈述
- ❌ 时效性内容（如"近年来"、"未来将"）
- ❌ 过于宽泛的通用知识

---

## 输出格式（严格JSON）

```json
{{
  "insights": [
    {{
      "insight_text": "[核心发现]。[理解过程/机理解释]，[领域意义]。",
      "original_text": {{
        "1": "原文精确引用1（50-200字符）",
        "2": "原文精确引用2（50-200字符）"
      }},
      "domain": "combustion_modeling|combustion_control|engine_diagnostics|emission_modeling|turbulence_combustion|combustion_dynamics",
      "tags": ["tag1", "tag2", "tag3"]
    }}
  ]
}}
```

请生成5条符合要求的洞察。
"""
    return prompt


def verify_citations(
    original_text_dict: Dict[str, str],
    entire_text: str,
    threshold: float = CITATION_THRESHOLD
) -> Tuple[bool, Dict[str, Any]]:
    """
    验证引用是否在原文中存在
    
    Args:
        original_text_dict: 引用文本字典
        entire_text: 论文全文
        threshold: 相似度阈值
    
    Returns:
        (是否全部通过, 详细结果)
    """
    entire_lower = entire_text.lower()
    entire_lower = ''.join(c for c in entire_lower if c.isalnum() or c.isspace())
    
    results = {}
    verified_count = 0
    failed_citations = []
    
    for cite_id, cite_text in original_text_dict.items():
        cite_clean = cite_text.lower()
        cite_clean = ''.join(c for c in cite_clean if c.isalnum() or c.isspace())
        
        # 快速检查：在原文中查找候选位置
        words = cite_clean.split()[:5]  # 前5个词
        search_term = ' '.join(words)
        
        candidate_positions = []
        start_pos = 0
        while True:
            pos = entire_lower.find(search_term, start_pos)
            if pos == -1:
                break
            candidate_positions.append(pos)
            start_pos = pos + 1
        
        # 在候选位置附近精确匹配
        best_similarity = 0.0
        best_snippet = ""
        
        for pos in candidate_positions:
            # 提取候选片段（前后各50%长度）
            start = max(0, pos - len(cite_clean) // 2)
            end = min(len(entire_lower), pos + len(cite_clean) + len(cite_clean) // 2)
            candidate = entire_lower[start:end]
            
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, cite_clean, candidate).ratio()
            if similarity > best_similarity:
                best_similarity = similarity
                best_snippet = entire_lower[pos:pos+100]
        
        verified = best_similarity >= threshold
        if verified:
            verified_count += 1
        else:
            failed_citations.append({
                "citation_id": cite_id,
                "text": cite_text[:100] + "...",
                "similarity": best_similarity
            })
        
        results[cite_id] = {
            "text": cite_text,
            "similarity": best_similarity,
            "verified": verified,
            "matched_snippet": best_snippet
        }
    
    all_verified = verified_count == len(original_text_dict)
    
    return all_verified, {
        "verified": all_verified,
        "total_citations": len(original_text_dict),
        "verified_citations": verified_count,
        "failed_citations": failed_citations,
        "details": results
    }


def generate_insights(seed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    生成5条高质量洞察
    """
    logger.info("=" * 60)
    logger.info("Generating Insights Pro")
    logger.info("=" * 60)
    
    # 构建prompt
    prompt = build_generation_prompt(seed_data)
    
    # 调用模型生成
    logger.info(f"Calling {GENERATION_MODEL}...")
    response = completion(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_base="https://api.siliconflow.cn/v1",
        api_key=os.environ.get('SILICONFLOW_API_KEY'),
        response_format={"type": "json_object"},
        max_tokens=25000,
        temperature=0.7
    )
    
    response_text = response.choices[0].message.content
    logger.info(f"✓ Got response: {len(response_text)} chars")
    
    # 解析JSON
    try:
        data = json.loads(response_text)
        insights = data.get("insights", [])
        logger.info(f"✓ Parsed {len(insights)} insights")
        return insights
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.error(f"Response: {response_text[:500]}")
        return []


def verify_all_citations(
    insights: List[Dict[str, Any]],
    entire_text: str
) -> List[Dict[str, Any]]:
    """
    验证所有洞察的引文
    """
    logger.info("=" * 60)
    logger.info("Citation Verification")
    logger.info(f"Threshold: {CITATION_THRESHOLD * 100}%")
    logger.info("=" * 60)
    
    verified_count = 0
    
    for i, insight in enumerate(insights, 1):
        logger.info(f"Verifying citations for insight {i}/{len(insights)}...")
        
        original_text = insight.get("original_text", {})
        if not original_text:
            logger.warning(f"  ⚠ No citations found")
            insight["citation_verification"] = {
                "verified": False,
                "total_citations": 0,
                "verified_citations": 0,
                "failed_citations": [],
                "details": {}
            }
            continue
        
        # 验证引文
        all_verified, verification_result = verify_citations(
            original_text, entire_text, CITATION_THRESHOLD
        )
        
        insight["citation_verification"] = verification_result
        
        if all_verified:
            logger.info(f"  ✅ All {verification_result['total_citations']} citations verified")
            verified_count += 1
        else:
            logger.warning(f"  ❌ {len(verification_result['failed_citations'])} citation(s) failed verification")
            for failed in verification_result['failed_citations']:
                logger.warning(f"     - Citation {failed['citation_id']}: {failed['similarity']*100:.1f}% similarity")
    
    logger.info(f"Citation Verification: {verified_count}/{len(insights)} insights passed")
    return insights


def add_metadata(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """添加元数据"""
    logger.info("=" * 60)
    logger.info("Adding Metadata")
    logger.info("=" * 60)
    
    for insight in insights:
        # 生成唯一ID
        import hashlib
        text_hash = hashlib.md5(insight['insight_text'].encode()).hexdigest()[:8]
        insight['insight_id'] = f"insight_pro_{text_hash}"
        
        # 添加来源信息
        insight['source'] = {
            "type": "with_reference",
            "paper_id": "PECS_combustion_review",
            "paper_title": "Combustion Science Review"
        }
        
        # 添加元数据
        insight['metadata'] = {
            "generation_model": GENERATION_MODEL,
            "created_at": datetime.now().isoformat(),
            "milestone": "milestone_1_insights_pro",
            "insight_length": len(insight['insight_text'])
        }
    
    logger.info(f"✓ Wrapped {len(insights)} insights")
    return insights


def save_insights(insights: List[Dict[str, Any]]) -> None:
    """保存洞察到JSONL文件"""
    logger.info("=" * 60)
    logger.info("Saving Insights")
    logger.info("=" * 60)
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for insight in insights:
            f.write(json.dumps(insight, ensure_ascii=False) + '\n')
    
    logger.info(f"✓ Insights saved to: {OUTPUT_FILE}")
    logger.info(f"  Total: {len(insights)} insights")


def generate_report(insights: List[Dict[str, Any]]) -> None:
    """生成质量报告"""
    logger.info("=" * 60)
    logger.info("Generating Report")
    logger.info("=" * 60)
    
    # 统计数据
    total = len(insights)
    citation_verified = sum(1 for i in insights if i.get('citation_verification', {}).get('verified', False))
    
    # 领域分布
    domain_count = {}
    for insight in insights:
        domain = insight.get('domain', 'unknown')
        domain_count[domain] = domain_count.get(domain, 0) + 1
    
    # 洞察长度统计
    lengths = [i['metadata']['insight_length'] for i in insights]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    min_length = min(lengths) if lengths else 0
    max_length = max(lengths) if lengths else 0
    
    # 生成Markdown报告
    report = f"""# Milestone 1 Insights Pro - Quality Report

**Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model**: {GENERATION_MODEL}  
**Total Insights**: {total}

---

## 📊 OVERALL RESULTS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Citations Verified** | {citation_verified}/{total} | {citation_verified/total*100:.1f}% |

---

## 📏 INSIGHT LENGTH STATISTICS

| Metric | Value |
|--------|-------|
| **Average Length** | {avg_length:.0f} characters |
| **Shortest Insight** | {min_length} characters |
| **Longest Insight** | {max_length} characters |

---

## 🎯 DOMAIN DISTRIBUTION

| Domain | Count |
|--------|-------|
"""
    
    for domain, count in sorted(domain_count.items(), key=lambda x: -x[1]):
        report += f"| {domain} | {count} |\n"
    
    report += "\n---\n\n## 📋 DETAILED INSIGHTS\n\n"
    
    # 详细洞察
    for i, insight in enumerate(insights, 1):
        verified = insight.get('citation_verification', {}).get('verified', False)
        status = "✅" if verified else "❌"
        
        report += f"\n### Insight {i} {status}\n\n"
        report += f"**Text**: {insight['insight_text']}\n\n"
        report += f"**Domain**: {insight.get('domain', 'unknown')}\n\n"
        report += f"**Tags**: {', '.join(insight.get('tags', []))}\n\n"
        report += f"**Length**: {insight['metadata']['insight_length']} chars\n\n"
        
        # 引文验证结果
        verification = insight.get('citation_verification', {})
        if verification:
            verified_cites = verification.get('verified_citations', 0)
            total_cites = verification.get('total_citations', 0)
            report += f"**Citations verified**: {status} ({verified_cites}/{total_cites})\n\n"
            
            if verification.get('failed_citations'):
                report += "**Citation issues**:\n"
                for failed in verification['failed_citations']:
                    report += f"  - Citation {failed['citation_id']}: {failed['similarity']*100:.1f}% similarity\n"
                report += "\n"
        
        # 原文引用
        report += "**Original Text**:\n"
        for cite_id, cite_text in insight.get('original_text', {}).items():
            report += f"{cite_id}. {cite_text}\n"
        report += "\n"
    
    # 保存报告
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"✓ Report saved to: {REPORT_FILE}")


def main():
    """主函数"""
    setup_logging()
    load_env_variables()
    
    logger.info("=" * 80)
    logger.info("Milestone 1 Insights Pro Generator - START")
    logger.info("=" * 80)
    
    try:
        # 加载论文数据
        paper_data = load_paper_data()
        
        # 生成洞察
        insights = generate_insights(paper_data)
        
        if not insights:
            logger.error("❌ Failed to generate insights")
            sys.exit(1)
        
        # 验证引文（仅检查引文存在性，不做合规性检查）
        insights = verify_all_citations(insights, paper_data['entire_text'])
        
        # 添加元数据
        insights = add_metadata(insights)
        
        # 保存结果
        save_insights(insights)
        
        # 生成报告
        generate_report(insights)
        
        logger.info("=" * 80)
        logger.info("✅ Milestone 1 Insights Pro completed!")
        logger.info(f"   Output: {OUTPUT_FILE}")
        logger.info(f"   Report: {REPORT_FILE}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
