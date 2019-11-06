#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 16:52
# @Author  : Lodge
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
# import logging
# from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# cwd = os.getcwd()   # 获取当前文件的路径

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 方法一
# BASE_DIR = os.path.dirname(cwd)    # 方法二

DETAIL_DIR = os.path.join(BASE_DIR, 'Job51', 'detail_and_down.py')   # 主动投递


def detail_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'crawl...')
    os.system(f'python {DETAIL_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


scheduler = BlockingScheduler()
scheduler.add_job(detail_auto, 'cron', hour='11,19', minute='30')


scheduler.start()
