#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/26 9:36
# @Author  : Lodge

import requests
import random
import json
from utils.logger import *

from spider.cookies import cookie                            # 里面配置cookie
account_main = 'wwet67827992'                                #
POST_URL = 'http://hr.gets.com:8989/api/autoAceUpdateResumeChannel.php?'   # post to
session = requests.Session()
base_url = "https://rd5.zhaopin.com/api/rd/assets/summary?"


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
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": cookie
    }
    return headers


def do_requests():
    params = params_get()
    headers = headers_get()
    try:
        info = requests.get(base_url, params=params, headers=headers, verify=False)
    except Exception as e:
        print('\rNone', end='')
    else:
        handle = json.loads(info.text)
        if handle.get('code') == 0:
            handle_to_api(handle)
        else:
            msg = '数据统计程序:cookie失效，需要重新添加cookie'
            # send_rtx_msg('聂清娜', msg)
            send_rtx_msg('系统机器人', msg)


def handle_to_api(handle_text):
    data = handle_text.get('data')
    if data:
        job = data.get('job')
        resume = data.get('resume')
        assets = data.get('assets')
        coins = data.get('coins')

        publish_posts_no = job.get('publishCount')
        posts_available_today = job.get('mayPublishCount')

        applied_for_resume = resume.get('latest')
        resume_received_no = resume.get('all')

        remain_downloads = assets.get('normalDownload')
        remain_refresh_no = assets.get('refresh')

        use_coin = coins.get('balance')
        expire_coin = data.get('coinsAlert')

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
    if info:
        try:
            rq = session.post(URL, json=data)
        except Exception as e:
            LOG.error('目标计算机拒绝链接')
        else:
            LOG.info(f'数据的插入详情为:{rq.text}')


def send_rtx_msg(receivers, msg):
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
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/statistical/effect',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": cookie
    }
    return headers


def report_do_requests():
    params = report_params_get()
    headers = report_headers_get()
    try:
        info = requests.get(report_url, params=params, headers=headers, verify=False)
    except Exception as e:
        print('\rNone', end='')
    else:
        handle = json.loads(info.text)
        if handle.get('code') == 0:
            report_handle_to_api(handle)
        else:
            msg = '数据统计程序:cookie失效，需要重新添加cookie'
            report_send_rtx_msg('聂清娜', msg)


def report_handle_to_api(handle_text):
    data1 = handle_text.get('data')
    if data1:
        data = data1.get('data')

        month_browse_no = data.get('applicationtotal')  # 被申请 1476次
        month_apply_no = data.get('hittotal')    # 在统计时间段内被浏览 19040次

        all_info = {
            'account': account_main,
            'data': {
                "month_browse_no": month_browse_no,
                "hittotal": month_apply_no
            }
        }

        report_do_post(all_info)


def report_do_post(info):
    data = info
    URL = POST_URL
    # URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'
    if info:
        try:
            rq = session.post(URL, json=data)
        except Exception as e:
            LOG.error('目标计算机拒绝链接')
        else:
            LOG.info(f'数据的插入详情为:{rq.text}')


def report_send_rtx_msg(receivers, msg):
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


if __name__ == '__main__':
    while True:
        do_requests()
        report_do_requests()
        for _ in range(86400):
            n = _ // 1728
            print(f'\rloading: {(50 -n) * "=" + n * ">"}', end="")
            time.sleep(1)
