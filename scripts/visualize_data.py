#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_jsonl_data(filepath):
    """Load JSONL data and return list of question objects"""
    data = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return data

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return "N/A"
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def format_question_card(question, index, category):
    """Format a single question as HTML card with complete information"""
    
    # Extract data with safe defaults
    qid = escape_html(question.get('question_id', f'{category}-{index}'))
    topic = escape_html(question.get('topic', 'Unknown Topic'))
    difficulty = question.get('difficulty', 'N/A')
    qtype = escape_html(question.get('type', 'Unknown Type'))
    
    # Question content
    question_text = escape_html(question.get('question_text', 'No question content available'))
    standard_answer = escape_html(question.get('standard_answer', 'No standard answer available'))
    
    # AI response data - handle missing fields properly
    candidate_answer = question.get('candidate_answer')
    is_correct = question.get('is_correct')
    grading_explanation = question.get('grading_explanation')
    
    # Determine status based on data completeness and category
    if category == 'validation':
        card_class = 'validation-card'
        status_badge = '<span class="badge success">✅ Validation Set</span>'
        # For validation set, assume correct answers if in this dataset
        if candidate_answer and is_correct is None:
            correct_status = '<span class="correct">✅ Assumed Correct (Validation Set)</span>'
        elif is_correct is True:
            correct_status = '<span class="correct">✅ Verified Correct</span>'
        elif is_correct is False:
            correct_status = '<span class="incorrect">❌ Incorrect</span>'
        else:
            correct_status = '<span class="unknown">❓ Not Evaluated</span>'
    elif category == 'benchmark':
        card_class = 'benchmark-card'
        status_badge = '<span class="badge error">❌ Benchmark (Challenging)</span>'
        # For benchmark, assume incorrect/challenging if in this dataset
        if candidate_answer and is_correct is None:
            correct_status = '<span class="incorrect">❌ Assumed Incorrect (Benchmark)</span>'
        elif is_correct is False:
            correct_status = '<span class="incorrect">❌ Verified Incorrect</span>'
        elif is_correct is True:
            correct_status = '<span class="correct">✅ Correct</span>'
        else:
            correct_status = '<span class="unknown">❓ Not Evaluated</span>'
    else:
        card_class = 'seed-card'
        status_badge = '<span class="badge info">🌱 Seed Example</span>'
        correct_status = '<span class="info">📚 Reference Material</span>'
    
    # Handle missing response data
    if not candidate_answer:
        candidate_answer = '<em class="missing-data">🚫 No AI response available - Question not yet answered</em>'
    else:
        candidate_answer = escape_html(candidate_answer)
        
    if not grading_explanation:
        grading_explanation = '<em class="missing-data">🚫 No grading explanation - Question not yet graded</em>'
    else:
        grading_explanation = escape_html(grading_explanation)
    
    # Model information
    generation_model = escape_html(question.get('generation_model', 'Unknown'))
    answering_model = escape_html(question.get('answering_model', 'Not answered yet'))
    grading_model = escape_html(question.get('grading_model', 'Not graded yet'))
    
    # Timestamps
    created_time = question.get('created_time', 'Unknown')
    answered_time = question.get('answered_time', 'Not answered yet')
    graded_time = question.get('graded_time', 'Not graded yet')
    
    # Performance metrics
    generation_time = question.get('generation_time', 'N/A')
    answering_time = question.get('answering_time', 'N/A')
    grading_time = question.get('grading_time', 'N/A')
    
    return f'''
    <div class="question-card {card_class}">
        <div class="card-header">
            <h3>Question ID: {qid}</h3>
            {status_badge}
            <div class="metadata">
                <span class="badge secondary">{qtype}</span>
                <span class="badge primary">{topic}</span>
                <span class="badge warning">Difficulty: {difficulty}</span>
            </div>
        </div>
        
        <div class="card-content">
            <div class="section">
                <h4>📝 Question / 题目内容</h4>
                <div class="content-box question-box">{question_text}</div>
            </div>
            
            <div class="section">
                <h4>✅ Standard Answer / 标准答案</h4>
                <div class="content-box standard-box">{standard_answer}</div>
            </div>
            
            <div class="section">
                <h4>🤖 AI Response / AI回答 {correct_status}</h4>
                <div class="content-box response-box">{candidate_answer}</div>
            </div>
            
            <div class="section">
                <h4>🎯 Grading Explanation / 判题说明</h4>
                <div class="content-box grading-box">{grading_explanation}</div>
            </div>
            
            <div class="section">
                <h4>⚙️ System Information / 系统信息</h4>
                <div class="info-grid">
                    <div><strong>Generation Model:</strong> {generation_model}</div>
                    <div><strong>Answering Model:</strong> {answering_model}</div>
                    <div><strong>Grading Model:</strong> {grading_model}</div>
                </div>
                <div class="info-grid">
                    <div><strong>Generation Time:</strong> {generation_time}s</div>
                    <div><strong>Answering Time:</strong> {answering_time}s</div>
                    <div><strong>Grading Time:</strong> {grading_time}s</div>
                </div>
                <div class="info-grid">
                    <div><strong>Created:</strong> {created_time}</div>
                    <div><strong>Answered:</strong> {answered_time}</div>
                    <div><strong>Graded:</strong> {graded_time}</div>
                </div>
            </div>
        </div>
    </div>
    '''

