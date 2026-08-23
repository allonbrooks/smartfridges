from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RecipeGenerateSerializer
from .services.recipe_generator import generate_recipe


@api_view(['POST'])
def generate_recipe_view(request):
    """选中食材生成菜谱"""
    user = request.wx_user
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    serializer = RecipeGenerateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    recipe = generate_recipe(
        serializer.validated_data['item_ids'],
        serializer.validated_data.get('preferences', '')
    )
    if 'error' in recipe:
        return Response({'error': recipe['error'], 'success': False}, status=400)
    return Response({'data': recipe, 'success': True})