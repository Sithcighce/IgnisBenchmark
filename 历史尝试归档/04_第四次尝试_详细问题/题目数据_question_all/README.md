# 燃烧科学领域问题数据集

**最终完成**: 2025-10-15  
**问题总数**: 1,398题（875通过 + 523未通过）  
**文献覆盖**: 299篇（100%覆盖）  

---

## 🚀 快速开始

### 查看人类可读版本
```bash
cd question_all_md
ls *.md                      # 列出所有通过的问题
ls *_notpass.md              # 列出所有未通过的问题
```

### 查看机器可读版本
```bash
cd question_all
ls */pass.json               # 所有通过的问题JSON
ls */not_pass.json           # 所有未通过的问题JSON
```

---

## 📁 文件结构

```
├── question_all/                    # JSON格式（机器可读）
│   ├── 文献A/
│   │   ├── 文献A.txt               # 原文
│   │   ├── pass.json               # 通过的问题
│   │   └── not_pass.json           # 未通过的问题
│   ├── 文献B/
│   │   └── ...
│   └── CONSOLIDATION_REPORT.md     # 详细报告
│
├── question_all_md/                 # Markdown格式（人类可读）
│   ├── 文献A.md                    # 通过的问题
│   ├── 文献A_notpass.md            # 未通过的问题
│   └── ...
│
└── FINAL_COMPLETION_REPORT.md      # 🎯 总结报告（推荐阅读）
```

---

## 📊 数据概览

| 指标 | 数值 |
|------|------|
| 总文献数 | 299 |
| ≥5题的文献 | 235 (78.6%) |
| 总问题数 | 1,398 |
| 通过率 | 62.6% (875/1398) |
| MD文件数 | 422 |

---

## 📖 推荐阅读顺序

1. **FINAL_COMPLETION_REPORT.md** - 总体完成情况
2. **question_all/CONSOLIDATION_REPORT.md** - 详细的文献级统计
3. **question_all_md/[任意文献].md** - 浏览具体问题

---

## 💡 使用示例

### Python读取所有通过的问题
```python
import json
from pathlib import Path

all_questions = []
for folder in Path("question_all").iterdir():
    pass_file = folder / "pass.json"
    if pass_file.exists():
        with open(pass_file) as f:
            all_questions.extend(json.load(f))

print(f"Total: {len(all_questions)} questions")
```

### PowerShell统计
```powershell
# 统计每个文献的问题数
Get-ChildItem question_all -Directory | ForEach-Object {
    $pass = if (Test-Path "$_/pass.json") { 
        (Get-Content "$_/pass.json" | ConvertFrom-Json).Count 
    } else { 0 }
    $notpass = if (Test-Path "$_/not_pass.json") { 
        (Get-Content "$_/not_pass.json" | ConvertFrom-Json).Count 
    } else { 0 }
    [PSCustomObject]@{
        Name = $_.Name
        Pass = $pass
        NotPass = $notpass
        Total = $pass + $notpass
    }
} | Sort-Object -Property Total -Descending
```

---

## 🎯 质量保证

每道题经过三维质量检查：
- ✅ **领域聚焦**: 需要燃烧/传热/流体/CFD专业知识
- ✅ **答案正确**: 事实准确、机理正确、≥300字符
- ✅ **合规性**: 无元信息、无时效性、不过于宽泛

---

## 📞 联系方式

- 查看详细文档: `docs/`
- 问题反馈: 项目Issues
- 技术细节: `FINAL_COMPLETION_REPORT.md`

---

**数据集版本**: v1.0  
**生成模型**: DeepSeek V3  
**质量评级**: ⭐⭐⭐⭐⭐
