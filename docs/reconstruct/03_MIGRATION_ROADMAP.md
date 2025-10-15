# 迁移路线图与实施计划

**制定日期**: 2025-10-14  
**预计周期**: 2-3周  
**风险等级**: 中等

---

## 🎯 迁移策略

### 核心原则
1. **渐进式迁移**: 不推倒重来，保持系统可运行
2. **适配器模式**: 新旧代码共存，逐步替换
3. **测试先行**: 先补充测试，再重构
4. **向后兼容**: 保持现有接口不变

### 迁移路径

```
Phase 0: 准备阶段 (2天)
    ├─ 补充单元测试
    ├─ 文档整理
    └─ 代码冻结

Phase 1: 基础设施层 (3天)
    ├─ ModelClient
    ├─ RetryManager
    └─ ConcurrencyManager

Phase 2: 适配器层 (2天)
    ├─ 适配现有模块
    └─ 集成测试

Phase 3: 流水线层 (3天)
    ├─ QuestionPipeline
    └─ BatchProcessor

Phase 4: 应用层 (2天)
    ├─ Milestone2脚本
    └─ 端到端测试

Phase 5: 优化与文档 (2天)
    ├─ 性能调优
    └─ 文档完善
```

---

## 📅 详细实施计划

### Phase 0: 准备阶段 (Day 1-2)

#### 目标
- 确保现有代码可测试
- 建立回归测试基线
- 代码库清理

#### 任务清单

**Day 1: 测试框架搭建**
- [ ] 安装pytest + pytest-asyncio
- [ ] 创建tests目录结构
  ```
  tests/
  ├── unit/
  │   ├── test_model_client.py
  │   ├── test_retry_manager.py
  │   └── test_concurrency_manager.py
  ├── integration/
  │   ├── test_pipeline.py
  │   └── test_batch_processor.py
  ├── legacy/
  │   ├── test_question_generator.py
  │   └── test_answering_module.py
  └── conftest.py
  ```
- [ ] 编写现有模块的测试
  - `test_question_generator.py`: 测试题目生成
  - `test_answering_module.py`: 测试解题
  - `test_grading_module.py`: 测试判题

**Day 2: 代码整理**
- [ ] 创建新目录结构
  ```
  src/
  ├── core/              # 新架构核心
  │   ├── __init__.py
  │   ├── interfaces.py
  │   ├── model_client.py
  │   ├── retry_manager.py
  │   ├── concurrency_manager.py
  │   └── pipeline.py
  ├── adapters/          # 适配器层
  │   ├── __init__.py
  │   └── legacy.py
  ├── legacy/            # 旧代码（重命名）
  │   ├── question_generator.py
  │   ├── answering_module.py
  │   └── grading_module.py
  └── utils/             # 工具函数
  ```
- [ ] 移动现有代码到legacy/
- [ ] 更新导入路径

---

### Phase 1: 基础设施层 (Day 3-5)

#### Day 3: ModelClient实现

**任务**:
```python
# src/core/model_client.py
# 1. 定义接口
class IModelClient(Protocol): ...

# 2. 实现ModelClient
class ModelClient:
    - __init__(configs)
    - call_with_fallback()
    - _call_single_model()
    - _format_model_name()

# 3. 编写测试
# tests/unit/test_model_client.py
class TestModelClient:
    - test_call_success()
    - test_fallback_on_failure()
    - test_all_models_fail()
    - test_metrics_collection()
```

**验收标准**:
- [ ] 所有单元测试通过
- [ ] 支持3种provider (Gemini, SiliconFlow, OpenAI)
- [ ] 自动回退逻辑正确
- [ ] Metrics正确记录

#### Day 4: RetryManager实现

**任务**:
```python
# src/core/retry_manager.py
class RetryManager:
    - with_retry()          # 核心重试逻辑
    - _should_retry()       # 判断是否重试
    - _calculate_delay()    # 指数退避

# tests/unit/test_retry_manager.py
class TestRetryManager:
    - test_success_on_first_attempt()
    - test_retry_on_failure()
    - test_exponential_backoff()
    - test_max_attempts_exceeded()
    - test_no_retry_on_auth_error()
```

**验收标准**:
- [ ] 指数退避计算正确
- [ ] Jitter添加正确
- [ ] 不可重试错误正确识别

#### Day 5: ConcurrencyManager实现

**任务**:
```python
# src/core/concurrency_manager.py
class ConcurrencyManager:
    - run_batch()           # 批量并发执行
    - _run_single()         # 单任务执行

class RateLimiter:
    - acquire()             # 令牌桶限流
    - _refill_tokens()      # 令牌补充

# tests/unit/test_concurrency_manager.py
class TestConcurrencyManager:
    - test_parallel_execution()
    - test_semaphore_limit()
    - test_rate_limiting()
    - test_progress_callback()
```

**验收标准**:
- [ ] 并发数限制生效
- [ ] 速率限制正确
- [ ] 异常处理正确
- [ ] 进度回调工作

---

### Phase 2: 适配器层 (Day 6-7)

