# 脚本使用指南

本目录包含了多个有用的脚本，用于系统管理、测试和数据处理。

## Python 脚本

### 🚀 run_app.py
启动主应用程序的Python脚本。
```bash
python scripts/run_app.py
```
**功能:**
- 设置正确的工作目录和Python路径
- 启动GUI应用程序
- 提供友好的错误处理和状态提示

### 🔍 system_check.py  
全面的系统状态检查脚本。
```bash
python scripts/system_check.py
```
**检查内容:**
- 环境变量配置(.env文件和API密钥)
- 目录结构完整性
- 关键文件存在性
- 核心模块导入能力

### 📊 validate_data.py
数据文件验证和格式检查脚本。
```bash
python scripts/validate_data.py
```
**功能:**
- 验证JSONL文件格式
- 检测JSON语法错误
- 统计有效/无效记录数
- 报告数据文件状态

### ⚡ quick_test.py
快速功能测试脚本。
```bash
python scripts/quick_test.py  
```
**测试内容:**
- 核心模块导入测试
- Prompt文件加载测试
- 数据持久化功能测试
- 基础功能完整性验证

### 🔧 data_tools.py
数据分析和批量处理工具。
```bash
python scripts/data_tools.py
```
**功能:**
- 分析benchmark数据统计信息
- 清理失败的判题记录
- 导出详细的统计报告
- 自动备份重要数据

## PowerShell 脚本

### 🏃 run.ps1
PowerShell版本的应用程序启动脚本。
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run.ps1
```
**特点:**
- 彩色输出和友好提示
- Python环境检查
- 自动设置工作目录
- 错误处理和状态报告

### ✅ check.ps1
综合系统检查PowerShell脚本。
```powershell  
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```
**功能:**
- Python环境验证
- 关键文件存在性检查
- 数据文件状态检查
- 调用Python深度检查脚本

### 🧪 test.ps1
PowerShell版本的快速测试脚本。
```powershell
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
```
**特点:**
- 创建临时测试文件
- 执行功能测试
- 自动清理临时文件
- 彩色结果输出

## 使用建议

### 日常开发流程
1. **首次使用:** 运行 `system_check.py` 确保环境配置正确
2. **启动应用:** 使用 `run_app.py` 或 `run.ps1` 启动应用程序
3. **数据维护:** 定期运行 `data_tools.py` 清理和分析数据
4. **问题排查:** 使用 `quick_test.py` 快速检测功能问题

### 推荐命令序列
```bash
# 完整的系统检查和启动流程
python scripts/system_check.py      # 检查系统状态
python scripts/validate_data.py     # 验证数据文件  
python scripts/quick_test.py        # 快速功能测试
python scripts/run_app.py          # 启动应用程序
```

### 数据维护
```bash
# 定期数据维护
python scripts/data_tools.py        # 分析和清理数据
python scripts/validate_data.py     # 验证数据完整性
```

## 注意事项

1. **禁止使用 `python -c` 命令** - 所有脚本都使用独立文件，避免命令行代码执行
2. **自动备份** - `data_tools.py` 会自动备份重要文件
3. **错误处理** - 所有脚本都包含完善的错误处理和重试机制
4. **日志记录** - 运行结果会记录在 `logs/` 目录中

## 改进内容

### 判题系统改进
- 添加了JSON解析失败时的重试机制(最多3次)
- 失败重试时会等待1秒后重试，而不是直接标记为错题
- 改进了错误信息，显示重试次数和详细原因

### 脚本系统改进  
- 创建了完整的脚本生态系统
- 所有脚本都避免使用 `python -c` 命令
- 提供了Python和PowerShell两种版本
- 添加了数据清理和分析工具

这些脚本将大大提高开发和维护效率，确保系统的稳定运行。