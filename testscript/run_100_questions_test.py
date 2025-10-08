#!/usr/bin/env python3
"""
100道题目完整测试脚本
运行10轮次，每轮次生成10道题目，总计100道题目
包含鲁棒的错误处理和重试机制
"""

import sys
import os
import time
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.question_generator import QuestionGenerator  
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.data_persistence import DataPersistence
from src.token_tracker import token_tracker
from src.utils import setup_logging

def main():
    """运行100道题目的完整测试"""
    print("🚀 启动100道题目完整测试...")
    print("=" * 60)
    
    # 初始化配置和日志
    try:
        config = ConfigLoader().load_config()
        logger = setup_logging()
        
        # 初始化各个模块
        question_gen = QuestionGenerator(config)
        answering_module = AnsweringModule(config)
        grading_module = GradingModule(config)
        data_persistence = DataPersistence(config)
        
        print(f"✅ 所有模块初始化成功")
        print(f"📊 初始token统计: {token_tracker.get_summary()}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        traceback.print_exc()
        return False
    
    # 运行10轮次测试
    total_questions = 0
    total_correct = 0
    total_errors = 0
    
    for round_num in range(1, 11):
        print(f"\n🔄 第 {round_num}/10 轮次开始...")
        round_start_time = time.time()
        
        try:
            # 1. 生成10道题目
            print(f"  📝 生成第{round_num}轮的10道题目...")
            questions = question_gen.generate_questions()
            
            if not questions:
                print(f"  ❌ 第{round_num}轮题目生成失败，跳过本轮")
                total_errors += 1
                continue
                
            print(f"  ✅ 成功生成 {len(questions)} 道题目")
            total_questions += len(questions)
            
            # 2. 模型解题
            print(f"  🤖 开始解题...")
            answered_questions = answering_module.answer_questions(questions)
            print(f"  ✅ 解题完成，获得 {len(answered_questions)} 个回答")
            
            # 3. 自动判题
            print(f"  📊 开始判题...")
            round_correct = 0
            for i, (question, answer) in enumerate(answered_questions, 1):
                try:
                    # 将答案设置到question对象中
                    question.candidate_answer = answer
                    grading_result = grading_module.grade_answer(question)
                    
                    # 数据持久化
                    data_persistence.save_result(
                        question, answer, grading_result
                    )
                    
                    if grading_result.is_correct:
                        round_correct += 1
                        total_correct += 1
                    
                    print(f"    题目 {i}: {'✅ 正确' if grading_result.is_correct else '❌ 错误'} (得分: {grading_result.score:.2f})")
                    
                except Exception as e:
                    print(f"    题目 {i}: ⚠️ 判题失败 - {e}")
                    total_errors += 1
            
            # 轮次统计
            round_time = time.time() - round_start_time
            accuracy = (round_correct / len(questions)) * 100 if questions else 0
            
            print(f"  📈 第{round_num}轮完成: {round_correct}/{len(questions)} 正确 ({accuracy:.1f}%), 用时 {round_time:.1f}秒")
            
        except Exception as e:
            print(f"  ❌ 第{round_num}轮发生错误: {e}")
            traceback.print_exc()
            total_errors += 1
            
            # 等待一段时间再继续下一轮
            print(f"  ⏳ 等待30秒后继续下一轮...")
            time.sleep(30)
    
    # 最终统计
    print("\n" + "="*60)
    print("🎯 100道题目测试完成!")
    print(f"📊 总题目数: {total_questions}")
    print(f"✅ 正确回答: {total_correct}")
    print(f"❌ 错误回答: {total_questions - total_correct}")
    print(f"⚠️ 处理错误: {total_errors}")
    
    if total_questions > 0:
        accuracy = (total_correct / total_questions) * 100
        print(f"🎯 总准确率: {accuracy:.2f}%")
    
    # Token统计
    final_stats = token_tracker.get_summary()
    print(f"💰 Token统计:")
    print(f"  生成: {final_stats['generation']['total_tokens']} tokens (${final_stats['generation']['total_cost']:.4f})")
    print(f"  判题: {final_stats['grading']['total_tokens']} tokens (${final_stats['grading']['total_cost']:.4f})")
    print(f"  总计: {final_stats['total']['total_tokens']} tokens (${final_stats['total']['total_cost']:.4f})")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 测试成功完成!")
        else:
            print("\n💥 测试失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 未捕获的错误: {e}")
        traceback.print_exc()
        sys.exit(1)