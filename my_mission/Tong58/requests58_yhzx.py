#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 15:08
# @Author  : Lodge
# 这里是处理主动投递信息的地方，纯接口，就很方便
import os
import re
from threading import Thread

import sys
import json
import time
import random
import logging
import urllib3
import importlib
from functools import wraps
from logging import getLogger

import requests
from fake_useragent import UserAgent
from helper import python_config

ua = UserAgent()     # fake useragent
LOG = getLogger()    # LOG recoder
LOG.setLevel(logging.DEBUG)  # Change the level of logging::
# You can modify the following code to change the location::
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
this_month = time.strftime('%Y%m', time.localtime())
filename = BASE_DIR + f'/helper/{this_month}.log'
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
# ========================================================================================== #


class TongCheng(object):
    def __init__(self):
        self.base_url = 'https://employer.58.com/'
        self.down_url = self.base_url + 'resumedownload?'
        self.down_url_api = self.base_url + 'resume/downloadlist?'
        self.auto_resume_url = self.base_url + 'resumereceive?'
        self.auto_resume_api = self.base_url + 'resume/deliverlist?'
        self.local_class = self.__class__.__name__
        self.session = requests.Session()

    @staticmethod
    def handle_name(data):
        true_name = data['trueName']
        family_name = data['familyName'][0]
        name_re = re.findall(r'(&#x[0-9a-z]+;)', true_name)
        if not name_re:
            return true_name
        else:
            true_name = true_name.replace(name_re[0], family_name)
            return true_name

    @staticmethod
    def requests_headers(referer_url):
        # 5.请求头
        cookies = importlib.reload(python_config).cookies
        headers = {
            'User-Agent': ua.random,
            'x-requested-with': 'XMLHttpRequest',
            'referer': referer_url,
            'cookie': cookies,
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        }
        return headers

    def post_data_auto(self, resume_data):
        info = {
            'account': python_config.account_from,
            'data': [resume_data]
        }
        url = python_config.POST_URL
        print(info)
        try:
            response = self.session.post(url, json=info)
        except Exception as e:
            LOG.error('目标计算机拒绝链接')
        else:
            LOG.info(f'数据插入详情为:{response.text}')

    def all_auto_get(self):
        referer_url = 'https://employer.58.com/resumereceive?'
        headers = self.requests_headers(referer_url)
        for pg in range(1, 2):      # 这里是自定义爬取多少页，每页50条，反正50条才请求一次，bomb
            time.sleep(random.uniform(1, 2))
            now_pg_data = requests.get(self.auto_resume_api, params={'pageindex': pg}, headers=headers, verify=False)
            new_data = now_pg_data.text.lstrip('(').rstrip(')')
            new_data = json.loads(new_data)
            resume_data = new_data['data']['resumeList']
            yield resume_data

    def auto_resume(self):
        auto_resume_data = self.all_auto_get()
        for each_data in auto_resume_data:
            need_post = self.transfer_useful_auto(each_data)
            for post_resume in need_post:
                self.post_data_auto(post_resume)

    def transfer_useful_auto(self, handled_data):
        # 这里是最后要处理数据的地方，在这之前还有很多地方的数据需要处理（解码为主）
        data_s = handled_data
        for _ in range(len(data_s)):
            data = data_s[_]
            gender_judge = data['sex']
            work_exp = data['experiences']
            if work_exp:
                work_experience = []
                for each_work in work_exp:
                    work_info = {
                        '起止时间': each_work['startDate'] + '-' + each_work['endDate'],
                        '公司信息': each_work['company'],
                        '工作内容': each_work['positionName'] + ":" + each_work['description']
                    }
                    work_experience.append(work_info)
            else:
                work_experience = []
            phone_num = data['mobile']
            name = self.handle_name(data)
            work_year = data['workYear']
            salary = data['targetSalary'] if '面议' not in data['targetSalary'] else '面议'
            age = int(data['age'])
            now_year = int(time.strftime('%Y', time.localtime()))

            json_info = {
                'name': name,
                'mobile_phone': phone_num,
                'company_dpt': 1,  # 不确定写啥
                'resume_key': data['targetPosition'] if data['targetPosition'] else '',
                'gender': 2 if gender_judge == '0' else 1,
                'date_of_birth': f'{now_year - age}-01-01',
                'current_residency': data['expectArea'],
                'years_of_working': work_year,
                'hukou': '',
                'current_salary': '',
                'politics_status': '',
                'marital_status': 2,
                'address': '',
                'zip_code': '',
                'email': '',
                'home_telephone': '',
                'personal_home_page': '',
                'excecutiveneed': '',
                'self_assessment': data['letter'],
                'i_can_start': '',
                'employment_type': 1,
                'industry_expected': '',
                'working_place_expected': data['expectArea'],
                'salary_expected': salary,
                'job_function_expected': 1,
                'current_situation': '',
                'word_experience': work_experience,
                'project_experience': [],
                'education': [],
                'honors_awards': [],
                'practical_experience': [],
                'training': '',
                'language': [],
                'it_skill': [],
                'certifications': [],
                'is_viewed': 1,
                'resume_date': time.strftime("%Y-%m-%d", time.localtime()),
                'get_type': 1,
                'external_resume_id': data['resumeid'][-49:],
                'labeltype': 1,
                'resume_logo': data['picUrl'],
                'resume_from': 4,  #
                'account_from': python_config.account_from,
                'update_date': time.strftime("%Y-%m-%d", time.localtime(int(data['updateDate']) / 1000)),
            }

            yield json_info

    def run_auto(self):
        self.auto_resume()   # 获取主动投递的简历信息


def send_rtx_msg(msg):
    """
    公司的内部的rtx信息发送接口, 接收人已经写成了配置文件了
    :param msg: 要发送的信息
    :return: 不返回
    """
    post_data = {
        "sender": "系统机器人",
        "receivers": python_config.receivers,
        "msg": msg,
    }
    # requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def clear_timer(set_time):
    """
    一个简单地定时器装置, 放入的 set_time 必须为集合, 列表, 元组。 里面的元素必须为字符串::方便设置指定的时间比如('18:21')
    :param set_time: 设定的触发时间: 全称: 小时。
    :return:
    """

    def work_time(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now_time = time.strftime("%H:%M", time.localtime())
            if now_time in set_time:
                print()
                func(*args, **kwargs)
                print('\r这个程序停了,正在休眠中...', end='')
                time.sleep(60)
            else:
                print('\r这个程序停了,继续休眠中...', end='')
                time.sleep(60)

        return wrapper
    return work_time


@clear_timer(['09:00', '11:30', '16:00', '18:30', '23:55'])
def main_auto():
    app = TongCheng()
    app.run_auto()


def main():
    app = TongCheng()
    app.run_auto()
    print('调试的时候卡死在这里')
    time.sleep(10000)
    while True:
        t_auto = Thread(target=main_auto)
        t_auto.start()
        t_auto.join()


if __name__ == '__main__':
    main()
