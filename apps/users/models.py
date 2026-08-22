import uuid
from django.db import models


class FamilyGroup(models.Model):
    """家庭组"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('家庭名称', max_length=64)
    invite_code = models.CharField('邀请码', max_length=16, unique=True)
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True,
        related_name='created_families', verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '家庭组'
        verbose_name_plural = '家庭组'

    def __str__(self):
        return self.name


class User(models.Model):
    """微信用户"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    openid = models.CharField('微信 OpenID', max_length=64, unique=True)
    nickname = models.CharField('微信昵称', max_length=64, default='')
    avatar_url = models.URLField('微信头像', max_length=512, default='', blank=True)
    current_family = models.ForeignKey(
        FamilyGroup, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='active_users', verbose_name='当前活跃家庭'
    )
    created_at = models.DateTimeField('注册时间', auto_now_add=True)
    last_active = models.DateTimeField('最后活跃时间', auto_now=True)

    class Meta:
        verbose_name = '微信用户'
        verbose_name_plural = '微信用户'

    def __str__(self):
        return self.nickname or self.openid[:12]


class Member(models.Model):
    """家庭成员"""
    class Role(models.TextChoices):
        ADMIN = 'admin', '管理员'
        MEMBER = 'member', '普通成员'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    family = models.ForeignKey(FamilyGroup, on_delete=models.CASCADE, related_name='members')
    role = models.CharField('角色', max_length=16, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField('加入时间', auto_now_add=True)

    class Meta:
        verbose_name = '家庭成员'
        verbose_name_plural = '家庭成员'
        unique_together = ('user', 'family')

    def __str__(self):
        return f'{self.user.nickname} @ {self.family.name}'