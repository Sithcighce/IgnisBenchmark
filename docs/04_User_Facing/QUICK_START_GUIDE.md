# 快速使用指南

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 2. API密钥配置
在 `.env` 文件中配置：
```bash
GEMINI_API_KEY=your_gemini_key
SILICONFLOW_API_KEY=your_siliconflow_key
```

### 3. 运行程序

#### 图形界面 (推荐新手)
```bash
python run.py --mode gui
```

#### 命令行生成
```bash
# 生成10道题，运行3轮
python run.py --mode generate -n 10 -r 3

# 生成少量题目测试
python run.py --mode generate -n 2 -r 1
```

#### 导出数据
```bash
# 导出为Markdown文件
python run.py --mode output
```

## 📊 主要功能

### 题目生成
- **自动生成**: 基于流体力学、燃烧科学领域
- **多模型支持**: Gemini、DeepSeek、Qwen自动切换
- **质量保证**: 自动判题和评分

### 数据管理
- **基准库**: 存储挑战性题目 (`data/benchmark_bank.jsonl`)
- **验证集**: 存储已验证题目 (`data/validation_set.jsonl`)
- **导出功能**: 生成可读的Markdown报告

### 配置选项
```yaml
# config.yaml 主要配置
questions_per_round: 10        # 每轮生成题目数
total_rounds: 10              # 总轮数
round_internal_concurrency: 5 # 并发数
```

## 🔧 故障排除

### 常见问题

#### 1. "Missing required environment variables"
**解决**: 检查 `.env` 文件是否正确配置API密钥

#### 2. "User location is not supported"  
**解决**: Gemini API地区限制，系统会自动切换到SiliconFlow

#### 3. "Model does not exist"
**解决**: 检查SiliconFlow API密钥是否有效

### 测试系统
```bash
# 运行安全测试 (无需API密钥)
python testscript\verify_fix.py

# 运行完整测试 (需要API密钥)  
python testscript\test_single_generation.py
```

## 📁 重要文件

- `run.py` - 主程序入口
- `config.yaml` - 系统配置
- `.env` - API密钥配置
- `data/` - 数据文件夹
- `logs/system.log` - 运行日志

## 💡 使用技巧

1. **首次使用**: 先运行 `python run.py --mode generate -n 2 -r 1` 测试
2. **批量生成**: 确认系统稳定后再增加数量
3. **查看进度**: 观察 `logs/system.log` 了解运行状态
4. **数据查看**: 使用 `--mode output` 生成易读报告

## 🆘 获取帮助

- **查看日志**: `cat logs/system.log`
- **检查配置**: `python testscript\verify_fix.py` 
- **重置数据**: 备份后删除 `data/*.jsonl` 文件

---

需要更多帮助请查看 `docs/` 目录中的详细文档。