#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 16:52
# @Author  : Lodge
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

cwd = os.getcwd()   # 获取当前文件的路径

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 方法一
BASE_DIR = os.path.dirname(cwd)    # 方法二

# REQUESTS_DIR = os.path.join(BASE_DIR, 'requests58_yhzx.py')
REQUESTS_DIR = os.path.join(BASE_DIR, 'spider_image_test.py')


def start_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '程序1')
    os.system(f'python {REQUESTS_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def start_down():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '程序2')
    os.system(f'python {REQUESTS_DIR}')


def my_listener(event):
    if event.exception:
        print('任务出错了！！！！！！')
    else:
        print('任务照常运行...')


# logging.basicConfig()
# logging.getLogger('ceshi').setLevel(logging.DEBUG)


scheduler = BlockingScheduler()
# scheduler.add_job(start_auto, 'cron', hour='8,11,17,19,23', minute='30')
scheduler.add_job(start_down, 'cron', hour='18,19', second='*/10')
# scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)    # 只能保证任务不停下，但是不能捕获错误

scheduler.start()

