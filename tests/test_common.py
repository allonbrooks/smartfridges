import pytest
from common.wechat_auth import WeChatAuthMiddleware
from common.pagination import StandardPagination
from common.llm_client import LLMClient
from common.prompts import VOICE_PARSE_PROMPT, RECIPE_GENERATE_PROMPT


class TestWeChatAuth:
    def test_exempt_admin_path(self):
        """/admin/ 路径跳过鉴权"""
        middleware = WeChatAuthMiddleware(lambda r: None)
        # 模拟请求
        class MockRequest:
            META = {}
            path_info = '/admin/'
        req = MockRequest()
        middleware.process_request(req)
        # 没有设置 X-WX-OPENID 也不会报错
        assert req.wx_user is None


class TestPagination:
    def test_standard_pagination_class(self):
        paginator = StandardPagination()
        assert paginator.page_size == 20
        assert paginator.page_size_query_param == 'page_size'
        assert paginator.max_page_size == 100


class TestPrompts:
    def test_voice_parse_prompt_contains_placeholder(self):
        assert '{raw_text}' in VOICE_PARSE_PROMPT

    def test_recipe_generate_prompt_contains_placeholder(self):
        assert '{ingredients}' in RECIPE_GENERATE_PROMPT


class TestLLMClient:
    def test_client_initialization(self):
        """验证客户端可以初始化（不调用 API）"""
        client = LLMClient()
        assert client is not None