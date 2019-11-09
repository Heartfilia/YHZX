#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/4 16:17
# @Author  : Lodge
import os
import sys
import time
import logging
import requests
from helper import python_config
BASE_DIR = os.path.dirname(os.getcwd())


def save_html(html, name):
    """
    存网页,供分析使用
    :param html: html文件
    :param name: 要存的文件的名字
    """
    with open(os.path.join(BASE_DIR, 'utils', f'{name}.html'), 'w', encoding='utf-8') as html_file:
        html_file.write(html)


def send_rtx_info(msg, receivers=python_config.RECEIVERS):
    """
    发送RT消息
    :param receivers: 接收者的名字
    :param msg: 消息
    """
    message = f"****** 速卖通广告杀手 ******\n原因:{msg}"
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": message,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def log(name, std_level=logging.INFO, file_level=logging.INFO):
    """
    日志信息
    :param name: 日志的名字
    :param std_level: 日志的报告的等级(客户端设置) ==> log.error('')【不用在里面写了,在前面写就好了】
    :param file_level: 日志的插入等级(达到预定等级才会插入日志)  ==> 此处debug等级不会插入
    file_name_date = time.strftime('%Y%m', time.localtime())
    full_name = f'{name}_{file_name_date}.log'
    # def logger(name, std_level=logging.INFO, file_level=logging.DEBUG):
    logger = logging.getLogger()
    # log_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    # log_filename = log_dir + '/log/' + name + '.log'
    # if not os.path.isdir(log_dir + "/log"):
    #     os.mkdir(log_dir + "/log")
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filename = os.path.join(log_dir, full_name)
    file_handler = logging.FileHandler(log_filename, mode='a', encoding="utf8")
    # maxBytes=102400000000,
    # backupCount=10

    # fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fmt = logging.Formatter("%(asctime)s=%(levelname)s=%(filename)s[line:%(lineno)d]=>%(message)s")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    stdout_handler.setLevel(std_level)
    logger.addHandler(stdout_handler)
    logger.setLevel(file_level)
    return logger
