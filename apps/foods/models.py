import uuid
from django.db import models


class StorageSpace(models.Model):
    """存储空间/区域"""
    class ZoneType(models.TextChoices):
        COLD = 'cold', '冷藏'
        FROZEN = 'frozen', '冷冻'
        NORMAL = 'normal', '常温'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        'users.FamilyGroup', on_delete=models.CASCADE,
        related_name='storage_spaces', verbose_name='所属家庭'
    )
    name = models.CharField('名称', max_length=32)
    zone_type = models.CharField('类型', max_length=16, choices=ZoneType.choices)
    icon = models.CharField('图标名', max_length=32, default='box')
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '存储空间'
        verbose_name_plural = '存储空间'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f'{self.family.name} - {self.name}'


class FoodItem(models.Model):
    """食品物品"""
    class Category(models.TextChoices):
        MEAT = 'meat', '肉类'
        VEGETABLE = 'vegetable', '蔬菜'
        DAIRY = 'dairy', '乳制品'
        SEASONING = 'seasoning', '调料'
        SNACK = 'snack', '零食'
        FRUIT = 'fruit', '水果'
        DRINK = 'drink', '饮料'
        OTHER = 'other', '其他'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        'users.FamilyGroup', on_delete=models.CASCADE,
        related_name='food_items', verbose_name='所属家庭'
    )
    name = models.CharField('物品名', max_length=64)
    category = models.CharField('分类', max_length=16, choices=Category.choices, default=Category.OTHER)
    storage_space = models.ForeignKey(
        StorageSpace, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='items', verbose_name='存放位置'
    )
    barcode = models.CharField('条码', max_length=64, blank=True, default='')
    icon = models.CharField('图标名', max_length=32, blank=True, default='')
    quantity = models.IntegerField('剩余数量', default=1)
    unit = models.CharField('单位', max_length=8, default='个')
    expiry_date = models.DateField('过期日期')
    days_to_expire = models.IntegerField('保质期天数', help_text='录入时计算的保质期')
    added_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True,
        related_name='added_items', verbose_name='录入人'
    )
    note = models.TextField('备注', blank=True, default='')
    calories = models.IntegerField('卡路里(每100g)', null=True, blank=True, help_text='单位：kcal/100g')
    is_consumed = models.BooleanField('是否已消耗', default=False)
    consumed_at = models.DateTimeField('消耗时间', null=True, blank=True)
    created_at = models.DateTimeField('录入时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '食品物品'
        verbose_name_plural = '食品物品'
        indexes = [
            models.Index(fields=['family', 'expiry_date']),
            models.Index(fields=['family', 'storage_space']),
            models.Index(fields=['family', 'category']),
            models.Index(fields=['family', 'is_consumed']),
        ]

    def __str__(self):
        return f'{self.name} x{self.quantity}'


class BarcodeCache(models.Model):
    """条码缓存"""
    barcode = models.CharField('条码', max_length=64, primary_key=True)
    name = models.CharField('商品名', max_length=128)
    default_expiry_days = models.IntegerField('默认保质期天数', default=7)
    category = models.CharField('分类', max_length=16, choices=FoodItem.Category.choices, default=FoodItem.Category.OTHER)
    icon = models.CharField('图标名', max_length=32, blank=True, default='')
    last_queried = models.DateTimeField('最近查询时间', auto_now=True)
    query_count = models.IntegerField('查询次数', default=0)

    class Meta:
        verbose_name = '条码缓存'
        verbose_name_plural = '条码缓存'

    def __str__(self):
        return f'{self.name} ({self.barcode})'


class OperationLog(models.Model):
    """操作日志"""
    class Action(models.TextChoices):
        ADD = 'add', '新增'
        CONSUME = 'consume', '消耗'
        DELETE = 'delete', '删除'
        MODIFY = 'modify', '修改'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        'users.FamilyGroup', on_delete=models.CASCADE,
        related_name='operation_logs', verbose_name='家庭组'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True,
        related_name='operation_logs', verbose_name='操作人'
    )
    action = models.CharField('操作', max_length=16, choices=Action.choices)
    item = models.ForeignKey(
        FoodItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='operation_logs', verbose_name='操作物品'
    )
    item_name = models.CharField('物品名称快照', max_length=64, blank=True, default='')
    detail = models.CharField('详情', max_length=128, blank=True, default='')
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['family', 'created_at']),
        ]

    def __str__(self):
        return f'{self.get_action_display()} {self.item_name} by {self.user}'