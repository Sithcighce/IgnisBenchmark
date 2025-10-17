# 第九阶段：三模型验证系统

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
