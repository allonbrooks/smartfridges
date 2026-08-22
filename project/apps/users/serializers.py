from rest_framework import serializers
from .models import User, FamilyGroup, Member
import secrets
import string


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'openid', 'nickname', 'avatar_url', 'current_family_id', 'created_at']


class FamilyGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = FamilyGroup
        fields = ['id', 'name', 'invite_code', 'created_by_id', 'member_count', 'created_at']
        read_only_fields = ['invite_code', 'created_by_id', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.wx_user if request else None
        invite_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        family = FamilyGroup.objects.create(
            **validated_data, invite_code=invite_code, created_by=user
        )
        Member.objects.create(user=user, family=family, role=Member.Role.ADMIN)
        user.current_family = family
        user.save(update_fields=['current_family'])
        return family


class MemberSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.URLField(source='user.avatar_url', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'user_id', 'user_nickname', 'user_avatar', 'role', 'joined_at']


class JoinFamilySerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=16)