def generate_html(validation_data, benchmark_data, seed_data, output_path):
    """Generate complete HTML visualization"""
    
    total_validation = len(validation_data)
    total_benchmark = len(benchmark_data)
    total_seed = len(seed_data)
    total_questions = total_validation + total_benchmark + total_seed
    
    accuracy = (total_validation / (total_validation + total_benchmark) * 100) if (total_validation + total_benchmark) > 0 else 0
    
    # Generate question cards
    validation_cards = ''.join([format_question_card(q, i, 'validation') for i, q in enumerate(validation_data)])
    benchmark_cards = ''.join([format_question_card(q, i, 'benchmark') for i, q in enumerate(benchmark_data)])
    seed_cards = ''.join([format_question_card(q, i, 'seed') for i, q in enumerate(seed_data)])
    
    # Fallback for empty sections
    if not validation_cards:
        validation_cards = '<div class="empty-section">No validation questions available</div>'
    if not benchmark_cards:
        benchmark_cards = '<div class="empty-section">No benchmark questions available</div>'
    if not seed_cards:
        seed_cards = '<div class="empty-section">No seed examples available</div>'
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Question Bank Viewer - Complete Analysis</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .header p {{ font-size: 1.1rem; opacity: 0.9; }}
        
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; 
                  margin: 2rem; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-item {{ text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        
        .tabs {{ display: flex; margin: 0 2rem; background: white; border-radius: 10px 10px 0 0; overflow: hidden; }}
        .tab-button {{ flex: 1; padding: 1rem 2rem; border: none; background: #e9ecef; cursor: pointer; 
                       font-size: 1.1rem; transition: all 0.3s; }}
        .tab-button.active {{ background: white; color: #667eea; }}
        .tab-button:hover {{ background: #dee2e6; }}
        
        .tab-content {{ display: none; margin: 0 2rem 2rem; background: white; border-radius: 0 0 10px 10px; 
                        padding: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .tab-content.active {{ display: block; }}
        
        .question-card {{ border: 1px solid #ddd; border-radius: 8px; margin-bottom: 2rem; overflow: hidden; 
                          box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .validation-card {{ border-left: 4px solid #28a745; }}
        .benchmark-card {{ border-left: 4px solid #dc3545; }}
        .seed-card {{ border-left: 4px solid #17a2b8; }}
        
        .card-header {{ background: #f8f9fa; padding: 1rem; border-bottom: 1px solid #ddd; }}
        .card-header h3 {{ margin-bottom: 0.5rem; color: #495057; }}
        .metadata {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        
        .badge {{ padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; color: white; }}
        .badge.success {{ background: #28a745; }}
        .badge.error {{ background: #dc3545; }}
        .badge.info {{ background: #17a2b8; }}
        .badge.warning {{ background: #ffc107; color: #333; }}
        .badge.primary {{ background: #007bff; }}
        .badge.secondary {{ background: #6c757d; }}
        
        .card-content {{ padding: 1.5rem; }}
        .section {{ margin-bottom: 1.5rem; }}
        .section h4 {{ margin-bottom: 0.5rem; color: #495057; }}
        
        .content-box {{ background: #f8f9fa; border-radius: 5px; padding: 1rem; 
                        border-left: 3px solid #dee2e6; font-family: monospace; }}
        .question-box {{ border-left-color: #6f42c1; background: #f8f7ff; }}
        .standard-box {{ border-left-color: #28a745; background: #f8fff9; }}
        .response-box {{ border-left-color: #17a2b8; background: #f0fdff; }}
        .grading-box {{ border-left-color: #ffc107; background: #fffef0; }}
        
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                      gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9rem; }}
        
        .correct {{ color: #28a745; font-weight: bold; }}
        .incorrect {{ color: #dc3545; font-weight: bold; }}
        .unknown {{ color: #6c757d; font-weight: bold; }}
        .info {{ color: #17a2b8; font-weight: bold; }}
        
        .missing-data {{ 
            color: #fd7e14; 
            font-style: italic; 
            background: #fff3cd; 
            padding: 0.5rem; 
            border-radius: 4px; 
            border: 1px solid #ffeaa7; 
            display: block; 
            margin: 0.25rem 0; 
        }}
        
        .empty-section {{ text-align: center; color: #6c757d; padding: 3rem; background: #f8f9fa; 
                          border-radius: 8px; font-style: italic; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 Question Bank Analysis</h1>
        <p>Complete visualization of generated questions with AI responses and grading results</p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{total_questions}</div>
            <div>Total Questions</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{total_validation}</div>
            <div>Correct Answers</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{total_benchmark}</div>
            <div>Incorrect Answers</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{accuracy:.1f}%</div>
            <div>Accuracy Rate</div>
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
        <h3>✅ Validation Set - Questions Answered Correctly</h3>
        <p>These questions were answered correctly by the AI system and serve as validation examples.</p>
        <hr style="margin: 1rem 0;">
        {validation_cards}
    </div>
    
    <div id="benchmark" class="tab-content">
        <h3>❌ Benchmark Bank - Questions Answered Incorrectly</h3>
        <p>These questions were answered incorrectly by the AI and represent challenging problems for model improvement.</p>
        <hr style="margin: 1rem 0;">
        {benchmark_cards}
    </div>
    
    <div id="seed" class="tab-content">
        <h3>🌱 Seed Examples - Reference Questions</h3>
        <p>High-quality reference questions used for few-shot learning in question generation.</p>
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
    </script>
</body>
</html>'''
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"📄 Complete question browser generated: {output_path}")
    print(f"📊 Total: {total_questions} questions ({accuracy:.1f}% accuracy)")

def main():
    print("🎨 Generating Complete Question Browser...")
    
    # File paths
    project_root = Path(__file__).parent.parent
    validation_path = project_root / "data" / "validation_set.jsonl"
    benchmark_path = project_root / "data" / "benchmark_bank.jsonl"
    seed_path = project_root / "data" / "seed_examples.jsonl"
    output_path = project_root / "output" / "complete_question_browser.html"
    
    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)
    
    # Load data
    validation_data = load_jsonl_data(validation_path)
    benchmark_data = load_jsonl_data(benchmark_path)
    seed_data = load_jsonl_data(seed_path)
    
    print(f"📚 Loaded {len(validation_data)} validation, {len(benchmark_data)} benchmark, {len(seed_data)} seed questions")
    
    # Generate HTML
    generate_html(validation_data, benchmark_data, seed_data, output_path)
    
    print(f"✅ Complete! Open {output_path} in your browser.")

if __name__ == "__main__":
    main()
