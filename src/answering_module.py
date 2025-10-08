"""
模型解题模块 - 使用硅基流动API
"""

import logging
import os
import time
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import litellm
from .models import QuestionUnit
from .prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class AnsweringModule:
    """模型解题模块 - 使用硅基流动Qwen"""
    
    def __init__(
        self, 
        api_base: str = "https://api.siliconflow.cn/v1",
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        concurrency: int = 1,
        prompt_manager: Optional[PromptManager] = None
    ):
        """
        初始化解题模块
        
        Args:
            api_base: 硅基流动API地址
            model_name: 模型名称
            concurrency: 并发数
            prompt_manager: Prompt管理器实例
        """
        self.api_base = api_base
        self.model_name = model_name
        self.concurrency = concurrency
        self.prompt_manager = prompt_manager or PromptManager()
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY environment variable is required")
        
        logger.info(f"AnsweringModule初始化完成: 模型={model_name}, 并发={concurrency}")
    
    def _build_prompt(self, question_text: str) -> str:
        """
        构建解题Prompt
        
        Args:
            question_text: 题目文本
        
        Returns:
            构建好的prompt
        """
        prompt_template = self.prompt_manager.get_answering_prompt()
        prompt = prompt_template.replace("{question_text}", question_text)
        
        return prompt
    
    def _answer_single_question(self, question: QuestionUnit) -> QuestionUnit:
        """
        解答单个问题 - 使用硅基流动API
        
        Args:
            question: 问题对象
        
        Returns:
            包含答案的问题对象
        """
        prompt = self._build_prompt(question.question_text)
        
        # 重试配置
        max_retries = 3
        base_timeout = 120  # 基础超时时间（2分钟，比之前60秒更宽松）
        
        for attempt in range(max_retries):
            try:
                # 逐步增加超时时间
                timeout = base_timeout + (attempt * 30)  # 120s, 150s, 180s
                logger.info(f"正在解答问题 {question.question_id[:8]}...（第{attempt+1}次尝试，超时{timeout}秒）")
                
                response = litellm.completion(
                    model=f"siliconflow/{self.model_name}",  # 硅基流动格式
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    api_key=self.api_key,
                    api_base=self.api_base,
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=timeout
                )
                
                if response and response.choices:
                    answer = response.choices[0].message.content
                    if answer and answer.strip():  # 确保答案不为空
                        question.candidate_answer = answer
                        logger.info(f"成功获取答案: {question.question_id[:8]}...")
                        return question
                    else:
                        logger.warning(f"第{attempt+1}次尝试获取空答案，将重试")
                        continue
                else:
                    logger.warning(f"第{attempt+1}次尝试API调用返回空响应")
                    if attempt == max_retries - 1:
                        question.candidate_answer = "[ERROR] API返回空响应"
                        return question
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"第{attempt+1}次尝试出错: {error_msg}")
                
                if attempt == max_retries - 1:  # 最后一次尝试
                    if "timeout" in error_msg.lower():
                        question.candidate_answer = f"[ERROR] 请求超时 ({timeout}秒)"
                    elif "rate limit" in error_msg.lower():
                        question.candidate_answer = "[ERROR] API调用频率限制"
                    else:
                        question.candidate_answer = f"[ERROR] {error_msg}"
                    return question
            
            # 等待一段时间再重试
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避: 1, 2, 4 秒
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        return question
    
    def answer_question(self, question: QuestionUnit) -> str:
        """
        解答单个问题
        
        Args:
            question: 问题对象
        
        Returns:
            答案字符串
        """
        try:
            answered_question = self._answer_single_question(question)
            return answered_question.candidate_answer or "[ERROR] 无答案"
        except Exception as e:
            logger.error(f"解答单个问题失败: {e}")
            return f"[ERROR] 解答失败: {str(e)}"
    
    def answer_questions(self, questions: List[QuestionUnit]) -> List[Tuple[QuestionUnit, str]]:
        """
        对一批问题进行解答，返回(问题，答案)元组列表
        
        Args:
            questions: 问题列表
        
        Returns:
            (问题，答案)元组列表
        """
        logger.info(f"开始解答 {len(questions)} 道题目，并发数: {self.concurrency}")
        
        # 使用线程池进行并发处理
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            answered_questions = list(executor.map(self._answer_single_question, questions))
        
        # 统计成功率
        successful = sum(1 for q in answered_questions if q.candidate_answer and not q.candidate_answer.startswith("[ERROR]"))
        logger.info(f"解答完成: {successful}/{len(questions)} 成功")
        
        # 返回(问题, 答案)元组列表
        result = []
        for question in answered_questions:
            answer = question.candidate_answer if question.candidate_answer else "[ERROR] 无答案"
            result.append((question, answer))
        
        return result
    
    def answer_questions_with_callback(self, questions: List[QuestionUnit], 
                                     process_callback=None) -> List[Tuple[QuestionUnit, str]]:
        """
        对一批问题进行解答，支持流式处理回调（解题完成立即回调处理）
        
        Args:
            questions: 问题列表
            process_callback: 处理回调函数(question, answer)，每完成一题立即调用
        
        Returns:
            (问题，答案)元组列表
        """
        logger.info(f"开始流式解答 {len(questions)} 道题目，并发数: {self.concurrency}")
        
        results = []
        
        # 使用ThreadPoolExecutor进行并发处理
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            # 提交所有任务
            future_to_question = {
                executor.submit(self._answer_single_question, q): q 
                for q in questions
            }
            
            # 流式处理结果
            for future in concurrent.futures.as_completed(future_to_question):
                question = future_to_question[future]
                try:
                    answered_question = future.result()
                    answer = answered_question.candidate_answer or "[ERROR] 无答案"
                    results.append((answered_question, answer))
                    
                    # 立即回调处理（这里可以进行判题）
                    if process_callback:
                        process_callback(answered_question, answer)
                    
                    logger.info(f"题目完成: {answered_question.question_text[:30]}...")
                
                except Exception as e:
                    logger.error(f"题目失败 [{question.question_text[:30]}...]: {e}")
                    error_answer = f"[ERROR] 解答失败: {e}"
                    results.append((question, error_answer))
                    
                    # 错误也要回调
                    if process_callback:
                        process_callback(question, error_answer)
        
        # 统计成功率
        successful = sum(1 for _, answer in results if not answer.startswith("[ERROR]"))
        logger.info(f"流式解答完成: {successful}/{len(questions)} 成功")
        
        return results