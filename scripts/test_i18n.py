#!/usr/bin/env python3
"""
Test script for internationalization functionality
国际化功能测试脚本
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.i18n import i18n

def test_i18n():
    """Test internationalization functionality"""
    print("🌐 Testing Internationalization System")
    print("="*50)
    
    # Test English
    print("\n📝 Testing English:")
    i18n.set_language('en')
    print(f"Window Title: {i18n.get_text('window_title')}")
    print(f"Control Panel: {i18n.get_text('control_panel')}")
    print(f"Start Button: {i18n.get_text('start_button')}")
    print(f"Language Button: {i18n.get_text('language_button')}")
    
    # Test Chinese
    print("\n📝 Testing Chinese:")
    i18n.set_language('zh')
    print(f"窗口标题: {i18n.get_text('window_title')}")
    print(f"控制面板: {i18n.get_text('control_panel')}")
    print(f"开始按钮: {i18n.get_text('start_button')}")
    print(f"语言按钮: {i18n.get_text('language_button')}")
    
    # Test stats formatting
    print("\n📊 Testing Statistics Formatting:")
    
    # Mock stats data
    mock_stats = {
        'generation_tokens': 12500,
        'answering_tokens': 8300,
        'grading_tokens': 4200,
        'total_tokens': 25000,
        'total_cost': 0.125,
        'avg_generation_time': 2.3,
        'avg_answering_time': 1.8,
        'avg_grading_time': 1.2
    }
    
    # Test English stats
    print("\nEnglish Stats:")
    i18n.set_language('en')
    english_stats = i18n.format_stats_text(5, 50, 32, 150, 85, mock_stats)
    print(english_stats[:200] + "..." if len(english_stats) > 200 else english_stats)
    
    # Test Chinese stats  
    print("\nChinese Stats:")
    i18n.set_language('zh')
    chinese_stats = i18n.format_stats_text(5, 50, 32, 150, 85, mock_stats)
    print(chinese_stats[:200] + "..." if len(chinese_stats) > 200 else chinese_stats)
    
    print("\n✅ Internationalization test completed successfully!")
    print("✅ 国际化测试成功完成！")

if __name__ == "__main__":
    test_i18n()