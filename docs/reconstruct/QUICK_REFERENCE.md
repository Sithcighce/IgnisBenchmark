# 重构快速参考卡

**一页纸速查手册**

---

## 🎯 核心问题

| # | 问题 | 严重度 | 文档 |
|---|------|--------|------|
| 1 | 模型调用逻辑重复 (60%) | 🔴 高 | [01](./01_ARCHITECTURE_ANALYSIS.md#问题1) |
| 2 | 并发配置混乱 | 🔴 高 | [05](./05_CONCURRENCY_DESIGN.md) |
| 3 | 配置初始化不一致 | 🟡 中 | [01](./01_ARCHITECTURE_ANALYSIS.md#问题3) |
| 4 | 数据流混乱 | 🟡 中 | [01](./01_ARCHITECTURE_ANALYSIS.md#问题4) |
| 5 | 错误处理碎片化 | 🟡 中 | [01](./01_ARCHITECTURE_ANALYSIS.md#问题5) |

---

## 🏗️ 新架构速览

```
Application  → Milestone1/2/3脚本
    ↓
Pipeline     → QuestionPipeline (编排3阶段)
    ↓
Service      → ModelClient + ConcurrencyMgr + DataRepo
    ↓
Infrastructure → LiteLLM + Asyncio + JSONL
```

**4大核心组件**:
1. `ModelClient` - 统一模型调用 + 自动回退
2. `RetryManager` - 指数退避重试
3. `ConcurrencyManager` - 三层并发控制
4. `QuestionPipeline` - 流水线编排

---

## 📅 实施时间表

| Phase | 内容 | 时间 | 关键产出 |
|-------|------|------|----------|
| 0 | 准备 | 2天 | 测试框架 |
| 1 | 基础设施 | 3天 | ModelClient, RetryManager, ConcurrencyManager |
| 2 | 适配器 | 2天 | 包装旧代码 |
| 3 | 流水线 | 3天 | Pipeline, BatchProcessor |
| 4 | 应用 | 2天 | Milestone2脚本 |
| 5 | 优化 | 2天 | 文档 + 调优 |
| **总计** | | **14天** | 可运行的M2 |

---

## ⚡ 并发模型

### 三层架构

```
Layer 1: Batch Level
    控制多少篇论文并发 (推荐3)

Layer 2: Stage Level
    - Generation: 1 (不并发)
    - Answering: 5 (5题并发)
    - Grading: 3 (3题并发)

Layer 3: Request Level
    全局限流 max=10, rate=5/s
```

### 配置示例

```yaml
concurrency:
  batch_level:
    max_concurrent_batches: 3
  stage_level:
    answering:
      concurrency: 5
    grading:
      concurrency: 3
  request_level:
    max_concurrent_requests: 10
    rate_limit:
      requests_per_second: 5.0
```

---

## 📊 性能预测

### Milestone 2 (100篇论文)

| 指标 | 旧 | 新 | 提升 |
|------|----|----|------|
| 总耗时 | 29.5h | 2.4h | **12.3x** |
| CPU | 20% | 70% | 3.5x |
| 网络 | 10% | 60% | 6x |

---

## 🔧 立即行动

### 今天

```bash
# 1. 安装依赖
pip install pytest pytest-asyncio pytest-cov

# 2. 创建目录
mkdir -p src/{core,adapters,legacy}
mkdir -p tests/{unit,integration,e2e}

# 3. 移动旧代码
mv src/question_generator.py src/legacy/
mv src/answering_module.py src/legacy/
mv src/grading_module.py src/legacy/
```

### 本周

```python
# Day 3: ModelClient
# src/core/model_client.py
class ModelClient:
    async def call_with_fallback(...) -> ModelResponse
    
# Day 4: RetryManager
# src/core/retry_manager.py
class RetryManager:
    async def with_retry(...) -> T
    
# Day 5: ConcurrencyManager
# src/core/concurrency_manager.py
class ConcurrencyManager:
    async def run_batch(...) -> List[T]
```

---

## 🧪 测试策略

### 覆盖率目标

| 模块 | 目标 |
|------|------|
| ModelClient | 90% |
| RetryManager | 95% |
| ConcurrencyManager | 90% |
| Pipeline | 85% |
| Adapters | 80% |

### 测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest --cov=src --cov-report=html

# 只测试单元
pytest tests/unit/ -v

# 只测试集成
pytest tests/integration/ -v
```

---

## 📚 文档索引

| 主题 | 文档 | 关键点 |
|------|------|--------|
| **为什么重构** | [01_ARCHITECTURE_ANALYSIS](./01_ARCHITECTURE_ANALYSIS.md) | 问题诊断 |
| **怎么设计** | [02_NEW_ARCHITECTURE_DESIGN](./02_NEW_ARCHITECTURE_DESIGN.md) | 组件设计 |
| **如何实施** | [03_MIGRATION_ROADMAP](./03_MIGRATION_ROADMAP.md) | 14天计划 |
| **并发控制** | [05_CONCURRENCY_DESIGN](./05_CONCURRENCY_DESIGN.md) | 三层模型 |
| **快速开始** | [README](./README.md) | 总览 |

---

## ⚠️ 避坑指南

### ❌ 不要做

- 删除旧代码 → 移到 `legacy/`
- 一次性重构 → 渐进式迁移
- 跳过测试 → 测试先行
- 改动config.yaml → 先向后兼容

### ✅ 必须做

- 每个功能写测试
- 频繁提交代码
- 保持向后兼容
- 文档同步更新

---

## 🎯 验收清单

### Phase 0 完成标志
- [ ] pytest可运行
- [ ] 旧代码有测试
- [ ] 目录结构调整完成

### Phase 1 完成标志
- [ ] ModelClient工作
- [ ] RetryManager工作
- [ ] ConcurrencyManager工作
- [ ] 单元测试通过

### Phase 3 完成标志
- [ ] Pipeline可运行
- [ ] BatchProcessor可运行
- [ ] M1可用新架构复现

### 最终验收标志
- [ ] M2脚本可运行
- [ ] 100论文 < 3小时
- [ ] 测试覆盖率 > 85%
- [ ] 文档齐全

---

## 🚨 紧急情况

### 如果卡住了

| 问题 | 检查 | 解决 |
|------|------|------|
| 测试失败 | 依赖安装？ | `pip install -r requirements.txt` |
| 导入错误 | PYTHONPATH？ | `export PYTHONPATH=$(pwd)` |
| 并发Bug | 信号量？ | 降低并发度 |
| API超时 | 重试配置？ | 增加timeout |

### 快速回滚

```bash
# 1. 停止新代码
git checkout legacy_stable

# 2. 恢复数据
cp data/backup/* data/

# 3. 验证
python -m pytest tests/legacy/ -v
```

---

## 📞 快速参考

### 关键文件位置

```
src/
  core/              # 新架构核心
    model_client.py
    retry_manager.py
    concurrency_manager.py
    pipeline.py
  adapters/          # 适配器
    legacy.py
  legacy/            # 旧代码
    question_generator.py
    answering_module.py
    grading_module.py

tests/
  unit/              # 单元测试
  integration/       # 集成测试
  e2e/               # 端到端测试

docs/reconstruct/    # 重构文档
```

### 常用命令

```bash
# 运行M1
python milestone1_generator.py

# 运行M2（新）
python milestone2_generator.py

# 测试
pytest tests/ -v --cov=src

# 性能分析
python -m cProfile milestone2_generator.py
```

---

**打印此页** - 放在手边随时参考！

**更新日期**: 2025-10-14
