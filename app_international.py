#!/usr/bin/env python3
"""
Intelligent Question Bank Generation & Assessment System - International Version
智能题库生成与评估系统 - 国际版
Implements concurrent question generation, solving, and grading with multi-language support
实现并发题目生成、解题、评分，支持多语言界面
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

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config_loader import load_config
from src.question_generator import QuestionGenerator
from src.answering_module import AnsweringModule
from src.grading_module import GradingModule
from src.data_persistence import DataPersistence
from src.token_tracker import token_tracker
from src.utils import setup_logging
from src.i18n import i18n

class InternationalQuestionGeneratorGUI:
    """International Question Generator System GUI with multi-language support"""
    
    def __init__(self, language='en'):
        self.root = tk.Tk()
        
        # Initialize internationalization
        i18n.set_language(language)
        self.current_language = language
        
        # Set window properties
        self.setup_window()
        
        # Load configuration
        self.config = load_config()
        
        # Initialize logger
        setup_logging(log_file=self.config.get('log_file', 'logs/system.log'))
        self.logger = logging.getLogger('InternationalQuestionGeneratorGUI')
        
        # State variables
        self.is_running = False
        self.current_round = 0
        self.total_questions = 0
        self.total_correct = 0
        
        # UI components (will be set in setup_ui)
        self.title_label = None
        self.control_frame = None
        self.stats_frame = None
        self.log_frame = None
        self.stats_text = None
        self.status_text = None
        self.start_button = None
        self.stop_button = None
        self.language_button = None
        
        # Initialize UI
        self.setup_ui()
        
        # Start periodic updates
        self.periodic_update()
    
    def setup_window(self):
        """Setup main window properties"""
        title = f"{i18n.get_text('window_title')} - {i18n.get_text('window_subtitle')}"
        self.root.title(title)
        self.root.geometry("1200x800")
        
        # Set minimum size
        self.root.minsize(800, 600)
    
    def setup_ui(self):
        """Setup user interface with current language"""
        # Clear existing widgets if any
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title with language switcher
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)
        
        self.title_label = ttk.Label(title_frame, text=i18n.get_text('window_title'), 
                                   font=('Arial', 16, 'bold'))
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Language switcher button
        self.language_button = ttk.Button(title_frame, text=self.get_language_display(), 
                                        command=self.toggle_language, width=10)
        self.language_button.grid(row=0, column=1, sticky=tk.E)
        
        # Control area
        self.control_frame = ttk.LabelFrame(main_frame, text=i18n.get_text('control_panel'), padding="10")
        self.control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Rounds setting
        ttk.Label(self.control_frame, text=i18n.get_text('rounds_label')).grid(row=0, column=0, padx=(0, 5))
        self.rounds_var = tk.StringVar(value="10")
        rounds_spinbox = ttk.Spinbox(self.control_frame, from_=1, to=100, width=10, 
                                   textvariable=self.rounds_var)
        rounds_spinbox.grid(row=0, column=1, padx=(0, 20))
        
        # Batch size setting
        ttk.Label(self.control_frame, text=i18n.get_text('batch_size_label')).grid(row=0, column=2, padx=(0, 5))
        self.batch_var = tk.StringVar(value="10")
        batch_spinbox = ttk.Spinbox(self.control_frame, from_=1, to=20, width=10,
                                  textvariable=self.batch_var)
        batch_spinbox.grid(row=0, column=3, padx=(0, 20))
        
        # Control buttons
        self.start_button = ttk.Button(self.control_frame, text=i18n.get_text('start_button'), 
                                     command=self.start_generation)
        self.start_button.grid(row=0, column=4, padx=(0, 10))
        
        self.stop_button = ttk.Button(self.control_frame, text=i18n.get_text('stop_button'), 
                                    command=self.stop_generation, state='disabled')
        self.stop_button.grid(row=0, column=5, padx=(0, 10))
        
        clear_button = ttk.Button(self.control_frame, text=i18n.get_text('clear_log_button'), 
                                command=self.clear_log)
        clear_button.grid(row=0, column=6)
        
        # Statistics area
        self.stats_frame = ttk.LabelFrame(main_frame, text=i18n.get_text('stats_panel'), padding="10")
        self.stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.stats_text = tk.Text(self.stats_frame, width=30, height=20, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, 
                                      command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.rowconfigure(0, weight=1)
        
        # Log area
        self.log_frame = ttk.LabelFrame(main_frame, text=i18n.get_text('log_panel'), padding="10")
        self.log_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_text = scrolledtext.ScrolledText(self.log_frame, width=60, height=20, 
                                                   wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        # Initialize statistics
        self.update_stats()
    
    def get_language_display(self):
        """Get display text for language button"""
        languages = i18n.get_available_languages()
        if self.current_language == 'zh':
            return "English"
        else:
            return "中文"
    
    def toggle_language(self):
        """Toggle between languages"""
        if self.current_language == 'en':
            new_language = 'zh'
        else:
            new_language = 'en'
        
        # Update language
        self.current_language = new_language
        i18n.set_language(new_language)
        
        # Update window title
        title = f"{i18n.get_text('window_title')} - {i18n.get_text('window_subtitle')}"
        self.root.title(title)
        
        # Rebuild UI with new language
        self.setup_ui()
        
        # Log the language change
        self.log_message(f"Language switched to {i18n.get_available_languages()[new_language]}", "INFO")
    
    def log_message(self, message, level="INFO"):
        """Add log message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color mapping for different log levels
        color_map = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange", 
            "ERROR": "red"
        }
        
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Safely update text in UI thread
        def update_text():
            if hasattr(self, 'status_text') and self.status_text:
                self.status_text.insert(tk.END, formatted_message)
                self.status_text.see(tk.END)
            
        if threading.current_thread() == threading.main_thread():
            update_text()
        else:
            self.root.after(0, update_text)
        
        # Also log to file
        if hasattr(self, 'logger'):
            getattr(self.logger, level.lower(), self.logger.info)(message)
    
    def update_stats(self):
        """Update statistics display"""
        try:
            # Get database statistics
            data_persistence = DataPersistence(
                self.config['benchmark_bank_path'],
                self.config['validation_set_path']
            )
            benchmark_count, validation_count = data_persistence.get_counts()
            
            # Get token statistics
            stats = token_tracker.get_stats()
            
            # Format stats text using i18n
            stats_text = i18n.format_stats_text(
                self.current_round,
                self.total_questions, 
                self.total_correct,
                benchmark_count,
                validation_count,
                stats
            )
            
            if hasattr(self, 'stats_text') and self.stats_text:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.log_message(f"{i18n.get_text('stats_update_error')}: {e}", "ERROR")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_message(i18n.get_text('clearing_log'))
        if hasattr(self, 'status_text') and self.status_text:
            self.status_text.delete(1.0, tk.END)
    
    def start_generation(self):
        """Start question generation process"""
        if self.is_running:
            return
            
        try:
            rounds = int(self.rounds_var.get())
            batch_size = int(self.batch_var.get())
            
            if rounds <= 0:
                messagebox.showerror("Error", i18n.get_text('invalid_rounds'))
                return
                
            if batch_size <= 0:
                messagebox.showerror("Error", i18n.get_text('invalid_batch_size'))
                return
                
        except ValueError:
            messagebox.showerror("Error", f"{i18n.get_text('invalid_rounds')} / {i18n.get_text('invalid_batch_size')}")
            return
        
        self.is_running = True
        self.current_round = 0
        self.total_questions = 0
        self.total_correct = 0
        
        # Update button states
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        
        self.log_message(i18n.get_text('starting_generation'))
        
        # Start generation in a separate thread
        self.generation_thread = threading.Thread(
            target=self.generation_worker, 
            args=(rounds, batch_size)
        )
        self.generation_thread.start()
    
    def stop_generation(self):
        """Stop the generation process"""
        if not self.is_running:
            return
            
        self.log_message(i18n.get_text('stopping_generation'))
        self.is_running = False
        
        # Update button states
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
    
    def generation_worker(self, total_rounds, batch_size):
        """Worker thread for question generation"""
        try:
            # Initialize modules
            question_generator = QuestionGenerator(self.config)
            answering_module = AnsweringModule(self.config)
            grading_module = GradingModule(self.config)
            data_persistence = DataPersistence(
                self.config['benchmark_bank_path'],
                self.config['validation_set_path']
            )
            
            for round_num in range(1, total_rounds + 1):
                if not self.is_running:
                    break
                    
                self.current_round = round_num
                round_start_time = time.time()
                
                # Generate questions for this round
                questions = []
                with ThreadPoolExecutor(max_workers=self.config.get('generation_workers', 3)) as executor:
                    futures = []
                    for _ in range(batch_size):
                        if not self.is_running:
                            break
                        future = executor.submit(question_generator.generate_question)
                        futures.append(future)
                    
                    for future in as_completed(futures):
                        if not self.is_running:
                            break
                        try:
                            question = future.result(timeout=120)  # 2 minute timeout
                            if question:
                                questions.append(question)
                        except Exception as e:
                            self.log_message(f"Question generation failed: {e}", "ERROR")
                
                if not self.is_running or not questions:
                    continue
                
                # Process questions concurrently
                with ThreadPoolExecutor(max_workers=self.config.get('processing_workers', 5)) as executor:
                    # Submit answering tasks
                    # AnsweringModule 提供 answer_question 接口，使用该方法替代不存在的 solve_question
                    answer_futures = {
                        executor.submit(answering_module.answer_question, q): q
                        for q in questions
                    }
                    
                    # Process completed answers
                    for future in as_completed(answer_futures):
                        if not self.is_running:
                            break
                            
                        question = answer_futures[future]
                        try:
                            result = future.result(timeout=60)  # 1 minute timeout
                            if result and 'answer' in result:
                                question.update(result)
                                
                                # Grade the answer
                                try:
                                    grade_result = grading_module.grade_answer(question)
                                    if grade_result:
                                        question.update(grade_result)
                                        
                                        # Update statistics
                                        self.total_questions += 1
                                        if question.get('is_correct', False):
                                            self.total_correct += 1
                                            # Save to validation set
                                            data_persistence.save_to_validation(question)
                                        else:
                                            # Save to benchmark bank
                                            data_persistence.save_to_benchmark(question)
                                        
                                        # Update UI stats
                                        self.root.after(0, self.update_stats)
                                        
                                except Exception as e:
                                    self.log_message(f"Grading failed: {e}", "ERROR")
                                    
                        except Exception as e:
                            self.log_message(f"Answering failed: {e}", "ERROR")
                
                round_time = time.time() - round_start_time
                if self.is_running:
                    accuracy = (self.total_correct / self.total_questions * 100) if self.total_questions > 0 else 0
                    self.log_message(
                        f"{i18n.get_text('round_unit')} {round_num}{i18n.get_text('of')}{total_rounds} "
                        f"completed in {round_time:.1f}{i18n.get_text('seconds_unit')} - "
                        f"Accuracy: {accuracy:.1f}%", 
                        "SUCCESS"
                    )
            
            if self.is_running:
                self.log_message(i18n.get_text('generation_complete'), "SUCCESS")
            else:
                self.log_message(i18n.get_text('generation_stopped'), "WARNING")
                
        except Exception as e:
            self.log_message(f"{i18n.get_text('error_occurred')}: {e}", "ERROR")
        finally:
            # Reset UI state
            self.root.after(0, lambda: (
                self.start_button.configure(state='normal'),
                self.stop_button.configure(state='disabled'),
                setattr(self, 'is_running', False)
            ))
    
    def periodic_update(self):
        """Periodic update of statistics and UI"""
        if hasattr(self, 'stats_text'):
            self.update_stats()
        
        # Schedule next update
        self.root.after(5000, self.periodic_update)  # Update every 5 seconds
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the international GUI"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intelligent Question Bank System - International GUI')
    parser.add_argument('--language', '-l', choices=['en', 'zh'], default='en',
                      help='Interface language (en=English, zh=Chinese)')
    
    args = parser.parse_args()
    
    # Create and run the GUI
    app = InternationalQuestionGeneratorGUI(language=args.language)
    app.run()

if __name__ == "__main__":
    main()