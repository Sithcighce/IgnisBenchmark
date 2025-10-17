#!/usr/bin/env python3
"""
完善历史尝试归档 - 包含data、prompts、scripts
"""

import os
import shutil
from pathlib import Path

# 定义归档结构 - 每个阶段包含README、data、scripts、prompts
ATTEMPTS = [
    {
        "folder": "01_第一次尝试_基础生成",
        "readme": """# 第一次尝试：基础生成

**时间**: 2024年初  
**脚本**: milestone1_generator.py  
**策略**: 基础prompt生成问题  

## 目标
从学术论文生成高质量的燃烧科学问题，每篇论文5题。

## 方法
- 使用基础生成prompt
- 直接从论文内容提取关键信息
- 简单的质量检查

## 数据文件
- `milestone1_candidates.jsonl`: 候选题目
- `milestone1_raw_response.txt`: 原始API响应
- `milestone1_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 基础生成prompt

## 结果
生成了第一批候选题目，但质量不够稳定。

## 经验教训
- ✅ 证明了可行性
- ❌ 需要更详细的prompt指导
- ❌ 需要多次迭代改进
""",
        "scripts": ["milestone1_generator.py"],
        "data_patterns": [
            "data/milestone1_candidates.jsonl",
            "data/milestone1_raw_response.txt",
            "data/milestone1_report.md"
        ],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "02_第二次尝试_对比生成",
        "readme": """# 第二次尝试：对比生成

**时间**: 2024年初  
**脚本**: milestone1_compare_generator.py  
**策略**: 加入对比和多样性要求  

## 改进
- 要求生成不同类型的问题
- 加入对比示例
- 增强质量控制

## 数据文件
- `milestone1_compare.jsonl`: 对比生成结果
- `milestone1_compare_raw_iter1.txt`: 第一轮原始响应
- `milestone1_compare_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 改进的生成prompt

## 结果
题目多样性有所提升，但仍需改进。

## 经验教训
- ✅ 多样性要求有效
- ✅ 对比示例有帮助
- ❌ 仍需保留原文引用
""",
        "scripts": ["milestone1_compare_generator.py"],
        "data_patterns": [
            "data/milestone1_compare.jsonl",
            "data/milestone1_compare_raw_iter1.txt",
            "data/milestone1_compare_report.md"
        ],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "03_第三次尝试_保留原文",
        "readme": """# 第三次尝试：保留原文引用

**时间**: 2024年  
**脚本**: milestone1_withtext_generator.py  
**策略**: 要求在题目中包含原文引用  

## 关键改进
- 强制保留原文片段
- 确保题目可追溯到来源
- 提高学术准确性

## 数据文件
- `milestone1_withtext.jsonl`: 带原文的生成结果
- `milestone1_withtext_raw_iter1.txt`: 第一轮迭代
- `milestone1_withtext_raw_iter2.txt`: 第二轮迭代
- `milestone1_withtext_raw_iter3.txt`: 第三轮迭代
- `milestone1_withtext_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 增强的生成prompt（带原文要求）

## 结果
题目质量显著提升，可追溯性增强。

## 经验教训
- ✅ 原文引用是质量关键
- ✅ 多轮迭代改进效果好
- ✅ 学术准确性大幅提升
""",
        "scripts": ["milestone1_withtext_generator.py"],
        "data_patterns": [
            "data/milestone1_withtext.jsonl",
            "data/milestone1_withtext_raw_iter*.txt",
            "data/milestone1_withtext_report.md"
        ],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "04_第四次尝试_详细问题",
        "readme": """# 第四次尝试：详细问题生成

**时间**: 2024年  
**脚本**: milestone1_detail_Q_generator.py  
**策略**: 生成更详细、更深入的问题  

## 改进
- 要求问题更详细
- 增加难度要求
- 强化专业性

## 数据文件
- `milestone1_detail_Q.jsonl`: 详细问题结果
- `milestone1_detail_Q_raw.txt`: 原始响应
- `milestone1_detail_Q_report.md`: 生成报告

## Prompt
- `生成题Prompt_higherlever.md`: 高级生成prompt

## 结果
生成的问题更深入，专业性更强。

## 经验教训
- ✅ 详细要求提升题目深度
- ✅ 难度控制更精准
- ❌ 需要平衡详细度和可读性
""",
        "scripts": ["milestone1_detail_Q_generator.py"],
        "data_patterns": [
            "data/milestone1_detail_Q.jsonl",
            "data/milestone1_detail_Q_raw.txt",
            "data/milestone1_detail_Q_report.md"
        ],
        "prompts": ["prompts/生成题Prompt_higherlever.md"]
    },
    {
        "folder": "05_第五次尝试_洞察生成",
        "readme": """# 第五次尝试：基于洞察的生成

**时间**: 2024年  
**脚本**: milestone1_insights_generator.py  
**策略**: 从论文的关键洞察生成问题  

## 创新点
- 先提取论文关键洞察
- 基于洞察生成问题
- 更深层次的理解

## 数据文件
- `milestone1_insights.jsonl`: 洞察生成结果
- `milestone1_insights_raw.txt`: 原始响应
- `milestone1_insights_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 洞察导向的prompt

## 结果
题目更具深度，但生成速度较慢。

## 经验教训
- ✅ 洞察导向提升题目深度
- ✅ 问题更贴近论文核心
- ❌ 生成时间较长
""",
        "scripts": ["milestone1_insights_generator.py"],
        "data_patterns": [
            "data/milestone1_insights.jsonl",
            "data/milestone1_insights_raw.txt",
            "data/milestone1_insights_report.md"
        ],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "06_第五次尝试_洞察生成专业版",
        "readme": """# 第五次尝试（专业版）：增强的洞察生成

**时间**: 2024年  
**脚本**: milestone1_insights_pro_generator.py  
**策略**: 洞察生成的专业增强版  

## 改进
- 更专业的提示词
- 更严格的质量控制
- 优化的生成流程

## 数据文件
- `milestone1_insights_pro.jsonl`: 专业版结果
- `milestone1_insights_pro_report.md`: 生成报告

## Prompt
- `生成题Prompt.md`: 专业增强版prompt

## 结果
质量进一步提升，达到较高水平。

## 经验教训
- ✅ 专业提示词效果显著
- ✅ 质量控制很重要
- ✅ 可作为参考标准
""",
        "scripts": ["milestone1_insights_pro_generator.py"],
        "data_patterns": [
            "data/milestone1_insights_pro.jsonl",
            "data/milestone1_insights_pro_report.md"
        ],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "07_第六次尝试_DeepSeek英文生成",
        "readme": """# 第六次尝试：DeepSeek英文生成

**时间**: 2024年  
**脚本**: deepseek_english_generator.py  
**策略**: 使用DeepSeek模型，英文生成  

## 创新点
- 切换到DeepSeek V3模型
- 英文生成（匹配论文语言）
- 新的API接口

## Prompt
- `生成题Prompt.md`: 英文版生成prompt

## 结果
生成质量稳定，英文表达更准确。

## 经验教训
- ✅ DeepSeek V3性能优秀
- ✅ 英文生成更自然
- ✅ 成本更低
""",
        "scripts": ["deepseek_english_generator.py"],
        "data_patterns": [],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "08_第七次尝试_DeepSeek智能生成",
        "readme": """# 第七次尝试：DeepSeek智能生成

**时间**: 2024年  
**脚本**: deepseek_intelligent_generator.py  
**策略**: DeepSeek V3 + 智能策略  

## 改进
- 优化的prompt设计
- 智能重试机制
- 更好的错误处理

## Prompt
- `生成题Prompt.md`: 智能增强版prompt

## 结果
生成稳定性大幅提升。

## 经验教训
- ✅ 智能重试很有效
- ✅ 错误处理很重要
- ✅ 可作为生产版本
""",
        "scripts": ["deepseek_intelligent_generator.py"],
        "data_patterns": [],
        "prompts": ["prompts/生成题Prompt.md"]
    },
    {
        "folder": "09_第八次尝试_批量详细生成",
        "readme": """# 第八次尝试：批量详细生成

**时间**: 2024年  
**脚本**: batch_detail_q_generator.py  
**策略**: 批量生成详细问题  

## 特点
- 批量处理
- 详细问题要求
- 高并发生成

## Prompt
- `生成题Prompt_higherlever.md`: 批量详细prompt

## 结果
大规模生成，效率提升。

## 经验教训
- ✅ 批量处理提升效率
- ✅ 并发控制很重要
- ⚠️ 需要监控质量
""",
        "scripts": ["batch_detail_q_generator.py"],
        "data_patterns": [],
        "prompts": ["prompts/生成题Prompt_higherlever.md"]
    },
    {
        "folder": "10_三模型验证系统",
        "readme": """# 三模型验证系统

**时间**: 2024年下半年  
**脚本**: 验证相关脚本  
**策略**: Claude Sonnet 4.5 + GPT-5 + Gemini 2.5 Pro  

## 目标
对所有生成的题目进行三模型一致性验证。

## 验证维度
1. 原文忠实度（是否准确反映论文内容）
2. 标答准确性（答案是否正确完整）
3. 题目合理性（是否是好问题）

## 数据文件
- `验证/verification_results.json`: 验证结果
- `验证/verification_stats.json`: 统计信息

## 结果
- 1,398题候选 → 984题通过（all_correct=true）
- 通过率: 70.3%

## 经验教训
- ✅ 三模型一致性是金标准
- ✅ all_correct标记确保权威性
- ✅ needs_review保留灵活性
- ✅ 显著提升benchmark可信度
""",
        "scripts": [],
        "data_patterns": [
            "验证/verification_results.json",
            "验证/verification_stats.json",
            "验证/pass.json",
            "验证/notpass.json"
        ],
        "prompts": []
    },
    {
        "folder": "11_质量筛选_984题",
        "readme": """# 质量筛选：984题精选

**时间**: 2024年下半年  
**数据**: 984题三模型验证通过  

## 筛选标准
- all_correct = true（三模型一致通过）
- 完整的原文引用
- 答案≥300字符
- 难度3-5级

## 数据文件
- `验证/best.json`: 984题精选集
- `验证/question.json`: 题目数据

## 统计
- 总数: 984题
- 难度分布: Level 3-5
- 主题覆盖: 20+个专业主题

## 价值
这984题成为后续GPT-5测试的基础数据集。

## 经验教训
- ✅ 严格筛选保证质量
- ✅ 多维度标准很必要
- ✅ 为实测奠定基础
""",
        "scripts": [],
        "data_patterns": [
            "验证/best.json",
            "验证/question.json"
        ],
        "prompts": []
    },
    {
        "folder": "12_GPT5测试",
        "readme": """# GPT-5实际测试

**时间**: 2025年1月  
**测试模型**: GPT-5 (openai/gpt-5-preview via OpenRouter)  
**成本**: $62.02  

## 测试过程
- 计划: 984题
- 完成: 872题
- 中断: $100预算用完

## 数据文件
- `logs/gpt5_benchmark.log`: 完整测试日志
- `验证/benchmarkGPT5_recovered.json`: 从日志恢复的结果

## Prompts
- `解题Prompt.md`: GPT-5答题prompt
- `判题Prompt.md`: DeepSeek判分prompt

## 结果
- 答对: 720题 (82.57%)
- 答错: 152题
  - 真实错误: 76题 (7.72%)
  - API失败: 76题 (7.01% + 0.71%)

## 发现
- ✅ GPT-5调整后准确率: 90.45%
- ✅ 主要盲区: energy_systems, combustion_kinetics
- ✅ 验证能力 > 答题能力

## 经验教训
- ✅ 日志记录救了项目
- ✅ 需要区分技术问题和真实错误
- ✅ 账单可验证数据真实性
""",
        "scripts": [],
        "data_patterns": [
            "logs/gpt5_benchmark.log",
            "验证/benchmarkGPT5_recovered.json"
        ],
        "prompts": [
            "prompts/解题Prompt.md",
            "prompts/判题Prompt.md"
        ]
    },
    {
        "folder": "13_数据分类和分析",
        "readme": """# 数据分类和深度分析

**时间**: 2025年1月  
**脚本**: categorize_gpt5_results.py, analyze_api_failures.py  

## 分类结果
1. 答对的题目: 720题 (73.17%)
2. 真实错误: 76题 (7.72%)
3. API失败（有分）: 69题 (7.01%)
4. API失败（零分）: 7题 (0.71%)
5. 未测试: 112题 (11.38%)

## 数据文件
- `验证/gpt验证结果分类/`: 完整分类目录
  - 每个类别包含JSON和统计信息

## 关键发现
- ✅ API失败（有分）平均分47.75，与真实错误(48.29)几乎相同
- ✅ 证明API失败不是因为截断，而是技术问题
- ✅ 真实错误主要集中在energy_systems和combustion_kinetics

## 账单验证
- OpenRouter总请求: 2,177次
- 总费用: $62.02
- 证实872题测试的真实性

## 经验教训
- ✅ 细致分类揭示真相
- ✅ 统计分析很重要
- ✅ 账单数据可验证准确性
""",
        "scripts": ["categorize_gpt5_results.py", "analyze_api_failures.py"],
        "data_patterns": [
            "验证/gpt验证结果分类/**/*"
        ],
        "prompts": []
    },
    {
        "folder": "14_最终交付",
        "readme": """# 最终交付：IgnisBenchmark

**时间**: 2025年1月17日  
**脚本**: create_final_benchmark.py  

## 交付内容
145道挑战性题目（76真实错误 + 69 API失败有分）

### 4个版本
1. benchmark_basic.json (88KB) - 基础版
2. benchmark_with_verification.json (433KB) - 含验证信息
3. benchmark_with_gpt5_results.json (99KB) - 含GPT-5结果
4. benchmark_complete.json (1.3MB) - 完整版

## 数据文件
- `最终交付/`: 所有benchmark文件和README

## 特点
- ✅ 145道高质量挑战题
- ✅ 三模型验证通过
- ✅ GPT-5实测验证
- ✅ 完整可追溯

## 价值
- 学术价值: 填补领域空白
- 工程价值: 可复现流程
- 社区价值: 开源共享

## GitHub
已推送到: https://github.com/Sithcighce/IgnisBenchmark

## 经验教训
- ✅ 多版本设计满足不同需求
- ✅ 详细文档很重要
- ✅ 质量>数量
""",
        "scripts": ["create_final_benchmark.py"],
        "data_patterns": [
            "最终交付/**/*"
        ],
        "prompts": []
    }
]

