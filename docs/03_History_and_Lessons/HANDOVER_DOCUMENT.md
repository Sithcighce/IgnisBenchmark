# 智能题库生成与评估系统 - 交接文档

## 📋 项目概况

**项目名称**: 智能题库生成与评估系统 (Question Generation & Evaluation System)  
**版本**: v1.0  
**完成时间**: 2025年10月7日  
**开发状态**: ✅ 完成并可投入使用  
**仓库**: https://github.com/Sithcighce/distillation_generation

## 🎯 系统功能

### 核心流程
1. **题目生成** - 使用 Gemini 2.5 Flash 生成高质量题目
2. **模型解题** - 本地 LM Studio (Qwen-8B) 解答题目
3. **自动判题** - Gemini 2.5 Flash 评估答案正确性
4. **数据积累** - 错题库 + 验证集双重数据资产

### 主要特性
- 📱 **图形界面操作** - 现代化 tkinter GUI
- ⚙️ **灵活批次配置** - 1-100批次可调 (每批10题)
- 💰 **成本监控** - 实时 Token 使用和成本追踪
- 🛡️ **鲁棒重试机制** - 自动处理网络错误和API限制
- 🔄 **智能API回退** - Gemini → DeepSeek 自动切换

## 📁 项目结构

```
questions/
├── 🎯 app.py                    # 唯一程序入口 (图形界面)
├── 📄 config.yaml               # 系统配置
├── 📄 requirements.txt          # 依赖清单
├── 📄 README.md                 # 项目说明
├── 📄 .env.example              # 环境变量模板
│
├── 📁 src/                      # 核心代码
│   ├── question_generator.py   # 题目生成 (Gemini)
│   ├── answering_module.py     # 解题模块 (LM Studio)
│   ├── grading_module.py       # 判题模块 (Gemini)
│   ├── data_persistence.py     # 数据持久化
│   ├── token_tracker.py        # Token统计
│   ├── siliconflow_api.py      # DeepSeek备用API
│   └── ...
│
├── 📁 prompts/                  # Prompt模板
│   ├── 生成题Prompt.md
│   ├── 解题Prompt.md
│   └── 判题Prompt.md
│
├── 📁 data/                     # 数据文件
│   ├── benchmark_bank.jsonl    # 错题库 (核心资产)
│   └── validation_set.jsonl    # 验证集
│
├── 📁 testscript/               # 测试脚本
│   ├── test_100_questions.py   # 100题批量测试
│   ├── test_gui.py             # GUI功能测试
│   └── final_test.py           # 完整功能验证
│
└── 📁 docs/                     # 文档目录
    ├── 📖 本文档及其他技术文档
    └── user_requirements/       # 用户需求文档
```

## 🚀 快速启动

### 环境要求
- Python 3.13.4
- 已配置的虚拟环境 (.venv)
- Google Gemini API Key
- 运行中的 LM Studio (localhost:1234)

### 启动命令
```bash
# 激活虚拟环境
.venv\Scripts\activate

# 启动图形界面
python app.py

# 查看帮助
python app.py --help
```

## ⚙️ 关键配置

### config.yaml 核心配置
```yaml
# 模型配置
generation_model: "gemini/gemini-2.5-flash"
grading_model: "gemini/gemini-2.5-flash" 
lm_studio_endpoint: "http://localhost:1234/v1/chat/completions"
lm_studio_model_name: "qwen/qwen3-8b"

# 处理参数
batch_size: 10              # 每批题目数
total_batches: 10           # 总批次数
few_shot_count: 2           # Few-shot示例数
lm_studio_concurrency: 1    # LM Studio并发数

# 成本控制
enable_token_tracking: true  # 启用Token统计
```

### .env 环境变量
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
SILICONFLOW_API_KEY=your_siliconflow_key_here  # DeepSeek备用
```

## 🏗️ 系统架构

### 模块依赖关系
```
app.py (GUI入口)
├── QuestionGenerator → Gemini API
├── AnsweringModule → LM Studio API  
├── GradingModule → Gemini API
├── DataPersistence → 本地JSONL文件
└── TokenTracker → 成本统计
```

### 数据流转
```
配置加载 → Few-shot抽样 → 题目生成 → 模型解题 → 自动判题 → 数据持久化
   ↓            ↓            ↓          ↓          ↓          ↓
