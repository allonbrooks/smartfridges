import json
import logging
from common.llm_client import LLMClient
from common.prompts import RECIPE_GENERATE_PROMPT

logger = logging.getLogger(__name__)


def generate_recipe(item_ids: list, preferences: str = '') -> dict:
    """
    根据冰箱食材生成菜谱。

    返回: {
        'recipes': [
            {
                'title': str,
                'ingredients': [{'name': str, 'quantity': int, 'unit': str, 'in_fridge': bool}],
                'missing_items': [str],
                'steps': [str],
                'estimated_time': str,
                'suitable_for': str,
                'taste': str,
            }
        ]
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
        return _fallback_response(items)

    try:
        data = json.loads(result)
        recipes = data.get('recipes', [data])  # 兼容单菜谱旧格式
        for recipe in recipes:
            recipe.setdefault('title', '自定义菜谱')
            recipe.setdefault('ingredients', [])
            recipe.setdefault('missing_items', [])
            recipe.setdefault('steps', [])
            recipe.setdefault('estimated_time', '30分钟')
            recipe.setdefault('suitable_for', '适合全家')
            recipe.setdefault('taste', '家常')
            # 标记冰箱里已有的食材
            fridge_names = {item.name for item in items}
            for ing in recipe['ingredients']:
                ing['in_fridge'] = ing['name'] in fridge_names
        return {'recipes': recipes}
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f'菜谱生成 JSON 解析失败: {e}, 原始响应: {result}')
        return _fallback_response(items)


def _fallback_response(items):
    """LLM 不可用时的兜底响应"""
    return {
        'recipes': [{
            'title': '解析失败',
            'ingredients': [
                {'name': item.name, 'quantity': item.quantity, 'unit': item.unit, 'in_fridge': True}
                for item in items
            ],
            'missing_items': [],
            'steps': ['LLM 服务暂时不可用，请稍后重试'],
            'estimated_time': 'N/A',
            'suitable_for': '适合全家',
            'taste': '家常',
        }]
    }