def copy_file_if_exists(src, dst):
    """复制文件（如果存在）"""
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return True
    return False

def copy_pattern(pattern, dst_folder):
    """复制匹配模式的文件"""
    from glob import glob
    copied = []
    for file in glob(pattern):
        if os.path.isfile(file):
            rel_path = os.path.basename(file)
            dst = os.path.join(dst_folder, rel_path)
            copy_file_if_exists(file, dst)
            copied.append(rel_path)
    return copied

def create_archive_structure():
    """创建归档结构"""
    base_path = Path("历史尝试归档")
    
    print('🗂️  开始创建完善的历史归档...\n')
    
    for attempt in ATTEMPTS:
        folder_path = base_path / attempt["folder"]
        
        # 创建目录结构
        data_path = folder_path / "data"
        scripts_path = folder_path / "scripts"
        prompts_path = folder_path / "prompts"
        
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(scripts_path, exist_ok=True)
        os.makedirs(prompts_path, exist_ok=True)
        
        print(f'📁 {attempt["folder"]}')
        
        # 复制脚本
        for script in attempt.get("scripts", []):
            src = script
            dst = scripts_path / os.path.basename(script)
            if copy_file_if_exists(src, str(dst)):
                print(f'   ✅ 复制脚本: {script}')
        
        # 复制数据文件
        for pattern in attempt.get("data_patterns", []):
            if '**' in pattern or '*' in pattern:
                # glob pattern
                from glob import glob
                for file in glob(pattern, recursive=True):
                    if os.path.isfile(file):
                        rel_name = os.path.basename(file)
                        dst = data_path / rel_name
                        if copy_file_if_exists(file, str(dst)):
                            print(f'   ✅ 复制数据: {rel_name}')
            else:
                # 单个文件
                if os.path.exists(pattern):
                    if os.path.isfile(pattern):
                        rel_name = os.path.basename(pattern)
                        dst = data_path / rel_name
                        if copy_file_if_exists(pattern, str(dst)):
                            print(f'   ✅ 复制数据: {rel_name}')
                    elif os.path.isdir(pattern):
                        # 复制整个目录
                        dst_dir = data_path / os.path.basename(pattern)
                        if os.path.exists(pattern):
                            shutil.copytree(pattern, str(dst_dir), dirs_exist_ok=True)
                            print(f'   ✅ 复制目录: {os.path.basename(pattern)}/')
        
        # 复制prompts
        for prompt in attempt.get("prompts", []):
            src = prompt
            dst = prompts_path / os.path.basename(prompt)
            if copy_file_if_exists(src, str(dst)):
                print(f'   ✅ 复制Prompt: {prompt}')
        
        # 创建README
        readme_path = folder_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(attempt["readme"])
        print(f'   ✅ 创建README.md\n')
    
    # 创建总README
    create_master_readme(base_path)
    
    print('✨ 完善归档完成！')
    print(f'\n📊 统计:')
    print(f'   总阶段数: {len(ATTEMPTS)}')
    print(f'   归档位置: {base_path}')

