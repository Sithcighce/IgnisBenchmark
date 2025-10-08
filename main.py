"""
主控程序 - 智能题库生成与评估系统
统一入口：启动WebUI监控面板并运行后台任务
"""

import logging
import threading
import time
from datetime import datetime
from src.utils import load_config, setup_logging, load_env_variables
from src.prompt_manager import PromptManager
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.data_persistence import DataPersistence
from src.models import BenchmarkEntry
from src.token_tracker import token_tracker
from src.siliconflow_api import siliconflow_api


logger = logging.getLogger(__name__)


def run_generation_cycle():
    """运行题目生成循环"""
    # 加载配置
    config = load_config()
    
    # 设置日志
    setup_logging(
        log_level=config.get("log_level", "INFO"),
        log_file=config.get("log_file")
    )
    
    logger.info("=" * 60)
    logger.info("智能题库生成与评估系统启动")
    logger.info("=" * 60)
    
    # 加载环境变量
    try:
        load_env_variables(config["env_file_path"])
    except Exception as e:
        logger.error(f"加载环境变量失败: {e}")
        return
    
    # 检查硅基流动API可用性
    if siliconflow_api.is_available():
        logger.info("硅基流动API (DeepSeek备选方案) 已配置")
    else:
        logger.warning("硅基流动API未配置，DeepSeek备选方案不可用")
    
    # 初始化Prompt管理器
    prompt_manager = PromptManager()
    
    # 初始化数据持久化模块
    data_persistence = DataPersistence(
        benchmark_path=config["benchmark_bank_path"],
        validation_path=config["validation_set_path"]
    )
    
    # 初始化各模块
    question_generator = QuestionGenerator(
        model_name=config["generation_model"],
        batch_size=config.get("batch_size", 10),
        prompt_manager=prompt_manager
    )
    answering_module = AnsweringModule(
        endpoint=config["lm_studio_endpoint"],
        model_name=config["lm_studio_model_name"],
        concurrency=config["lm_studio_concurrency"],
        prompt_manager=prompt_manager
    )
    grading_module = GradingModule(
        model_name=config["grading_model"],
        prompt_manager=prompt_manager
    )
    
    # 显示当前数据集状态
    benchmark_count, validation_count = data_persistence.get_counts()
    logger.info(f"当前Benchmark错题库: {benchmark_count} 道题")
    logger.info(f"当前Validation验证集: {validation_count} 道题")
    
    # 主循环
    try:
        # 步骤1: 从Benchmark错题库随机抽取Few-shot样本
        few_shot_count = config.get("few_shot_count", 3)
        few_shot_samples = data_persistence.get_random_samples(few_shot_count)
        
        if few_shot_samples:
            logger.info(f"从Benchmark错题库抽取了 {len(few_shot_samples)} 道题目作为Few-shot样本")
        else:
            logger.warning("Benchmark错题库为空或样本不足，将不使用Few-shot")
        
        # 步骤2: 生成新题目
        logger.info("-" * 60)
        logger.info("步骤1: 生成新题目")
        logger.info("-" * 60)
        new_questions = question_generator.generate_questions(few_shot_samples)
        
        if not new_questions:
            logger.error("题目生成失败，程序退出")
            return
        
        logger.info(f"成功生成 {len(new_questions)} 道新题目")
        
        # 步骤3: 模型解题
        logger.info("-" * 60)
        logger.info("步骤2: 模型解题")
        logger.info("-" * 60)
        answered_questions = answering_module.answer_questions(new_questions)
        
        # 步骤4: 自动判题
        logger.info("-" * 60)
        logger.info("步骤3: 自动判题")
        logger.info("-" * 60)
        grading_results = grading_module.grade_batch(answered_questions)
        
        # 步骤5: 数据持久化
        logger.info("-" * 60)
        logger.info("步骤4: 数据持久化")
        logger.info("-" * 60)
        
        wrong_count = 0
        correct_count = 0
        
        for question, result in grading_results:
            if not result.is_correct:
                # 保存到Benchmark错题库（包含错误答案）
                benchmark_entry = BenchmarkEntry(
                    question_data=question,
                    model_name=config["lm_studio_model_name"],
                    candidate_answer=question.candidate_answer or "",
                    grading_result=result
                )
                data_persistence.save_to_benchmark(benchmark_entry)
                wrong_count += 1
            else:
                # 保存到Validation验证集
                data_persistence.save_to_validation(question)
                correct_count += 1
        
        logger.info(f"保存了 {wrong_count} 道错题到Benchmark")
        logger.info(f"保存了 {correct_count} 道正确题到Validation")
        
        # 显示最终统计
        final_benchmark, final_validation = data_persistence.get_counts()
        logger.info("=" * 60)
        logger.info(f"运行完成！")
        logger.info(f"Benchmark错题库: {benchmark_count} -> {final_benchmark} (+{final_benchmark - benchmark_count})")
        logger.info(f"Validation验证集: {validation_count} -> {final_validation} (+{final_validation - validation_count})")
        logger.info("=" * 60)
        
        # 显示Token统计摘要
        if config.get("enable_token_tracking", True):
            token_tracker.log_summary()
        
        # 显示一些错题示例
        if wrong_count > 0:
            logger.info("\n错题示例:")
            sample_count = 0
            for question, result in grading_results:
                if not result.is_correct and sample_count < 3:
                    sample_count += 1
                    logger.info(f"\n--- 错题 {sample_count} ---")
                    logger.info(f"问题: {question.question_text[:100]}...")
                    logger.info(f"标答: {question.standard_answer[:100]}...")
                    logger.info(f"模型答案: {question.candidate_answer[:100] if question.candidate_answer else 'N/A'}...")
                    logger.info(f"判题理由: {result.reasoning}")
        
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)


def main():
    """主函数 - 统一入口点"""
    logger.info("启动智能题库生成与评估系统")
    
    # 启动Web监控界面 (在后台线程)
    from web_ui import app
    
    def run_web_ui():
        """运行Web UI"""
        try:
            logger.info("启动Web监控界面 - http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"Web界面启动失败: {e}")
    
    # 在后台线程启动Web UI
    web_thread = threading.Thread(target=run_web_ui, daemon=True)
    web_thread.start()
    
    # 等待Web界面启动
    time.sleep(2)
    
    try:
        # 运行题目生成循环
        run_generation_cycle()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"主程序执行出错: {e}", exc_info=True)


if __name__ == "__main__":
    main()
