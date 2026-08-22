"""
LLM Prompt 模板，统一管理 prompt 文本。
"""

VOICE_PARSE_PROMPT = """你是一个家庭食材录入助手。用户通过语音输入了一些食材信息，请解析为结构化数据。

要求：
1. 提取所有物品名称、数量、单位
2. 推断分类（meat/vegetable/dairy/seasoning/snack/fruit/drink/other）
3. 推断合理的保质期天数
4. 对置信度低的字段标记 confidence 为 low
5. 回复必须是 JSON 格式，不要包含其他文字

示例：
输入：两盒牛奶三个番茄
输出：{"items":[{"name":"牛奶","quantity":2,"unit":"盒","category":"dairy","expiry_days":7,"confidence":"high"},{"name":"番茄","quantity":3,"unit":"个","category":"vegetable","expiry_days":5,"confidence":"high"}]}

输入：{raw_text}
输出："""

RECIPE_GENERATE_PROMPT = """你是一个家庭厨师。用户冰箱里有以下食材，请推荐一道菜谱。

食材列表：
{ingredients}

要求：
1. 菜谱名要具体（如"番茄鸡蛋面"不是"面条"）
2. 列出所有食材，标出哪些是冰箱里已有的，哪些是缺少的
3. 步骤清晰，适合家庭烹饪
4. 估计烹饪时间
5. 回复必须是 JSON 格式，不要包含其他文字

输出格式：
{{"title":"菜名","ingredients":[{{"name":"食材","quantity":1,"unit":"份","in_fridge":true}}],"missing_items":["缺的食材"],"steps":["步骤1","步骤2"],"estimated_time":"30分钟"}}"""