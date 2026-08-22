import json
import logging
from common.llm_client import LLMClient
from common.prompts import RECIPE_GENERATE_PROMPT

logger = logging.getLogger(__name__)


def generate_recipe(item_ids: list, preferences: str = '') -> dict:
    """
    根据冰箱食材生成菜谱。

    返回: {
        'title': str,
        'ingredients': [{'name': str, 'quantity': int, 'unit': str, 'in_fridge': bool}],
        'missing_items': [str],
        'steps': [str],
        'estimated_time': str
    }
    """
    from apps.foods.models import FoodItem
    items = FoodItem.objects.filter(id__in=item_ids, is_consumed=False)
    if not items:
        return {'error': '未找到选中的食材或食材已消耗'}

    ingredients_text = ', '.join(f'{item.name} x{item.quantity}{item.unit}' for item in items)
    if preferences:
        ingredients_text += f'\n偏好：{preferences}'

    client = LLMClient()
    prompt = RECIPE_GENERATE_PROMPT.format(ingredients=ingredients_text)
    try:
        result = client.chat([
            {'role': 'system', 'content': '你是一个家庭厨师，只输出 JSON。'},
            {'role': 'user', 'content': prompt},
        ])
    except Exception as e:
        logger.error(f'LLM 调用失败: {e}')
        return {
            'title': '解析失败',
            'ingredients': [{'name': item.name, 'quantity': item.quantity, 'unit': item.unit, 'in_fridge': True} for item in items],
            'missing_items': [],
            'steps': ['LLM 服务暂时不可用，请稍后重试'],
            'estimated_time': 'N/A',
        }
    try:
        recipe = json.loads(result)
        # 确保必填字段
        recipe.setdefault('title', '自定义菜谱')
        recipe.setdefault('ingredients', [])
        recipe.setdefault('missing_items', [])
        recipe.setdefault('steps', [])
        recipe.setdefault('estimated_time', '30分钟')
        # 标记冰箱里已有的食材
        fridge_names = {item.name for item in items}
        for ing in recipe['ingredients']:
            ing['in_fridge'] = ing['name'] in fridge_names
        return recipe
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f'菜谱生成 JSON 解析失败: {e}, 原始响应: {result}')
        return {
            'title': '解析失败',
            'ingredients': [{'name': item.name, 'quantity': item.quantity, 'unit': item.unit, 'in_fridge': True} for item in items],
            'missing_items': [],
            'steps': ['LLM 解析失败，请稍后重试'],
            'estimated_time': 'N/A',
        }