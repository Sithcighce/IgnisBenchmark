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
    
    def __init__(self, config_or_model_name, batch_size: int = None, prompt_manager: Optional[PromptManager] = None):
        """
        初始化题目生成器 - 支持配置字典或单独参数
        
        Args:
            config_or_model_name: 配置字典或模型名称
            batch_size: 每批生成的题目数量
            prompt_manager: Prompt管理器实例
        """
        # 处理配置字典或单独参数
        if isinstance(config_or_model_name, dict):
            config = config_or_model_name
            self.model_name = config.get('generation_model', 'gemini/gemini-2.5-flash')
            self.batch_size = config.get('questions_per_round', 10)
        else:
            # 向后兼容：单独参数
            self.model_name = config_or_model_name
            self.batch_size = batch_size or 10
            
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
    
    def generate_question(self, few_shot_examples: Optional[List[QuestionUnit]] = None) -> Optional[QuestionUnit]:
        """
        生成单个题目
        
        Args:
            few_shot_examples: Few-shot示例列表
        
        Returns:
            生成的题目对象，失败时返回None
        """
        questions = self.generate_questions(few_shot_examples)
        return questions[0] if questions else None
    
    def generate_questions(
        self, 
        few_shot_examples: Optional[List[QuestionUnit]] = None
    ) -> List[QuestionUnit]:
        """
        生成一批题目，支持多模型回退和重试机制
        
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
        
        # 从配置文件获取生成模型列表（带提供商前缀）
        model_fallbacks = [
            "gemini/gemini-2.5-flash",  # 主模型 - Gemini
            "siliconflow/deepseek-ai/DeepSeek-V3",  # DeepSeek备选
            "siliconflow/Qwen/Qwen2.5-7B-Instruct",  # Qwen小模型（更稳定）
        ]
        
        logger.info(f"开始生成 {self.batch_size} 道题目，主模型: {self.model_name}")
        
        # 尝试所有模型组合，直到成功
        for attempt in range(3):  # 最多3轮尝试
            for model_index, current_model in enumerate(model_fallbacks):
                try:
                    if attempt > 0 or model_index > 0:
                        logger.info(f"第{attempt+1}轮，尝试模型: {current_model}")
                    
                    # 调用LLM生成题目
                    response = completion(
                        model=current_model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8,  # 提高温度以增加多样性
                        # 无max_tokens限制，模型自由生成任意长度内容
                    )
                    
                    # 统计token使用(仅Gemini)
                    if "gemini" in current_model.lower() and hasattr(response, 'usage') and response.usage:
                        try:
                            usage_dict = response.usage.__dict__ if hasattr(response.usage, '__dict__') else response.usage
                            logger.info(f"Gemini生成API usage: {usage_dict}")
                            from .token_tracker import token_tracker
                            token_tracker.track_generation_usage(usage_dict)
                        except Exception as e:
                            logger.error(f"Token统计失败: {e}")
                    
                    # 解析响应并转换为题目列表
                    questions = self._parse_response(response.choices[0].message.content, current_model)
                    
                    if questions:
                        logger.info(f"✅ 使用模型 {current_model} 成功生成 {len(questions)} 道题目")
                        return questions
                    else:
                        logger.warning(f"模型 {current_model} 返回了空的题目列表")
                        continue
                        
                except Exception as e:
                    logger.warning(f"❌ 模型 {current_model} 第{attempt+1}轮失败: {e}")
                    continue
        
        # 如果所有尝试都失败了
        logger.error(f"❌ 所有模型和重试都失败了，无法生成题目")
        return []
    
    def _parse_response(self, content: str, model_name: str) -> List[QuestionUnit]:
        """
        解析模型响应内容，提取题目列表
        
        Args:
            content: 模型响应的文本内容
            model_name: 使用的模型名称
            
        Returns:
            解析出的题目列表
        """
        try:
            # 尝试提取JSON（可能包含markdown代码块）
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # 处理可能的截断问题 - 检查是否有有效的JSON开始
            if '"prompt_text"' in content and not '"questions"' in content:
                logger.warning("响应中只包含prompt_text，没有questions数据，可能是截断或格式问题")
                return []
            
            if not content.strip().endswith('}'):
                logger.warning("响应似乎被截断，尝试修复JSON格式")
                # 尝试找到最后一个完整的问题对象
                if '"questions"' in content:
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
                        generation_model=model_name  # 使用实际成功的模型
                    )
                    questions.append(question)
                except Exception as e:
                    logger.error(f"处理单个题目数据时出错: {e}")
                    continue
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            logger.error(f"响应内容: {content[:500]}...")
            return []
        except Exception as e:
            logger.error(f"解析响应时出错: {e}")
            return []
