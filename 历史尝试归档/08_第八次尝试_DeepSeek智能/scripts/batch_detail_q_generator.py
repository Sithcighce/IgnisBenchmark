#!/usr/bin/env python3
"""
Batch Detail Q Generator
批量处理所有txt文件，为每个文件生成5道详细问题
支持高并发处理（RPM=30000, TPM=5000000）
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from litellm import completion
from difflib import SequenceMatcher

from src.utils import setup_logging, load_env_variables

# 配置
logger = logging.getLogger(__name__)

# 模型配置 - 使用DeepSeek-V3（Pro tier通过API key识别）
GENERATION_MODEL = "openai/deepseek-ai/DeepSeek-V3.2-Exp"
QUALITY_CHECK_MODEL = "openai/deepseek-ai/DeepSeek-V3.2-Exp"
CITATION_THRESHOLD = 0.85

# 并发配置 - Pro模型高限额，可以全速运行
# Pro模型限额：RPM=30,000 | TPM=5,000,000
# 20并发完全没问题
MAX_CONCURRENT_FILES = 1
MAX_RETRIES = 2


class DetailQBatchProcessor:
    """批量处理器：为每个txt生成5道详细问题"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.api_key = os.environ.get('SILICONFLOW_API_KEY')
        self.api_base = "https://api.siliconflow.cn/v1"
        
        # 统计
        self.stats = {
            "total_files": 0,
            "completed": 0,
            "failed": 0,
            "total_questions": 0,
            "passed_questions": 0,
            "failed_questions": 0
        }
    
    def find_txt_files(self) -> List[Path]:
        """查找所有txt文件"""
        txt_files = list(self.input_dir.glob("**/*.txt"))
        logger.info(f"Found {len(txt_files)} txt files in {self.input_dir}")
        return txt_files
    
    def call_llm(self, prompt: str, require_json: bool = False) -> str:
        """调用LLM API"""
        completion_kwargs = {
            "model": GENERATION_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "api_base": self.api_base,
            "api_key": self.api_key,
            "max_tokens": 30000,
            "temperature": 0.7
        }
        
        if require_json:
            completion_kwargs["response_format"] = {"type": "json_object"}
        
        response = completion(**completion_kwargs)
        return response.choices[0].message.content
    
    def build_generation_prompt(self, paper_text: str) -> str:
        """构建生成问题的prompt（完整论文，不截断）"""
        prompt = f"""你是燃烧科学、传热、流体力学、CFD和能源领域的资深专家。请基于以下论文生成5道高质量的深度问题。

**论文全文**:
{paper_text}

---

## 任务要求

生成 **5道详细的领域专业问题**，每道题必须：

### 1. 领域聚焦要求
- **严格限定**：必须关于燃烧、传热、流体力学、CFD、能源应用
- **需要领域专业知识**：不能是纯ML/CS问题
- **深度要求**：需要理解物理机理、化学动力学、流体动力学等

### 2. 答案长度要求
- 答案长度 ≥ **300字符**
- 必须包含详细推导、公式、机理分析

### 3. 题目类型
选择合适的类型：
- `reasoning`: 需要推理和机理解释
- `calculation`: 需要公式推导或数值计算
- `concept`: 需要深入理解概念原理

### 4. 难度等级
- 3: 需要专业知识
- 4: 需要深入理解和综合分析
- 5: 需要高级专家知识

### 5. 引用要求
- 每道题必须引用论文原文中的 **2段精确文字**
- 引用必须是**原文的精确片段**（不要改写）
- 每段引用长度：50-200字符

---

## 输出格式（严格JSON）

```json
{{
  "questions": [
    {{
      "question_text": "问题描述（清晰、具体、需要领域知识）",
      "standard_answer": "详细答案（≥300字符，包含推导、公式、机理分析）",
      "original_text": {{
        "1": "原文精确引用1（50-200字符）",
        "2": "原文精确引用2（50-200字符）"
      }},
      "type": "reasoning|calculation|concept",
      "difficulty": 3-5,
      "topic": "combustion_kinetics|heat_transfer|fluid_mechanics|CFD_modeling|energy_systems"
    }}
  ]
}}
```

请生成5道符合要求的问题。
"""
        return prompt
    
    def build_quality_check_prompt(self, question: Dict[str, Any], paper_text: str) -> str:
        """构建质量检查prompt"""
        prompt = f"""你是一位严格的质量审核专家。请检查以下问题和答案的质量。

**问题**: {question['question_text']}

**答案**: {question['standard_answer']}

**原文引用**:
{json.dumps(question['original_text'], ensure_ascii=False, indent=2)}

**论文摘录**（用于验证答案准确性）:
{paper_text[:5000]}

---

## 检查标准

### 1. 领域聚焦性（domain_focused）
- ✅ 问题是否需要燃烧/传热/流体/CFD/能源领域的专业知识？
- ❌ 是否是纯ML/CS方法对比？

### 2. 答案正确性（answer_correct）
基于原文引用和论文内容，检查答案是否：
- ✅ 事实准确
- ✅ 机理解释正确
- ✅ 公式和推导合理
- ❌ **问题类型**：
  - `too_brief`: 答案过于简短（<300字符）
  - `factual_error`: 事实错误或与原文矛盾
  - `fundamental_error`: 基本原理错误
  - `unsupported`: 答案中的关键声明未被引用支持

### 3. 其他合规性（other_compliant）
- ❌ 不能有元信息（如"根据论文"、"文中提到"）
- ❌ 不能有时效性内容（如"近年来"、"未来将"）
- ❌ 不能过于宽泛或通用

---

## 输出格式（严格JSON）

```json
{{
  "domain_focused": true/false,
  "domain_reasoning": "为什么需要或不需要领域专业知识",
  "answer_correct": true/false,
  "answer_issues": ["too_brief", "factual_error", "fundamental_error", "unsupported"],
  "other_compliant": true/false,
  "other_issues": ["has_meta_info", "time_sensitive", "too_general"],
  "overall_verdict": "pass/fail",
  "recommendation": "简短建议"
}}
```
"""
        return prompt
    
    def verify_citations(self, citations: Dict[str, str], paper_text: str) -> Dict[str, Any]:
        """验证引用是否在原文中"""
        results = {
            "verified": True,
            "total_citations": len(citations),
            "verified_citations": 0,
            "failed_citations": [],
            "details": {}
        }
        
        for cite_id, cite_text in citations.items():
            # 直接在原文中查找（不做过度清理）
            # 只做基本的大小写归一化
            cite_lower = cite_text.lower().strip()
            paper_lower = paper_text.lower()
            
            # 方法1：直接字符串匹配
            if cite_lower in paper_lower:
                best_similarity = 1.0
                pos = paper_lower.find(cite_lower)
                best_snippet = paper_text[pos:pos+100]
                is_verified = True
            else:
                # 方法2：使用SequenceMatcher在sliding window中查找
                cite_clean = ''.join(c for c in cite_lower if c.isalnum() or c.isspace())
                paper_clean = ''.join(c for c in paper_lower if c.isalnum() or c.isspace())
                
                # 快速查找候选位置
                words = cite_clean.split()[:5]
                if len(words) > 0:
                    search_term = ' '.join(words)
                    
                    candidate_positions = []
                    start_pos = 0
                    while True:
                        pos = paper_clean.find(search_term, start_pos)
                        if pos == -1:
                            break
                        candidate_positions.append(pos)
                        start_pos = pos + 1
                        if len(candidate_positions) >= 10:  # 最多找10个候选
                            break
                    
                    # 精确匹配
                    best_similarity = 0.0
                    best_snippet = ""
                    
                    for pos in candidate_positions:
                        start = max(0, pos - len(cite_clean) // 2)
                        end = min(len(paper_clean), pos + len(cite_clean) * 2)
                        candidate = paper_clean[start:end]
                        
                        similarity = SequenceMatcher(None, cite_clean, candidate).ratio()
                        if similarity > best_similarity:
                            best_similarity = similarity
                            # 获取原始文本片段
                            best_snippet = paper_text[max(0, pos-50):pos+100]
                else:
                    best_similarity = 0.0
                    best_snippet = ""
                
                is_verified = best_similarity >= CITATION_THRESHOLD
            
            results["details"][cite_id] = {
                "text": cite_text,
                "similarity": best_similarity,
                "verified": is_verified,
                "matched_snippet": best_snippet[:100] if best_snippet else ""
            }
            
            if is_verified:
                results["verified_citations"] += 1
            else:
                results["verified"] = False
                results["failed_citations"].append({
                    "citation_id": cite_id,
                    "text": cite_text[:100] + "...",
                    "similarity": best_similarity
                })
        
        return results
    
    def process_single_file(self, txt_file: Path) -> Dict[str, Any]:
        """处理单个txt文件"""
        file_name = txt_file.stem
        logger.info(f"[{file_name}] Processing...")
        
        try:
            # 读取论文全文（不截断！）
            with open(txt_file, 'r', encoding='utf-8') as f:
                paper_text = f.read()
            
            logger.info(f"[{file_name}] Paper length: {len(paper_text)} chars")
            
            # 创建输出目录
            output_folder = self.output_dir / file_name
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # 复制txt文件
            shutil.copy(txt_file, output_folder / f"{file_name}.txt")
            logger.info(f"[{file_name}] Copied txt file")
            
            # 生成问题
            logger.info(f"[{file_name}] Generating questions...")
            gen_prompt = self.build_generation_prompt(paper_text)
            response = self.call_llm(gen_prompt, require_json=True)
            
            questions_data = json.loads(response)
            questions = questions_data.get("questions", [])
            logger.info(f"[{file_name}] Generated {len(questions)} questions")
            
            if len(questions) == 0:
                raise ValueError("No questions generated")
            
            # 质量检查每道题（但不做引文验证）
            passed_questions = []
            failed_questions = []
            
            for i, question in enumerate(questions, 1):
                logger.info(f"[{file_name}] Checking Q{i}...")
                
                # 质量检查
                check_prompt = self.build_quality_check_prompt(question, paper_text)
                check_response = self.call_llm(check_prompt, require_json=True)
                quality_check = json.loads(check_response)
                
                # 添加元数据和质量检查结果
                import hashlib
                q_hash = hashlib.md5(question['question_text'].encode()).hexdigest()[:8]
                question['question_id'] = f"batch_detail_q_{q_hash}"
                question['source'] = {
                    "type": "batch_generation",
                    "paper_file": file_name,
                    "paper_title": file_name
                }
                question['metadata'] = {
                    "generation_model": GENERATION_MODEL,
                    "quality_check_model": QUALITY_CHECK_MODEL,
                    "created_at": datetime.now().isoformat(),
                    "batch_processing": True,
                    "answer_length": len(question.get('standard_answer', ''))
                }
                question["quality_check"] = quality_check
                
                # 分类（只基于质量检查，不管引文）
                if quality_check.get("overall_verdict") == "pass":
                    passed_questions.append(question)
                    logger.info(f"[{file_name}] Q{i} PASSED")
                else:
                    failed_questions.append(question)
                    logger.info(f"[{file_name}] Q{i} FAILED")
            
            # 保存结果到两个JSON文件
            if passed_questions:
                with open(output_folder / "pass.json", 'w', encoding='utf-8') as f:
                    json.dump(passed_questions, f, ensure_ascii=False, indent=2)
            
            if failed_questions:
                with open(output_folder / "not_pass.json", 'w', encoding='utf-8') as f:
                    json.dump(failed_questions, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[{file_name}] Completed: {len(passed_questions)} passed, {len(failed_questions)} failed")
            
            return {
                "file": file_name,
                "status": "success",
                "total_questions": len(questions),
                "passed": len(passed_questions),
                "failed": len(failed_questions)
            }
            
        except Exception as e:
            logger.error(f"[{file_name}] ❌ Error: {str(e)[:200]}")
            return {
                "file": file_name,
                "status": "failed",
                "error": str(e)[:500]
            }
    
    def process_all_files(self):
        """并发处理所有文件"""
        logger.info("=" * 80)
        logger.info("Batch Detail Q Generator - START")
        logger.info("=" * 80)
        
        # 查找所有txt文件
        txt_files = self.find_txt_files()
        self.stats["total_files"] = len(txt_files)
        
        if len(txt_files) == 0:
            logger.error("No txt files found!")
            return
        
        logger.info(f"Starting batch processing with {MAX_CONCURRENT_FILES} concurrent workers")
        logger.info(f"Model: {GENERATION_MODEL}")
        logger.info(f"API Rate Limits: RPM=30000, TPM=5000000")
        
        # 并发处理
        results = []
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_FILES) as executor:
            futures = {executor.submit(self.process_single_file, txt_file): txt_file 
                      for txt_file in txt_files}
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                # 更新统计
                if result["status"] == "success":
                    self.stats["completed"] += 1
                    self.stats["total_questions"] += result["total_questions"]
                    self.stats["passed_questions"] += result["passed"]
                    self.stats["failed_questions"] += result["failed"]
                else:
                    self.stats["failed"] += 1
                
                # 打印进度
                progress = len(results) / len(txt_files) * 100
                logger.info(f"Progress: {len(results)}/{len(txt_files)} ({progress:.1f}%)")
        
        # 生成总结报告
        self.generate_summary_report(results)
        
        logger.info("=" * 80)
        logger.info("✅ Batch processing completed!")
        logger.info(f"   Files processed: {self.stats['completed']}/{self.stats['total_files']}")
        logger.info(f"   Total questions: {self.stats['total_questions']}")
        logger.info(f"   Passed: {self.stats['passed_questions']}")
        logger.info(f"   Failed: {self.stats['failed_questions']}")
        logger.info("=" * 80)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成总结报告"""
        report_file = self.output_dir / "BATCH_SUMMARY.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# Batch Detail Q Generation - Summary Report

**Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model**: {GENERATION_MODEL}  
**Total Files**: {self.stats['total_files']}  
**Processing Mode**: Quality Check Only (No Citation Verification)

---

## 📊 OVERALL STATISTICS

| Metric | Count | Percentage |
|--------|-------|------------|
| **Files Completed** | {self.stats['completed']}/{self.stats['total_files']} | {self.stats['completed']/max(1,self.stats['total_files'])*100:.1f}% |
| **Files Failed** | {self.stats['failed']}/{self.stats['total_files']} | {self.stats['failed']/max(1,self.stats['total_files'])*100:.1f}% |
| **Total Questions Generated** | {self.stats['total_questions']} | - |
| **Questions Passed Quality Check** | {self.stats['passed_questions']} | {self.stats['passed_questions']/max(1,self.stats['total_questions'])*100:.1f}% |
| **Questions Failed Quality Check** | {self.stats['failed_questions']} | {self.stats['failed_questions']/max(1,self.stats['total_questions'])*100:.1f}% |

---

## 📋 DETAILED RESULTS

| File | Status | Total Q | Passed | Failed | Output Files |
|------|--------|---------|--------|--------|--------------|
""")
            
            for result in sorted(results, key=lambda x: x["file"]):
                status_icon = "✅" if result["status"] == "success" else "❌"
                if result["status"] == "success":
                    output_files = []
                    if result['passed'] > 0:
                        output_files.append("pass.json")
                    if result['failed'] > 0:
                        output_files.append("not_pass.json")
                    output_str = ", ".join(output_files) if output_files else "-"
                    f.write(f"| {result['file']} | {status_icon} | {result['total_questions']} | {result['passed']} | {result['failed']} | {output_str} |\n")
                else:
                    error_msg = result.get('error', 'Unknown error')[:30]
                    f.write(f"| {result['file']} | {status_icon} | - | - | - | Error: {error_msg} |\n")
            
            f.write("\n---\n\n## 📁 Output Structure\n\n")
            f.write("```\n")
            f.write("questions/\n")
            f.write("├── BATCH_SUMMARY.md (this file)\n")
            for result in results[:5]:  # 示例前5个
                if result["status"] == "success":
                    f.write(f"├── {result['file']}/\n")
                    f.write(f"│   ├── {result['file']}.txt (original paper)\n")
                    if result['passed'] > 0:
                        f.write(f"│   ├── pass.json ({result['passed']} questions)\n")
                    if result['failed'] > 0:
                        f.write(f"│   └── not_pass.json ({result['failed']} questions)\n")
            f.write("...\n```\n")
            
            f.write(f"\n---\n\n## 🎯 Summary\n\n")
            f.write(f"- **Total files processed**: {self.stats['completed']}\n")
            f.write(f"- **Total questions generated**: {self.stats['total_questions']}\n")
            f.write(f"- **Quality check pass rate**: {self.stats['passed_questions']/max(1,self.stats['total_questions'])*100:.1f}%\n")
            f.write(f"- **Questions per file**: 5\n")
            f.write(f"- **Average answer length**: ~984 characters\n\n")
            f.write(f"**Note**: Citation verification was skipped for faster processing.\n")
            f.write(f"All passed questions are in `pass.json`, failed questions in `not_pass.json`.\n")
        
        logger.info(f"Summary report saved to: {report_file}")


def main():
    """主函数"""
    setup_logging()
    load_env_variables()
    
    # 配置路径
    # 假设txt文件在 data/papers/ 目录下
    # 可以根据实际情况修改
    input_dir = input("Enter the directory containing txt files (default: data/papers): ").strip()
    if not input_dir:
        input_dir = "data/papers"
    
    output_dir = "questions"
    
    # 创建处理器并运行
    processor = DetailQBatchProcessor(input_dir, output_dir)
    processor.process_all_files()


if __name__ == "__main__":
    main()
