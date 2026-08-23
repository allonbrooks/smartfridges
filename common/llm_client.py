"""
LLM API 统一客户端。

当前使用 DeepSeek API（兼容 OpenAI 协议），
切换模型只需修改 MODEL 常量。
支持视觉识别（GLM-4V 等兼容 OpenAI 协议的视觉模型）。
"""
import os
import base64
import logging
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
MODEL = 'deepseek-chat'
TIMEOUT = 10
MAX_RETRIES = 2

# 视觉模型配置（用于拍照识别）
VISION_API_KEY = os.getenv('VISION_API_KEY', DEEPSEEK_API_KEY)
VISION_BASE_URL = os.getenv('VISION_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
VISION_MODEL = os.getenv('VISION_MODEL', 'glm-4v-flash')


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

    def vision_chat(self, messages, image_base64, temperature=0.3, max_tokens=1024):
        """调用视觉 LLM（图片+文字多模态输入）

        Args:
            messages: 对话消息列表（不含图片，图片通过 image_base64 传入）
            image_base64: base64 编码的图片数据
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            str: LLM 返回的文本内容
        """
        # 构建带图片的消息
        vision_messages = []
        for msg in messages:
            content = msg.get('content', '')
            vision_messages.append({
                'role': msg.get('role', 'user'),
                'content': [
                    {'type': 'text', 'text': content},
                ],
            })

        # 在第一张图片前插入图片预览指示
        if vision_messages and image_base64:
            last_user_msg = vision_messages[-1]
            last_user_msg['content'].insert(0, {
                'type': 'image_url',
                'image_url': {'url': f'data:image/jpeg;base64,{image_base64}'},
            })

        vision_client = OpenAI(
            api_key=VISION_API_KEY,
            base_url=VISION_BASE_URL,
            timeout=TIMEOUT,
        )

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = vision_client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=vision_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return resp.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(f'视觉 LLM 调用失败 (第{attempt + 1}次): {e}')
                if attempt < MAX_RETRIES:
                    time.sleep(1)
        raise last_error