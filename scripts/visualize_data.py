#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目数据可视化脚本
用于将JSON格式的题库数据转换为易读的HTML格式，方便研究人员查看和分析题目内容
"""

import json
import os
from datetime import datetime
from pathlib import Path

def load_jsonl_data(filepath):
    """加载JSONL格式的数据文件"""
    data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"解析第{line_num}行JSON失败: {e}")
        except Exception as e:
            print(f"读取文件 {filepath} 失败: {e}")
    return data

def truncate_text(text, max_length=200):
    """截断过长的文本"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def format_question_html(question, index, data_type):
    """格式化单个题目为HTML"""
    # 获取基本信息
    question_id = question.get('question_id', f'{data_type}-{index}')
    topic = question.get('topic', 'Unknown')
    difficulty = question.get('difficulty', 'N/A')
    question_type = question.get('type', 'Unknown')
    question_text = question.get('question_text', '无题目内容')
    standard_answer = question.get('standard_answer', '无标准答案')
    generation_model = question.get('generation_model', 'Unknown')
    
    # 候选答案（如果有）
    candidate_answer = question.get('candidate_answer', '')
    
    # 判题结果（如果有）
    score = question.get('score', 'N/A')
    is_correct = question.get('is_correct', None)
    
    # 创建时间
    timestamp = question.get('creation_timestamp', 'Unknown')
    
    # 样式类名
    card_class = "correct-question" if data_type == "validation" else "incorrect-question" if data_type == "benchmark" else "seed-question"
    
    html = f'''
    <div class="question-card {card_class}">
        <div class="question-header">
            <div class="question-meta">
                <span class="question-id">ID: {question_id[:8]}...</span>
                <span class="question-topic">📚 {topic}</span>
                <span class="question-difficulty">⭐ 难度: {difficulty}</span>
                <span class="question-type">📝 类型: {question_type}</span>
                {f'<span class="question-score">🎯 分数: {score}</span>' if score != 'N/A' else ''}
            </div>
        </div>
        
        <div class="question-content">
            <div class="question-text">
                <h4>📋 题目内容：</h4>
                <p>{question_text}</p>
            </div>
            
            <div class="standard-answer">
                <h4>✅ 标准答案：</h4>
                <p>{truncate_text(standard_answer)}</p>
            </div>
            
            {f'''
            <div class="candidate-answer">
                <h4>🤖 模型答案：</h4>
                <p>{truncate_text(candidate_answer)}</p>
            </div>
            ''' if candidate_answer else ''}
            
            <div class="question-footer">
                <small>
                    <strong>生成模型:</strong> {generation_model} | 
                    <strong>创建时间:</strong> {timestamp}
                    {f' | <strong>正确性:</strong> {"✅ 正确" if is_correct else "❌ 错误"}' if is_correct is not None else ''}
                </small>
            </div>
        </div>
    </div>
    '''
    return html

