#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/17 18:07
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


class Search(object):
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

    # ============================================================= #

    def search_each(self, all_resume_search, token):
        verify_headers = {
            'Authorization': token
        }
        request_each_url = 'http://hr.91job.com/api/position/resume/getDetail?'
        for each_resume in all_resume_search:
            user_id = each_resume.get('userId', None)
            if user_id:
                t = int(time.time() * 1000)
                data = {
                    'resumeId': user_id,
                    'positionId': '',
                    't': t
                }
                time.sleep(random.uniform(0, 1))
                each_data = self.session.get(request_each_url, params=data, headers=verify_headers)
                self.transfer_useful(each_data.text, False)

    def search(self, token):
        search_url = self.base_url + '/api/search/resume/core/list'
        verify_headers = {
            'Authorization': token
        }
        for each_pos in python_config.SEARCH_KEYS:
            data = {
                'hopeDistrict': '义乌市',
                'pageNo': 1,
                'keyword': each_pos,
                'pageSize': 50,      # 这里数据好像想写多少写多少，我就写50把 # 每天会跑3次数据,就是60条了。
                'age': -1,
                'arrival': -1,
                'hopeCity': "",
                'sex': -1,
                'hopeSalary': -1,
                'hopeTrade': "",
                'education': "null"
            }
            time.sleep(random.uniform(1, 2))
            data_list = self.session.post(search_url, json=data, headers=verify_headers)
            response_data = json.loads(data_list.text)
            all_data = response_data.get('data').get('rows')
            yield all_data

    def go_to_search(self, token):
        every_position_all = self.search(token)
        for each_position_resume_all in every_position_all:
            self.search_each(each_position_resume_all, token)

    def transfer_useful(self, json_info, flag=None, inner=None):
        # flag 的状态量   False          搜索的简历
        data = json.loads(json_info).get('data').get('resume')
        name = data.get('name', None)
        if not name:
            print("not name::", data)
            return
        phone_num = data.get('mobileNum', '')
        resume_key = data.get('hopeWork', '')
        salary_info = {
            '-1': '不限',
            '1': "0-1000元",
            '2': "1000-1500元",
            '3': "1500-2000元",
            '4': "2000-2500元",
            '5': "2500-3000元",
            '6': "3000-3500元",
            '7': "3500-4000元",
            '8': "4500-5000元",
            '10': "5000-6000元",
            '12': "6000-7000元",
            '14': "7000-8000元",
            '16': "8000-12000元",
            '24': "12000-15000元",
            '30': "15000-20000元",
            '40': "20000-25000元",
            '50': "25000-30000元",
            '60': "30000元以上"
        }

        work_exps = data.get('workExps', None)
        work_experience = []
        if work_exps:
            for each_work in work_exps:
                dic = {
                    '公司信息': each_work.get('companyName', ''),
                    '起止时间': f"{each_work.get('startDate', '')}"
                    f"-{each_work['endDate'] if each_work.get('endDate', None) else '至今'}",
                    '工作标题': each_work.get('positionName', ''),
                    '工作内容': each_work.get('description', ''),
                }
                work_experience.append(dic)

        skill = data.get('skills', None)
        skills = []
        if skill:
            for sk in skill:
                s_name = sk.get('name')
                skills.append({'证书名称': s_name})

        trans = data.get('trainings', None)
        trainings = trans[0] if trans else ''

        project_exps = data.get('projectExps', None)
        pro_exp = []
        if project_exps:
            for pep in project_exps:
                pro_exp.append(pep)

        certificates = data.get('certificates', None)
        cert = []
        if certificates:
            for cer in certificates:
                dic = {
                    '证书名称': cer.get('name'),
                    '获取时间': cer.get('date')
                }
                cert.append(dic)

        study_start = data.get('studyStart', None)
        if study_start:
            edu = {
                '开始时间': data.get('studyStart'),
                '结束时间': data.get('studyEnd'),
                '学校': data.get('school'),
                '专业': data.get('specialty')
            }
        else:
            edu = ''

        json_info = {
            'name': name,
            'mobile_phone': phone_num,
            'company_dpt': 2,
            'resume_key': resume_key,
            'gender': data.get('sex') if data.get('sex') != 0 else 1,
            'date_of_birth': data.get('birthday', ''),
            'current_residency': data.get('living', '保密'),
            'years_of_working': data.get('exp', 0),
            'hukou': data.get('birthplace', '保密'),
            'current_salary': '保密',
            'politics_status': '',
            'marital_status': 2,
            'address': f'{data.get("living", "保密")}',
            'zip_code': '',
            'email': '',
            'home_telephone': '',
            'personal_home_page': '',
            'excecutiveneed': '',
            'self_assessment': data.get('description', '').replace(' ', ''),
            'i_can_start': '',
            'employment_type': 1,
            'industry_expected': '',
            'working_place_expected': data.get('hopeDistrict', '') + data.get('hopeStreet', ''),
            'salary_expected': salary_info.get(str(data.get('hopeSalary', -1))),
            'job_function_expected': 1,
            'current_situation': '',
            'word_experience': work_experience,
            'project_experience': [],
            'education': [edu],
            'honors_awards': [],
            'practical_experience': [],
            'training': trainings,
            'language': [],
            'it_skill': skills,
            'certifications': cert,
            'is_viewed': 1,
            'resume_date': time.strftime("%Y-%m-%d", time.localtime()),
            'get_type': 2 if flag else 1,
            'external_resume_id': f"91_{data.get('id')}_({phone_num}",
            'labeltype': 1,
            'resume_logo': data.get('headPic', ''),
            'resume_from': 8,
            'account_from': python_config.ACCOUNT_FROM,
            'update_date': data.get('modifyDate'),
        }

        if flag is False:
            self.post_resume(json_info, flag, inner)

    def post_resume(self, json_info, flag, inner=None):
        info = {
            'account': python_config.EN_ACCOUNT,
            'add_user': python_config.EN_ACCOUNT,
            'data': [json_info]
        }
        # print(f'flag:{flag},info:{info}')

        if flag is False:
            info['add_user'] = python_config.DOWNLOAD_USER
            print('主动搜索:', info)
            try:
                rq = self.session.post(python_config.POST_URL_SEARCH, json=info)
            except Exception as e:
                LOG.error('目标计算机拒绝链接')
            else:
                LOG.info(f'主动搜索数据的插入详情为:{rq.text}')

    def run(self):
        token = self.get_token()  # 1,第一步获取到token尤为重要
        self.go_to_search(token)


def run():
    app = Search()
    app.run()


if __name__ == '__main__':
    run()
