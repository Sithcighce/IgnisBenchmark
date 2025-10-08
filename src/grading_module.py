"""
自动判题模块
"""

import json
import logging
import time
from typing import List, Optional
from litellm import completion
from .models import QuestionUnit, GradingResult
from .prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class GradingModule:
    """自动判题模块"""
    
    def __init__(self, config_or_model_name, prompt_manager: Optional[PromptManager] = None):
        """
        初始化判题模块 - 支持配置字典或单独参数
        
        Args:
            config_or_model_name: 配置字典或模型名称
            prompt_manager: Prompt管理器实例
        """
        # 处理配置字典或单独参数
        if isinstance(config_or_model_name, dict):
            config = config_or_model_name
            self.model_name = config.get('grading_model', 'gemini/gemini-2.5-flash')
        else:
            # 向后兼容：单独参数
            self.model_name = config_or_model_name
            
        self.prompt_manager = prompt_manager or PromptManager()
    
    def _build_prompt(
        self, 
        question_text: str, 
        standard_answer: str, 
        candidate_answer: str
    ) -> str:
        """
        构建判题prompt
        
        Args:
            question_text: 题目文本
            standard_answer: 标准答案
            candidate_answer: 待评估的答案
        
        Returns:
            构建好的prompt
        """
        # 获取prompt模板
        prompt_template = self.prompt_manager.get_grading_prompt()
        
        # 替换占位符
        prompt = prompt_template.replace("{question_text}", question_text)
        prompt = prompt.replace("{standard_answer}", standard_answer)
        prompt = prompt.replace("{candidate_answer}", candidate_answer)
        
        return prompt
    
    def grade_answer(self, question: QuestionUnit, error_callback=None) -> GradingResult:
        """
        对单个答案进行判题
        
        Args:
            question: 包含候选答案的问题对象
            error_callback: 判题系统错误时的回调函数，参数为(question, candidate_answer, error_reason)
        
        Returns:
            判题结果
        """
        if not question.candidate_answer:
            logger.warning(f"问题 {question.question_id[:8]}... 没有候选答案")
            return GradingResult(
                is_correct=False,
                score=0.0,
                reasoning="没有候选答案"
            )
        
        # 如果候选答案是错误信息，直接判为错误
        if question.candidate_answer.startswith("[ERROR]"):
            return GradingResult(
                is_correct=False,
                score=0.0,
                reasoning=f"解题过程出错: {question.candidate_answer}"
            )
        
        prompt = self._build_prompt(
            question.question_text,
            question.standard_answer,
            question.candidate_answer
        )
        
        # 重试配置
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在判题: {question.question_id[:8]}... (第{attempt+1}次尝试)")
                
                # 调用LLM进行判题
                response = completion(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # 较低温度以保证判题的一致性
                    # 无max_tokens限制，模型自由生成任意长度的判题理由
                )
                
                # 统计token使用(仅Gemini)
                if "gemini" in self.model_name.lower() and hasattr(response, 'usage') and response.usage:
                    try:
                        usage_dict = response.usage.__dict__ if hasattr(response.usage, '__dict__') else response.usage
                        logger.info(f"Gemini判题API usage: {usage_dict}")
                        from .token_tracker import token_tracker
                        token_tracker.track_grading_usage(usage_dict)
                    except Exception as e:
                        logger.error(f"Token统计失败: {e}")
                
                # 解析响应
                content = response.choices[0].message.content
                
                # 尝试提取JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                data = json.loads(content)
                
                # 验证必要字段
                if "is_correct" not in data or "score" not in data or "reasoning" not in data:
                    raise ValueError("响应缺少必要字段")
                
                result = GradingResult(
                    is_correct=bool(data["is_correct"]),
                    score=float(data["score"]),
                    reasoning=data["reasoning"]
                )
                
                logger.info(f"判题完成: {question.question_id[:8]}... - {'正确' if result.is_correct else '错误'} (分数: {result.score})")
                return result
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"第{attempt+1}次尝试解析失败: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"将进行第{attempt+2}次尝试...")
                    time.sleep(1)  # 等待1秒后重试
                    continue
                else:
                    logger.error(f"JSON解析失败，已尝试{max_retries}次")
                    logger.error(f"最终响应内容: {content if 'content' in locals() else '无响应内容'}")
                    error_reason = f"JSON解析失败，已重试{max_retries}次"
                    
                    # 调用错误回调
                    if error_callback:
                        error_callback(question, question.candidate_answer, error_reason)
                    
                    return GradingResult(
                        is_correct=False,
                        score=0.0,
                        reasoning=f"判题系统错误: {error_reason}"
                    )
            except Exception as e:
                logger.error(f"第{attempt+1}次尝试时出现其他错误: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"将进行第{attempt+2}次尝试...")
                    time.sleep(1)
                    continue
                else:
                    error_reason = f"{str(e)}，已重试{max_retries}次"
                    
                    # 调用错误回调
                    if error_callback:
                        error_callback(question, question.candidate_answer, error_reason)
                    
                    return GradingResult(
                        is_correct=False,
                        score=0.0,
                        reasoning=f"判题系统错误: {error_reason}"
                    )
    
    def grade_batch(self, questions: List[QuestionUnit]) -> List[tuple]:
        """
        批量判题
        
        Args:
            questions: 问题列表
        
        Returns:
            (问题, 判题结果)元组的列表
        """
        logger.info(f"开始批量判题，共 {len(questions)} 道题")
        
        results = []
        for question in questions:
            result = self.grade_answer(question)
            results.append((question, result))
        
        # 统计
        correct_count = sum(1 for _, result in results if result.is_correct)
        logger.info(f"判题完成: {correct_count}/{len(questions)} 正确")
        
        return results