config.yaml → 错题库 → Gemini API → LM Studio → Gemini API → 错题库/验证集
```

## 🧪 测试体系

### 测试脚本说明
1. **test_gui.py** - GUI模块功能测试 (5项测试)
2. **test_100_questions.py** - 100题批量处理测试  
3. **final_test.py** - 完整系统验证
4. **emergency_fix_test.py** - 关键bug修复验证

### 运行测试
```bash
# GUI功能测试
python testscript\test_gui.py

# 完整系统测试  
python testscript\final_test.py

# 100题批量测试 (完整流程)
python testscript\test_100_questions.py
```

## 💰 成本估算

### Token费用 (Gemini 2.5 Flash)
- **输入**: $0.075 / 1M tokens
- **输出**: $0.30 / 1M tokens

### 预估成本 (100题)
- 题目生成: ~50K tokens ≈ $0.02
- 自动判题: ~30K tokens ≈ $0.01  
- **总计**: ~$0.03 / 100题

## 🛡️ 鲁棒性机制

### 错误处理
1. **API限制** - 指数退避重试 (1s → 2s → 4s)
2. **网络超时** - 渐进超时 (60s → 120s → 180s)  
3. **模型过载** - 自动切换 Gemini → DeepSeek
4. **JSON解析** - 多重解析策略 (标准→正则→容错)

### 监控机制
- 实时Token使用统计
- 详细操作日志记录
- GUI进度可视化
- 错误自动恢复

## 📊 数据资产

### benchmark_bank.jsonl (错题库)
- **用途**: 模型弱点评估、训练数据
- **格式**: `{question_data, failed_attempt{model_name, candidate_answer, grading_result}}`
- **价值**: 持续积累的挑战性题目集

### validation_set.jsonl (验证集)  
- **用途**: 模型性能验证、Few-shot示例池
- **格式**: `QuestionUnit` 标准格式
- **价值**: 高质量题目和标准答案

## 🔧 维护指南

### 常见问题排查
1. **Gemini API错误** - 检查API密钥和网络
2. **LM Studio连接失败** - 确认服务运行在localhost:1234
3. **Token统计异常** - 检查API响应格式变化
4. **GUI无响应** - 后台任务阻塞，重启程序

### 日志位置
- **系统日志**: `logs/system.log`
- **GUI日志**: 界面右侧实时显示
- **错误追踪**: 完整异常堆栈记录

### 配置调优
```yaml
# 性能优化
lm_studio_concurrency: 3        # 提高并发 (小心过载)
batch_size: 20                   # 增加批次大小
few_shot_count: 3               # 更多示例 (提高质量)

# 成本控制
total_batches: 5                # 减少总批次
enable_token_tracking: true     # 实时成本监控
```

## 🚨 已知限制

1. **LM Studio依赖** - 需要本地运行，消耗GPU资源
2. **网络依赖** - Gemini/DeepSeek API需要稳定网络  
3. **成本累积** - 大批量使用需要监控API费用
4. **并发限制** - 过高并发可能触发API限制

## 🔄 扩展建议

### 短期改进
1. **更多模型支持** - 添加OpenAI、Claude等API
2. **题目类型扩展** - 支持图像、代码等题型
3. **批量配置优化** - 更灵活的批次策略

### 长期发展  
1. **分布式处理** - 支持多机并行处理
2. **智能调度** - 根据API负载自动调整
3. **质量评估** - 题目质量自动评分机制

## 📞 技术支持

### 关键文件清单
- `app.py` - 主程序入口 ✅ 已完成
- `config.yaml` - 系统配置 ✅ 已配置  
- `src/*.py` - 核心模块 ✅ 全部就绪
- `testscript/*.py` - 测试套件 ✅ 验证通过

### 交接检查清单
- [x] 所有模块正常导入
- [x] GUI界面正常显示  
- [x] 配置文件正确加载
- [x] 日志系统正常工作
- [x] Token统计功能正常
- [x] 完整测试套件通过
- [x] 错误处理机制就绪
- [x] 文档完整性检查

---

**📋 交接完成**: 系统已100%就绪，可立即投入生产使用。  
**🎯 运行命令**: `python app.py`  
**📖 详细文档**: 见 `docs/` 目录其他技术文档