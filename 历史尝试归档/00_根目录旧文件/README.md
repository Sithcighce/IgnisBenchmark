# 根目录旧文件归档

这个目录保存了项目开发过程中在根目录产生的旧文件和整理过程的中间产物。

## 📁 目录结构

### 1. **旧生成数据/** (2693个文件)
早期批量生成的题目数据，已全部移动到此归档。

#### 各批次说明（2025-10-15）：
- **questions_test/** (0:18) - 测试批次，2篇论文
- **questions/** (7:29) - 硅基流动第一批中文，199篇
- **questions copy/** (7:27) - 硅基流动第三批补全，298篇  
- **question_reverse/** (10:57) - 倒序生成批次，247篇
- **question_english/** (16:10) - DeepSeek英文批次，298篇（对应07_第六次尝试）
- **question_english copy/** (19:53) - 英文批次备份

#### 汇总说明：
所有批次数据最终通过 `consolidate_and_complete.py` 合并到 `question_all/`（已移动或删除），
再通过 `extract_questions_to_md.py` 提取为 `question_all_md/` 的Markdown格式。

---

### 2. **旧文档/** (已分配完成 ✅)
各阶段的交付文档，现已移动到对应的历史尝试文件夹：

| 文档名称 | 已移动到 | 说明 |
|---------|---------|------|
| MILESTONE1_DELIVERY.md | 01_基础生成 | 第一次尝试交付报告 |
| COMPARISON.md | 01_基础生成 | 新旧生成器对比 |
| MILESTONE1_COMPARE_SUMMARY.md | 02_对比生成 | 对比生成器总结 |
| MILESTONE1_WITHTEXT_DELIVERY.md | 03_保留原文 | 保留原文策略交付 |
| WITHTEXT_STATUS.md | 03_保留原文 | WithText状态报告 |
| BATCH_DETAIL_Q_README.md | 04_详细问题 | 批量详细生成说明 |
| MILESTONE1_DETAIL_INSIGHTS_DELIVERY.md | 05_洞察生成 | 洞察生成交付报告 |
| MILESTONE1_INSIGHTS_PRO_DELIVERY.md | 06_洞察生成专业版 | Pro版本交付报告 |
| FINAL_COMPLETION_REPORT.md | 14_最终交付 | 最终完成报告 |
| 重塑项目需求！ | 保留在00 | 整体需求定义文档 |

---

### 3. **旧日志/** (已分配完成 ✅)
运行日志文件，现已移动到对应的历史尝试：
- `milestone1_withtext.log` → 03_保留原文/logs/
- `milestone1_withtext_run.log` → 03_保留原文/logs/

---

### 4. **prompts原始版本/**
Prompt的演化历史，保留作为参考：
- `解题Prompt.md` - 解题策略
- `判题Prompt.md` - 判题标准  
- `生成题Prompt.md` - 基础生成prompt
- `生成题Prompt_higherlever.md` - 详细版生成prompt
- `旧版本/` - 更早期的prompt版本

**注意**：各历史尝试文件夹中的prompts/是实际使用的版本，这里是演化记录。

---

### 5. **我们的整理脚本/**
整理项目结构时使用的工具脚本：
- `archive_history.py` - 归档历史尝试
- `archive_history_complete.py` - 完整归档方案
- `organize_question_dirs.py` - 整理question目录（注释了各文件夹用途）
- `organize_root.py` - 整理根目录文件

这些脚本帮助我们理解了批量生成的历史和数据流转。

---

### 6. **旧脚本/** (空文件夹)
原计划存放旧脚本，但所有脚本已直接分配到对应的历史尝试文件夹的scripts/子目录。

---

## 🔄 数据流转图

```
硅基流动批次 (questions + questions copy + question_reverse)
           +
DeepSeek批次 (question_english + questions_deepseek)
           ↓
   consolidate_and_complete.py  ← 合并所有批次
           ↓
       question_all/  (JSON格式，按论文组织)
           ↓
   extract_questions_to_md.py  ← 提取为Markdown
           ↓
     question_all_md/  (人类可读格式)
```

---

## 📝 整理笔记

- **_整理笔记.md** - 批量生成时间线完整梳理
- **_文档移动计划.txt** - 文档分配记录

---

## ⚠️ 注意事项

1. **不要删除**：这些数据虽已归档，但包含完整的批量生成历史，对理解项目演化至关重要
2. **查看实际使用文件**：要查看某阶段的实际代码和数据，请访问对应的历史尝试文件夹（01-14）
3. **备份价值**：question_english等批次数据是大规模生成的备份，包含数千个JSON和TXT文件

---

## 🗂️ 相关文件夹

完整的历史尝试归档请查看：
- `历史尝试归档/01_第一次尝试_基础生成/`
- `历史尝试归档/02_第二次尝试_对比生成/`
- ...
- `历史尝试归档/14_最终交付/`
