#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/11 16:52
# @Author  : Lodge
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

cwd = os.getcwd()   # ��ȡ��ǰ�ļ���·��

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ����һ
BASE_DIR = os.path.dirname(cwd)    # ������

# REQUESTS_DIR = os.path.join(BASE_DIR, 'requests58_yhzx.py')
REQUESTS_DIR = os.path.join(BASE_DIR, 'spider_image_test.py')


def start_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '����1')
    os.system(f'python {REQUESTS_DIR}')                 # win������pythonĬ��3 linux�¿��ܻ���õ�python2 ��Ҫ�޸�


def start_down():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '����2')
    os.system(f'python {REQUESTS_DIR}')


def my_listener(event):
    if event.exception:
        print('��������ˣ�����������')
    else:
        print('�����ճ�����...')


scheduler = BlockingScheduler()
# scheduler.add_job(start_auto, 'cron', hour='8,11,17,19,23', minute='30')
scheduler.add_job(start_down, 'cron', hour='18,19', second='*/10')
# scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)    # ֻ�ܱ�֤����ͣ�£����ǲ��ܲ������
scheduler.start() 

