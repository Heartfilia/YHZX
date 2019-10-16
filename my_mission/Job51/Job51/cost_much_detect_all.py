#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/26 9:36
# @Author  : Lodge
import importlib
from fake_useragent import UserAgent
import requests



ua = UserAgent()
# 智联：银河在线：每日账号数据情况以及账号30天的情况
POST_URL = 'http://hr.gets.com:8989/api/autoAceUpdateResumeChannel.php?'   # post to
session = requests.Session()
base_url = "https://rd5.zhaopin.com/api/rd/assets/summary?"

from spider.helper import python_config
receivers = python_config.receivers
company_name = python_config.company_name
handler = python_config.handler
account_name = company_name
account_main = python_config.account_main


def do_post():
    data = {'account': 'gzwb537', 'data': {'applied_for_resume': '250', 'remain_refresh_no': '1', 'remain_downloads': '1059', 'recent_received_num': '9452', 'hr_put_position': '', 'use_coin': 0, 'expire_coin': 0, 'hittotal': 0, 'month_browse_no': 0, 'posts_available_today': 0, 'publish_posts_no': '43'}}
    URL = POST_URL
    rq = session.post(URL, json=data)
    print(rq.text)


do_post()



