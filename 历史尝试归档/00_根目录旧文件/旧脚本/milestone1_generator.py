"""
Milestone 1: 基于PECS文献的自动出题验证
目标：从1篇论文生成20道高质量问题
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any
from litellm import completion

from src.utils import load_config, setup_logging, load_env_variables
from src.models import QuestionUnit

logger = logging.getLogger(__name__)


class Milestone1Generator:
    """Milestone 1 题目生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("generation_model", "gemini/gemini-2.5-flash")
        self.paper_path = config.get("paper_path", "main.txt")
        self.output_path = config.get("output_path", "data/milestone1_candidates.jsonl")
        self.report_path = config.get("report_path", "data/milestone1_report.md")
        
    def load_paper_text(self) -> str:
        """加载论文文本"""
        logger.info(f"正在读取论文: {self.paper_path}")
        
        if not os.path.exists(self.paper_path):
            raise FileNotFoundError(f"论文文件不存在: {self.paper_path}")
        
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        logger.info(f"论文加载成功，共 {len(text)} 字符")
        return text
    
    def build_generation_prompt(self, paper_text: str) -> str:
        """构建生成提示词"""
        prompt = f"""# ROLE
你是燃烧科学和工程热物理领域的资深专家，擅长基于科研文献设计高质量的教学题目。

# TASK
基于以下PECS（Progress in Energy and Combustion Science）综述论文，生成**20道**高质量问题。

## 题目要求：
1. **基于论文内容**：问题必须源于论文的核心概念、理论或实验发现
2. **深度优先**：避免简单定义题，应测试对概念的深层理解和应用能力
3. **类型多样**：
   - **concept（概念理解）**：测试对关键概念的理解
   - **reasoning（推理分析）**：需要逻辑推理和因果分析
   - **application（应用）**：将理论应用到实际场景
   - **calculation（计算）**：涉及定量分析和计算（如适用）

4. **难度分级**（1-5）：
   - 1-2: 基础概念
   - 3: 中等难度，需要综合理解
   - 4-5: 高难度，需要深入分析或跨领域知识

5. **标准答案**：必须详细、准确，包含：
   - 核心论点
   - 支撑理由/机理解释
   - 必要的公式或数据（如有）

## 论文内容：
{paper_text[:50000]}  

# OUTPUT FORMAT
输出必须是一个JSON对象，包含questions数组，每个问题包含以下字段：

```json
{{
  "questions": [
    {{
      "topic": "具体子领域（如ignition_theory, flame_propagation等）",
      "difficulty": 1-5,
      "type": "concept/reasoning/application/calculation",
      "question_text": "问题文本（中文或英文）",
      "standard_answer": "详细标准答案（中文或英文）"
    }}
  ]
}}
```

**重要**：
- 只返回JSON，不要包含任何其他文本、解释或markdown代码块
- 确保生成正好20道题
- 标准答案必须足够详细（至少100字）
"""
        return prompt
    
    def generate_questions_from_paper(self, paper_text: str) -> List[Dict[str, Any]]:
        """调用LLM生成题目（仅AI字段）"""
        logger.info("=" * 60)
        logger.info("步骤1: 调用LLM生成题目")
        logger.info(f"使用模型: {self.model_name}")
        logger.info("=" * 60)
        
        prompt = self.build_generation_prompt(paper_text)
        
        # 准备模型回退列表
        model_fallbacks = [
            {'model': self.model_name},
            {'model': 'openai/deepseek-ai/DeepSeek-V3', 
             'api_base': 'https://api.siliconflow.cn/v1', 
             'api_key': os.environ.get('SILICONFLOW_API_KEY')}
        ]
        
        # 尝试所有模型
        for attempt in range(2):
            for model_index, m in enumerate(model_fallbacks):
                try:
                    if attempt > 0 or model_index > 0:
                        logger.info(f"第{attempt+1}轮，尝试模型: {m['model']}")
                    
                    # 构建completion参数
                    completion_kwargs = {
                        "model": m['model'],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 8000,
                        "timeout": 180
                    }
                    
                    # 添加JSON格式强制（对支持的模型）
                    if "gemini" in m['model'].lower() or "openai" in m['model']:
                        completion_kwargs["response_format"] = {"type": "json_object"}
                    
                    if 'api_base' in m and m['api_base']:
                        completion_kwargs['api_base'] = m['api_base']
                    if 'api_key' in m and m['api_key']:
                        completion_kwargs['api_key'] = m['api_key']
                    
                    # 调用LiteLLM
                    response = completion(**completion_kwargs)
                    
                    # 检查响应
                    if not response or not response.choices:
                        logger.warning(f"模型 {m['model']} 返回了空响应")
                        continue
                    
                    message = response.choices[0].message
                    if not message.content:
                        logger.warning(f"模型 {m['model']} 返回内容为空")
                        continue
                    
                    response_text = message.content.strip()
                    
                    # 移除可能的markdown代码块标记
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.startswith("```"):
                        response_text = response_text[3:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    response_text = response_text.strip()
                    
                    # 保存原始响应用于调试
                    debug_path = "data/milestone1_raw_response.txt"
                    os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(response_text)
                    logger.info(f"原始响应已保存至: {debug_path}")
                    
                    # 解析JSON
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON解析失败: {e}")
                        logger.warning(f"错误位置: 第{e.lineno}行, 第{e.colno}列")
                        
                        # 尝试修复常见JSON问题
                        logger.info("尝试自动修复JSON格式...")
                        import re
                        # 移除可能的尾随逗号
                        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
                        try:
                            data = json.loads(response_text)
                            logger.info("✓ JSON修复成功")
                        except:
                            logger.error(f"JSON修复失败，跳过此模型")
                            continue
                    
                    questions = data.get("questions", [])
                    
                    if not questions:
                        logger.warning(f"模型 {m['model']} 返回的questions为空")
                        continue
                    
                    logger.info(f"✅ 使用模型 {m['model']} 成功生成 {len(questions)} 道题目")
                    return questions
                    
                except Exception as e:
                    logger.warning(f"❌ 模型 {m['model']} 第{attempt+1}轮失败: {e}")
                    import traceback
                    logger.debug(traceback.format_exc())
                    continue
        
        # 所有尝试都失败
        raise RuntimeError("所有模型和重试都失败了，无法生成题目")
    
    def wrap_with_metadata(self, questions: List[Dict[str, Any]], paper_id: str = "PECS_2020_Vol85_p1", 
                          paper_title: str = "Combustion Theory Review") -> List[Dict[str, Any]]:
        """添加系统metadata字段"""
        logger.info("=" * 60)
        logger.info("步骤2: 添加系统metadata")
        logger.info("=" * 60)
        
        wrapped_questions = []
        
        for q in questions:
            wrapped = {
                # 系统生成字段
                "question_id": f"comb_qa_{str(uuid.uuid4())[:8]}",
                
                # AI生成字段（保持原样）
                "question_text": q.get("question_text", ""),
                "standard_answer": q.get("standard_answer", ""),
                "type": q.get("type", "reasoning"),
                "difficulty": q.get("difficulty", 3),
                "topic": q.get("topic", "general_combustion"),
                
                # 来源信息
                "source": {
                    "type": "with_reference",
                    "paper_id": paper_id,
                    "paper_title": paper_title
                },
                
                # 元数据
                "metadata": {
                    "generation_model": self.model_name,
                    "created_at": datetime.now().isoformat(),
                    "milestone": "milestone_1"
                }
            }
            wrapped_questions.append(wrapped)
        
        logger.info(f"✓ 成功包装 {len(wrapped_questions)} 道题目")
        return wrapped_questions
    
    def save_questions(self, questions: List[Dict[str, Any]]) -> None:
        """保存题目到JSONL文件"""
        logger.info("=" * 60)
        logger.info("步骤3: 保存题目")
        logger.info("=" * 60)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for q in questions:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        
        logger.info(f"✓ 题目已保存至: {self.output_path}")
        logger.info(f"  共 {len(questions)} 道题")
    
    def generate_quality_report(self, questions: List[Dict[str, Any]]) -> str:
        """生成质量评估报告"""
        logger.info("=" * 60)
        logger.info("步骤4: 生成质量评估报告")
        logger.info("=" * 60)
        
        # 统计分析
        total = len(questions)
        
        # 类型分布
        type_count = {}
        for q in questions:
            qtype = q.get("type", "unknown")
            type_count[qtype] = type_count.get(qtype, 0) + 1
        
        # 难度分布
        difficulty_count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for q in questions:
            diff = q.get("difficulty", 3)
            if diff in difficulty_count:
                difficulty_count[diff] += 1
        
        # 主题分布
        topic_count = {}
        for q in questions:
            topic = q.get("topic", "unknown")
            topic_count[topic] = topic_count.get(topic, 0) + 1
        
        # 答案长度分析
        answer_lengths = [len(q.get("standard_answer", "")) for q in questions]
        avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        min_length = min(answer_lengths) if answer_lengths else 0
        max_length = max(answer_lengths) if answer_lengths else 0
        
        # 生成Markdown报告
        report = f"""# Milestone 1 质量评估报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**使用模型**: {self.model_name}  
**数据来源**: {self.paper_path}

---

## 📊 整体统计

- **总题目数**: {total} 道
- **目标数量**: 20 道
- **完成率**: {total/20*100:.1f}%

---

## 🎯 题目类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
"""
        for qtype, count in sorted(type_count.items()):
            percentage = count / total * 100
            report += f"| {qtype} | {count} | {percentage:.1f}% |\n"
        
        report += f"""
---

## 📈 难度分布

| 难度等级 | 数量 | 占比 | 说明 |
|----------|------|------|------|
| 1 | {difficulty_count[1]} | {difficulty_count[1]/total*100:.1f}% | 基础 |
| 2 | {difficulty_count[2]} | {difficulty_count[2]/total*100:.1f}% | 简单 |
| 3 | {difficulty_count[3]} | {difficulty_count[3]/total*100:.1f}% | 中等 |
| 4 | {difficulty_count[4]} | {difficulty_count[4]/total*100:.1f}% | 困难 |
| 5 | {difficulty_count[5]} | {difficulty_count[5]/total*100:.1f}% | 极难 |

---

## 🔬 主题分布

"""
        for topic, count in sorted(topic_count.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total * 100
            report += f"- **{topic}**: {count} 道 ({percentage:.1f}%)\n"
        
        report += f"""
---

## 📝 答案质量分析

- **平均答案长度**: {avg_length:.0f} 字符
- **最短答案**: {min_length} 字符
- **最长答案**: {max_length} 字符

"""
        
        # 质量评估（简单规则）
        short_answers = [i+1 for i, q in enumerate(questions) if len(q.get("standard_answer", "")) < 100]
        if short_answers:
            report += f"""
### ⚠️ 潜在问题

- **答案过短的题目** (< 100字符): 第 {', '.join(map(str, short_answers[:5]))} 题等 ({len(short_answers)} 道)
"""
        
        # 可用性估计
        usable_count = sum(1 for q in questions if len(q.get("standard_answer", "")) >= 100)
        report += f"""
---

## ✅ 验收标准检查

- [{'x' if total == 20 else ' '}] 成功生成20道完整的Q&A
- [{'x' if usable_count >= 15 else ' '}] 至少15道题符合质量标准（答案≥100字符）
- [x] 输出为标准JSON格式
- **预估可用题目**: {usable_count} / 20 道

---

## 💡 建议

"""
        if usable_count >= 18:
            report += "✨ **质量优秀**！绝大多数题目符合标准，可以进入Milestone 2。\n"
        elif usable_count >= 15:
            report += "✓ **质量合格**。建议人工审核答案较短的题目，然后进入Milestone 2。\n"
        else:
            report += "⚠️ **需要改进**。建议调整prompt或few-shot示例，重新生成。\n"
        
        report += f"""
---

## 📋 示例题目（前3道）

"""
        for i, q in enumerate(questions[:3], 1):
            report += f"""
### 题目 {i}

- **ID**: `{q['question_id']}`
- **类型**: {q['type']}
- **难度**: {q['difficulty']}/5
- **主题**: {q['topic']}

**问题**:  
{q['question_text']}

**标准答案**:  
{q['standard_answer'][:200]}{'...' if len(q['standard_answer']) > 200 else ''}

---
"""
        
        return report
    
    def save_report(self, report: str) -> None:
        """保存评估报告"""
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ 评估报告已保存至: {self.report_path}")
    
    def run(self) -> None:
        """运行Milestone 1完整流程"""
        logger.info("=" * 60)
        logger.info("🚀 Milestone 1: 基于PECS文献的自动出题验证")
        logger.info("=" * 60)
        
        try:
            # Step 1: 加载论文
            paper_text = self.load_paper_text()
            
            # Step 2: 生成题目（AI字段）
            ai_questions = self.generate_questions_from_paper(paper_text)
            
            # Step 3: 包装metadata
            full_questions = self.wrap_with_metadata(
                ai_questions,
                paper_id="PECS_combustion_review",
                paper_title="Combustion Science Review"
            )
            
            # Step 4: 保存题目
            self.save_questions(full_questions)
            
            # Step 5: 生成报告
            report = self.generate_quality_report(full_questions)
            self.save_report(report)
            
            # 在控制台也打印报告
            print("\n" + report)
            
            logger.info("=" * 60)
            logger.info("✅ Milestone 1 完成！")
            logger.info("=" * 60)
            logger.info(f"📄 题目文件: {self.output_path}")
            logger.info(f"📊 报告文件: {self.report_path}")
            
        except Exception as e:
            logger.error(f"❌ Milestone 1 执行失败: {e}")
            raise


def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 设置日志
    setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file="logs/milestone1.log"
    )
    
    # 加载环境变量
    load_env_variables(config.get("env_file_path", ".env"))
    
    # Milestone 1 配置
    m1_config = {
        "generation_model": config.get("generation_model", "gemini/gemini-2.5-flash"),
        "paper_path": "main.txt",
        "output_path": "data/milestone1_candidates.jsonl",
        "report_path": "data/milestone1_report.md"
    }
    
    # 运行
    generator = Milestone1Generator(m1_config)
    generator.run()


if __name__ == "__main__":
    main()
