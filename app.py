#!/usr/bin/env python3
"""
智能题库生成与评估系统 - 新版本
实现每轮10题，并发解题+并发判题，判完就写入
"""
import sys
import os
import threading

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    pass  # dotenv not installed
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import logging
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.data_persistence import DataPersistence
from src.token_tracker import token_tracker
from src.utils import setup_logging

class QuestionGeneratorGUI:
    """题目生成系统图形界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("智能题库生成与评估系统 v2.0 - 并发优化版")
        self.root.geometry("1200x800")
        
        # 加载配置
        self.config = load_config()
        
        # 初始化logger
        setup_logging(log_file=self.config.get('log_file', 'logs/system.log'))
        self.logger = logging.getLogger('QuestionGeneratorGUI')
        
        # 状态变量
        self.is_running = False
        self.current_round = 0
        self.total_questions = 0
        self.total_correct = 0
        
        # 初始化界面
        self.setup_ui()
        
        # 启动定期更新
        self.periodic_update()
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="智能题库生成与评估系统 v2.0", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 控制区域
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 轮次设置
        ttk.Label(control_frame, text="运行轮次:").grid(row=0, column=0, padx=(0, 5))
        self.rounds_var = tk.StringVar(value="10")
        rounds_spinbox = ttk.Spinbox(control_frame, from_=1, to=100, width=10, 
                                   textvariable=self.rounds_var)
        rounds_spinbox.grid(row=0, column=1, padx=(0, 20))
        
        # 每轮题目数设置
        ttk.Label(control_frame, text="每轮题目数:").grid(row=0, column=2, padx=(0, 5))
        self.batch_var = tk.StringVar(value="10")
        batch_spinbox = ttk.Spinbox(control_frame, from_=1, to=20, width=10,
                                  textvariable=self.batch_var)
        batch_spinbox.grid(row=0, column=3, padx=(0, 20))
        
        # 控制按钮
        self.start_button = ttk.Button(control_frame, text="开始生成", 
                                     command=self.start_generation)
        self.start_button.grid(row=0, column=4, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止", 
                                    command=self.stop_generation, state='disabled')
        self.stop_button.grid(row=0, column=5, padx=(0, 10))
        
        clear_button = ttk.Button(control_frame, text="清空日志", 
                                command=self.clear_log)
        clear_button.grid(row=0, column=6)
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_frame, text="统计信息", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, width=30, height=20, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, 
                                      command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="系统日志", padding="10")
        log_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_text = scrolledtext.ScrolledText(log_frame, width=60, height=20, 
                                                   wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 初始化统计信息
        self.update_stats()
        
    def log_message(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 根据级别设置颜色
        color_map = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange", 
            "ERROR": "red"
        }
        
        formatted_message = f"[{timestamp}] {message}\n"
        
        # 在UI线程中安全地更新文本
        def update_text():
            self.status_text.insert(tk.END, formatted_message)
            self.status_text.see(tk.END)
            
        if threading.current_thread() == threading.main_thread():
            update_text()
        else:
            self.root.after(0, update_text)
        
        # 同时记录到日志文件
        if hasattr(self, 'logger'):
            getattr(self.logger, level.lower(), self.logger.info)(message)
    
    def update_stats(self):
        """更新统计信息"""
        try:
            # 获取数据库统计
            data_persistence = DataPersistence(
                self.config['benchmark_bank_path'],
                self.config['validation_set_path']
            )
            benchmark_count, validation_count = data_persistence.get_counts()
            
            # 获取token统计
            stats = token_tracker.get_stats()
            
            # 计算准确率
            total_processed = self.total_questions
            accuracy = (self.total_correct / total_processed * 100) if total_processed > 0 else 0
            
            stats_info = f"""📊 实时统计
            
🎯 当前进度:
  轮次: {self.current_round}
  本次生成: {self.total_questions} 题
  本次正确: {self.total_correct} 题
  准确率: {accuracy:.1f}%

📚 数据库状态:
  错题库: {benchmark_count} 题
  验证集: {validation_count} 题
  总题库: {benchmark_count + validation_count} 题

💰 Token使用:
  生成Token: {stats.get('generation_tokens', 0):,}
  解题Token: {stats.get('answering_tokens', 0):,}
  判题Token: {stats.get('grading_tokens', 0):,}
  总Token: {stats.get('total_tokens', 0):,}
  预估成本: ${stats.get('total_cost', 0):.4f}

⏱️ 性能指标:
  平均生成时间: {stats.get('avg_generation_time', 0):.1f}s
  平均解题时间: {stats.get('avg_answering_time', 0):.1f}s
  平均判题时间: {stats.get('avg_grading_time', 0):.1f}s