def generate_html_report():
    """生成HTML可视化报告"""
    print("🎨 开始生成题目可视化HTML报告...")
    
    # 加载数据
    benchmark_data = load_jsonl_data('data/benchmark_bank.jsonl')
    validation_data = load_jsonl_data('data/validation_set.jsonl')
    seed_data = load_jsonl_data('data/seed_examples.jsonl')
    
    # 统计信息
    total_questions = len(benchmark_data) + len(validation_data)
    accuracy = (len(validation_data) / total_questions * 100) if total_questions > 0 else 0
    
    # 开始生成HTML
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 智能题目生成系统 - 题目数据浏览器</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #f0f0f0;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .section {{
            margin: 30px 0;
        }}
        
        .section-header {{
            background: #343a40;
            color: white;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            margin: 0;
            font-size: 1.3em;
        }}
        
        .question-card {{
            border: 1px solid #e9ecef;
            border-radius: 0 0 8px 8px;
            margin-bottom: 20px;
            background: white;
            transition: box-shadow 0.3s ease;
        }}
        
        .question-card:hover {{
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .correct-question {{
            border-left: 5px solid #28a745;
        }}
        
        .incorrect-question {{
            border-left: 5px solid #dc3545;
        }}
        
        .seed-question {{
            border-left: 5px solid #17a2b8;
        }}
        
        .question-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .question-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .question-meta span {{
            background: #e9ecef;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .question-content {{
            padding: 20px;
        }}
        
        .question-text, .standard-answer, .candidate-answer {{
            margin: 15px 0;
        }}
        
        .question-text h4, .standard-answer h4, .candidate-answer h4 {{
            color: #495057;
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }}
        
        .question-text p, .standard-answer p, .candidate-answer p {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 0;
            line-height: 1.6;
            border-left: 3px solid #6c757d;
        }}
        
        .question-footer {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
        }}
        
        .nav-tabs {{
            display: flex;
            border-bottom: 1px solid #dee2e6;
            margin: 20px 0 0 0;
        }}
        
        .nav-tab {{
            padding: 12px 24px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-bottom: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        
        .nav-tab.active {{
            background: white;
            border-bottom: 1px solid white;
            margin-bottom: -1px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .timestamp {{
            text-align: right;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 智能题目生成系统</h1>
            <p style="color: #6c757d; font-size: 1.1em;">题目数据浏览器 - 流体力学与燃烧领域专业评测题库</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{total_questions}</div>
                <div class="stat-label">总题目数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(validation_data)}</div>
                <div class="stat-label">正确题目</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(benchmark_data)}</div>
                <div class="stat-label">错题库</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{accuracy:.1f}%</div>
                <div class="stat-label">准确率</div>
            </div>
        </div>
        
        <div class="nav-tabs">
            <div class="nav-tab active" onclick="showTab('validation')">✅ 验证集 ({len(validation_data)}题)</div>
            <div class="nav-tab" onclick="showTab('benchmark')">❌ 错题库 ({len(benchmark_data)}题)</div>
            <div class="nav-tab" onclick="showTab('seed')">🌱 种子样本 ({len(seed_data)}题)</div>
        </div>
        
        <div id="validation-content" class="tab-content active">
            <h3 class="section-header">✅ 验证集题目 - 模型答对的题目</h3>
    '''
    
    # 添加验证集题目
    for i, question in enumerate(validation_data, 1):
        html_content += format_question_html(question, i, "validation")
    
    html_content += '''
        </div>
        
        <div id="benchmark-content" class="tab-content">
            <h3 class="section-header">❌ 错题库 - 模型答错的挑战性题目</h3>
    '''
    
    # 添加错题库题目
    for i, question in enumerate(benchmark_data, 1):
        html_content += format_question_html(question, i, "benchmark")
    
    html_content += '''
        </div>
        
        <div id="seed-content" class="tab-content">
            <h3 class="section-header">🌱 种子样本 - 高质量示例题目</h3>
    '''
    
    # 添加种子样本题目
    for i, question in enumerate(seed_data, 1):
        html_content += format_question_html(question, i, "seed")
    
    html_content += f'''
        </div>
        
        <div class="timestamp">
            📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // 隐藏所有标签页内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // 移除所有标签页的active类
            document.querySelectorAll('.nav-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签页内容
            document.getElementById(tabName + '-content').classList.add('active');
            
            // 为选中的标签页添加active类
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
    '''
    
    # 保存HTML文件
    output_path = 'question_browser.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 题目浏览器已生成: {output_path}")
    print(f"📊 数据概览:")
    print(f"  - 验证集: {len(validation_data)} 题")
    print(f"  - 错题库: {len(benchmark_data)} 题") 
    print(f"  - 种子样本: {len(seed_data)} 题")
    print(f"  - 总计: {total_questions} 题")
    print(f"  - 准确率: {accuracy:.1f}%")
    
    return output_path

def main():
    """主函数"""
    try:
        output_path = generate_html_report()
        print(f"\n🎉 成功生成题目可视化浏览器!")
        print(f"📁 文件路径: {output_path}")
        print(f"💡 在浏览器中打开此文件即可查看所有题目内容")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()