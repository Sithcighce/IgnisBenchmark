# 系统使用指南 v2.0

## 🎯 功能概述

智能题库生成与评估系统是一个基于AI的自动化题目生成、解答和评估平台。系统采用并发处理架构，能够高效地生成高质量物理题目，并通过AI模型进行自动解答和评分。

## 🚀 快速开始

### 启动系统
```bash
# 方法1: 图形界面（推荐）
python app.py

# 方法2: 命令行模式  
python main.py
```

### 基本操作
1. **设置参数**
   - 运行轮次: 1-100轮
   - 每轮题目数: 1-20题（推荐10题）

2. **开始生成**
   - 点击"开始生成"按钮
   - 系统自动执行: 生成→解题→判题→保存

3. **监控进度**
   - 实时查看统计信息
   - 监控Token使用和成本
   - 查看详细日志输出

## 📊 界面功能

### 控制面板
- **运行轮次设置** - 控制总的处理轮数
- **每轮题目数** - 每批次生成的题目数量
- **开始/停止按钮** - 控制任务执行
- **清空日志** - 清理界面日志显示

### 统计信息区
```
📊 实时统计
🎯 当前进度: 轮次、题目数、正确率
📚 数据库状态: 错题库、验证集数量  
💰 Token使用: 各模块用量和成本
⏱️ 性能指标: 平均处理时间
```

### 系统日志区
- 实时显示系统运行状态
- 分级别显示信息 (INFO/SUCCESS/WARNING/ERROR)
- 支持滚动查看历史日志

## ⚡ 并发处理机制

### 处理流程
```
每轮处理 (10题):
├── 步骤1: 批量生成题目 (串行)
├── 步骤2: 并发解题 (10线程)
├── 步骤3: 并发判题 (10线程) 
└── 步骤4: 实时保存结果
```

### 性能优势
- **10倍并发** - 10个题目同时处理
- **实时保存** - 每题判题完成立即写入
- **无阻塞设计** - 界面始终响应用户操作

## 📁 数据管理

### 数据文件
```
data/
├── benchmark_bank.jsonl    # 错题库 (AI答错的题)
├── validation_set.jsonl    # 验证集 (AI答对的题)
└── seed_examples.jsonl     # 种子题库 (Few-shot示例)
```

### 数据字段
```json
{
  "question_id": "唯一标识符",
  "topic": "主题领域", 
  "difficulty": "难度级别 (2-5)",
  "type": "题型 (Logical/Knowledge/Application)",
  "question_text": "题目内容",
  "standard_answer": "标准答案",
  "candidate_answer": "AI回答", 
  "generation_model": "生成模型",
  "creation_timestamp": "创建时间"
}
```

## 🔧 配置管理

### 主要配置项
```yaml
# API设置
siliconflow_base_url: "https://api.siliconflow.cn/v1"
siliconflow_answering_model: "Qwen/Qwen2.5-7B-Instruct"
generation_model: "gemini/gemini-2.0-flash-exp"
grading_model: "gemini/gemini-2.5-flash"

# 性能设置
batch_size: 10                    # 每批题目数
lm_studio_concurrency: 10         # 并发线程数
timeout: 120                      # 超时时间(秒)

# Few-shot设置
few_shot_count: 3                 # Few-shot示例数量
few_shot_source: "benchmark_bank" # 示例来源
```

### 环境变量
```bash
# .env文件
SILICONFLOW_API_KEY=your_api_key_here
GEMINI_API_KEY=your_gemini_key_here
```

## 📈 质量保证

### 题目生成质量
- **Few-shot学习** - 基于5道高质量种子题
- **多样性控制** - 涵盖不同难度和题型
- **领域专业性** - 物理学专业内容

### 判题准确性  
- **严格评分标准** - 基于物理原理验证
- **详细评分理由** - 包含错误分析
- **分数区间** - 0.0-1.0精确评分

### 数据完整性
- **实时保存** - 避免数据丢失
- **完整字段** - 包含所有必要元数据
- **JSON格式** - 标准化数据结构

## 🔍 监控和调试

### 日志系统
```bash
# 查看实时日志
tail -f logs/system.log

# 过滤错误信息
grep "ERROR" logs/system.log

# 查看特定模块日志  
grep "QuestionGenerator" logs/system.log
```

### 性能监控
- **处理速度** - 每题平均时间
- **成功率** - 各阶段成功率统计
- **资源使用** - Token消耗和成本

### 常见问题诊断
1. **生成失败** - 检查Gemini API配置
2. **解题超时** - 检查硅基流动API连接
3. **判题错误** - 检查Gemini API额度
4. **数据未保存** - 检查文件写入权限

## 💡 使用技巧

### 最佳实践
1. **合理设置批次** - 推荐每轮10题，既保证效率又控制风险
2. **监控成本** - 定期查看Token使用统计
3. **数据备份** - 重要数据定期备份
4. **错误处理** - 遇到错误及时查看日志

### 性能优化
1. **网络环境** - 确保稳定的网络连接
2. **API配额** - 提前检查各API的使用限制  
3. **并发控制** - 可根据机器性能调整并发数
4. **定期清理** - 清理日志文件避免磁盘占满

### 扩展使用
1. **自定义题型** - 修改种子题库适配新领域
2. **调整难度** - 修改配置文件调整题目难度分布
3. **模型切换** - 可替换不同的AI模型
4. **批量导出** - 支持批量导出题目数据

## 🆘 故障排除

### 常见错误及解决方案

#### API相关错误
```
错误: "API key not found"
解决: 检查.env文件中的API密钥配置

错误: "Rate limit exceeded"  
解决: 降低并发数或等待限制重置

错误: "Model not found"
解决: 检查config.yaml中的模型名称配置
```

#### 数据相关错误
```
错误: "Permission denied writing file"
解决: 检查data目录的写入权限

错误: "JSON decode error"
解决: 检查数据文件格式完整性

错误: "Database connection failed"
解决: 检查数据文件路径配置
```

#### 性能相关问题
```
问题: 处理速度慢
解决: 增加并发数或升级网络带宽

问题: 内存使用过高
解决: 降低批次大小或重启程序

问题: 界面无响应
解决: 检查后台任务状态，必要时重启
```

---

📞 **技术支持**: 如遇问题请查看详细日志或提交Issue  
📚 **更多文档**: 查看docs目录下的完整技术文档