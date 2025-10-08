#!/usr/bin/env python3
"""
Enhanced Complete Question Visualization System
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_jsonl_data(filepath):
    """Load JSONL format data file"""
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
                            print(f"JSON parsing error at line {line_num}: {e}")
        except Exception as e:
            print(f"Failed to read file {filepath}: {e}")
    return data

def format_text_for_html(text):
    """Format text for HTML display safely"""
    if not text:
        return "N/A"
    
    # Convert to string and escape HTML
    text = str(text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    
    # Convert newlines to HTML breaks
    text = text.replace('\\n', '<br>').replace('\n', '<br>')
    
    return text

def create_question_card(question, index, data_type):
    """Create HTML card for a single question"""
    
    # Extract question data safely
    question_id = question.get('question_id', f'{data_type}-{index}')
    topic = format_text_for_html(question.get('topic', 'Unknown'))
    difficulty = question.get('difficulty', 'N/A')
    question_type = question.get('type', 'Unknown')
    question_text = format_text_for_html(question.get('question_text', 'No content available'))
    standard_answer = format_text_for_html(question.get('standard_answer', 'No standard answer'))
    
    # Model information
    generation_model = format_text_for_html(question.get('generation_model', 'Unknown'))
    answering_model = format_text_for_html(question.get('answering_model', 'Unknown'))
    grading_model = format_text_for_html(question.get('grading_model', 'Unknown'))
    
    # Answer and grading information
    candidate_answer = format_text_for_html(question.get('candidate_answer', 'No answer provided'))
    is_correct = question.get('is_correct', None)
    grading_explanation = format_text_for_html(question.get('grading_explanation', 'No grading explanation available'))
    
    # Timestamps
    created_time = question.get('created_time', 'Unknown')
    answered_time = question.get('answered_time', 'Unknown')
    graded_time = question.get('graded_time', 'Unknown')
    
    # Performance metrics
    generation_time = question.get('generation_time', 'N/A')
    answering_time = question.get('answering_time', 'N/A')
    grading_time = question.get('grading_time', 'N/A')
    
    # Determine card styling based on data type
    if data_type == 'validation':
        card_class = 'card-validation'
        status_badge = '<span class="badge badge-success">✓ Correct</span>'
    elif data_type == 'benchmark':
        card_class = 'card-benchmark'
        status_badge = '<span class="badge badge-danger">✗ Incorrect</span>'
    else:
        card_class = 'card-seed'
        status_badge = '<span class="badge badge-info">🌱 Seed</span>'
    
    # Correctness indicator
    if is_correct is not None:
        correct_indicator = '✅ Correct' if is_correct else '❌ Incorrect'
        correct_class = 'text-success' if is_correct else 'text-danger'
    else:
        correct_indicator = '❓ Unknown'
        correct_class = 'text-muted'
    
    # Generate the card HTML
    card_html = f"""
    <div class="question-card {card_class}">
        <div class="card-header">
            <div class="card-title">
                <span class="question-id">ID: {question_id}</span>
                {status_badge}
                <span class="badge badge-secondary">{question_type}</span>
                <span class="badge badge-info">📚 {topic}</span>
            </div>
        </div>
        
        <div class="card-body">
            <!-- Question Content -->
            <div class="section">
                <h5>📝 Question Content / 题目内容:</h5>
                <div class="content-box question-content">{question_text}</div>
            </div>
            
            <!-- Standard Answer -->
            <div class="section">
                <h5>✅ Standard Answer / 标准答案:</h5>
                <div class="content-box answer-box">{standard_answer}</div>
            </div>
            
            <!-- AI Response -->
            <div class="section">
                <h5>🤖 AI Response / AI回答: 
                    <span class="{correct_class}"><strong>{correct_indicator}</strong></span>
                </h5>
                <div class="content-box response-box">{candidate_answer}</div>
            </div>
            
            <!-- Grading Explanation -->
            <div class="section">
                <h5>🎯 Grading Explanation / 判题说明:</h5>
                <div class="content-box grading-box">{grading_explanation}</div>
            </div>
            
            <!-- Model Information -->
            <div class="section">
                <h5>⚙️ Model Information / 模型信息:</h5>
                <div class="model-info">
                    <div><strong>Generation:</strong> {generation_model}</div>
                    <div><strong>Answering:</strong> {answering_model}</div>
                    <div><strong>Grading:</strong> {grading_model}</div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="section">
                <h5>📊 Performance Metrics / 性能指标:</h5>
                <div class="metrics">
                    <div><strong>Generation Time:</strong> {generation_time}s</div>
                    <div><strong>Answering Time:</strong> {answering_time}s</div>
                    <div><strong>Grading Time:</strong> {grading_time}s</div>
                </div>
            </div>
            
            <!-- Timestamps -->
            <div class="section timestamps">
                <div><strong>Created:</strong> {created_time}</div>
                <div><strong>Answered:</strong> {answered_time}</div>
                <div><strong>Graded:</strong> {graded_time}</div>
            </div>
        </div>
    </div>
    """
    
    return card_html

def generate_complete_html_report(validation_data, benchmark_data, seed_data, output_path):
    """Generate complete HTML visualization report"""
    
    # Calculate statistics
    total_validation = len(validation_data)
    total_benchmark = len(benchmark_data)
    total_seed = len(seed_data)
    total_questions = total_validation + total_benchmark + total_seed
    
    accuracy = (total_validation / (total_validation + total_benchmark) * 100) if (total_validation + total_benchmark) > 0 else 0
    
    # Generate question cards
    validation_cards = ''.join([create_question_card(q, i, 'validation') for i, q in enumerate(validation_data)])
    benchmark_cards = ''.join([create_question_card(q, i, 'benchmark') for i, q in enumerate(benchmark_data)])
    seed_cards = ''.join([create_question_card(q, i, 'seed') for i, q in enumerate(seed_data)])
    
    # If no data, show placeholder
    if not validation_cards:
        validation_cards = '<div class="no-questions">No validation questions available / 暂无验证题目</div>'
    if not benchmark_cards:
        benchmark_cards = '<div class="no-questions">No benchmark questions available / 暂无基准题目</div>'
    if not seed_cards:
        seed_cards = '<div class="no-questions">No seed questions available / 暂无种子题目</div>'
    
    # Complete HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Question Bank Viewer / 完整题库查看器</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats {{
            background: white;
            margin: 2rem;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            text-align: center;
        }}
        
        .stat-item {{
            padding: 1rem;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .tabs {{
            display: flex;
            background: white;
            margin: 0 2rem;
            border-radius: 10px 10px 0 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .tab-button {{
            flex: 1;
            padding: 1rem 2rem;
            border: none;
            background: #e9ecef;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }}
        
        .tab-button.active {{
            background: white;
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-button:hover {{
            background: #dee2e6;
        }}
        
        .tab-content {{
            display: none;
            margin: 0 2rem 2rem;
            background: white;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: 500px;
            padding: 2rem;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .question-card {{
            border: 1px solid #dee2e6;
            border-radius: 10px;
            margin-bottom: 2rem;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}
        
        .question-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .card-validation {{ border-left: 4px solid #28a745; }}
        .card-benchmark {{ border-left: 4px solid #dc3545; }}
        .card-seed {{ border-left: 4px solid #17a2b8; }}
        
        .card-header {{
            background: #f8f9fa;
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .card-title {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }}
        
        .question-id {{
            font-weight: bold;
            color: #495057;
        }}
        
        .badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: white;
        }}
        
        .badge-success {{ background-color: #28a745; }}
        .badge-danger {{ background-color: #dc3545; }}
        .badge-info {{ background-color: #17a2b8; }}
        .badge-secondary {{ background-color: #6c757d; }}
        
        .card-body {{ padding: 1.5rem; }}
        
        .section {{ margin-bottom: 1.5rem; }}
        
        .section h5 {{
            color: #495057;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .content-box {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 1rem;
            border-left: 3px solid #dee2e6;
            font-family: 'Consolas', 'Monaco', monospace;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .question-content {{
            border-left-color: #6f42c1;
            background: #f8f7ff;
        }}
        
        .answer-box {{
            border-left-color: #28a745;
            background: #f8fff9;
        }}
        
        .response-box {{
            border-left-color: #17a2b8;
            background: #f0fdff;
        }}
        
        .grading-box {{
            border-left-color: #ffc107;
            background: #fffef0;
        }}
        
        .model-info, .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
            font-size: 0.9rem;
        }}
        
        .timestamps {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.5rem;
            font-size: 0.8rem;
            color: #6c757d;
        }}
        
        .text-success {{ color: #28a745 !important; }}
        .text-danger {{ color: #dc3545 !important; }}
        .text-muted {{ color: #6c757d !important; }}
        
        .no-questions {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 3rem;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .stats {{ margin: 1rem; grid-template-columns: 1fr; }}
            .tabs {{ margin: 0 1rem; }}
            .tab-content {{ margin: 0 1rem 1rem; }}
            .card-title {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Complete Question Bank Viewer</h1>
        <p>📊 Comprehensive Analysis of Generated Questions / 生成题目的全面分析</p>
        <p>🕒 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{total_questions}</div>
            <div>Total Questions<br>总题目数</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{total_validation}</div>
            <div>Correct Answers<br>正确答案</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{total_benchmark}</div>
            <div>Incorrect Answers<br>错误答案</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{accuracy:.1f}%</div>
            <div>Accuracy Rate<br>准确率</div>
        </div>
    </div>
    
    <div class="tabs">
        <button class="tab-button active" onclick="openTab(event, 'validation')">
            ✅ Validation Set ({total_validation})
        </button>
        <button class="tab-button" onclick="openTab(event, 'benchmark')">
            ❌ Benchmark Bank ({total_benchmark})
        </button>
        <button class="tab-button" onclick="openTab(event, 'seed')">
            🌱 Seed Examples ({total_seed})
        </button>
    </div>
    
    <div id="validation" class="tab-content active">
        <h3>✅ Validation Set - Correctly Answered Questions / 验证集 - 正确回答的题目</h3>
        <p>Questions that were answered correctly by the AI system / AI系统正确回答的题目</p>
        <hr style="margin: 1rem 0;">
        {validation_cards}
    </div>
    
    <div id="benchmark" class="tab-content">
        <h3>❌ Benchmark Bank - Incorrectly Answered Questions / 基准库 - 错误回答的题目</h3>
        <p>Questions that were answered incorrectly, used for system improvement / AI系统错误回答的题目，用于系统改进</p>
        <hr style="margin: 1rem 0;">
        {benchmark_cards}
    </div>
    
    <div id="seed" class="tab-content">
        <h3>🌱 Seed Examples - Reference Questions / 种子样本 - 参考题目</h3>
        <p>High-quality reference questions used for few-shot learning / 用于少样本学习的高质量参考题目</p>
        <hr style="margin: 1rem 0;">
        {seed_cards}
    </div>
    
    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].classList.remove("active");
            }}
            tablinks = document.getElementsByClassName("tab-button");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].classList.remove("active");
            }}
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }}
        
        // Auto-scroll to top when switching tabs
        document.addEventListener('DOMContentLoaded', function() {{
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    setTimeout(() => {{
                        window.scrollTo({{ top: 0, behavior: 'smooth' }});
                    }}, 100);
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Complete question browser generated: {output_path}")
    print(f"📊 Statistics: {total_questions} total questions")
    print(f"   ✅ {total_validation} correct answers")
    print(f"   ❌ {total_benchmark} incorrect answers")
    print(f"   🌱 {total_seed} seed examples")
    print(f"   📈 {accuracy:.1f}% accuracy rate")

def main():
    """Main function"""
    print("🎨 Generating Enhanced Complete Question Browser...")
    print("🎨 生成增强版完整题目浏览器...")
    
    # Define file paths
    project_root = Path(__file__).parent.parent
    validation_path = project_root / "data" / "validation_set.jsonl"
    benchmark_path = project_root / "data" / "benchmark_bank.jsonl"
    seed_path = project_root / "data" / "seed_examples.jsonl"
    output_path = project_root / "output" / "complete_question_browser.html"
    
    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)
    
    # Load data
    print("📖 Loading question data...")
    validation_data = load_jsonl_data(validation_path)
    benchmark_data = load_jsonl_data(benchmark_path)
    seed_data = load_jsonl_data(seed_path)
    
    print(f"   📚 Loaded {len(validation_data)} validation questions")
    print(f"   📚 Loaded {len(benchmark_data)} benchmark questions")
    print(f"   📚 Loaded {len(seed_data)} seed questions")
    
    # Generate HTML report
    print("🔨 Generating HTML report...")
    generate_complete_html_report(validation_data, benchmark_data, seed_data, output_path)
    
    print(f"✅ Complete! Open {output_path} in your browser to view all questions.")
    print(f"✅ 完成！在浏览器中打开 {output_path} 查看所有题目。")

if __name__ == "__main__":
    main()