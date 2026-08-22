"""
LLM API 统一客户端。

当前使用 DeepSeek API（兼容 OpenAI 协议），
切换模型只需修改 MODEL 常量。
"""
import os
import logging
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
MODEL = 'deepseek-chat'
TIMEOUT = 10
MAX_RETRIES = 2


class LLMClient:
    """LLM 调用客户端，封装重试和超时"""

    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            timeout=TIMEOUT,
        )

    def chat(self, messages, temperature=0.3, max_tokens=1024):
        """调用 LLM 对话接口"""
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return resp.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(f'LLM 调用失败 (第{attempt + 1}次): {e}')
                if attempt < MAX_RETRIES:
                    time.sleep(1)
        raise last_error