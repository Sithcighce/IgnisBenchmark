#!/usr/bin/env python3
"""
生成152道错题的可视化摘要
"""
import json

def main():
    # 加载数据
    with open(r'c:\Users\13031\Desktop\workspace\distillation_generation\验证\gpt5_incorrect_detailed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    incorrect = data['incorrect_questions_with_details']
    
    print(f"\n{'='*70}")
    print(f"152道错题最终确认报告")
    print(f"{'='*70}\n")
    
    print(f"✅ **确认**: 这152道题是:")
    print(f"   1. 来自 best.json (3家模型一致认可的高质量题目)")
    print(f"   2. 验证阶段: Claude 4.5 + GPT-5 + Gemini 2.5 都说 '题目正确'")
    print(f"   3. 基准测试: GPT-5 自己答题时答错了\n")
    
    print(f"{'='*70}")
    print(f"数据恢复情况")
    print(f"{'='*70}\n")
    
    print(f"✅ 成功恢复:")
    print(f"   - 题目ID: 152个")
    print(f"   - 题目文本: 152个")
    print(f"   - 标准答案: 152个")
    print(f"   - GPT-5分数: 152个")
    print(f"   - GPT-5回答长度: {sum(1 for q in incorrect if q['gpt5_result']['answer_length'] != 'unknown')} 个\n")
    
    print(f"❌ 无法恢复:")
    print(f"   - GPT-5的原始回答文本: 0个 (全部丢失)")
    print(f"   - DeepSeek的判分理由: 0个 (全部丢失)\n")
    
    print(f"{'='*70}")
    print(f"为什么会出现 '验证说对，答题答错' 的情况？")
    print(f"{'='*70}\n")
    
    print(f"💡 最可能的解释:\n")
    print(f"**验证任务 vs 回答任务是完全不同的！**\n")
    
    print(f"验证阶段 (GPT-5作为验证者):")
    print(f"   输入: 问题 + 标准答案 + 原文引用")
    print(f"   任务: 判断标准答案是否正确、有逻辑、有依据")
    print(f"   能力: 需要批判性思维、逻辑推理")
    print(f"   结果: ✅ 能判断出答案是对的\n")
    
    print(f"基准测试 (GPT-5作为答题者):")
    print(f"   输入: 只有问题（看不到标准答案和原文）")
    print(f"   任务: 自己从记忆中生成答案")
    print(f"   能力: 需要领域知识、准确记忆")
    print(f"   结果: ❌ 答错了 (知识盲区或记忆错误)\n")
    
    print(f"类比:")
    print(f"   就像一个老师能判断学生答案对不对（批改能力强）")
    print(f"   但自己考试可能也会做错题（知识有盲区）\n")
    
    print(f"{'='*70}")
    print(f"10道得0分的题目 (完全错误)")
    print(f"{'='*70}\n")
    
    zero_score = [q for q in incorrect if q['gpt5_result']['score'] == 0]
    for i, q in enumerate(zero_score, 1):
        print(f"{i}. {q['question_id']}")
        print(f"   难度{q['difficulty']} | {q['topic']} | {q['type']}")
        print(f"   回答长度: {q['gpt5_result']['answer_length']}")
        print(f"   问题: {q['question_text'][:80]}...")
        print()
    
    print(f"{'='*70}")
    print(f"关键统计")
    print(f"{'='*70}\n")
    
    # 统计回答长度
    with_length = [q for q in incorrect if q['gpt5_result']['answer_length'] != 'unknown']
    without_length = [q for q in incorrect if q['gpt5_result']['answer_length'] == 'unknown']
    
    print(f"有回答长度记录: {len(with_length)} 题")
    print(f"无回答长度记录: {len(without_length)} 题\n")
    
    # 0分题目中有多少有回答
    zero_with_answer = [q for q in zero_score if q['gpt5_result']['answer_length'] != 'unknown']
    print(f"0分题目中:")
    print(f"   有回答: {len(zero_with_answer)} 题")
    print(f"   无回答记录: {len(zero_score) - len(zero_with_answer)} 题")
    print(f"   → 说明有些0分可能是GPT-5 API失败返回空字符串\n")
    
    # 分数段统计
    score_ranges = {
        '0-20': [q for q in incorrect if q['gpt5_result']['score'] <= 20],
        '21-40': [q for q in incorrect if 21 <= q['gpt5_result']['score'] <= 40],
        '41-60': [q for q in incorrect if 41 <= q['gpt5_result']['score'] <= 60],
        '61-80': [q for q in incorrect if 61 <= q['gpt5_result']['score'] <= 80]
    }
    
    print(f"分数分布:")
    for range_name, questions in score_ranges.items():
        print(f"   {range_name}分: {len(questions)} 题 ({len(questions)/len(incorrect)*100:.1f}%)")
    print()
    
    print(f"{'='*70}")
    print(f"最终结论")
    print(f"{'='*70}\n")
    
    print(f"1. ✅ 题目质量很高 (3家模型一致认可)")
    print(f"2. ⚠️  GPT-5验证能力 > 回答能力")
    print(f"3. ❌ 关键数据永久丢失 (GPT-5回答文本)")
    print(f"4. 💡 发现重要现象: 验证 ≠ 回答")
    print(f"5. 💰 花费~$100，教训深刻\n")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
