"""
题目生成模块
"""

import json
import logging
from typing import List, Optional
from litellm import completion
from .models import QuestionUnit
from .prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class QuestionGenerator:
    """题目生成器"""
    
    def __init__(self, model_name: str, batch_size: int = 10, prompt_manager: Optional[PromptManager] = None):
        """
        初始化题目生成器
        
        Args:
            model_name: 使用的模型名称
            batch_size: 每批生成的题目数量
            prompt_manager: Prompt管理器实例
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.prompt_manager = prompt_manager or PromptManager()
    
    def _build_prompt(self, few_shot_examples: List[QuestionUnit]) -> str:
        """
        构建动态Prompt
        
        Args:
            few_shot_examples: Few-shot示例列表
        
        Returns:
            构建好的完整prompt
        """
        # 获取prompt模板
        prompt_template = self.prompt_manager.get_generation_prompt()
        
        # 将Few-shot示例转换为JSON字符串
        examples_data = [
            {
                "topic": q.topic,
                "difficulty": q.difficulty,
                "type": q.type,
                "question_text": q.question_text,
                "standard_answer": q.standard_answer
            }
            for q in few_shot_examples
        ]
        few_shot_json = json.dumps(examples_data, ensure_ascii=False, indent=2)
        
        # 替换占位符
        prompt = prompt_template.replace("{few_shot_examples_json_string}", few_shot_json)
        prompt = prompt.replace("{batch_size}", str(self.batch_size))
        
        return prompt
    
    def generate_questions(
        self, 
        few_shot_examples: Optional[List[QuestionUnit]] = None
    ) -> List[QuestionUnit]:
        """
        生成一批题目
        
        Args:
            few_shot_examples: Few-shot示例列表，如果为None则不使用Few-shot
        
        Returns:
            生成的题目列表
        """
        # 如果没有提供Few-shot示例，使用默认的空列表
        if few_shot_examples is None:
            few_shot_examples = []
        
        # 构建prompt
        prompt = self._build_prompt(few_shot_examples)
        
        logger.info(f"开始使用 {self.model_name} 生成 {self.batch_size} 道题目")
        
        try:
            # 调用LLM生成题目
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 提高温度以增加多样性
                max_tokens=8192,  # 提高token限制，支持更长的思考过程
            )
            
            # 解析响应
            content = response.choices[0].message.content
            
            # 尝试提取JSON（可能包含markdown代码块）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # 处理可能的截断问题 - 检查是否有有效的JSON开始
            if '"prompt_text"' in content and not '"questions"' in content:
                logger.warning("响应中只包含prompt_text，没有questions数据，可能是截断或格式问题")
                logger.error(f"响应内容过短或格式错误: {content[:500]}...")
                return []
            
            if not content.strip().endswith('}'):
                logger.warning("响应似乎被截断，尝试修复JSON格式")
                # 尝试找到最后一个完整的问题对象
                if '"questions"' in content:
                    # 找到questions数组的开始
                    questions_start = content.find('"questions"')
                    bracket_start = content.find('[', questions_start)
                    if bracket_start != -1:
                        # 寻找最后一个完整的问题对象
                        content_part = content[bracket_start:]
                        # 简单修复：如果没有正确结尾，添加结尾
                        if not content.strip().endswith(']}'):
                            if content.count('{') > content.count('}'):
                                # 缺少结尾括号
                                content += '}]}'
                            elif not content.strip().endswith(']'):
                                content += ']}'
                            elif not content.strip().endswith('}'):
                                content += '}'
                else:
                    logger.error("响应中没有找到questions字段，可能是严重截断")
                    return []
            
            data = json.loads(content)
            
            # 提取questions列表
            questions_data = data.get("questions", [])
            
            if not questions_data:
                logger.error("生成的响应中没有找到questions字段")
                return []
            
            # 转换为QuestionUnit对象
            questions = []
            for q_data in questions_data:
                try:
                    question = QuestionUnit(
                        topic=q_data["topic"],
                        difficulty=int(q_data["difficulty"]),
                        type=q_data["type"],
                        question_text=q_data["question_text"],
                        standard_answer=q_data["standard_answer"],
                        generation_model=self.model_name
                    )
                    questions.append(question)
                except Exception as e:
                    logger.error(f"解析单个题目时出错: {e}, 数据: {q_data}")
                    continue
            
            logger.info(f"成功生成 {len(questions)} 道题目")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            logger.error(f"响应内容: {content}")
            return []
        except Exception as e:
            logger.error(f"生成题目时出错: {e}")
            return []
