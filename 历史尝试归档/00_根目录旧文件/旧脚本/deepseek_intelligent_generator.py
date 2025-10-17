#!/usr/bin/env python3
"""
DeepSeek Detail Q Generator with Intelligent Retry
使用DeepSeek官方API，支持智能重试机制
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
MAX_RETRIES_PER_QUESTION = 3  # 每题最多重试3次
MAX_CONCURRENT_FILES = 20  # 并发处理文件数


class DeepSeekDetailQGenerator:
    """使用DeepSeek API的智能题目生成器"""
    
    def __init__(self, output_dir: str = "questions_deepseek"):
        self.output_dir = Path(output_dir)
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        logger.info(f"Initialized DeepSeek Generator")
        logger.info(f"Model: {DEEPSEEK_MODEL}")
        logger.info(f"API Base: {DEEPSEEK_API_BASE}")
        
        # 统计
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
            "model": "deepseek/" + DEEPSEEK_MODEL,  # litellm需要provider前缀
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
        """构建生成题目的prompt"""
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
- `reasoning`: 需要推理和机理解释
- `calculation`: 需要公式推导或数值计算
- `concept`: 需要深入理解概念原理

### 4. 难度等级
- 3: 需要专业知识
- 4: 需要深入理解和综合分析
- 5: 需要高级专家知识

### 5. 引用要求
- 每道题必须引用论文原文中的 **2段精确文字**
- 引用必须是**原文的精确片段**
- 每段引用长度：50-200字符

---

## 输出格式（严格JSON）

```json
{{
  "questions": [
    {{
      "question_text": "问题描述",
      "standard_answer": "详细答案（≥300字符）",
      "original_text": {{
        "1": "原文精确引用1",
        "2": "原文精确引用2"
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
    
    def build_quality_check_prompt(self, question: Dict[str, Any], paper_excerpt: str) -> str:
        """构建质量检查prompt"""
        prompt = f"""你是一位严格的质量审核专家。请检查以下问题和答案的质量。

**问题**: {question['question_text']}

**答案**: {question['standard_answer']}

**原文引用**:
{json.dumps(question['original_text'], ensure_ascii=False, indent=2)}

**论文摘录**（用于验证）:
{paper_excerpt[:8000]}

---

## 检查标准

### 1. 领域聚焦性（domain_focused）
- ✅ 问题是否需要燃烧/传热/流体/CFD/能源领域的专业知识？
- ❌ 是否是纯ML/CS方法对比？

### 2. 答案正确性（answer_correct）
- ✅ 事实准确
- ✅ 机理解释正确
- ✅ 公式和推导合理
- ❌ 问题类型：
  - `too_brief`: 答案过于简短（<300字符）
  - `factual_error`: 事实错误
  - `fundamental_error`: 基本原理错误
  - `unsupported`: 关键声明未被支持

### 3. 其他合规性（other_compliant）
- ❌ 不能有元信息
- ❌ 不能有时效性内容
- ❌ 不能过于宽泛

---

## 输出格式（严格JSON）

```json
{{
  "domain_focused": true/false,
  "domain_reasoning": "为什么需要或不需要领域知识",
  "answer_correct": true/false,
  "answer_issues": ["issue1", "issue2"],
  "other_compliant": true/false,
  "other_issues": ["issue1"],
  "overall_verdict": "pass/fail",
  "recommendation": "如果失败，给出具体改进建议（如何修改问题或答案）"
}}
```
"""
        return prompt
    
    def build_retry_prompt(self, question: Dict[str, Any], quality_result: Dict[str, Any], paper_text: str) -> str:
        """构建重试prompt（包含原题和审核意见）"""
        prompt = f"""你是燃烧科学、传热、流体力学、CFD和能源领域的资深专家。

之前生成的题目未通过质量审核，请根据审核意见进行优化。

**原问题**:
{question['question_text']}

**原答案**:
{question['standard_answer']}

**原引用**:
{json.dumps(question['original_text'], ensure_ascii=False, indent=2)}

