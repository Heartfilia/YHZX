#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 16:52
# @Author  : Lodge
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
print('测试任务开始...')
# cwd = os.getcwd()   # 获取当前文件的路径

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 方法一
# BASE_DIR = os.path.dirname(cwd)    # 方法二

# REQUESTS_DIR = os.path.join(BASE_DIR, 'requests58_yhzx.py')
HOMEPAGE_TEST = os.path.join(BASE_DIR, 'app', 'selenium_test', 'homepage_test.py')

MAIN_PAGE_VIEW = os.path.join(BASE_DIR, 'app', 'selenium_test', 'main_page_view.py')

SEARCH_ITEM = os.path.join(BASE_DIR, 'app', 'selenium_test', 'search_item_test.py')

PAYMENT_ORDER = os.path.join(BASE_DIR, 'app', 'selenium_test', 'pay_order_test.py')

PERSONAL_PAGE = os.path.join(BASE_DIR, 'app', 'selenium_test', 'personal_page.py')

GOOGLE_TEST = os.path.join(BASE_DIR, 'app', 'google_aly', 'detect_score.py')

TEST_DIR = os.path.join(BASE_DIR, 'test.py')


def homepage_test():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '主页登录测试')
    os.system(f'python {HOMEPAGE_TEST}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def main_page_test():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '主页商品测试')
    os.system(f'python {MAIN_PAGE_VIEW}')                # win下面是python默认3 linux下可能会调用到python2 需要修改


def search_item_test():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '商品搜索测试')
    os.system(f'python {SEARCH_ITEM}')                   # win下面是python默认3 linux下可能会调用到python2 需要修改


def pay_order_test():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '商品支付测试')
    os.system(f'python {PAYMENT_ORDER}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def personal_page():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '个人中心页测试')
    os.system(f'python {PERSONAL_PAGE}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def google_detect():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '谷歌评分检测')
    os.system(f'python {GOOGLE_TEST}')                   # win下面是python默认3 linux下可能会调用到python2 需要修改


def test_all():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '随机项目测试')
    os.system(f'python {TEST_DIR}')                      # win下面是python默认3 linux下可能会调用到python2 需要修改


scheduler = BlockingScheduler()
# scheduler.add_job(test_t, 'cron', second='*/10')
scheduler.add_job(homepage_test, 'cron', hour='4', minute='30')
scheduler.add_job(main_page_test, 'cron', hour='1', minute='30')
scheduler.add_job(search_item_test, 'cron', hour='3', minute='30')
scheduler.add_job(pay_order_test, 'cron', hour='2', minute='0')
scheduler.add_job(personal_page, 'cron', hour='2', minute='30')
scheduler.add_job(google_detect, 'cron', hour='9', minute='0')
# scheduler.add_job(test_all, 'cron', hour='23', minute='10')

scheduler.start()
