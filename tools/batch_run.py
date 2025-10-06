"""
批量运行脚本 - 自动化运行多个题目生成、解答、判题周期
"""
import sys
import time
from pathlib import Path
from typing import Dict, Any

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_loader import load_config
from prompt_manager import PromptManager
from question_generator import QuestionGenerator
from answering_module import AnsweringModule
from grading_module import GradingModule
from data_persistence import DataPersistence
from models import BenchmarkEntry


def run_batch(cycles: int, questions_per_cycle: int) -> Dict[str, Any]:
    """
    运行批量生成周期
    
    Args:
        cycles: 运行周期数
        questions_per_cycle: 每个周期生成的题目数量
    
    Returns:
        统计信息字典
    """
    # 加载配置
    config = load_config()
    
    # 初始化模块
    prompt_manager = PromptManager(config["prompts_dir"])
    generator = QuestionGenerator(config, prompt_manager)
    answerer = AnsweringModule(config, prompt_manager)
    grader = GradingModule(config, prompt_manager)
    
    # 初始化数据持久化
    data_persistence = DataPersistence(
        benchmark_path=config["benchmark_bank_path"],
        validation_path=config["validation_set_path"]
    )
    
    # 统计信息
    stats = {
        "total_generated": 0,
        "total_benchmark": 0,
        "total_validation": 0,
        "cycles_completed": 0,
        "start_time": time.time(),
        "errors": []
    }
    
    print(f"\n{'='*60}")
    print(f"开始批量运行: {cycles} 个周期, 每周期 {questions_per_cycle} 题")
    print(f"{'='*60}\n")
    
    for cycle in range(1, cycles + 1):
        print(f"\n--- 周期 {cycle}/{cycles} ---")
        cycle_start = time.time()
        
        try:
            # 1. 生成题目
            print(f"  生成 {questions_per_cycle} 个题目...")
            questions = generator.generate_questions(
                num_questions=questions_per_cycle,
                topic_hint=config.get("default_topic", "物理"),
                difficulty_range=(3, 5)
            )
            
            if not questions:
                print("  ⚠ 未生成任何题目，跳过本周期")
                stats["errors"].append(f"Cycle {cycle}: No questions generated")
                continue
            
            print(f"  ✓ 生成了 {len(questions)} 个题目")
            stats["total_generated"] += len(questions)
            
            # 2. 解答题目
            print(f"  解答题目...")
            answers = []
            for i, q in enumerate(questions):
                answer = answerer.answer_question(q)
                answers.append(answer)
                print(f"    题目 {i+1}: {answer[:50]}...")
            
            # 3. 判题
            print(f"  判题...")
            grading_results = grader.grade_batch(questions, answers)
            
            # 4. 分类保存
            benchmark_count = 0
            validation_count = 0
            
            for question, result in grading_results:
                if not result.is_correct:
                    # 保存到错题库
                    benchmark_entry = BenchmarkEntry(
                        question_data=question,
                        failed_attempt={
                            "answer": result.student_answer,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        },
                        grading_result=result
                    )
                    data_persistence.save_to_benchmark(benchmark_entry)
                    benchmark_count += 1
                else:
                    # 保存到验证集
                    data_persistence.save_to_validation(question)
                    validation_count += 1
            
            stats["total_benchmark"] += benchmark_count
            stats["total_validation"] += validation_count
            stats["cycles_completed"] += 1
            
            cycle_time = time.time() - cycle_start
            print(f"  ✓ 周期完成 ({cycle_time:.1f}秒)")
            print(f"    错题库: +{benchmark_count}, 验证集: +{validation_count}")
            
        except Exception as e:
            error_msg = f"Cycle {cycle} error: {str(e)}"
            stats["errors"].append(error_msg)
            print(f"  ✗ 错误: {e}")
            continue
    
    # 总结统计
    total_time = time.time() - stats["start_time"]
    stats["total_time"] = total_time
    
    print(f"\n{'='*60}")
    print(f"批量运行完成!")
    print(f"{'='*60}")
    print(f"总用时: {total_time:.1f}秒")
    print(f"完成周期: {stats['cycles_completed']}/{cycles}")
    print(f"生成题目: {stats['total_generated']}")
    print(f"错题库增加: {stats['total_benchmark']}")
    print(f"验证集增加: {stats['total_validation']}")
    
    if stats["errors"]:
        print(f"\n错误数: {len(stats['errors'])}")
        for err in stats["errors"]:
            print(f"  - {err}")
    
    # 显示最终数据库状态
    counts = data_persistence.get_counts()
    print(f"\n当前数据库状态:")
    print(f"  错题库总数: {counts['benchmark']}")
    print(f"  验证集总数: {counts['validation']}")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量运行题目生成系统")
    parser.add_argument("--cycles", type=int, default=5, help="运行周期数 (默认: 5)")
    parser.add_argument("--questions", type=int, default=3, help="每周期生成题目数 (默认: 3)")
    
    args = parser.parse_args()
    
    run_batch(cycles=args.cycles, questions_per_cycle=args.questions)
