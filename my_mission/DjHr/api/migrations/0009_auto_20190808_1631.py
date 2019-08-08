# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-08-08 08:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20190808_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='account',
            field=models.CharField(default='1', help_text='账号信息默认:1>广州市银河在线饰品有限公司 2>广州外宝电子商务有限公司 3>广州时时美电子商务有限公司', max_length=30, verbose_name='账号信息'),
        ),
    ]