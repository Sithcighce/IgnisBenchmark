# 技术架构文档

## 🏗️ 系统架构概览

### 整体设计模式
- **架构模式**: 分层架构 + 模块化设计
- **数据流**: 单向流转 (配置 → 生成 → 解答 → 判题 → 持久化)
- **错误处理**: 防御式编程 + 优雅降级
- **并发模型**: ThreadPoolExecutor + GUI线程分离

## 📦 核心模块详解

### 1. 用户界面层 (UI Layer)
**文件**: `app.py`
- **QuestionGeneratorGUI** - 主GUI控制器
- **职责**: 用户交互、进度显示、配置管理
- **技术**: tkinter + threading
- **关键特性**: 
  - 非阻塞UI设计
  - 实时日志显示
  - Token成本监控
  - 批次进度可视化

### 2. 业务逻辑层 (Business Layer)

#### QuestionGenerator (题目生成器)
**文件**: `src/question_generator.py`
- **模型**: Gemini 2.5 Flash
- **输入**: Few-shot示例 + 生成配置
- **输出**: 结构化题目列表
- **特性**: 
  - 动态Few-shot构建
  - 无token限制生成
  - 自动API回退 (Gemini → DeepSeek)

#### AnsweringModule (解题模块)  
**文件**: `src/answering_module.py`
- **服务**: LM Studio本地API
- **并发**: ThreadPoolExecutor
- **重试机制**: 3次重试 + 指数退避
- **超时策略**: 渐进超时 (60s → 120s → 180s)

#### GradingModule (判题模块)
**文件**: `src/grading_module.py`  
- **模型**: Gemini 2.5 Flash
- **核心功能**: 
  - 鲁棒JSON解析 (正则+容错)
  - 语义化评分 (0-100分)
  - 详细判题理由生成

### 3. 数据持久层 (Data Layer)

#### DataPersistence (数据持久化)
**文件**: `src/data_persistence.py`
- **存储格式**: JSONL (换行分隔JSON)
- **双库设计**:
  - `benchmark_bank.jsonl` - 错题库 (答错题目)  
  - `validation_set.jsonl` - 验证集 (答对题目)
- **操作**: 追加写入、随机抽样、数据加载

## 🔄 数据流转详解

### 1. 初始化流程
```
app.py 启动 → 加载config.yaml → 初始化各模块 → 显示GUI界面
```

### 2. 单批次处理流程
```
设置批次参数 → 抽取Few-shot → 生成题目 → 并发解题 → 逐一判题 → 分类存储
     ↓              ↓            ↓          ↓          ↓          ↓
   GUI配置 → DataPersistence → Gemini API → LM Studio → Gemini API → 双库存储
```

### 3. 错误恢复流程
```
API错误 → 重试机制 → 指数退避 → 超时处理 → 降级策略 → 继续处理
```

## 🛡️ 鲁棒性设计

### API调用保护
```python
# 三层防护
1. 连接重试 (网络层)
2. 指数退避 (时间层)  
3. 服务切换 (服务层)
```

### 数据解析保护
```python
# JSON解析策略
1. 标准解析 (json.loads)
2. 正则提取 (re.search)  
3. 容错解析 (_parse_boolean/_parse_float)
```

### 并发控制保护
```python
# ThreadPoolExecutor配置
- max_workers = lm_studio_concurrency
- timeout管理
- 异常隔离
```

## 📊 性能优化

### 1. 异步处理
- GUI主线程 + 后台工作线程
- 非阻塞用户界面
- 实时进度更新

### 2. 批量处理  
- 题目批量生成 (10题/批)
- 并发解题处理
- 批量数据写入

### 3. 缓存策略
- Prompt模板缓存
- 配置文件缓存
- Few-shot示例缓存

## 🔧 配置系统

### 配置层次结构
```yaml
config.yaml (主配置)
├── 服务端点配置
├── 模型参数配置  
├── 处理控制配置
└── 日志系统配置

.env (环境变量)
├── GOOGLE_API_KEY
└── SILICONFLOW_API_KEY
```

### 配置热加载
- 程序启动时加载
- GUI动态配置覆盖
- 无需重启即可调整参数

## 🎯 扩展接口

### 1. 新增生成模型
```python
# 在QuestionGenerator中添加
def _call_new_model_api(self, prompt):
    # 实现新模型调用逻辑
    pass
```

### 2. 新增解题模型
```python  
# 在AnsweringModule中添加
def _answer_with_new_model(self, question):
    # 实现新模型解题逻辑
    pass
```

### 3. 新增数据格式
```python
# 在models.py中定义
class NewQuestionFormat:
    # 定义新的题目格式
    pass
```

## 📈 监控体系

### 1. 实时监控
- Token使用量统计
- API响应时间
- 错误率统计  
- 处理进度跟踪

### 2. 日志系统
```
logs/system.log - 详细系统日志
GUI界面 - 实时操作日志  
控制台 - 调试输出
```

### 3. 性能指标
- 题目生成速度 (题/分钟)
- 解题处理速度 (题/分钟)  
- API成功率 (%)
- 总体准确率 (%)

## 🔒 安全考虑

### 1. API密钥安全
- 环境变量存储
- 不在代码中硬编码
- .gitignore保护

### 2. 数据安全
- 本地文件存储
- JSONL格式易备份
- 增量数据保护

### 3. 错误信息安全
- 敏感信息过滤
- 安全的日志记录
- 异常信息脱敏

---

**📋 架构设计完成**: 模块化、可扩展、高可用的系统架构  
**🎯 设计原则**: 单一职责、开闭原则、依赖注入  
**🔧 维护性**: 高内聚低耦合，易于测试和扩展