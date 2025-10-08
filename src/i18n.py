#!/usr/bin/env python3
"""
Internationalization support for the Question Generator System
国际化支持模块
"""

class I18n:
    """
    Enhanced Internationalization class for managing multi-language support
    增强的国际化类，支持多语言管理
    """
    
    LANGUAGES = {
        'en': 'English',
        'zh': '中文'
    }
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(I18n, cls).__new__(cls)
        return cls._instance
    
    TEXTS = {
        'en': {
            # Window titles
            'window_title': 'Intelligent Question Bank Generation & Assessment System v2.0',
            'window_subtitle': 'Concurrent Optimization Version',
            
            # Control panel
            'control_panel': 'Control Panel',
            'rounds_label': 'Rounds:',
            'batch_size_label': 'Questions per round:',
            'start_button': 'Start Generation',
            'stop_button': 'Stop',
            'clear_log_button': 'Clear Log',
            'language_button': 'Language',
            
            # Statistics panel
            'stats_panel': 'Statistics',
            'current_progress': '🎯 Current Progress',
            'rounds': 'Rounds',
            'generated_this_run': 'Generated this run',
            'correct_this_run': 'Correct this run',
            'accuracy': 'Accuracy',
            'database_status': '📚 Database Status',
            'benchmark_bank': 'Benchmark Bank',
            'validation_set': 'Validation Set',
            'total_questions': 'Total Questions',
            'token_usage': '💰 Token Usage',
            'generation_tokens': 'Generation Tokens',
            'answering_tokens': 'Answering Tokens',
            'grading_tokens': 'Grading Tokens',
            'total_tokens': 'Total Tokens',
            'estimated_cost': 'Estimated Cost',
            'performance_metrics': '⏱️ Performance Metrics',
            'avg_generation_time': 'Avg Generation Time',
            'avg_answering_time': 'Avg Answering Time',
            'avg_grading_time': 'Avg Grading Time',
            
            # Log panel
            'log_panel': 'System Log',
            
            # Status messages
            'starting_generation': 'Starting question generation...',
            'stopping_generation': 'Stopping generation...',
            'generation_complete': 'Generation completed',
            'generation_stopped': 'Generation stopped by user',
            'error_occurred': 'Error occurred',
            'clearing_log': 'Clearing log...',
            
            # Units
            'questions_unit': 'questions',
            'seconds_unit': 's',
            'round_unit': 'Round',
            'of': 'of',
            
            # Errors and warnings
            'invalid_rounds': 'Invalid number of rounds',
            'invalid_batch_size': 'Invalid batch size',
            'config_load_error': 'Failed to load configuration',
            'stats_update_error': 'Failed to update statistics',
        },
        'zh': {
            # Window titles
            'window_title': '智能题库生成与评估系统 v2.0',
            'window_subtitle': '并发优化版',
            
            # Control panel
            'control_panel': '控制面板',
            'rounds_label': '运行轮次:',
            'batch_size_label': '每轮题目数:',
            'start_button': '开始生成',
            'stop_button': '停止',
            'clear_log_button': '清空日志',
            'language_button': '语言',
            
            # Statistics panel
            'stats_panel': '统计信息',
            'current_progress': '🎯 当前进度',
            'rounds': '轮次',
            'generated_this_run': '本次生成',
            'correct_this_run': '本次正确',
            'accuracy': '准确率',
            'database_status': '📚 数据库状态',
            'benchmark_bank': '错题库',
            'validation_set': '验证集',
            'total_questions': '总题库',
            'token_usage': '💰 Token使用',
            'generation_tokens': '生成Token',
            'answering_tokens': '解题Token',
            'grading_tokens': '判题Token',
            'total_tokens': '总Token',
            'estimated_cost': '预估成本',
            'performance_metrics': '⏱️ 性能指标',
            'avg_generation_time': '平均生成时间',
            'avg_answering_time': '平均解题时间',
            'avg_grading_time': '平均判题时间',
            
            # Log panel
            'log_panel': '系统日志',
            
            # Status messages
            'starting_generation': '开始生成题目...',
            'stopping_generation': '正在停止生成...',
            'generation_complete': '生成完成',
            'generation_stopped': '用户停止生成',
            'error_occurred': '发生错误',
            'clearing_log': '清空日志中...',
            
            # Units
            'questions_unit': '题',
            'seconds_unit': 's',
            'round_unit': '第',
            'of': '/',
            
            # Errors and warnings
            'invalid_rounds': '无效的轮次数',
            'invalid_batch_size': '无效的批次大小',
            'config_load_error': '配置加载失败',
            'stats_update_error': '统计信息更新失败',
        }
    }
    
    def __init__(self, language='en'):
        self.current_language = language
    
    def set_language(self, language):
        """Set the current language"""
        if language in self.LANGUAGES:
            self.current_language = language
            return True
        return False
    
    def get_language(self):
        """Get the current language"""
        return self.current_language
    
    def get_text(self, key, default=None):
        """Get translated text for the current language"""
        texts = self.TEXTS.get(self.current_language, self.TEXTS['en'])
        return texts.get(key, default or key)
    
    def get_available_languages(self):
        """Get list of available languages"""
        return self.LANGUAGES
    
    def format_stats_text(self, current_round, total_questions, total_correct, 
                         benchmark_count, validation_count, stats):
        """Format the statistics text with proper localization"""
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        if self.current_language == 'zh':
            return f"""📊 实时统计

{self.get_text('current_progress')}:
  {self.get_text('rounds')}: {current_round}
  {self.get_text('generated_this_run')}: {total_questions} {self.get_text('questions_unit')}
  {self.get_text('correct_this_run')}: {total_correct} {self.get_text('questions_unit')}
  {self.get_text('accuracy')}: {accuracy:.1f}%

{self.get_text('database_status')}:
  {self.get_text('benchmark_bank')}: {benchmark_count} {self.get_text('questions_unit')}
  {self.get_text('validation_set')}: {validation_count} {self.get_text('questions_unit')}
  {self.get_text('total_questions')}: {benchmark_count + validation_count} {self.get_text('questions_unit')}

{self.get_text('token_usage')}:
  {self.get_text('generation_tokens')}: {stats.get('generation_tokens', 0):,}
  {self.get_text('answering_tokens')}: {stats.get('answering_tokens', 0):,}
  {self.get_text('grading_tokens')}: {stats.get('grading_tokens', 0):,}
  {self.get_text('total_tokens')}: {stats.get('total_tokens', 0):,}
  {self.get_text('estimated_cost')}: ${stats.get('total_cost', 0):.4f}

{self.get_text('performance_metrics')}:
  {self.get_text('avg_generation_time')}: {stats.get('avg_generation_time', 0):.1f}{self.get_text('seconds_unit')}
  {self.get_text('avg_answering_time')}: {stats.get('avg_answering_time', 0):.1f}{self.get_text('seconds_unit')}
  {self.get_text('avg_grading_time')}: {stats.get('avg_grading_time', 0):.1f}{self.get_text('seconds_unit')}
"""
        else:
            return f"""📊 Real-time Statistics

{self.get_text('current_progress')}:
  {self.get_text('rounds')}: {current_round}
  {self.get_text('generated_this_run')}: {total_questions} {self.get_text('questions_unit')}
  {self.get_text('correct_this_run')}: {total_correct} {self.get_text('questions_unit')}
  {self.get_text('accuracy')}: {accuracy:.1f}%

{self.get_text('database_status')}:
  {self.get_text('benchmark_bank')}: {benchmark_count} {self.get_text('questions_unit')}
  {self.get_text('validation_set')}: {validation_count} {self.get_text('questions_unit')}
  {self.get_text('total_questions')}: {benchmark_count + validation_count} {self.get_text('questions_unit')}

{self.get_text('token_usage')}:
  {self.get_text('generation_tokens')}: {stats.get('generation_tokens', 0):,}
  {self.get_text('answering_tokens')}: {stats.get('answering_tokens', 0):,}
  {self.get_text('grading_tokens')}: {stats.get('grading_tokens', 0):,}
  {self.get_text('total_tokens')}: {stats.get('total_tokens', 0):,}
  {self.get_text('estimated_cost')}: ${stats.get('total_cost', 0):.4f}

{self.get_text('performance_metrics')}:
  {self.get_text('avg_generation_time')}: {stats.get('avg_generation_time', 0):.1f}{self.get_text('seconds_unit')}
  {self.get_text('avg_answering_time')}: {stats.get('avg_answering_time', 0):.1f}{self.get_text('seconds_unit')}
  {self.get_text('avg_grading_time')}: {stats.get('avg_grading_time', 0):.1f}{self.get_text('seconds_unit')}
"""

# Global instance
i18n = I18n()