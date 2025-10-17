# GPT-5实际测试

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
