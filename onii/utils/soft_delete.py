#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """默认过滤已软删除的记录"""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteAllManager(models.Manager):
    """包含软删除记录的 Manager"""
    pass


class SoftDeleteMixin(models.Model):
    """
    软删除混入类

    用法:
        class MyModel(SoftDeleteMixin, models.Model):
            name = models.CharField(max_length=100)

        MyModel.objects.all()        # 只返回未删除的
        MyModel.all_objects.all()    # 包含已删除的
        obj.delete()                 # 软删除
        obj.hard_delete()            # 真删除
        obj.restore()                # 恢复
    """

    is_deleted = models.BooleanField(default=False, verbose_name="是否删除", db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")

    objects = SoftDeleteManager()
    all_objects = SoftDeleteAllManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
