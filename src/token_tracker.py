"""
Token统计模块 - 仅统计Gemini API请求的token开销
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token使用统计"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def add(self, other: 'TokenUsage'):
        """累加token使用量"""
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens


@dataclass
class ApiCosts:
    """API成本统计"""
    generation_usage: TokenUsage = field(default_factory=TokenUsage)
    grading_usage: TokenUsage = field(default_factory=TokenUsage)
    total_cost: float = 0.0
    
    # Gemini 2.5 Flash定价 (每1M token)
    GEMINI_FLASH_INPUT_COST = 0.075  # USD per 1M input tokens
    GEMINI_FLASH_OUTPUT_COST = 0.30  # USD per 1M output tokens
    
    def calculate_cost(self) -> float:
        """计算总成本"""
        total_usage = TokenUsage()
        total_usage.add(self.generation_usage)
        total_usage.add(self.grading_usage)
        
        input_cost = (total_usage.prompt_tokens / 1_000_000) * self.GEMINI_FLASH_INPUT_COST
        output_cost = (total_usage.completion_tokens / 1_000_000) * self.GEMINI_FLASH_OUTPUT_COST
        
        self.total_cost = input_cost + output_cost
        return self.total_cost


class TokenTracker:
    """Token追踪器 - 仅统计Gemini请求"""
    
    def __init__(self):
        """初始化token追踪器"""
        self.costs = ApiCosts()
        self.session_start = datetime.now()
        
    def track_generation_usage(self, usage_dict: Dict):
        """
        记录生成题目的token使用
        
        Args:
            usage_dict: litellm返回的usage字典
        """
        try:
            prompt_tokens = usage_dict.get('prompt_tokens', 0)
            completion_tokens = usage_dict.get('completion_tokens', 0) 
            total_tokens = usage_dict.get('total_tokens', 0)
            
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
            
            self.costs.generation_usage.add(usage)
            
            logger.info(f"题目生成Token使用: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={total_tokens}")
            
        except Exception as e:
            logger.error(f"统计生成token使用时出错: {e}")
    
    def track_grading_usage(self, usage_dict: Dict):
        """
        记录判题的token使用
        
        Args:
            usage_dict: litellm返回的usage字典
        """
        try:
            prompt_tokens = usage_dict.get('prompt_tokens', 0)
            completion_tokens = usage_dict.get('completion_tokens', 0)
            total_tokens = usage_dict.get('total_tokens', 0)
            
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens, 
                total_tokens=total_tokens
            )
            
            self.costs.grading_usage.add(usage)
            
            logger.info(f"判题Token使用: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={total_tokens}")
            
        except Exception as e:
            logger.error(f"统计判题token使用时出错: {e}")
    
    def get_summary(self) -> Dict:
        """
        获取统计摘要
        
        Returns:
            包含详细统计信息的字典
        """
        cost = self.costs.calculate_cost()
        
        total_usage = TokenUsage()
        total_usage.add(self.costs.generation_usage)
        total_usage.add(self.costs.grading_usage)
        
        return {
            "session_duration": str(datetime.now() - self.session_start),
            "generation": {
                "prompt_tokens": self.costs.generation_usage.prompt_tokens,
                "completion_tokens": self.costs.generation_usage.completion_tokens,
                "total_tokens": self.costs.generation_usage.total_tokens
            },
            "grading": {
                "prompt_tokens": self.costs.grading_usage.prompt_tokens,
                "completion_tokens": self.costs.grading_usage.completion_tokens,
                "total_tokens": self.costs.grading_usage.total_tokens
            },
            "total": {
                "prompt_tokens": total_usage.prompt_tokens,
                "completion_tokens": total_usage.completion_tokens, 
                "total_tokens": total_usage.total_tokens,
                "estimated_cost_usd": round(cost, 4)
            }
        }
    
    def get_stats(self) -> Dict:
        """
        获取统计信息 (为了兼容性)
        
        Returns:
            包含统计信息的字典
        """
        cost = self.costs.calculate_cost()
        
        total_usage = TokenUsage()
        total_usage.add(self.costs.generation_usage)
        total_usage.add(self.costs.grading_usage)
        
        return {
            "generation_tokens": self.costs.generation_usage.total_tokens,
            "answering_tokens": 0,  # 硅基流动API不统计
            "grading_tokens": self.costs.grading_usage.total_tokens,
            "total_tokens": total_usage.total_tokens,
            "total_cost": round(cost, 4),
            "avg_generation_time": 0,  # 待实现
            "avg_answering_time": 0,   # 待实现  
            "avg_grading_time": 0      # 待实现
        }
    
    def log_summary(self):
        """记录统计摘要到日志"""
        summary = self.get_summary()
        
        logger.info("=" * 60)
        logger.info("Gemini API Token使用统计")
        logger.info("=" * 60)
        logger.info(f"会话时长: {summary['session_duration']}")
        logger.info(f"生成题目: {summary['generation']['total_tokens']:,} tokens")
        logger.info(f"自动判题: {summary['grading']['total_tokens']:,} tokens")
        logger.info(f"总计使用: {summary['total']['total_tokens']:,} tokens")
        logger.info(f"估算成本: ${summary['total']['estimated_cost_usd']:.4f} USD")
        logger.info("=" * 60)


# 全局token追踪器实例
token_tracker = TokenTracker()