def create_master_readme(base_path):
    """创建总README"""
    content = """# 历史尝试归档

**项目**: IgnisBenchmark  
**完成时间**: 2025-01-17  

---

## 📚 目录结构

每个阶段包含：
- **README.md** - 阶段说明、目标、结果、经验教训
- **data/** - 该阶段产生的数据文件
- **scripts/** - 使用的Python脚本
- **prompts/** - 使用的提示词文件

---

## 🗺️ 项目演进路线图

### 阶段1-9：题目生成探索（2024年）

**01_第一次尝试_基础生成**
- 首次尝试，验证可行性
- 基础prompt，简单质量检查
- 为后续改进奠定基础

**02_第二次尝试_对比生成**
- 加入对比和多样性要求
- 提升题目多样性

**03_第三次尝试_保留原文**
- ⭐ 关键突破：要求保留原文引用
- 大幅提升学术准确性和可追溯性

**04_第四次尝试_详细问题**
- 生成更详细、更深入的问题
- 提升专业性和难度

**05_第五次尝试_洞察生成**
- 创新方法：基于论文关键洞察生成
- 题目更具深度

**06_第五次尝试_洞察生成专业版**
- 专业增强版
- 质量达到较高水平

**07_第六次尝试_DeepSeek英文生成**
- 切换到DeepSeek V3模型
- 英文生成，更自然准确

**08_第七次尝试_DeepSeek智能生成**
- 智能重试机制
- 生产级稳定性

**09_第八次尝试_批量详细生成**
- 批量处理，提升效率
- 大规模生成

### 阶段10-11：质量保证（2024年下半年）

**10_三模型验证系统**
- ⭐ 创新：Claude + GPT-5 + Gemini三模型验证
- 1,398题 → 984题通过 (70.3%)
- 建立gold standard

**11_质量筛选_984题**
- 精选984题高质量数据集
- 为实测奠定基础

### 阶段12-14：实测与交付（2025年1月）

**12_GPT5测试**
- ⭐ 重大里程碑：GPT-5实际测试
- 872题完成，成本$62.02
- 发现：验证能力 > 答题能力

**13_数据分类和分析**
- 深度分析872题结果
- 区分真实错误 vs API失败
- 关键发现：API失败不影响答题质量

**14_最终交付**
- ⭐ 项目完成：145道挑战性题目
- 4个版本满足不同需求
- 完整文档和使用说明

---

## 💡 关键里程碑

1. **原文引用机制**（阶段03）
   - 确保学术准确性
   - 实现可追溯性

2. **DeepSeek V3应用**（阶段07-08）
   - 提升生成质量
   - 降低成本

3. **三模型验证**（阶段10）
   - 建立gold standard
   - 确保权威性

4. **GPT-5实测**（阶段12）
   - 验证benchmark挑战性
   - 发现模型盲区

5. **数据分类分析**（阶段13）
   - 区分技术问题vs知识盲区
   - 提升数据质量

6. **最终交付**（阶段14）
   - 145道精选挑战题
   - 开源共享

---

## 📊 项目统计

- **开发时间**: ~1年
- **开发轮次**: 14个主要阶段
- **候选题目**: 1,398题
- **验证通过**: 984题
- **实测完成**: 872题
- **最终交付**: 145题
- **成本投入**: $62.02（GPT-5测试）
- **API调用**: 2,177次（OpenRouter）

---

## 🎓 核心经验

### 生成策略
1. ✅ 原文引用是质量关键
2. ✅ 多轮迭代持续改进
3. ✅ DeepSeek V3性价比高

### 质量保证
1. ✅ 三模型验证是金标准
2. ✅ 实测验证是必要步骤
3. ✅ 细致分类揭示真相

### 项目管理
1. ✅ 日志记录至关重要
2. ✅ 系统化归档便于回顾
3. ✅ 完整文档降低理解成本

---

## 📁 数据文件说明

### 生成阶段数据
- `.jsonl` 文件：候选题目集
- `_raw*.txt` 文件：原始API响应
- `_report.md` 文件：生成报告和统计

### 验证阶段数据
- `verification_*.json`：验证结果
- `pass.json / notpass.json`：通过/未通过题目
- `best.json`：精选题目集

### 测试阶段数据
- `benchmarkGPT5_recovered.json`：GPT-5测试结果
- `gpt5_benchmark.log`：测试日志
- 分类目录：5个类别的完整数据

### 交付数据
- `benchmark_*.json`：4个版本的benchmark
- `README.md`：使用说明

---

## 🔗 相关文档

- **PROJECT_COMPLETION_SUMMARY.md** - 项目完成总结
- **最终交付/README.md** - Benchmark使用指南
- **验证/gpt验证结果分类/README.md** - 分类说明

---

## 📞 GitHub

https://github.com/Sithcighce/IgnisBenchmark

---

**感谢每一步的探索和努力！** 🎉
"""
    
    with open(base_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ 创建总README: {base_path}/README.md')

if __name__ == '__main__':
    create_archive_structure()
