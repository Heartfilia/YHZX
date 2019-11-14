#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:17
# @Author  : Lodge
import os
import sys
import json
import time
import logging
import requests
from helper import python_config
BASE_DIR = os.path.dirname(os.getcwd())


def get_killer():
    """
    获取杀手任务的账号
    :return:(dict)
    {
        "id": (int),
        "account": (string),
        "password": (string),
        "header": (string-dict),
        "cookies": (string-list(dict)),
        "register_city": (string)
    }
    """
    get_url = python_config.THIRD_ACCOUNT_GET + python_config.API_ACCOUNT
    resp = requests.get(get_url)
    return json.loads(resp.text)


def save_html(html, name):
    """
    存网页,供分析使用
    :param html:(string) html文件
    :param name:(string) 要存的文件的名字
    """
    with open(os.path.join(BASE_DIR, 'utils', f'{name}.html'), 'w', encoding='utf-8') as html_file:
        html_file.write(html)


def reply_log(task_id, ip, asin, account_id, account_email, target_status, page=0, rank=0,
              attack_clicks=0, attack_url=""):
    """
    更新广告杀手任务,并写入攻击日志
    :param task_id:(int) 任务id
    :param ip:(string) 攻击广告使用的ip
    :param account_id:(string) 账号ID
    :param account_email:(string) 账号邮箱
    :param asin:(string) 产品id
    :param target_status:(int) 广告存在的状态 1-存在  2-不存在            <==
    :param page:(int) 广告在第几页,广告存在时才需要传
    :param rank:(int) 广告在页面的排名,广告存在的时候才需要传
    :param attack_clicks:(int) 攻击的次数, 通常值为1,广告存在的时候才需要传
    :param attack_url:(string) 广告的URL,广告存在时才需要传
    :return: 状态码(string) 成功-0, 失败-others
    """
    post_url = python_config.API_GETS_POST + python_config.API_REPLY_LOG
    post_data = {
        "task_id": task_id,
        "ip": ip,
        "account_id": account_id,
        "account_email": account_email,
        "asin": asin,
        "target_status": target_status,
        "page": page,
        "rank": rank,
        "attack_clicks": attack_clicks,
        "attack_url": attack_url
    }
    try:
        response = requests.post(post_url, data=post_data)
        resp = json.loads(response.text).get("msg")
    except Exception as e:
        return "default"
    else:
        return resp


def get_goal_items():
    """
    这里要从api拿数据,现在模拟一些数据
    :return:(dict) 任务列表
    """
    items = requests.get(python_config.API_GETS_GET)
    item = json.loads(items.text)
    return item


def send_rtx_info(msg, receivers=python_config.RECEIVERS):
    """
    发送RT消息
    :param receivers:(string) 接收者的名字
    :param msg:(string) 消息
    """
    message = f"****** 速卖通广告杀手 ******\n原因:{msg}"
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": message,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def log(name, std_level=logging.INFO, file_level=logging.INFO):
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


# reply_log(111, '127.0.0.1', "SFDSF234JN23", "Abby", "abby@163.com", 2)
