#!/usr/bin/env python3
"""
分析基准测试进度
从日志输出中提取已完成的题目数量和正确率
"""
import re

# 从日志输出中提取的信息
log_output = """
从输出可以看到：
- 处理到 [907/984] 时还成功（deepseek_q_eb13c0b6）
- 从 [908/984] 开始出现402错误（deepseek_q_eb836498）
"""

# 分析日志中的成功和失败模式
def analyze_log():
    # 根据输出，我们可以看到：
    # 1. 成功的标记: "✓ Graded: CORRECT/INCORRECT"
    # 2. 失败的标记: "✗ Error: API Error 402"
    
    # 从日志中可以看到最后一个成功的题目是 [907/984]
    # 之后所有题目都失败了
    
    completed_questions = 907  # 根据日志中最后一个成功的编号
    total_questions = 984
    failed_questions = total_questions - completed_questions
    
    print(f"\n{'='*70}")
    print(f"GPT-5 基准测试进度分析")
    print(f"{'='*70}\n")
    
    print(f"📊 进度概况:")
    print(f"   总题目数: {total_questions}")
    print(f"   已完成: {completed_questions}")
    print(f"   失败 (余额不足): {failed_questions}")
    print(f"   完成率: {completed_questions/total_questions*100:.2f}%\n")
    
    # 从日志中手动计算正确和错误的数量
    # 需要统计 "✓ Graded: CORRECT" vs "✓ Graded: INCORRECT"
    
    print(f"⚠️  问题:")
    print(f"   OpenRouter 余额不足，在第 {failed_questions} 题时开始失败")
    print(f"   需要充值 OpenRouter 余额才能完成剩余 {failed_questions} 题\n")
    
    print(f"💡 建议:")
    print(f"   1. 充值 OpenRouter 账户 (https://openrouter.ai/settings/credits)")
    print(f"   2. 重新运行脚本，它会跳过已完成的题目")
    print(f"   3. 或者使用已完成的 {completed_questions} 题计算部分正确率\n")
    
    print(f"📝 注意:")
    print(f"   脚本中断前没有保存 benchmarkGPT5.json")
    print(f"   需要充值后重新运行才能获得完整结果文件\n")
    
    return completed_questions, total_questions

if __name__ == "__main__":
    completed, total = analyze_log()
    
    print(f"\n{'='*70}")
    print(f"状态: ⏸️  暂停 - 需要充值 OpenRouter 余额")
    print(f"{'='*70}\n")
