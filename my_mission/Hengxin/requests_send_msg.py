#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/16 15:37
# @Author  : Lodge
import os
import re
import sys
import time
import json
import random
import urllib3
import logging

import requests
from logging import getLogger
from fake_useragent import UserAgent

from helper import python_config


ua = UserAgent()     # fake useragent
LOG = getLogger()    # LOG recoder
LOG.setLevel(logging.DEBUG)  # Change the level of logging::
# You can modify the following code to change the location::
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
this_month = time.strftime('%Y%m', time.localtime())
filename = os.path.join(BASE_DIR, 'helper', f'{this_month}.log')
formatter = logging.Formatter(
        "%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s"
)  # Define the log output format
fh = logging.FileHandler(filename=filename, encoding="utf-8")
fh.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
LOG.addHandler(fh)
LOG.addHandler(console_handler)
LOG.setLevel(logging.INFO)
urllib3.disable_warnings()   # disabled requests' verify warning
# ==================================================================================== #


class SendMsg(object):
    def __init__(self):
        self.base_url = 'http://hr.91job.com'
        self.token_url = self.base_url + '/api/auth/jwt/hr/token'
        self.ua = UserAgent()
        self.session = requests.Session()

    def get_token(self):  # 第一件事情，就是通过登录获取token
        data = {
            'type': 1,
            'password': python_config.PASSWORD,
            'username': python_config.ACCOUNT_FROM
        }
        get_token_headers = {
            'Referer': 'http://hr.91job.com/',
            'User-Agent': ua.random,
        }
        token_get = self.session.post(self.token_url, json=data, headers=get_token_headers)
        token = json.loads(token_get.text).get('data', None)
        return token

    # ===================================================== #
    @staticmethod
    def judge_need_down():
        # 从接口中获取数据
        interview_url = 'http://hr.gets.com:8989/api/autoGetInterview.php?type=getInterview'
        send_info = requests.get(interview_url)
        if send_info:
            send_info = json.loads(send_info.text)
            need_send_info = []
            add_user = python_config.DOWNLOAD_USER
            for n_s_i in send_info:
                if n_s_i.get('add_user') == add_user:
                    ex_id = n_s_i.get('external_resume_id')
                    inner_id = n_s_i.get('resume_id')
                    need_send_info.append((ex_id, inner_id))

            return need_send_info
        else:
            return None

    @staticmethod
    def judge_date():
        t_t = time.time() + 86400
        tm_day = time.localtime(t_t)                           # 获取明天的信息
        tm_t_day = tm_day.tm_wday                              # 获取明天的星期
        if tm_t_day == 6:   # 如果明天是星期天，那么就邀约到下周一
            invite_day = time.strftime("%Y-%m-%d 10:00:00", time.localtime(t_t + 86400))
        else:
            invite_day = time.strftime("%Y-%m-%d 10:00:00", time.localtime(t_t))
        return invite_day

    def handle_interview(self, all_resume, token):
        send_msg_url = python_config.SEND_MSG_URL
        verify_headers = {
            'Authorization': token
        }
        for ex_resume, inner_id in all_resume:
            phone_num = re.findall(r'_\((\d+)', ex_resume)
            resume_id = re.findall(r'91_(\d+)_', ex_resume)

            if phone_num:
                date = self.judge_date()
                data = {
                    "address": "浙江省义乌市城西街道鸿运路315号陆港电商小镇6号楼8层",
                    "changeVal": 2,
                    "companyName": "兴禾网络",
                    "hrId": python_config.HR_ID,
                    "hrMobile": python_config.HR_MOBILE,
                    "hrName": "赵小姐",
                    "interviewerMobile": phone_num[0],
                    "positionId": "647065",
                    "positionName": "外贸电子商务业务",
                    "remark": "",
                    "resumeId": resume_id[0],
                    "sms": "true",
                    "source": 1,
                    "startDateStr": date,
                    "status": 1
                }
                time.sleep(random.uniform(1, 2))
                back_status = self.session.post(send_msg_url, json=data, headers=verify_headers).text
                status = json.loads(back_status).get('status')
                if int(status) == 200:
                    LOG.info(f'外部简历为:{ex_resume},内部简历为:{inner_id}的简历短信邀约成功...')
                    msg = f'*********** HR程序自动化 ***********\n状态: {phone_num}的短信邀约信息发送成功.'
                    send_msg_tx(msg)
                    url_clear = python_config.CLEAR_URL_HEAD + inner_id
                    clear_info = requests.get(url_clear)
                    print(f'清除信息的状态为:{clear_info.text}')

    def run(self):
        status = self.judge_need_down()   # 1. 判断是否有需要下载的简历
        if status:
            token = self.get_token()  # 2,第一步获取到token尤为重要
            self.handle_interview(status, token)


def run():
    app = SendMsg()
    app.run()


def send_msg_tx(msg):
    post_data = {
        "sender": "系统机器人",
        "receivers": python_config.RECEIVERS,
        "msg": msg,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    run()