#### Day 6: 适配器实现

**任务**:
```python
# src/adapters/legacy.py

class LegacyGeneratorAdapter(IQuestionGenerator):
    """适配旧版生成器"""
    - __init__(old_generator)
    - generate(paper, few_shot)
    - _convert_to_new_format()

class LegacyAnswererAdapter(IAnsweringModule):
    """适配旧版解题器"""
    - __init__(old_answerer)
    - answer(question)

class LegacyGraderAdapter(IGradingModule):
    """适配旧版判题器"""
    - __init__(old_grader)
    - grade(question)

# tests/integration/test_adapters.py
class TestLegacyAdapters:
    - test_generator_adapter()
    - test_answerer_adapter()
    - test_grader_adapter()
```

**验收标准**:
- [ ] 适配器正确包装旧代码
- [ ] 接口一致性测试通过
- [ ] 性能无明显下降

#### Day 7: 集成测试

**任务**:
```python
# tests/integration/test_integration.py
class TestIntegration:
    - test_end_to_end_single_question()
    - test_model_client_with_real_api()
    - test_retry_with_real_failures()
    - test_concurrent_answering()
```

**验收标准**:
- [ ] 端到端流程可运行
- [ ] 与真实API集成成功
- [ ] 错误处理正确

---

### Phase 3: 流水线层 (Day 8-10)

#### Day 8: Pipeline核心实现

**任务**:
```python
# src/core/pipeline.py

@dataclass
class PipelineConfig: ...

@dataclass
class PipelineResult: ...

class QuestionPipeline:
    - __init__(...)
    - process_paper(paper)          # 主流程
    - _run_generation(paper)        # 生成阶段
    - _run_answering(questions)     # 解题阶段
    - _run_grading(questions)       # 判题阶段
    - _save_results(results)        # 保存结果

# tests/unit/test_pipeline.py
class TestPipeline:
    - test_pipeline_initialization()
    - test_generation_stage()
    - test_answering_stage()
    - test_grading_stage()
    - test_full_pipeline()
```

**验收标准**:
- [ ] 三阶段流水线正确执行
- [ ] 进度回调工作
- [ ] 中间结果可保存

#### Day 9: BatchProcessor实现

**任务**:
```python
# src/core/batch_processor.py

class BatchPaperProcessor:
    - __init__(pipeline, concurrency)
    - process_batch(papers)         # 批量处理
    - _process_single_paper(paper)  # 单篇处理
    - get_statistics()              # 获取统计

# tests/unit/test_batch_processor.py
class TestBatchProcessor:
    - test_single_paper_processing()
    - test_batch_processing()
    - test_concurrent_papers()
    - test_error_handling()
```

**验收标准**:
- [ ] 并发处理多篇论文
- [ ] 失败不影响其他论文
- [ ] 统计信息正确

#### Day 10: 数据仓库重构

**任务**:
```python
# src/core/data_repository.py

class IDataRepository(Protocol): ...

class JsonlRepository(IDataRepository):
    - save_to_validation()
    - save_to_benchmark()
    - save_error()
    - get_few_shot_samples()
    - get_statistics()

# 支持异步IO
class AsyncJsonlRepository(IDataRepository):
    - async save_to_validation()
    - async save_to_benchmark()
    ...
```

**验收标准**:
- [ ] 支持同步/异步两种模式
- [ ] 文件操作原子性
- [ ] 并发写入安全

---

### Phase 4: 应用层 (Day 11-12)

#### Day 11: Milestone2脚本

**任务**:
```python
# milestone2_generator.py

async def main():
    # 1. 加载配置
    config = load_config("config.yaml")
    
    # 2. 构建组件
    pipeline = build_pipeline(config)
    processor = BatchPaperProcessor(pipeline, concurrency=3)
    
    # 3. 加载论文
    papers = load_papers("papers/", limit=100)
    
    # 4. 批量处理
    results = await processor.process_batch(
        papers,
        progress_callback=print_progress
    )
    
    # 5. 生成报告
    report = generate_report(results)
    save_report(report, "data/milestone2_report.md")

if __name__ == "__main__":
    asyncio.run(main())
```

**验收标准**:
- [ ] 可处理100篇论文
- [ ] 进度显示清晰
- [ ] 报告格式正确

#### Day 12: 端到端测试

**任务**:
```python
# tests/e2e/test_milestone2.py
class TestMilestone2:
    - test_small_batch(5_papers)
    - test_medium_batch(20_papers)
    - test_error_recovery()
    - test_resume_from_checkpoint()
```

**验收标准**:
- [ ] 小批次测试通过
- [ ] 中批次测试通过
- [ ] 错误恢复正确

---

### Phase 5: 优化与文档 (Day 13-14)

#### Day 13: 性能优化

**任务**:
- [ ] 性能profiling
  ```bash
  python -m cProfile -o profile.stats milestone2_generator.py
  python -m pstats profile.stats
  ```
- [ ] 识别瓶颈
- [ ] 优化热点代码
- [ ] 调整并发参数

