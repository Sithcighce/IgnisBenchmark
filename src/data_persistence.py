"""
数据持久化模块 - 管理Benchmark错题库和Validation验证集
"""

import json
import logging
import random
import os
from typing import List, Tuple
from .models import QuestionUnit, BenchmarkEntry
from .utils import ensure_directory_exists


logger = logging.getLogger(__name__)


class DataPersistence:
    """数据持久化管理器"""
    
    def __init__(self, benchmark_path: str, validation_path: str):
        """
        初始化数据持久化管理器
        
        Args:
            benchmark_path: Benchmark错题库文件路径
            validation_path: Validation验证集文件路径
        """
        self.benchmark_path = benchmark_path
        self.validation_path = validation_path
        
        # 确保目录和文件存在
        ensure_directory_exists(benchmark_path)
        ensure_directory_exists(validation_path)
        
        for path in [benchmark_path, validation_path]:
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    pass
                logger.info(f"创建新数据文件: {path}")
    
    def load_benchmark_questions(self) -> List[QuestionUnit]:
        """
        从Benchmark错题库加载所有题目
        
        Returns:
            QuestionUnit列表
        """
        questions = []
        
        if not os.path.exists(self.benchmark_path):
            return questions
        
        try:
            with open(self.benchmark_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        # 兼容两种格式：
                        # 1. 简单的QuestionUnit（种子数据）
                        # 2. 完整的BenchmarkEntry
                        if "question_data" in data:
                            # 完整BenchmarkEntry格式
                            question_data = data["question_data"]
                        else:
                            # 简单QuestionUnit格式（种子题目）
                            question_data = data
                        
                        question = QuestionUnit.from_dict(question_data)
                        questions.append(question)
            
            logger.info(f"从Benchmark错题库加载了 {len(questions)} 道题目")
            return questions
            
        except Exception as e:
            logger.error(f"加载Benchmark错题库时出错: {e}")
            return []
    
    def get_random_samples(self, count: int) -> List[QuestionUnit]:
        """
        从Benchmark错题库随机抽取Few-shot样本
        
        Args:
            count: 抽取数量
        
        Returns:
            随机抽取的题目列表
        """
        all_questions = self.load_benchmark_questions()
        
        if len(all_questions) == 0:
            logger.warning("Benchmark错题库为空，无法抽取Few-shot样本")
            return []
        
        if len(all_questions) <= count:
            logger.warning(f"Benchmark错题库只有 {len(all_questions)} 道题，少于请求的 {count} 道")
            return all_questions
        
        samples = random.sample(all_questions, count)
        logger.info(f"从Benchmark错题库随机抽取了 {len(samples)} 道题目作为Few-shot样本")
        return samples
    
    def save_to_benchmark(self, entry: BenchmarkEntry):
        """
        保存错题到Benchmark错题库
        
        Args:
            entry: Benchmark条目
        """
        try:
            with open(self.benchmark_path, 'a', encoding='utf-8') as f:
                json_str = json.dumps(entry.to_dict(), ensure_ascii=False)
                f.write(json_str + '\n')
            
            logger.info(f"保存错题到Benchmark: {entry.question_data.question_id[:8]}...")
            
        except Exception as e:
            logger.error(f"保存到Benchmark错题库时出错: {e}")
    
    def save_to_validation(self, question: QuestionUnit):
        """
        保存正确答题的题目到Validation验证集
        
        Args:
            question: 题目对象
        """
        try:
            with open(self.validation_path, 'a', encoding='utf-8') as f:
                json_str = json.dumps(question.to_dict(), ensure_ascii=False)
                f.write(json_str + '\n')
            
            logger.info(f"保存到Validation验证集: {question.question_id[:8]}...")
            
        except Exception as e:
            logger.error(f"保存到Validation验证集时出错: {e}")
    
    def get_counts(self) -> Tuple[int, int]:
        """
        获取两个数据集的题目数量
        
        Returns:
            (benchmark_count, validation_count)
        """
        benchmark_count = 0
        validation_count = 0
        
        if os.path.exists(self.benchmark_path):
            try:
                with open(self.benchmark_path, 'r', encoding='utf-8') as f:
                    benchmark_count = sum(1 for line in f if line.strip())
            except Exception as e:
                logger.error(f"统计Benchmark数量时出错: {e}")
        
        if os.path.exists(self.validation_path):
            try:
                with open(self.validation_path, 'r', encoding='utf-8') as f:
                    validation_count = sum(1 for line in f if line.strip())
            except Exception as e:
                logger.error(f"统计Validation数量时出错: {e}")
        
        return benchmark_count, validation_count
