"""
数据模型定义
"""

from typing import Optional
from datetime import datetime
import uuid


class QuestionUnit:
    """题库数据单元"""
    
    def __init__(
        self,
        topic: str,
        difficulty: int,
        type: str,
        question_text: str,
        standard_answer: str,
        generation_model: str,
        question_id: Optional[str] = None,
        creation_timestamp: Optional[str] = None,
        candidate_answer: Optional[str] = None
    ):
        self.question_id = question_id or str(uuid.uuid4())
        self.topic = topic
        self.difficulty = difficulty
        self.type = type
        self.question_text = question_text
        self.standard_answer = standard_answer
        self.generation_model = generation_model
        self.creation_timestamp = creation_timestamp or datetime.now().isoformat()
        self.candidate_answer = candidate_answer
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "question_id": self.question_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "type": self.type,
            "question_text": self.question_text,
            "standard_answer": self.standard_answer,
            "generation_model": self.generation_model,
            "creation_timestamp": self.creation_timestamp,
            "candidate_answer": self.candidate_answer
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuestionUnit':
        """从字典创建实例"""
        return cls(
            question_id=data.get("question_id"),
            topic=data["topic"],
            difficulty=data["difficulty"],
            type=data["type"],
            question_text=data["question_text"],
            standard_answer=data["standard_answer"],
            generation_model=data["generation_model"],
            creation_timestamp=data.get("creation_timestamp"),
            candidate_answer=data.get("candidate_answer")
        )


class GradingResult:
    """判题结果单元"""
    
    def __init__(
        self,
        is_correct: bool,
        score: float,
        reasoning: str
    ):
        self.is_correct = is_correct
        self.score = score
        self.reasoning = reasoning
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "is_correct": self.is_correct,
            "score": self.score,
            "reasoning": self.reasoning
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GradingResult':
        """从字典创建实例"""
        return cls(
            is_correct=data["is_correct"],
            score=data["score"],
            reasoning=data["reasoning"]
        )


class BenchmarkEntry:
    """
    Benchmark错题库条目
    包含题目数据和模型的错误尝试记录
    """
    
    def __init__(
        self,
        question_data: QuestionUnit,
        model_name: str,
        candidate_answer: str,
        grading_result: GradingResult
    ):
        self.question_data = question_data
        self.model_name = model_name
        self.candidate_answer = candidate_answer
        self.grading_result = grading_result
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "question_data": {
                "question_id": self.question_data.question_id,
                "topic": self.question_data.topic,
                "difficulty": self.question_data.difficulty,
                "type": self.question_data.type,
                "question_text": self.question_data.question_text,
                "standard_answer": self.question_data.standard_answer,
                "generation_model": self.question_data.generation_model,
                "creation_timestamp": self.question_data.creation_timestamp
            },
            "failed_attempt": {
                "model_name": self.model_name,
                "candidate_answer": self.candidate_answer,
                "grading_result": self.grading_result.to_dict()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BenchmarkEntry':
        """从字典创建实例"""
        question_data = QuestionUnit.from_dict(data["question_data"])
        failed_attempt = data["failed_attempt"]
        grading_result = GradingResult.from_dict(failed_attempt["grading_result"])
        
        return cls(
            question_data=question_data,
            model_name=failed_attempt["model_name"],
            candidate_answer=failed_attempt["candidate_answer"],
            grading_result=grading_result
        )

