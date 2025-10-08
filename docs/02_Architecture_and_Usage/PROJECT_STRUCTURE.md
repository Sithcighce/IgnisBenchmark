# 项目结构说明

## 📁 根目录结构

```
questions/
├── 📄 app.py                    # 🎯 唯一程序入口（图形界面）
├── 📄 run.py                    # 🚀 启动脚本（重定向到app.py）
├── 📄 main.py                   # 🔄 旧版命令行入口（保留备份）
├── 📄 config.yaml               # ⚙️ 配置文件（含批次设置）
├── 📄 requirements.txt          # 📦 依赖包列表
├── 📄 README.md                 # 📖 项目说明
├── 📄 .env.example              # 🔑 环境变量模板
├── 📄 .gitignore               # 🚫 Git忽略列表
│
├── 📁 src/                     # 🏗️ 核心源代码
│   ├── __init__.py
│   ├── config_loader.py        # 配置加载器
│   ├── question_generator.py   # 题目生成模块
│   ├── answering_module.py     # 模型解题模块
│   ├── grading_module.py       # 自动判题模块
│   ├── data_persistence.py     # 数据持久化模块
│   ├── token_tracker.py        # Token统计模块
│   ├── siliconflow_api.py      # DeepSeek API模块
│   ├── prompt_manager.py       # Prompt管理器
│   ├── models.py               # 数据模型定义
│   └── utils.py                # 工具函数
│
├── 📁 docs/                    # 📚 所有文档（按准则要求）
│   ├── PROJECT_COMPLETION_REPORT.md
│   ├── user_requirements/      # 用户需求文档
│   │   ├── 高质量题目示例.md
│   │   ├── 开发准则.md
│   │   └── 实现细节.md
│   └── system_generated/       # 系统生成文档
│
├── 📁 prompts/                 # 🎭 Prompt模板（按准则分离存储）
│   ├── 生成题Prompt.md
│   ├── 解题Prompt.md
│   └── 判题Prompt.md
│
├── 📁 data/                    # 💾 数据文件
│   ├── benchmark_bank.jsonl    # 错题库
│   ├── validation_set.jsonl    # 验证集
│   └── README.md
│
├── 📁 logs/                    # 📋 日志文件
│   └── system.log
│
├── 📁 testscript/              # 🧪 测试脚本（按准则只放测试）
│   ├── test_100_questions.py   # 100题批量测试
│   └── test_setup.py           # 环境测试
│
└── 📁 tools/                   # 🔧 工具脚本
    ├── analyze_data.py         # 数据分析工具
    └── batch_run.py            # 批量运行工具
```

## 🎯 程序入口

### 主入口（推荐）
```bash
python app.py
```
- 🖥️ 图形界面
- 📊 实时进度监控
- 💰 Token成本追踪
- ⚙️ 可配置批次数（1-100批次）
- 📋 详细日志显示

### 备用入口
```bash
python run.py
```
- 重定向到app.py
- 保持兼容性

## 📋 开发准则遵守情况

✅ **准则1**: 所有md文档都在docs文件夹  
✅ **准则2**: 根目录只保留程序入口和必要文件  
✅ **准则3**: 合理组织代码结构（src/, tools/, testscript/）  
✅ **准则4**: 项目整洁规范，无冗余代码  
✅ **准则5**: 所有prompt分离存储在prompts/  
✅ **准则6**: API调用前预估开销（Token追踪）  
✅ **准则7**: 项目结构适合git管理  
✅ **准则8**: 20%精力用于测试（testscript/）  
✅ **准则9**: 不使用python -c命令，使用独立文件

## 🚀 功能特性

- **图形界面操作**: 直观的GUI界面
- **批次配置**: 可设置1-100批次（每批次10题）
- **实时监控**: 进度条、Token统计、详细日志
- **鲁棒重试**: 自动处理网络错误、API限制
- **成本控制**: 实时Token使用和成本估算
- **数据积累**: 双重数据库（错题库+验证集）