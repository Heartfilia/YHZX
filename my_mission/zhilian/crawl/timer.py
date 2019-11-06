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

DETAIL_DIR = os.path.join(BASE_DIR, 'spider', 'Zhaopin_detail_yhzx.py')   # 主动投递

DOWN_DIR = os.path.join(BASE_DIR, 'spider', 'Zhaopin_all_download_get.py')    # 下载

COST_DIR = os.path.join(BASE_DIR, 'spider', 'Zhilian_cost_much_detect_all_yhzx.py')   # 每日花销

INFO_DIR = os.path.join(BASE_DIR, 'spider', 'ZhiLian.py')  # 基本信息


def detail_auto():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '主动投递')
    os.system(f'python {DETAIL_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def down_get():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '下载的简历')
    os.system(f'python {DOWN_DIR}')                 # win下面是python默认3 linux下可能会调用到python2 需要修改


def cost_detect():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '每日花销')
    os.system(f'python {COST_DIR}')


def all_detect():
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '职位状态')
    os.system(f'python {INFO_DIR}')


scheduler = BlockingScheduler()
scheduler.add_job(detail_auto, 'cron', hour='8,11,16,19,23', minute='30')
scheduler.add_job(down_get, 'cron', hour='12,18,22', minute='30')
scheduler.add_job(cost_detect, 'cron', hour='1')
scheduler.add_job(all_detect, 'cron', hour='3')

scheduler.start()