**优化点**:
1. **缓存机制**: 缓存Few-shot样本
2. **批量写入**: 减少磁盘IO
3. **连接池**: 复用HTTP连接
4. **内存优化**: 流式处理大文件

#### Day 14: 文档完善

**任务**:
- [ ] 更新README.md
- [ ] 编写API文档
- [ ] 编写使用示例
- [ ] 编写故障排查指南

**文档结构**:
```
docs/
├── reconstruct/           # 重构文档（本系列）
├── api/
│   ├── model_client.md
│   ├── pipeline.md
│   └── batch_processor.md
├── guides/
│   ├── quick_start.md
│   ├── configuration.md
│   └── troubleshooting.md
└── examples/
    ├── milestone1_example.py
    ├── milestone2_example.py
    └── custom_pipeline.py
```

---

## 🔍 测试策略

### 单元测试覆盖率目标

| 模块 | 目标覆盖率 | 关键测试点 |
|------|------------|------------|
| ModelClient | 90% | 回退逻辑、异常处理 |
| RetryManager | 95% | 重试策略、延迟计算 |
| ConcurrencyManager | 90% | 并发控制、限流 |
| Pipeline | 85% | 流程编排、错误处理 |
| Adapters | 80% | 接口适配、数据转换 |

### 集成测试场景

1. **正常流程**: 单篇论文完整处理
2. **模型失败**: 主模型失败，回退到备用模型
3. **并发压力**: 10篇论文并发处理
4. **异常恢复**: 中途失败，断点续传
5. **边界条件**: 空论文、超长论文

### 性能测试基准

| 场景 | 目标 | 测量指标 |
|------|------|----------|
| 单论文处理 | <2分钟 | 端到端延迟 |
| 10论文批处理 | <5分钟 | 吞吐量 |
| 100论文批处理 | <40分钟 | 总耗时 |
| 并发解题 | 5x加速 | vs串行基准 |

---

## ⚠️ 风险管理

### 高风险项

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **API配额超限** | 高 | 高 | 1. 添加配额监控<br>2. 实现降级策略<br>3. 准备备用API |
| **并发引入Bug** | 中 | 高 | 1. 充分的集成测试<br>2. 金丝雀发布<br>3. 快速回滚机制 |
| **性能不达预期** | 中 | 中 | 1. 提前性能测试<br>2. 预留优化时间<br>3. 可调参数 |

### 中风险项

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| **旧代码兼容性** | 中 | 中 | 1. 适配器模式<br>2. 渐进式迁移 |
| **文档不足** | 高 | 低 | 1. 边开发边写文档<br>2. 代码注释完善 |
| **测试时间不足** | 中 | 中 | 1. 自动化测试<br>2. CI/CD集成 |

---

## 🚦 里程碑检查点

### Checkpoint 1: 基础设施完成 (Day 5)
- [ ] ModelClient工作
- [ ] RetryManager工作
- [ ] ConcurrencyManager工作
- [ ] 所有单元测试通过

### Checkpoint 2: 适配器完成 (Day 7)
- [ ] 三个适配器实现
- [ ] 集成测试通过
- [ ] 旧代码功能保持

### Checkpoint 3: 流水线完成 (Day 10)
- [ ] Pipeline可运行
- [ ] BatchProcessor可运行
- [ ] Milestone1可用新架构重现

### Checkpoint 4: 应用完成 (Day 12)
- [ ] Milestone2脚本可运行
- [ ] 端到端测试通过
- [ ] 性能满足预期

### Final: 项目交付 (Day 14)
- [ ] 所有测试通过
- [ ] 文档齐全
- [ ] 代码Review完成
- [ ] 性能达标

---

## 📊 成功标准

### 功能完整性
- ✅ Milestone1功能保持
- ✅ Milestone2可执行
- ✅ 所有现有功能可用

### 代码质量
- ✅ 单元测试覆盖率 > 85%
- ✅ 代码重复率 < 10%
- ✅ 圈复杂度 < 10

### 性能指标
- ✅ Milestone2总耗时 < 50分钟 (100篇论文)
- ✅ 并发解题加速比 > 4x
- ✅ 内存占用 < 1GB

### 可维护性
- ✅ 所有模块有文档
- ✅ API接口清晰
- ✅ 错误信息明确

---

## 🔄 回滚计划

### 触发条件
- 关键功能不可用
- 性能严重下降 (>2x)
- 数据一致性问题

### 回滚步骤
1. 停止新代码部署
2. 恢复到legacy/分支
3. 修复数据问题（如有）
4. 分析失败原因
5. 制定改进方案

---

## 📝 下一步行动

### 立即行动 (今天)
1. ✅ 创建测试框架 → `tests/conftest.py`
2. ✅ 创建目录结构 → `src/core/`, `src/adapters/`
3. ✅ 移动旧代码 → `src/legacy/`

### 明天开始
1. 📝 实现ModelClient
2. 📝 编写单元测试
3. 📝 集成LiteLLM

---

**制定者**: AI架构师  
**审阅**: 待审核  
**状态**: 计划制定完成 → 等待批准执行
