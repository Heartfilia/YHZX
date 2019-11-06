#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/26 9:36
# @Author  : Lodge
import importlib
from fake_useragent import UserAgent
import requests
import random
import json
from utils.logger import *

ua = UserAgent()
# 智联：银河在线：每日账号数据情况以及账号30天的情况
POST_URL = 'http://hr.gets.com:8989/api/autoAceUpdateResumeChannel.php?'   # post to
session = requests.Session()
base_url = "https://rd5.zhaopin.com/api/rd/assets/summary?"

from helper import python_config
receivers = python_config.receivers
company_name = python_config.company_name
handler = python_config.handler
account_name = company_name
account_main = python_config.account_main


def params_get():
    t = time.time()
    node = int(t * 1000)
    front = [
        '46ba3dcc4781446ab7b77f11468b6c36',
        '15f87159b7c440078fedea3be92d26e7',
        '97ea329932f04166b268e0cb0b2bfd61',
        'bf37a85ca31548808cc4f6222bf07783',
        'c2f9f466ee1942649d95a08fb7d13555'
    ]
    max_len = len(front) - 1
    params = {
        "_": f"{node}",
        "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 800000)}",
        'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
        'isNewList': 'true'
    }
    return params


def headers_get():
    from spider import cookies
    cookie = importlib.reload(cookies).cookie
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': ua.random,
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": cookie
    }
    return headers


def do_requests():
    params = params_get()
    headers = headers_get()
    try:
        requests.packages.urllib3.disable_warnings()
        info = requests.get(base_url, params=params, headers=headers, verify=False)
    except Exception as e:
        print('\rNone', end='')
    else:
        handle = json.loads(info.text)
        if handle.get('code') == 0:
            handle_to_api(handle)
        else:
            pass


def handle_to_api(handle_text):
    data = handle_text.get('data')
    if data:
        job = data.get('job')
        resume = data.get('resume')
        assets = data.get('assets')
        coins = data.get('coins')

        publish_posts_no = job.get('publishCount', 0)
        posts_available_today = job.get('mayPublishCount', 0)

        applied_for_resume = resume.get('latest', 0)
        resume_received_no = resume.get('all', 0)

        remain_downloads = assets.get('normalDownload', 0)
        remain_refresh_no = assets.get('refresh', 0)

        use_coin = coins.get('balance', 0)
        expire_coin = data.get('coinsAlert', 0)

        all_info = {
            'account': account_main,
            'data': {
                "publish_posts_no": publish_posts_no,
                "applied_for_resume": applied_for_resume,
                "remain_downloads": remain_downloads,
                "posts_available_today": posts_available_today,
                "resume_received_no": resume_received_no,
                "remain_refresh_no": remain_refresh_no,
                "use_coin": use_coin,
                "expire_coin": expire_coin
            }
        }

        do_post(all_info)


def do_post(info):
    data = info
    URL = POST_URL
    # URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'
    print(info)
    if info:
        try:
            rq = session.post(URL, json=data)
        except Exception as e:
            LOG.error('目标计算机拒绝链接')
        else:
            LOG.info(f'数据的插入详情为:{rq.text}')


def send_rtx_msg(msg):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


# ========================================== #
report_url = "https://rd5.zhaopin.com/api/rd/statistical/effect/list/daily?"


def report_params_get():
    t = time.time()
    node = int(t * 1000)
    front = [
        '46ba3dcc4781446ab7b77f11468b6c36',
        '15f87159b7c440078fedea3be92d26e7',
        '97ea329932f04166b268e0cb0b2bfd61',
        'bf37a85ca31548808cc4f6222bf07783',
        'c2f9f466ee1942649d95a08fb7d13555'
    ]
    max_len = len(front) - 1

    last_month = time.localtime(time.time() - 2678400)
    yesterday = time.localtime(time.time() - 86400)

    last_month_year = last_month.tm_year
    last_month_month = last_month.tm_mon
    last_month_day = last_month.tm_mday

    yesterday_year = yesterday.tm_year
    yesterday_month = yesterday.tm_mon
    yesterday_day = yesterday.tm_mday

    last_month_info = f"{last_month_year}-{last_month_month}-{last_month_day}"
    yesterday_info = f"{yesterday_year}-{yesterday_month}-{yesterday_day}"
    params = {
        "_": f"{node}",
        "startdate": f"{last_month_info}",
        "enddate": f"{yesterday_info}",
        "pageindex": 1,
        "pagesize": 20,
        "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 800000)}",
        'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
    }
    return params


def report_headers_get():
    from spider import cookies
    cookie = importlib.reload(cookies).cookie
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/statistical/effect',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': ua.random,
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": cookie
    }
    return headers


def report_do_requests():
    params = report_params_get()
    headers = report_headers_get()
    try:
        requests.packages.urllib3.disable_warnings()
        info = requests.get(report_url, params=params, headers=headers, verify=False)
    except Exception as e:
        print('\rNone', end='')
    else:
        handle = json.loads(info.text)
        if handle.get('code') == 0:
            report_handle_to_api(handle)
        else:
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：智联{company_name}账号状态详情查询程序异常
处理标准：请人为到服务器替换本地cookie,也可以找相关技术人员协助
"""
            report_send_rtx_msg(msg)


def report_handle_to_api(handle_text):
    data1 = handle_text.get('data')
    if data1:
        data = data1.get('data')

        month_browse_no = data.get('applicationtotal', 0)  # 被申请 1476次
        month_apply_no = data.get('hittotal', 0)    # 在统计时间段内被浏览 19040次

        all_info = {
            'account': account_main,
            'data': {
                "month_browse_no": month_browse_no,
                "hittotal": month_apply_no
            }
        }
        print(all_info)
        report_do_post(all_info)


def report_do_post(info):
    data = info
    URL = POST_URL
    if info:
        try:
            rq = session.post(URL, json=data)
        except Exception as e:
            LOG.error('目标计算机拒绝链接')
        else:
            LOG.info(f'数据的插入详情为:{rq.text}')


def report_send_rtx_msg(msg):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def msg_params():
    t = time.time()
    node = int(t * 1000)
    front = [
        '46ba3dcc4781446ab7b77f11468b6c36',
        '15f87159b7c440078fedea3be92d26e7',
        '97ea329932f04166b268e0cb0b2bfd61',
        'bf37a85ca31548808cc4f6222bf07783',
        'c2f9f466ee1942649d95a08fb7d13555'
    ]
    max_len = len(front) - 1
    params = {
        "_": f"{node}",
        "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 800000)}",
        'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
    }
    return params


if __name__ == '__main__':
    # print('等待第二天中...')
    # time.sleep(50624)
    do_requests()
    report_do_requests()
#     while True:
#         try:
#             do_requests()
#             report_do_requests()
#         except:
#             msg = f"""
# ********* HR 数据自动化 *********
# 负责人：{handler}
# 状态原因：智联{company_name}账号状态详情查询程序异常
# 处理标准：请人为到服务器替换本地cookie,也可以找相关技术人员协助
# """
#             send_rtx_msg(msg)
#             input('添加cookie后在终端按回车键继续')
#         for _ in range(86400):
#             n = int(_ / 1728 * 50)
#             # print(f'\rloading: {n} * ">" + {(50 - n) * "="}', end="")
#             time.sleep(1)
