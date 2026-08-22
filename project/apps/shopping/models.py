import uuid
from django.db import models


class ShoppingList(models.Model):
    """购物清单"""
    class Reason(models.TextChoices):
        MANUAL = 'manual', '手动添加'
        AUTO_PREDICTED = 'auto_predicted', '自动预测'
        RECIPE_REQUIRED = 'recipe_required', '菜谱所需'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        'users.FamilyGroup', on_delete=models.CASCADE,
        related_name='shopping_list', verbose_name='家庭组'
    )
    item_name = models.CharField('物品名', max_length=64)
    quantity = models.IntegerField('数量', default=1)
    unit = models.CharField('单位', max_length=8, default='个')
    reason = models.CharField('来源', max_length=20, choices=Reason.choices, default=Reason.MANUAL)
    is_purchased = models.BooleanField('是否已买', default=False)
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True,
        related_name='shopping_items', verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    purchased_at = models.DateTimeField('购买时间', null=True, blank=True)

    class Meta:
        verbose_name = '购物清单'
        verbose_name_plural = '购物清单'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.item_name} x{self.quantity}'