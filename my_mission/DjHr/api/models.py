from django.db import models
import datetime

pf = (
    (1, '智联'),
    (2, '前程无忧')
)

act = (
    (1, '广州市银河在线饰品有限公司'),
    (2, '广州外宝电子商务有限公司'),
    (3, '广州时时美电子商务有限公司')
)

# Create your models here.
class Info(models.Model):
    info = models.CharField(max_length=100, verbose_name='招聘信息')
    isRemind = models.BooleanField(default=True, verbose_name='是否提醒', help_text='是否提醒')
    lateRemind = models.IntegerField(default=2, verbose_name='触发天数', help_text='这个数值为最大触发提醒的天数，如 10 那么超过 10 天就会提醒')
    account = models.CharField(max_length=30, default='1', choices=act, verbose_name='账号信息', help_text='账号信息默认:广州市银河在线饰品有限公司')
    platform = models.CharField(max_length=10, default=1, choices=pf, verbose_name='招聘平台', help_text='招聘平台默认:智联,可选参数：前程无忧')
    lastFresh = models.CharField(max_length=50, null=True, verbose_name='上次刷新')

    def __str__(self):
        return self.info

    class Meta:
        db_table = 'Info'
        verbose_name = '刷新信息'
        verbose_name_plural = verbose_name

class Rate(models.Model):
    keyword = models.CharField(max_length=100, null=False, verbose_name='关键字信息', help_text='必填信息')
    pageinfo = models.IntegerField(default=0, verbose_name='页数信息', help_text='公司信息最先出现的页数,自己定义的时候需要默认输入0表示不在指定页数')
    posi_nums = models.IntegerField(default=0, verbose_name='岗位数量', help_text='这个岗位的总共的数量，自己定义的时候需要默认输入0表示未查询')
    plateform = models.CharField(max_length=10, default=1, choices=pf, verbose_name='平台信息')

    def __str__(self):
        return self.keyword

    class Meta:
        db_table = 'keyword'
        verbose_name = '排名信息'
        verbose_name_plural = verbose_name
