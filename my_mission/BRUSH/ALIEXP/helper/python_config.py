#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 11:34
# @Author  : Lodge

PROCESS_NUM = 2  # 进程数量
ACCOUNT_NUM = 10  # 每次拿账号的数量,进程数不要高于这个数

CHROME_PORT = 16881
# chrome.exe --remote-debugging-port=16881 --user-data-dir="C:\selenium_ali_ad1\AutomationProfile"
LIMIT_PAGE = 5   # 页数超过了限定页数退出,限定多少页来处理这个广告(不包含当前页)
RECEIVERS = ''

API_GETS_GET = 'http://in131.gets.com:8383/api/index.php?sec=20171212getscn&act=getAliexpressAdvertisingAttack'
API_GETS_POST = 'http://in131.gets.com:8383/api/'

THIRD_ACCOUNT_GET = 'http://third.gets.com:8080/api/index.php?'

# 这里是后缀,拼接到上面的地址的
API_REPLY_LOG = 'index.php?sec=20171212getscn&act=modifyAliexpressAdvertisingAttack'
API_ACCOUNT = f'sec=20171212getscn&act=getAliexpressAdAttackAccount&limit={ACCOUNT_NUM}'

# 下面是默认的我们的产品ID,刷点击的时候需要忽略
OUR_PRODUCT_ID = [
    '4000320919983',
    '32971247675',
    '32961187679',
    '32962923195',
    '32970987767',
    '32963254246',
    '4000075521477',
    '4000289010170',
    '4000311304726',
    '4000212188044',
    '32966220376',
    '4000311726859',
    '32959839163',
    '4000259496978',
    '33059583386',
    '32966435634',
]