"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_info)
            
        except Exception as e:
            self.log_message(f"更新统计信息失败: {e}", "ERROR")
    
    def start_generation(self):
        """启动生成"""
        if self.is_running:
            return
            
        try:
            rounds = int(self.rounds_var.get())
            batch_size = int(self.batch_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        self.is_running = True
        self.current_round = 0
        self.total_questions = 0
        self.total_correct = 0
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        self.log_message("=" * 60)
        self.log_message(f"开始新的生成任务: {rounds} 轮 × {batch_size} 题/轮")
        self.log_message("=" * 60)
        
        # 在新线程中运行生成
        thread = threading.Thread(target=self.run_generation_loop, 
                                args=(rounds, batch_size))
        thread.daemon = True
        thread.start()
    
    def run_generation_loop(self, rounds, batch_size):
        """运行生成循环"""
        try:
            # 初始化模块
            self.log_message("初始化系统模块...")
            
            question_gen = QuestionGenerator(
                model_name=self.config['generation_model'],
                batch_size=batch_size
            )
            
            answering_module = AnsweringModule(
                api_base=self.config['siliconflow_base_url'],
                model_name=self.config['siliconflow_answering_model'],
                concurrency=10  # 10个并发解题
            )
            
            grading_module = GradingModule(
                model_name=self.config['grading_model']
            )
            
            data_persistence = DataPersistence(
                self.config['benchmark_bank_path'],
                self.config['validation_set_path']
            )
            
            self.log_message("✅ 所有模块初始化完成")
            
            # 开始轮次循环
            for round_num in range(1, rounds + 1):
                if not self.is_running:
                    self.log_message("用户停止了生成过程", "WARNING")
                    break
                    
                self.current_round = round_num
                round_start_time = time.time()
                
                self.log_message(f"\n🔄 第 {round_num}/{rounds} 轮开始")
                
                # 步骤1: 生成题目
                self.log_message(f"  📝 生成 {batch_size} 道题目...")
                # 获取few-shot示例（如果有的话）
                few_shot_examples = []
                try:
                    few_shot_examples = data_persistence.get_random_samples(3)
                except:
                    pass  # 如果获取失败，使用空列表
                questions = question_gen.generate_questions(few_shot_examples)
                
                if not questions:
                    self.log_message(f"  ❌ 第 {round_num} 轮生成失败", "ERROR")
                    continue
                
                self.log_message(f"  ✅ 成功生成 {len(questions)} 道题目")
                
                # 步骤2: 并发解题和判题
                self.log_message(f"  🧠 开始并发解题 (10线程)...")
                round_correct = 0
                
                # 使用ThreadPoolExecutor进行并发处理
                with ThreadPoolExecutor(max_workers=10) as executor:
                    # 提交所有解题任务
                    answer_futures = {
                        executor.submit(self.solve_and_grade_question, 
                                      question, answering_module, grading_module, 
                                      data_persistence): question 
                        for question in questions
                    }
                    
                    # 处理完成的任务
                    completed_count = 0
                    for future in as_completed(answer_futures):
                        completed_count += 1
                        try:
                            is_correct = future.result()
                            if is_correct:
                                round_correct += 1
                                self.total_correct += 1
                            
                            # 更新进度
                            self.log_message(f"    ✓ 题目 {completed_count}/{len(questions)} 完成")
                            
                        except Exception as e:
                            self.log_message(f"    ❌ 题目 {completed_count} 处理失败: {e}", "ERROR")
                
                # 轮次统计
                self.total_questions += len(questions)
                round_time = time.time() - round_start_time
                accuracy = (round_correct / len(questions)) * 100
                
                self.log_message(f"  📊 第 {round_num} 轮完成: {round_correct}/{len(questions)} 正确 "
                               f"({accuracy:.1f}%), 用时 {round_time:.1f}秒", "SUCCESS")
                
                # 更新统计信息
                self.root.after(0, self.update_stats)
                
                # 短暂休息
                if round_num < rounds and self.is_running:
                    time.sleep(2)
            
            # 任务完成
            if self.is_running:
                final_accuracy = (self.total_correct / self.total_questions * 100) if self.total_questions > 0 else 0
                self.log_message("=" * 60)
                self.log_message(f"🎉 所有任务完成! 总计: {self.total_correct}/{self.total_questions} "
                               f"正确 ({final_accuracy:.1f}%)", "SUCCESS")
                self.log_message("=" * 60)
            
        except Exception as e:
            self.log_message(f"生成过程出错: {e}", "ERROR")
            
        finally:
            # 恢复界面状态
            self.root.after(0, lambda: [
                setattr(self, 'is_running', False),
                self.start_button.config(state='normal'),
                self.stop_button.config(state='disabled'),
                self.update_stats()
            ])
    
    def solve_and_grade_question(self, question, answering_module, grading_module, data_persistence):
        """解题并判题单个问题"""
        try:
            # 解题
            answer = answering_module.answer_question(question)
            question.candidate_answer = answer
            
            # 判题
            grading_result = grading_module.grade_answer(question)
            
            # 立即保存结果
            if grading_result.is_correct:
                data_persistence.save_to_validation(question)
            else:
                from src.models import BenchmarkEntry
                entry = BenchmarkEntry(
                    question_data=question,
                    model_name=self.config['siliconflow_answering_model'],
                    candidate_answer=answer,
                    grading_result=grading_result
                )
                data_persistence.save_to_benchmark(entry)
            
            return grading_result.is_correct
            
        except Exception as e:
            self.log_message(f"处理问题时出错: {e}", "ERROR")
            return False
    
    def stop_generation(self):
        """停止生成"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.log_message("用户停止了生成过程", "WARNING")
    
    def clear_log(self):
        """清空日志"""
        self.status_text.delete(1.0, tk.END)
    
    def periodic_update(self):
        """定期更新界面"""
        if self.is_running:
            self.update_stats()
        self.root.after(5000, self.periodic_update)  # 每5秒更新一次
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = QuestionGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main()