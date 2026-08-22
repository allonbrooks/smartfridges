from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """统一错误响应格式"""
    response = exception_handler(exc, context)
    if response is not None:
        return Response(
            {'error': response.data, 'success': False},
            status=response.status_code
        )
    return Response(
        {'error': '服务器内部错误', 'success': False},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )