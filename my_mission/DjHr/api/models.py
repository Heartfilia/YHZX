from django.db import models
import datetime


# Create your models here.
class Info(models.Model):
    info = models.CharField(max_length=100, verbose_name='招聘信息', help_text='招聘信息')
    isRemind = models.BooleanField(default=True, verbose_name='是否提醒', help_text='是否提醒')
    lateRemind = models.IntegerField(default=2, verbose_name='触发天数', help_text='触发天数')

    def __str__(self):
        return self.info

    class Meta:
        db_table = 'Info'
        verbose_name = '刷新信息'
        verbose_name_plural = verbose_name
