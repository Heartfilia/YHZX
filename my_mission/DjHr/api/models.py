from django.db import models
import datetime


# Create your models here.
class Info(models.Model):
    info = models.CharField(max_length=100, verbose_name='招聘信息', help_text='招聘信息')
    isRemind = models.BooleanField(default=True, verbose_name='是否提醒', help_text='是否提醒:1 为提醒，其他值不提醒，建议不提醒的值设置为 0')
    lateRemind = models.IntegerField(default=2, verbose_name='触发天数', help_text='触发天数')
    account = models.CharField(max_length=30, default='1', verbose_name='账号信息', help_text='账号信息默认:1>广州市银河在线饰品有限公司 2>广州外宝电子商务有限公司')
    platform = models.CharField(max_length=20, default='智联', verbose_name='招聘平台', help_text='招聘平台默认:智联,可选参数：前程无忧')
    # lastPost = models.CharField(max_length=50, null=True, verbose_name='上次发布', help_text='上次发布')

    def __str__(self):
        return self.info

    class Meta:
        db_table = 'Info'
        verbose_name = '刷新信息'
        verbose_name_plural = verbose_name
