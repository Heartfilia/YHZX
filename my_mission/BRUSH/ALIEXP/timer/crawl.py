#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 16:52
# @Author  : Lodge
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# cwd = os.getcwd()   # 获取当前文件的路径

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 方法一
# BASE_DIR = os.path.dirname(cwd)    # 方法二

# REQUESTS_DIR = os.path.join(BASE_DIR, 'requests58_yhzx.py')
REQUESTS_DIR = os.path.join(BASE_DIR, 'Selenium_call_find.py')

POSITION_DIR = os.path.join(BASE_DIR, 'Selenium_position.py')

TEST_DIR = os.path.join(BASE_DIR, 'test.py')


def start_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '打招呼')
    os.system(f'python {REQUESTS_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def start_put():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '发布职位')
    os.system(f'python {POSITION_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def test_t():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '测试')
    os.system(f'python {TEST_DIR}')


scheduler = BlockingScheduler()
# scheduler.add_job(test_t, 'cron', second='*/10')
scheduler.add_job(start_auto, 'cron', hour='9-16', minute='*/30')
scheduler.add_job(start_put, 'cron', hour='23', minute='10')
# scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)    # 只能保证任务不停下，但是不能捕获错误

scheduler.start()
