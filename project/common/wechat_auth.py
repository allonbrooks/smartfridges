"""
微信鉴权中间件。

从请求头 X-WX-OPENID（由微信云托管自动注入）获取用户标识，
自动创建或查询 User 记录，并注入到 request.wx_user。
"""
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


class WeChatAuthMiddleware(MiddlewareMixin):
    """通过 X-WX-OPENID 识别用户"""

    EXEMPT_PATHS = ['/admin/']

    def process_request(self, request):
        request.wx_user = None
        request.wx_family = None

        path = request.path_info
        if any(path.startswith(p) for p in self.EXEMPT_PATHS):
            return

        openid = request.META.get('HTTP_X_WX_OPENID', '')
        if not openid:
            return

        from apps.users.models import User
        user, created = User.objects.get_or_create(
            openid=openid,
            defaults={'nickname': f'用户{openid[:8]}'}
        )
        user.last_active = timezone.now()
        user.save(update_fields=['last_active'])
        request.wx_user = user

        if user.current_family_id:
            request.wx_family = user.current_family