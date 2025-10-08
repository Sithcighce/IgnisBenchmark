#!/usr/bin/env python3
"""
100题目批量测试脚本
运行10轮次，每轮次生成10题，总共100题
测试系统的鲁棒性和稳定性
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule  
from src.grading_module import GradingModule
from src.data_persistence import DataPersistence
from src.prompt_manager import PromptManager
from src.token_tracker import token_tracker

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_100_questions.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_single_round(round_num: int, config: dict) -> dict:
    """
    运行单轮测试（10题）
    
    Args:
        round_num: 轮次编号
        config: 配置字典
    
    Returns:
        本轮统计结果
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 开始第 {round_num} 轮测试 (生成10题)")
    
    round_stats = {
        'round': round_num,
        'questions_generated': 0,
        'questions_answered': 0,  
        'questions_graded': 0,
        'correct_answers': 0,
        'errors': [],
        'start_time': time.time()
    }
    
    try:
        # 1. 初始化模块
        prompt_manager = PromptManager()
        data_persistence = DataPersistence(
            config['benchmark_bank_path'],
            config['validation_set_path']
        )
        
        generator = QuestionGenerator(
            model_name=config['generation_model'],
            batch_size=config['batch_size'],
            prompt_manager=prompt_manager
        )
        
        answerer = AnsweringModule(
            endpoint=config['lm_studio_endpoint'],
            model_name=config['lm_studio_model_name'], 
            concurrency=config['lm_studio_concurrency']
        )
        
        grader = GradingModule(
            model_name=config['grading_model'],
            prompt_manager=prompt_manager
        )
        
        # 2. 生成题目
        logger.info(f"第 {round_num} 轮: 开始生成题目...")
        few_shot_examples = data_persistence.get_random_samples(config['few_shot_count'])
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                questions = generator.generate_questions(few_shot_examples)
                if questions:
                    round_stats['questions_generated'] = len(questions)
                    logger.info(f"第 {round_num} 轮: 成功生成 {len(questions)} 道题目")
                    break
                else:
                    logger.warning(f"第 {round_num} 轮: 生成题目失败，尝试 {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                logger.error(f"第 {round_num} 轮: 生成题目异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                round_stats['errors'].append(f"生成失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"第 {round_num} 轮: 生成题目彻底失败，跳过本轮")
                    return round_stats
        
        if not questions:
            logger.error(f"第 {round_num} 轮: 无法生成题目，跳过本轮")
            return round_stats
        
        # 3. 解答题目
        logger.info(f"第 {round_num} 轮: 开始解答题目...")
        try:
            answered_questions = answerer.answer_questions(questions)
            round_stats['questions_answered'] = len([q for q in answered_questions if q.candidate_answer and not q.candidate_answer.startswith("[ERROR]")])
            logger.info(f"第 {round_num} 轮: 成功解答 {round_stats['questions_answered']}/{len(questions)} 道题目")
        except Exception as e:
            logger.error(f"第 {round_num} 轮: 解答题目失败: {e}")
            round_stats['errors'].append(f"解答失败: {str(e)}")
            # 即使解答失败，也继续判题（标记为解题失败）
            answered_questions = questions
            for q in answered_questions:
                if not hasattr(q, 'candidate_answer') or not q.candidate_answer:
                    q.candidate_answer = "[ERROR] 解答模块异常"
        
        # 4. 判题
        logger.info(f"第 {round_num} 轮: 开始判题...")
        try:
            grading_results = grader.grade_batch(answered_questions)
            round_stats['questions_graded'] = len(grading_results)
            round_stats['correct_answers'] = sum(1 for _, result in grading_results if result.is_correct)
            logger.info(f"第 {round_num} 轮: 判题完成 {round_stats['correct_answers']}/{len(grading_results)} 正确")
        except Exception as e:
            logger.error(f"第 {round_num} 轮: 判题失败: {e}")
            round_stats['errors'].append(f"判题失败: {str(e)}")
            return round_stats
        
        # 5. 数据持久化
        logger.info(f"第 {round_num} 轮: 开始数据持久化...")
        try:
            benchmark_count = 0
            validation_count = 0
            
            # 遍历判题结果进行分类保存
            for (question, answer), grading_result in zip(answered_questions, grading_results):
                if grading_result.is_correct:
                    data_persistence.save_to_validation(question)
                    validation_count += 1
                else:
                    from src.models import BenchmarkEntry
                    entry = BenchmarkEntry(
                        question_data=question,
                        failed_attempt={
                            "model_name": config['lm_studio_model_name'],
                            "candidate_answer": answer,
                            "grading_result": grading_result.__dict__
                        }
                    )
                    data_persistence.save_to_benchmark(entry)
                    benchmark_count += 1
                    
            logger.info(f"第 {round_num} 轮: 保存到benchmark: {benchmark_count}, 保存到validation: {validation_count}")
        except Exception as e:
            logger.error(f"第 {round_num} 轮: 数据持久化失败: {e}")
            round_stats['errors'].append(f"数据持久化失败: {str(e)}")
        
        round_stats['duration'] = time.time() - round_stats['start_time']
        logger.info(f"✅ 第 {round_num} 轮测试完成，耗时 {round_stats['duration']:.1f}秒")
        
    except Exception as e:
        logger.error(f"❌ 第 {round_num} 轮测试出现严重错误: {e}")
        round_stats['errors'].append(f"严重错误: {str(e)}")
        round_stats['duration'] = time.time() - round_stats['start_time']
    
    return round_stats

def print_progress_summary(all_stats: list):
    """打印进度总结"""
    logger = logging.getLogger(__name__)
    
    total_generated = sum(s['questions_generated'] for s in all_stats)
    total_answered = sum(s['questions_answered'] for s in all_stats)
    total_graded = sum(s['questions_graded'] for s in all_stats) 
    total_correct = sum(s['correct_answers'] for s in all_stats)
    total_errors = sum(len(s['errors']) for s in all_stats)
    total_time = sum(s.get('duration', 0) for s in all_stats)
    
    logger.info("=" * 60)
    logger.info("📊 当前进度总结:")
    logger.info(f"   轮次: {len(all_stats)}/10")
    logger.info(f"   题目生成: {total_generated}")
    logger.info(f"   题目解答: {total_answered}")
    logger.info(f"   题目判题: {total_graded}")
    logger.info(f"   正确答案: {total_correct}")
    logger.info(f"   错误次数: {total_errors}")
    logger.info(f"   总用时: {total_time:.1f}秒")
    logger.info(f"   Token统计: {token_tracker.get_summary()}")
    logger.info("=" * 60)

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🎯 开始100题目批量测试 (10轮次 × 10题/轮)")
    start_time = time.time()
    
    # 加载配置
    try:
        config = load_config()
        logger.info("✅ 配置加载成功")
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        return 1
    
    # 获取初始token统计
    initial_stats = token_tracker.get_summary()
    logger.info("🔄 Token统计已重置")
    
    all_stats = []
    
    # 运行10轮测试
    for round_num in range(1, 11):
        try:
            round_stats = run_single_round(round_num, config)
            all_stats.append(round_stats)
            
            # 每3轮打印一次进度
            if round_num % 3 == 0 or round_num == 10:
                print_progress_summary(all_stats)
            
            # 轮次间短暂休息，避免API压力过大
            if round_num < 10:
                time.sleep(2)
                
        except KeyboardInterrupt:
            logger.warning(f"⚠️  用户中断测试，已完成 {len(all_stats)} 轮")
            break
        except Exception as e:
            logger.error(f"❌ 第 {round_num} 轮出现意外错误: {e}")
            # 记录错误但继续下一轮
            all_stats.append({
                'round': round_num,
                'questions_generated': 0,
                'questions_answered': 0,
                'questions_graded': 0, 
                'correct_answers': 0,
                'errors': [f"意外错误: {str(e)}"],
                'duration': 0
            })
    
    # 最终统计
    total_time = time.time() - start_time
    
    logger.info("🏁 100题目批量测试完成！")
    logger.info("=" * 80)
    logger.info("📈 最终统计报告:")
    
    total_generated = sum(s['questions_generated'] for s in all_stats)
    total_answered = sum(s['questions_answered'] for s in all_stats)
    total_graded = sum(s['questions_graded'] for s in all_stats)
    total_correct = sum(s['correct_answers'] for s in all_stats)
    total_errors = sum(len(s['errors']) for s in all_stats)
    
    logger.info(f"   完成轮次: {len(all_stats)}/10")
    logger.info(f"   题目生成: {total_generated}/100 ({total_generated/100*100:.1f}%)")
    logger.info(f"   题目解答: {total_answered} ({total_answered/max(total_generated,1)*100:.1f}%)")
    logger.info(f"   题目判题: {total_graded} ({total_graded/max(total_generated,1)*100:.1f}%)")
    logger.info(f"   正确率: {total_correct}/{total_graded} ({total_correct/max(total_graded,1)*100:.1f}%)" if total_graded > 0 else "   正确率: N/A")
    logger.info(f"   总错误数: {total_errors}")
    logger.info(f"   总耗时: {total_time:.1f}秒 ({total_time/60:.1f}分钟)")
    
    # Token统计
    token_summary = token_tracker.get_summary()
    logger.info(f"   Token统计: {token_summary}")
    
    # 错误详情
    if total_errors > 0:
        logger.info("\n❌ 错误详情:")
        for i, stats in enumerate(all_stats, 1):
            if stats['errors']:
                logger.info(f"   第{i}轮: {'; '.join(stats['errors'])}")
    
    logger.info("=" * 80)
    
    return 0 if total_generated >= 50 else 1  # 至少生成50题才算成功

if __name__ == "__main__":
    exit(main())