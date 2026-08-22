"""
语音语义解析服务。

接收微信语音识别后的文字，调用 LLM 解析为结构化物品数据。
"""
import json
import logging
from common.llm_client import LLMClient
from common.prompts import VOICE_PARSE_PROMPT

logger = logging.getLogger(__name__)


def parse_voice_text(raw_text: str) -> dict:
    """
    解析语音文字为结构化物品列表。

    返回: {
        'items': [{'name': str, 'quantity': int, 'unit': str, 'category': str, 'expiry_days': int, 'confidence': str}],
        'unclear_items': [],
        'suggestion': str
    }
    """
    try:
        client = LLMClient()
        prompt = VOICE_PARSE_PROMPT.format(raw_text=raw_text)
        result = client.chat([
            {'role': 'system', 'content': '你是一个食材解析助手，只输出 JSON。'},
            {'role': 'user', 'content': prompt},
        ])
        parsed = json.loads(result)
        items = parsed.get('items', [])
        unclear = [item for item in items if item.get('confidence') == 'low']
        clear = [item for item in items if item.get('confidence') != 'low']
        suggestion_items = ', '.join(str(i['quantity']) + i['unit'] + i['name'] for i in clear)
        return {
            'items': items,
            'unclear_items': unclear,
            'suggestion': f'确认录入 {suggestion_items}？'
        }
    except (json.JSONDecodeError, KeyError, TypeError, Exception) as e:
        logger.error(f'语音解析失败: {e}')
        return {
            'items': [{'name': raw_text, 'quantity': 1, 'unit': '个', 'category': 'other', 'expiry_days': 7, 'confidence': 'low'}],
            'unclear_items': [{'name': raw_text, 'quantity': 1, 'unit': '个', 'category': 'other', 'expiry_days': 7, 'confidence': 'low'}],
            'suggestion': f'解析失败，请确认 "{raw_text}" 是否正确？'
        }