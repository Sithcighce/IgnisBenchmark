"""
测试token统计功能
"""

import os
import sys
sys.path.append('c:/Users/13031/Desktop/workspace/questions')

from src.token_tracker import token_tracker

# 模拟一些token使用
fake_usage = {
    'prompt_tokens': 100,
    'completion_tokens': 50,
    'total_tokens': 150
}

print("添加token统计前:", token_tracker.get_summary())

# 添加生成token使用
token_tracker.track_generation_usage(fake_usage)
print("添加生成token后:", token_tracker.get_summary())

# 添加判题token使用
token_tracker.track_grading_usage(fake_usage)
print("添加判题token后:", token_tracker.get_summary())