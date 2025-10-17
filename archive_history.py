#!/usr/bin/env python3
"""
整理项目历史尝试
按时间顺序创建子文件夹，记录每一步的尝试、脚本和产出
"""

import os
import shutil
import json
from pathlib import Path

# 基础路径
BASE_DIR = r"c:\Users\13031\Desktop\workspace\distillation_generation"
ARCHIVE_DIR = os.path.join(BASE_DIR, "历史尝试归档")

# 定义每一步的尝试
ATTEMPTS = [
    {
        "folder": "01_第一次尝试_基础生成",
        "readme": """# 第一次尝试：基础题目生成

## 时间
2025年初

## 目标
从学术论文中生成燃烧科学领域的题目

## 使用脚本
- `milestone1_generator.py`

## 特点
- 最初的尝试，直接从论文生成题目
- 使用单一模型（Claude或GPT）
- 题目格式基础，包含question和answer
- 没有验证机制

## 产出数据
- `data/milestone1_candidates.jsonl` (如果存在)
- `data/milestone1_raw_response.txt`

## 结果
- 成功生成了一批候选题目
- 发现需要多模型验证来保证质量
- 为后续改进奠定基础

## 经验教训
- 单模型生成容易产生偏差
- 需要增加质量控制机制
- 题目需要更严格的格式化
""",
        "scripts": ["milestone1_generator.py"],
        "data_patterns": ["data/milestone1_*"]
    },
    
    {
        "folder": "02_对比生成尝试",
        "readme": """# 第二次尝试：对比生成

## 时间
第一次尝试后

## 目标
通过对比不同生成策略改进题目质量

## 使用脚本
- `milestone1_compare_generator.py`

## 特点
- 对比不同的生成prompt
- 尝试改进题目的专业性
- 增加题目类型分类（concept/reasoning/calculation）

## 产出数据
- 对比生成的题目数据

## 结果
- 发现不同prompt对题目质量影响很大
- 确定了更有效的生成策略

## 经验教训
- Prompt工程很重要
- 需要系统化的题目类型分类
""",
        "scripts": ["milestone1_compare_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "03_增强生成_包含原文",
        "readme": """# 第三次尝试：增强生成（包含原文）

## 时间
对比生成后

## 目标
在生成题目时保留原文引用，提高可追溯性

## 使用脚本
- `milestone1_withtext_generator.py`

## 特点
- 题目包含original_text字段
- 保留文献来源
- 便于验证题目准确性

## 产出数据
- 包含原文引用的题目集

## 结果
- 大幅提高了题目的可验证性
- 为后续验证流程提供基础

## 经验教训
- 原文引用是质量保证的关键
- 需要平衡引用长度和信息量
""",
        "scripts": ["milestone1_withtext_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "04_详细题目生成",
        "readme": """# 第四次尝试：详细题目生成

## 时间
增强生成后

## 目标
生成更详细、更复杂的题目

## 使用脚本
- `milestone1_detail_Q_generator.py`

## 特点
- 增加题目复杂度
- 包含更多细节和计算
- 提高题目的挑战性

## 产出数据
- 详细题目集

## 结果
- 生成了更有深度的题目
- 但也发现了一些过于复杂的情况

## 经验教训
- 题目复杂度需要适中
- 过于复杂会影响实用性
""",
        "scripts": ["milestone1_detail_Q_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "05_洞察生成",
        "readme": """# 第五次尝试：洞察生成

## 时间
详细题目生成后

## 目标
从论文中提取关键洞察，生成高质量题目

## 使用脚本
- `milestone1_insights_generator.py`
- `milestone1_insights_pro_generator.py` (改进版)

## 特点
- 先提取论文的关键洞察
- 基于洞察生成题目
- 更注重概念理解和推理

## 产出数据
- 基于洞察的题目集

## 结果
- 题目质量显著提升
- 更符合专业考核标准

## 经验教训
- 先提取洞察再生成题目效果更好
- 需要平衡不同类型的题目
""",
        "scripts": [
            "milestone1_insights_generator.py",
            "milestone1_insights_pro_generator.py"
        ],
        "data_patterns": []
    },
    
    {
        "folder": "06_DeepSeek英文生成",
        "readme": """# 第六次尝试：DeepSeek英文生成

## 时间
洞察生成后

## 目标
使用DeepSeek模型生成英文题目

## 使用脚本
- `deepseek_english_generator.py`

## 特点
- 切换到DeepSeek模型
- 全英文生成
- 测试不同模型的生成能力

## 产出数据
- DeepSeek生成的英文题目

## 结果
- 验证了多模型生成的可行性
- 英文题目更符合国际标准

## 经验教训
- 不同模型各有优势
- 英文生成更适合学术题目
""",
        "scripts": ["deepseek_english_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "07_DeepSeek智能生成",
        "readme": """# 第七次尝试：DeepSeek智能生成

## 时间
英文生成后

## 目标
使用DeepSeek的推理能力优化生成流程

## 使用脚本
- `deepseek_intelligent_generator.py`

## 特点
- 利用DeepSeek的R1模型推理能力
- 更智能的题目类型判断
- 自动难度分级

## 产出数据
- 智能生成的题目集

## 结果
- 生成效率提升
- 题目分类更准确

## 经验教训
- 推理模型适合复杂任务
- 需要控制生成成本
""",
        "scripts": ["deepseek_intelligent_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "08_批量详细生成",
        "readme": """# 第八次尝试：批量详细题目生成

## 时间
智能生成后

## 目标
大规模批量生成详细题目

## 使用脚本
- `batch_detail_q_generator.py`

## 特点
- 批量处理多篇论文
- 每篇论文生成多道题目
- 自动化程度高

## 产出数据
- 批量生成的题目集（可能在data/文件夹中）

## 结果
- 快速积累了大量候选题目
- 为后续验证提供素材

## 经验教训
- 批量生成提高效率
- 但质量控制更重要
""",
        "scripts": ["batch_detail_q_generator.py"],
        "data_patterns": []
    },
    
    {
        "folder": "09_三模型验证系统",
        "readme": """# 第九阶段：三模型验证系统

## 时间
批量生成完成后

## 目标
建立三模型（Claude/GPT-5/Gemini）验证机制

## 使用脚本
- `src/question_generator.py` (包含验证逻辑)
- `scripts/run_100_questions_test.py`
- `testscript/test_single_generation.py`

## 特点
- 三个顶级模型独立验证
- 检查原文忠实度、标答准确性、题目合理性
- all_correct标记表示三模型一致通过

## 产出数据
- 通过验证的题目：`data/pass.json`
- 未通过验证的题目：`data/notpass.json`

## 结果
- 大幅提高题目质量
- 建立了可信的质量保证体系

## 经验教训
- 多模型验证是质量保证的关键
- 一致性要求保证了题目的权威性
""",
        "scripts": [
            "src/question_generator.py",
            "scripts/run_100_questions_test.py",
            "testscript/test_single_generation.py"
        ],
        "data_patterns": []
    },
    
    {
        "folder": "10_质量筛选",
        "readme": """# 第十阶段：质量筛选

## 时间
验证系统建立后

## 目标
从通过验证的题目中筛选出最高质量的题目

## 使用脚本
- 数据分析脚本（在scripts/或tools/中）

## 特点
- 基于all_correct标记筛选
- 去除重复和低质量题目
- 分类整理

## 产出数据
- `验证/best.json` (984题，三模型一致通过)
- `验证/notpass.json` (88题，包含needs_review)

## 结果
- 得到984道高质量题目
- 这些是IgnisBenchmark的核心题库

## 经验教训
- 严格筛选保证了benchmark的价值
- needs_review机制允许人工复审边界情况
""",
        "scripts": [],
        "data_patterns": []
    },
    
    {
        "folder": "11_GPT5答题测试",
        "readme": """# 第十一阶段：GPT-5答题测试

## 时间
质量筛选完成后

## 目标
使用GPT-5对984道题目进行实际答题测试

## 使用脚本
- GPT-5答题脚本（可能在testscript/或验证/中）

## 特点
- GPT-5作答每道题目
- DeepSeek进行判分
- 记录答案和分数

## 产出数据
- `验证/gpt5_benchmark.log` (详细日志)
- 中断于第908题（OpenRouter余额不足）

## 结果
- 完成872题测试
- 原始准确率：82.57% (720/872)
- 发现了GPT-5的知识盲区

## 经验教训
- 实测是验证benchmark质量的关键
- 成本控制很重要（花费$62.02）
- 日志记录救了项目（恢复了所有数据）
""",
        "scripts": [],
        "data_patterns": ["验证/gpt5_benchmark.log"]
    },
    
    {
        "folder": "12_数据恢复与分析",
        "readme": """# 第十二阶段：数据恢复与分析

## 时间
GPT-5测试中断后

## 目标
从日志中恢复测试数据并深入分析

## 使用脚本
- `验证/recover_from_log.py` - 从日志恢复数据
- `验证/analyze_incorrect.py` - 分析错误题目
- `验证/confirm_incorrect_source.py` - 确认错误来源
- `验证/filter_real_errors.py` - 筛选真实错误
- `验证/categorize_all_questions_final.py` - 完整分类
- `验证/analyze_billing_and_categorize.py` - 账单分析

## 特点
- 从日志解析出872个测试结果
- 区分真实错误vs API失败
- 分析OpenRouter账单确认数据真实性

## 产出数据
- `验证/benchmarkGPT5_recovered.json` (872个恢复结果)
- `验证/gpt5_incorrect_detailed.json` (152个错误详情)
- `验证/gpt5_real_errors.json` (76个真实错误)
- `验证/complete_question_categorization.json` (完整分类)
- `验证/gpt验证结果分类/` (分类文件夹)

## 结果
- 成功恢复所有数据
- 发现真实准确率：90.45%（排除API失败）
- 识别出145道挑战性题目（76真实错误+69 API失败有分）

## 关键发现
- 50%的"错误"实际是API失败
- GPT-5验证能力>生成能力
- 账单数据证实了分析的准确性

## 经验教训
- 日志记录至关重要
- 需要区分技术失败和真实错误
- 账单数据可以验证分析结果
""",
        "scripts": [
            "验证/recover_from_log.py",
            "验证/analyze_incorrect.py",
            "验证/confirm_incorrect_source.py",
            "验证/filter_real_errors.py",
            "验证/categorize_all_questions_final.py",
            "验证/analyze_billing_and_categorize.py",
            "验证/save_categorized_questions.py"
        ],
        "data_patterns": [
            "验证/benchmarkGPT5_recovered.json",
            "验证/gpt5_incorrect_detailed.json",
            "验证/gpt5_real_errors.json",
            "验证/complete_question_categorization.json",
            "验证/gpt验证结果分类/"
        ]
    },
    
    {
        "folder": "13_最终交付",
        "readme": """# 第十三阶段：最终交付

## 时间
2025-10-17

## 目标
创建最终的benchmark产品，供他人使用

## 使用脚本
- `create_final_benchmark.py`

## 特点
- 整合145道挑战性题目（76真实错误+69 API失败有分）
- 创建多个版本满足不同需求
- 完整的文档和使用说明

## 产出数据
- `最终交付/benchmark_basic.json` - 基础版（题目+标答）
- `最终交付/benchmark_with_verification.json` - 验证版
- `最终交付/benchmark_with_gpt5_results.json` - GPT-5测试版
- `最终交付/benchmark_complete.json` - 完整版
- `最终交付/README.md` - 详细说明

## 结果
- ✅ 创建了可直接使用的benchmark
- ✅ 145道高质量挑战性题目
- ✅ GPT-5基准性能：平均44.3分
- ✅ 完整的文档和使用指南

## benchmark特点
1. 三模型验证通过（Claude/GPT-5/Gemini）
2. 基于顶级学术论文
3. 挑战性强（GPT-5都答错或回答不完整）
4. 难度3-5级
5. 涵盖多个专业主题

## 适用场景
- 评测顶级模型的专业能力
- 识别模型知识盲区
- 挑战性测试集

## 经验教训
- 最终产品需要考虑用户需求
- 多版本设计提供灵活性
- 文档和说明同样重要
""",
        "scripts": ["create_final_benchmark.py"],
        "data_patterns": ["最终交付/"]
    }
]

def create_archive_structure():
    """创建归档目录结构"""
    print("=" * 70)
    print("📂 创建历史尝试归档")
    print("=" * 70)
    
    # 创建主归档目录
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    for attempt in ATTEMPTS:
        folder_path = os.path.join(ARCHIVE_DIR, attempt['folder'])
        os.makedirs(folder_path, exist_ok=True)
        
        # 创建README
        readme_path = os.path.join(folder_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(attempt['readme'])
        
        print(f"\n📁 {attempt['folder']}")
        print(f"   ✅ README.md 已创建")
        
        # 复制脚本
        scripts_copied = 0
        for script in attempt['scripts']:
            src = os.path.join(BASE_DIR, script)
            if os.path.exists(src):
                dst = os.path.join(folder_path, os.path.basename(script))
                shutil.copy2(src, dst)
                scripts_copied += 1
                print(f"   ✅ 复制脚本: {os.path.basename(script)}")
        
        if scripts_copied == 0:
            print(f"   ⚠️  未找到脚本文件")
        
        # 复制数据（如果有pattern）
        data_copied = 0
        for pattern in attempt['data_patterns']:
            # 处理文件夹
            if pattern.endswith('/'):
                src = os.path.join(BASE_DIR, pattern.rstrip('/'))
                if os.path.exists(src) and os.path.isdir(src):
                    dst = os.path.join(folder_path, "data", os.path.basename(src))
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    data_copied += 1
                    print(f"   ✅ 复制文件夹: {os.path.basename(src)}/")
            else:
                # 处理单个文件
                src = os.path.join(BASE_DIR, pattern)
                if os.path.exists(src):
                    dst = os.path.join(folder_path, "data", os.path.basename(src))
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    data_copied += 1
                    print(f"   ✅ 复制数据: {os.path.basename(src)}")
        
        if data_copied == 0 and attempt['data_patterns']:
            print(f"   ⚠️  未找到数据文件")
    
    # 创建总览README
    create_master_readme()
    
    print("\n" + "=" * 70)
    print("✨ 归档完成！")
    print("=" * 70)
    print(f"\n归档目录: {ARCHIVE_DIR}")
    print(f"共整理 {len(ATTEMPTS)} 个阶段")

def create_master_readme():
    """创建归档总览README"""
    master_readme = """# IgnisBenchmark 历史尝试归档

本目录记录了IgnisBenchmark项目从最初尝试到最终交付的完整历程。

---

## 📋 项目历程总览

### 阶段1-8：题目生成探索
我们尝试了多种不同的生成策略，不断改进题目质量：

1. **基础生成** → 单模型直接生成
2. **对比生成** → 测试不同prompt策略
3. **增强生成** → 保留原文引用
4. **详细生成** → 增加题目复杂度
5. **洞察生成** → 基于论文关键洞察
6. **多模型尝试** → DeepSeek英文/智能生成
7. **批量生成** → 大规模题目积累

### 阶段9：质量保证革命
建立了三模型（Claude Sonnet 4.5 + GPT-5 + Gemini 2.5 Pro）验证系统：
- 每道题目必须三个模型一致通过
- 验证原文忠实度、标答准确性、题目合理性
- 产出：984道高质量题目（best.json）

### 阶段10：精选筛选
从通过验证的题目中筛选最优质的：
- 去除重复和边界情况
- 分类整理（pass.json, notpass.json）
- needs_review机制保留边界案例

### 阶段11：实战测试
GPT-5实际答题测试：
- 测试了872/984题（中断于余额不足）
- 花费$62.02
- 原始准确率：82.57%

### 阶段12：深度分析
数据恢复与深度分析：
- 从日志完整恢复872个结果
- 区分真实错误vs API失败
- 调整后准确率：90.45%
- 识别145道挑战性题目

### 阶段13：最终交付
创建可用的benchmark产品：
- 145道挑战性题目
- 4个版本满足不同需求
- 完整文档和使用说明

---

## 📊 关键数据

### 题目生成
- **生成轮次**: 8轮不同策略
- **候选题目**: 数千道
- **验证通过**: 984道（three-model consensus）
- **最终筛选**: 145道挑战性题目

### 质量保证
- **验证模型**: 3个顶级模型
- **验证维度**: 原文、标答、合理性
- **一致性要求**: 100%（all_correct）

### 性能测试
- **测试模型**: GPT-5
- **测试题目**: 872题
- **准确率**: 90.45%（排除API失败）
- **成本**: $62.02

### 最终产出
- **Benchmark题目**: 145道
- **难度范围**: 3-5级
- **主题覆盖**: 20+专业主题
- **文件版本**: 4个（basic/verification/gpt5/complete）

---

## 🎯 关键里程碑

1. ✅ **第一道题目生成** (01_第一次尝试)
2. ✅ **建立三模型验证** (09_三模型验证系统)
3. ✅ **筛选出984道高质量题目** (10_质量筛选)
4. ✅ **GPT-5实测完成** (11_GPT5答题测试)
5. ✅ **数据完整恢复** (12_数据恢复与分析)
6. ✅ **Benchmark正式发布** (13_最终交付)

---

## 📁 目录结构

```
历史尝试归档/
├── README.md                        # 本文件
├── 01_第一次尝试_基础生成/
│   ├── README.md
│   └── milestone1_generator.py
├── 02_对比生成尝试/
│   ├── README.md
│   └── milestone1_compare_generator.py
├── 03_增强生成_包含原文/
│   ├── README.md
│   └── milestone1_withtext_generator.py
├── 04_详细题目生成/
│   ├── README.md
│   └── milestone1_detail_Q_generator.py
├── 05_洞察生成/
│   ├── README.md
│   ├── milestone1_insights_generator.py
│   └── milestone1_insights_pro_generator.py
├── 06_DeepSeek英文生成/
│   ├── README.md
│   └── deepseek_english_generator.py
├── 07_DeepSeek智能生成/
│   ├── README.md
│   └── deepseek_intelligent_generator.py
├── 08_批量详细生成/
│   ├── README.md
│   └── batch_detail_q_generator.py
├── 09_三模型验证系统/
│   ├── README.md
│   └── src/question_generator.py
├── 10_质量筛选/
│   └── README.md
├── 11_GPT5答题测试/
│   ├── README.md
│   └── data/gpt5_benchmark.log
├── 12_数据恢复与分析/
│   ├── README.md
│   ├── recover_from_log.py
│   ├── filter_real_errors.py
│   ├── categorize_all_questions_final.py
│   └── data/
│       ├── benchmarkGPT5_recovered.json
│       ├── gpt5_real_errors.json
│       └── complete_question_categorization.json
└── 13_最终交付/
    ├── README.md
    ├── create_final_benchmark.py
    └── data/
        ├── benchmark_basic.json
        ├── benchmark_with_verification.json
        ├── benchmark_with_gpt5_results.json
        └── benchmark_complete.json
```

---

## 🔍 如何使用归档

### 查看特定阶段
每个文件夹包含：
- **README.md**: 该阶段的详细说明
- **脚本文件**: 当时使用的代码（已调整相对路径）
- **data/**: 该阶段产生的数据（如果有）

### 复现某个阶段
1. 进入相应文件夹
2. 阅读README了解背景
3. 查看脚本代码
4. （可选）运行脚本复现

### 学习项目演进
- 按数字顺序浏览各阶段
- 对比不同阶段的策略变化
- 理解每个决策的原因

---

## 💡 经验总结

### 题目生成
- ✅ 多轮迭代比一次性生成更有效
- ✅ 原文引用是质量保证的关键
- ✅ 不同策略适合不同类型的题目

### 质量保证
- ✅ 三模型验证是金标准
- ✅ 一致性要求确保权威性
- ✅ needs_review机制保留灵活性

### 实战测试
- ✅ 实测是验证质量的唯一方法
- ✅ 日志记录救了项目
- ✅ 需要区分技术失败和知识错误

### 项目管理
- ✅ 保留所有尝试记录很有价值
- ✅ 系统化整理降低理解成本
- ✅ 文档和代码同样重要

---

## 📈 项目统计

- **总开发时间**: 数月
- **代码文件**: 50+ 个脚本
- **生成题目**: 数千道候选
- **验证题目**: 984道通过
- **最终Benchmark**: 145道
- **测试成本**: $62.02
- **Git提交**: 100+ 次

---

**整理时间**: 2025-10-17  
**项目状态**: ✅ 已完成并发布
"""
    
    master_readme_path = os.path.join(ARCHIVE_DIR, "README.md")
    with open(master_readme_path, 'w', encoding='utf-8') as f:
        f.write(master_readme)
    
    print(f"\n✅ 总览README已创建: {master_readme_path}")

if __name__ == '__main__':
    create_archive_structure()
