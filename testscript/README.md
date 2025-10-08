# 测试说明文档

## 测试脚本说明

### 1. `verify_fix.py` - 安全导入测试
**用途**: 验证系统配置和导入，无需API密钥
**运行命令**: `python testscript\verify_fix.py`
**特点**: 
- 检查配置文件格式
- 验证模块导入
- 检查LiteLLM provider格式
- 无网络调用，安全运行

### 2. `test_model_fix.py` - 模型配置测试
**用途**: 测试模型配置和初始化
**运行命令**: `python testscript\test_model_fix.py`
**特点**:
- 验证配置字段完整性
- 测试模块初始化
- 检查API密钥可用性
- 支持有/无API密钥运行

### 3. `test_single_generation.py` - 完整端到端测试
**用途**: 测试完整的题目生成流程
**运行命令**: `python testscript\test_single_generation.py`
**前置条件**: 需要配置API密钥
**特点**:
- 生成一道测试题目
- 验证完整流程
- 需要GEMINI_API_KEY和SILICONFLOW_API_KEY

## 最近修复的问题

### 问题1: LiteLLM Provider错误
**错误**: `api base needs to be a string. api_base={'generation_models': ...}`
**原因**: 模块构造函数被传入了整个配置字典，而不是具体参数
**修复**: 修改了`AnsweringModule`、`QuestionGenerator`、`GradingModule`的构造函数，支持配置字典参数

### 问题2: 并发配置未生效
**原因**: 配置参数未正确传递到模块
**修复**: 从配置字典中正确提取`round_internal_concurrency`等参数

### 问题3: 模型名称格式问题
**原因**: SiliconFlow模型需要去掉provider前缀
**修复**: 在AnsweringModule中自动处理模型名称格式

## 推荐测试流程

1. **首先运行**: `python testscript\verify_fix.py`
   - 验证基本配置和导入

2. **配置API密钥** (创建 `.env` 文件):
   ```
   GEMINI_API_KEY=your_gemini_key
   SILICONFLOW_API_KEY=your_siliconflow_key
   ```

3. **运行完整测试**: `python testscript\test_single_generation.py`
   - 验证端到端功能

4. **运行主程序**: `python run.py --mode generate -n 1 -r 1`
   - 生成少量题目验证

## CI/自动化测试建议

- 默认运行 `verify_fix.py` (无需API密钥)
- 仅在有API密钥时运行完整测试
- 添加mock测试支持离线验证