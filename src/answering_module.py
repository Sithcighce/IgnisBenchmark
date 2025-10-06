"""
模型解题模块
"""

import logging
import requests
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from .models import QuestionUnit
from .prompt_manager import PromptManager


logger = logging.getLogger(__name__)


class AnsweringModule:
    """模型解题模块"""
    
    def __init__(
        self, 
        endpoint: str, 
        model_name: str,
        concurrency: int = 1,
        prompt_manager: Optional[PromptManager] = None
    ):
        """
        初始化解题模块
        
        Args:
            endpoint: LM Studio API端点
            model_name: 使用的模型名称
            concurrency: 并发数
            prompt_manager: Prompt管理器实例
        """
        self.endpoint = endpoint
        self.model_name = model_name
        self.concurrency = concurrency
        self.prompt_manager = prompt_manager or PromptManager()
    
    def _build_prompt(self, question_text: str) -> str:
        """
        构建解题prompt
        
        Args:
            question_text: 题目文本
        
        Returns:
            构建好的prompt
        """
        # 获取prompt模板
        prompt_template = self.prompt_manager.get_answering_prompt()
        
        # 替换占位符
        prompt = prompt_template.replace("{question_text}", question_text)
        
        return prompt
    
    def _answer_single_question(self, question: QuestionUnit) -> QuestionUnit:
        """
        对单个问题进行解答
        
        Args:
            question: 问题对象
        
        Returns:
            包含答案的问题对象
        """
        prompt = self._build_prompt(question.question_text)
        
        try:
            logger.info(f"正在解答问题: {question.question_id[:8]}...")
            
            # 调用本地LM Studio API
            response = requests.post(
                self.endpoint,
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=120  # 2分钟超时
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                question.candidate_answer = answer
                logger.info(f"成功获取答案: {question.question_id[:8]}...")
            else:
                logger.error(f"API调用失败 (状态码 {response.status_code}): {response.text}")
                question.candidate_answer = f"[ERROR] API返回状态码 {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {question.question_id[:8]}...")
            question.candidate_answer = "[ERROR] 请求超时"
        except Exception as e:
            logger.error(f"解答问题时出错: {e}")
            question.candidate_answer = f"[ERROR] {str(e)}"
        
        return question
    
    def answer_questions(self, questions: List[QuestionUnit]) -> List[QuestionUnit]:
        """
        对一批问题进行解答
        
        Args:
            questions: 问题列表
        
        Returns:
            包含答案的问题列表
        """
        logger.info(f"开始解答 {len(questions)} 道题目，并发数: {self.concurrency}")
        
        # 使用线程池进行并发处理
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            answered_questions = list(executor.map(self._answer_single_question, questions))
        
        # 统计成功率
        success_count = sum(1 for q in answered_questions if q.candidate_answer and not q.candidate_answer.startswith("[ERROR]"))
        logger.info(f"解答完成: {success_count}/{len(questions)} 成功")
        
        return answered_questions