**审核意见**:
- 领域聚焦: {"通过" if quality_result.get('domain_focused') else "❌ " + quality_result.get('domain_reasoning', '')}
- 答案正确性: {"通过" if quality_result.get('answer_correct') else "❌ " + str(quality_result.get('answer_issues', []))}
- 其他合规性: {"通过" if quality_result.get('other_compliant') else "❌ " + str(quality_result.get('other_issues', []))}
- **改进建议**: {quality_result.get('recommendation', '请优化题目')}

**论文全文**:
{paper_text}

---

## 任务要求

请根据审核意见优化这道题目：
1. 保持领域专业性（燃烧/传热/流体/CFD/能源）
2. 确保答案≥300字符，包含详细推导
3. 使用原文精确引用（2段，50-200字符）
4. 修正审核意见中指出的所有问题

## 输出格式（严格JSON）

```json
{{
  "question_text": "优化后的问题",
  "standard_answer": "优化后的答案（≥300字符）",
  "original_text": {{
    "1": "原文引用1",
    "2": "原文引用2"
  }},
  "type": "reasoning|calculation|concept",
  "difficulty": 3-5,
  "topic": "combustion_kinetics|heat_transfer|fluid_mechanics|CFD_modeling|energy_systems"
}}
```
"""
        return prompt
    
    def retry_question(self, question: Dict[str, Any], quality_result: Dict[str, Any], 
                      paper_text: str, paper_excerpt: str, retry_count: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """重试生成单个问题"""
        logger.info(f"  Retry #{retry_count}: Regenerating question...")
        
        # 构建重试prompt
        retry_prompt = self.build_retry_prompt(question, quality_result, paper_text)
        
        # 调用API重新生成
        response = self.call_deepseek(retry_prompt, require_json=True)
        new_question = json.loads(response)
        
        # 质量检查新问题
        check_prompt = self.build_quality_check_prompt(new_question, paper_excerpt)
        check_response = self.call_deepseek(check_prompt, require_json=True)
        new_quality_result = json.loads(check_response)
        
        self.stats["total_retries"] += 1
        
        return new_question, new_quality_result
    
    def process_single_question(self, question: Dict[str, Any], paper_text: str, 
                                paper_excerpt: str, q_index: int) -> Dict[str, Any]:
        """处理单个问题（含智能重试）"""
        logger.info(f"  Processing Q{q_index}...")
        
        # 初始质量检查
        check_prompt = self.build_quality_check_prompt(question, paper_excerpt)
        check_response = self.call_deepseek(check_prompt, require_json=True)
        quality_result = json.loads(check_response)
        
        current_question = question
        retry_count = 0
        
        # 智能重试：不合格则立即重试（最多3次）
        while quality_result.get("overall_verdict") != "pass" and retry_count < MAX_RETRIES_PER_QUESTION:
            retry_count += 1
            logger.info(f"  Q{q_index} FAILED - Retrying ({retry_count}/{MAX_RETRIES_PER_QUESTION})...")
            
            current_question, quality_result = self.retry_question(
                current_question, quality_result, paper_text, paper_excerpt, retry_count
            )
        
        # 添加质量检查结果
        current_question["quality_check"] = quality_result
        current_question["retry_count"] = retry_count
        
        # 判断最终状态
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
            # 读取论文全文
            with open(txt_file, 'r', encoding='utf-8') as f:
                paper_text = f.read()
            
            logger.info(f"[{file_name}] Paper length: {len(paper_text)} chars")
            
            # 创建输出目录
            output_folder = self.output_dir / file_name
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # 复制原文
            shutil.copy(txt_file, output_folder / f"{file_name}.txt")
            
            # 生成5道题
            logger.info(f"[{file_name}] Generating 5 questions...")
            gen_prompt = self.build_generation_prompt(paper_text)
            response = self.call_deepseek(gen_prompt, require_json=True, timeout=180)
            
            questions_data = json.loads(response)
            questions = questions_data.get("questions", [])
            logger.info(f"[{file_name}] Generated {len(questions)} questions")
            
            if len(questions) == 0:
                raise ValueError("No questions generated")
            
            # 论文摘录（用于质量检查）
            paper_excerpt = paper_text[:8000]
            
            # 并发处理5道题（含智能重试）
            passed_questions = []
            failed_questions = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(self.process_single_question, q, paper_text, paper_excerpt, i): i
                    for i, q in enumerate(questions, 1)
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    
                    # 添加元数据
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
            
            # 保存结果
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
    
    def test_with_main_txt(self) -> bool:
        """使用main.txt测试，检查通过率"""
        logger.info("=" * 80)
        logger.info("PHASE 1: Testing with main.txt")
        logger.info("=" * 80)
        
        main_txt = Path("main.txt")
        if not main_txt.exists():
            logger.error("main.txt not found!")
            return False
        
        result = self.process_single_file(main_txt)
        
        if result["status"] != "success":
            logger.error("main.txt processing failed!")
            return False
        
        pass_rate = result["passed"] / result["total_questions"] * 100
        logger.info(f"main.txt results: {result['passed']}/{result['total_questions']} passed ({pass_rate:.1f}%)")
        
        if pass_rate >= 60:
            logger.info(f"✅ Pass rate {pass_rate:.1f}% >= 60%, proceeding to batch processing...")
            return True
        else:
            logger.warning(f"❌ Pass rate {pass_rate:.1f}% < 60%, stopping here.")
            return False
    
    def process_all_files_reverse(self):
        """按字典序倒序批量处理所有文件"""
        logger.info("=" * 80)
        logger.info("PHASE 2: Batch Processing (Reverse Order)")
        logger.info("=" * 80)
        
        # 查找所有txt文件（倒序）
        compliant_dir = Path("compliant")
        txt_files = sorted(list(compliant_dir.glob("*.txt")), reverse=True)
        
        logger.info(f"Found {len(txt_files)} txt files (reverse order)")
        logger.info(f"First 5 files: {[f.name for f in txt_files[:5]]}")
        logger.info(f"Concurrent workers: {MAX_CONCURRENT_FILES}")
        
        self.stats["total_files"] = len(txt_files)
        
        # 并发处理
        results = []
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_FILES) as executor:
            futures = {executor.submit(self.process_single_file, f): f for f in txt_files}
            
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
        logger.info(f"   Files: {self.stats['completed']}/{self.stats['total_files']}")
        logger.info(f"   Questions: {self.stats['passed_questions']}/{self.stats['total_questions']} passed")
        logger.info(f"   Total retries: {self.stats['total_retries']}")
        logger.info("=" * 80)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """生成总结报告"""
        report_file = self.output_dir / "BATCH_SUMMARY.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# DeepSeek Detail Q Generation - Summary Report

**Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model**: {DEEPSEEK_MODEL}  
**API Base**: {DEEPSEEK_API_BASE}  
**Processing Mode**: Intelligent Retry (Max 3 retries per question)

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
    print("DeepSeek Detail Q Generator with Intelligent Retry")
    print("=" * 80)
    print(f"Model: {DEEPSEEK_MODEL}")
    print(f"API: {DEEPSEEK_API_BASE}")
    print(f"Max retries per question: {MAX_RETRIES_PER_QUESTION}")
    print("=" * 80)
    
    generator = DeepSeekDetailQGenerator("question_reverse")
    
    # 阶段1: 使用main.txt测试
    print("\n[PHASE 1] Testing with main.txt...")
    if not generator.test_with_main_txt():
        print("\n❌ Test failed or pass rate < 60%. Stopping.")
        return
    
    # 阶段2: 批量处理（倒序）
    print("\n[PHASE 2] Starting batch processing (reverse order)...")
    generator.process_all_files_reverse()
    
    print("\n✅ ALL DONE!")
    print(f"Check: question_reverse/BATCH_SUMMARY.md")


if __name__ == "__main__":
    main()
