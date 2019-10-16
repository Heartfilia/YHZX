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

SEND_MSG_DIR = os.path.join(BASE_DIR, 'requests_send_msg.py')
REQUESTS_DIR = os.path.join(BASE_DIR, 'requests_91job.py')


def start_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ':其它信息程序')
    os.system(f'python {REQUESTS_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def send_msg():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ':发送信息程序')
    os.system(f'python {SEND_MSG_DIR}')


scheduler = BlockingScheduler()
scheduler.add_job(start_auto, 'cron', hour='8,11,19', minute='30')
scheduler.add_job(send_msg, 'cron', hour='9-21', second='*/10')

scheduler.start()

