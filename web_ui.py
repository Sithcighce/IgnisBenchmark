"""
Web监控界面
"""

import logging
from flask import Flask, render_template_string
from src.utils import load_config, setup_logging
from src.data_persistence import DataPersistence


app = Flask(__name__)
logger = logging.getLogger(__name__)


# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>智能题库系统 - 监控面板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-label {
            color: #666;
            font-size: 1em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            color: #667eea;
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-description {
            color: #999;
            font-size: 0.9em;
        }
        
        .info-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .info-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .config-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .config-item:last-child {
            border-bottom: none;
        }
        
        .config-label {
            color: #666;
            font-weight: 500;
        }
        
        .config-value {
            color: #333;
            font-family: monospace;
            background: #f5f5f5;
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        .refresh-note {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-running {
            background: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 智能题库系统 - 监控面板</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Benchmark错题库</div>
                <div class="stat-value">{{ benchmark_count }}</div>
                <div class="stat-description">核心评测基准题目数量</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Validation验证集</div>
                <div class="stat-value">{{ validation_count }}</div>
                <div class="stat-description">回归测试验证集数量</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">系统状态</div>
                <div class="stat-value">
                    <span class="status-badge status-running">运行中</span>
                </div>
                <div class="stat-description">监控面板正常工作</div>
            </div>
        </div>
        
        <div class="info-section">
            <h2>📋 配置信息</h2>
            <div class="config-item">
                <span class="config-label">生成模型</span>
                <span class="config-value">{{ config.generation_model }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">判题模型</span>
                <span class="config-value">{{ config.grading_model }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">本地解题模型</span>
                <span class="config-value">{{ config.lm_studio_model_name }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">LM Studio端点</span>
                <span class="config-value">{{ config.lm_studio_endpoint }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">并发数</span>
                <span class="config-value">{{ config.lm_studio_concurrency }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Few-shot数量</span>
                <span class="config-value">{{ config.few_shot_count }}</span>
            </div>
            <div class="config-item">
                <span class="config-label">批次大小</span>
                <span class="config-value">{{ config.batch_size }}</span>
            </div>
        </div>
        
        <div class="refresh-note">
            ⏱️ 页面每30秒自动刷新
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """主页"""
    try:
        # 加载配置
        config = load_config()
        
        # 获取题库信息
        data_persistence = DataPersistence(
            benchmark_path=config["benchmark_bank_path"],
            validation_path=config["validation_set_path"]
        )
        benchmark_count, validation_count = data_persistence.get_counts()
        
        return render_template_string(
            HTML_TEMPLATE,
            benchmark_count=benchmark_count,
            validation_count=validation_count,
            config=config
        )
        
    except Exception as e:
        logger.error(f"渲染页面时出错: {e}")
        return f"<h1>错误</h1><p>{str(e)}</p>", 500


def main():
    """启动Web服务器"""
    # 设置日志
    setup_logging(log_level="INFO")
    
    logger.info("启动Web监控界面...")
    logger.info("访问 http://localhost:5000 查看监控面板")
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()
