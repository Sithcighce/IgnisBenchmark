#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能题目生成系统 - 主程序入口
Intelligent Question Generation System - Main Entry Point

专为流体力学、燃烧科学和航空航天工程领域设计的自动化题目生成与评估系统
Automated question generation and evaluation system specialized for 
fluid mechanics, combustion science, and aerospace engineering
"""

import sys
import os
import argparse
from pathlib import Path

# 添加源码目录到Python路径
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

def print_banner():
    """显示程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎓 Intelligent Question Generation System                  ║
║                                                                              ║
║         Specialized for Fluid Mechanics, Combustion & Aerospace             ║
║                     流体力学、燃烧科学与航空航天专用题库系统                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='Intelligent Question Generation System - 智能题目生成系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples / 使用示例:
  python run.py --mode gui              # 启动图形界面 (Start GUI)
  python run.py --mode cli              # 启动命令行界面 (Start CLI)  
  python run.py --mode web              # 启动Web界面 (Start Web UI)
  python run.py --mode generate -n 10  # 生成10道题目 (Generate 10 questions)
  python run.py --mode visualize       # 生成题目浏览器 (Generate question browser)
  python run.py --mode clean           # 清理数据 (Clean data)
        '''
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['gui', 'cli', 'web', 'generate', 'visualize', 'clean', 'validate'],
        default='gui',
        help='运行模式 (Run mode): gui=图形界面, cli=命令行, web=网页界面, generate=生成题目, visualize=可视化, clean=清理文件(不加-n)或数据(加-n), validate=验证系统'
    )
    
    parser.add_argument(
        '--questions', '-n',
        type=int,
        default=10,
        help='生成题目数量 (Number of questions to generate) [default: 10]'
    )
    
    parser.add_argument(
        '--rounds', '-r',
        type=int,
        default=1,
        help='运行轮数 (Number of rounds) [default: 1]'
    )
    
    parser.add_argument(
        '--lang', '-l',
        choices=['en', 'zh'],
        default='en',
        help='界面语言 (Interface language): en=English, zh=中文 [default: en]'
    )
    
    args = parser.parse_args()
    
    print_banner()
    print(f"Mode / 运行模式: {args.mode}")
    print(f"Language / 语言: {'English' if args.lang == 'en' else '中文'}")
    print("="*80)
    
    try:
        if args.mode == 'gui':
            print("🖥️  Starting GUI application...")
            print("    启动图形用户界面...")
            
            # Try international GUI first with language support
            try:
                from app_international import InternationalQuestionGeneratorGUI
                app = InternationalQuestionGeneratorGUI(language=args.lang)
                app.run()
            except ImportError:
                # Fall back to original GUI
                print("   📝 International GUI not available, using standard GUI...")
                print("   📝 国际化GUI不可用，使用标准GUI...")
                from app import main as gui_main
                gui_main()
            
        elif args.mode == 'cli':
            print("⌨️  Starting CLI application...")
            print("    启动命令行界面...")
            from main import main as cli_main
            cli_main()
            
        elif args.mode == 'web':
            print("🌐 Starting Web UI...")
            print("    启动Web界面...")
            from web_ui import main as web_main
            web_main()
            
        elif args.mode == 'generate':
            print(f"🚀 Starting question generation: {args.questions} questions, {args.rounds} rounds")
            print(f"    开始生成题目：{args.questions}道题目，{args.rounds}轮")
            from main import main as cli_main
            cli_main()
            
        elif args.mode == 'visualize':
            print("🎨 Generating complete question browser...")
            print("    生成完整题目浏览器...")
            os.system(f'"{sys.executable}" scripts/visualize_complete.py')
            
        elif args.mode == 'clean':
            if args.questions and args.questions > 0:
                print("🧹 Cleaning benchmark data...")
                print("    清理基准数据...")
                if os.path.exists('scripts/clean_benchmark.py'):
                    os.system(f'"{sys.executable}" scripts/clean_benchmark.py')
                else:
                    print("    Benchmark cleaning script not found")
            else:
                print("🧹 Cleaning output files...")
                print("    清理输出文件...")
                os.system(f'"{sys.executable}" scripts/clean_output.py')
            
        elif args.mode == 'validate':
            print("✅ Validating system...")
            print("    验证系统...")
            os.system(f'"{sys.executable}" scripts/validate_system.py')
            
    except KeyboardInterrupt:
        print("\n\n👋 User interrupted the program")
        print("    用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"    发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()