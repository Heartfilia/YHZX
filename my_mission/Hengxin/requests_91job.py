#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/14 16:45
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


class HenXin(object):
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

    # ========================================================== #

    def fresh_position(self, token):   # 此处为刷新那些招聘岗位的程序
        position_url = self.base_url + f'/api/position/core/list?close=0&pageNo=&pageSize=10&t={int(time.time())}'
        verify_headers = {
            'Authorization': token
        }
        info = self.session.get(position_url, headers=verify_headers)
        total = json.loads(info.text).get('data').get('total')
        data = {
            'close': 0,
            'pageSize': total,
            't': f'{int(time.time())}'
        }
        time.sleep(random.uniform(1, 2))
        detail_url = self.base_url + f'/api/position/core/list?'
        all_data = self.session.get(detail_url, params=data, headers=verify_headers)
        all_data = json.loads(all_data.text).get('data').get('rows')[0].get('positions')
        LOG.info(f"即将刷新职位信息,总共有{total}条职位信息需要刷新")
        for each_data in all_data:
            last_refresh = each_data.get('refreshCount', 0)   # 剩下的刷新数量
            position_id = each_data.get('id', 0)              # 职位的id
            yield (last_refresh, position_id)

    def fresh_position_one(self, p_id, token):
        time.sleep(random.uniform(0, 1))
        verify_headers = {
            'Authorization': token
        }
        need_fresh_url = self.base_url + f'/api/position/core/refreshPosition/{p_id}'
        self.session.get(need_fresh_url, headers=verify_headers)                     # 这里会直接成功的 不用返回了

    def handle_fresh(self, token):
        fresh_data = self.fresh_position(token)     # (last_refresh, position_id)
        for num, p_id in fresh_data:
            if num > 0:
                self.fresh_position_one(p_id, token)
            else:
                continue

    # ========================================================== #

    def handle_resume(self, token, action):
        time.sleep(random.uniform(0, 1))
        verify_headers = {
            'Authorization': token
        }
        resume_auto_url = self.base_url + '/api/position/resume/list'
        data = {
            'action': action,
            'hopeCity': '"义乌"',
            'hrId': python_config.HR_ID,
            'pageNo': 1,
        }
        base_info = self.session.post(resume_auto_url, json=data, headers=verify_headers)
        all_data = json.loads(base_info.text).get('data').get('rows')
        for each_data in all_data:
            resume_id = each_data.get('resumeId')
            position_id = each_data.get('positionId', None)
            yield (resume_id, position_id)

    def transfer_useful(self, json_info, flag=None, inner=None):
        # flag 的状态量 True 的话是    下载的简历
        #             None(默认值)    主动投递的简历
        #             False          搜索的简历
        #             xxx            程序下载的简历
        data = json.loads(json_info).get('data').get('resume')
        name = data['name']
        phone_num = data.get('mobileNum', '')
        resume_key = data.get('hopeWork', '')
        salary_info = {
            '-1': '不限',
            '1': "0 - 1000元",
            '2': "1000 - 1500元",
            '3': "1500 - 2000元",
            '4': "2000 - 2500元",
            '5': "2500 - 3000元",
            '6': "3000 - 3500元",
            '7': "3500 - 4000元",
            '8': "4500 - 5000元",
            '10': "5000 - 6000元",
            '12': "6000 - 7000元",
            '14': "7000 - 8000元",
            '16': "8000 - 12000元",
            '24': "12000 - 15000元",
            '30': "15000 - 20000元",
            '40': "20000 - 25000元",
            '50': "25000 - 30000元",
            '60': "30000元以上"
        }

        work_exps = data.get('workExps', None)
        work_experience = []
        if work_exps:
            for each_work in work_exps:
                dic = {
                    '公司信息': each_work.get('companyName', ''),
                    '起止时间': f"{each_work.get('startDate'), ''}"
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
            'gender': data.get('sex', '保密'),
            'date_of_birth': data.get('birthday', '保密'),
            'current_residency': data.get('living', '私密'),
            'years_of_working': data.get('exp', 0),
            'hukou': data.get('birthplace', '私密'),
            'current_salary': '私密',
            'politics_status': '',
            'marital_status': 2,
            'address': f'{data.get("living", "私密")}',
            'zip_code': '',
            'email': '',
            'home_telephone': '',
            'personal_home_page': '',
            'excecutiveneed': '',
            'self_assessment': data.get('description', ''),
            'i_can_start': '',
            'employment_type': 1,
            'industry_expected': '',
            'working_place_expected': data.get('hopeDistrict', '') + data.get('hopeStreet', ''),
            'salary_expected': salary_info.get(str(data['hopeSalary'])),
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
            'ACCOUNT_FROM': python_config.ACCOUNT_FROM,
            'update_date': data.get('modifyDate'),
        }

        if phone_num:
            self.post_resume(json_info, flag, inner)

    def post_resume(self, json_info, flag, inner=None):
        info = {
            'account': python_config.EN_ACCOUNT,
            'add_user': python_config.EN_ACCOUNT,
            'data': [json_info]
        }
        if flag:
            if flag == 'DOWN':
                info['noneDlivery_resume_id'] = inner
                info['add_user'] = python_config.DOWNLOAD_USER
                print('程序下载的简历:', info)
                try:
                    rq = self.session.post(python_config.POST_URL_DOWN, json=info)
                except Exception as e:
                    LOG.error('目标计算机拒绝链接')
                else:
                    LOG.info(f'数据的插入详情为:{rq.text}')
            else:
                print('主动下载的简历:', info)
                try:
                    rq = self.session.post(python_config.POST_URL_DOWN, json=info)
                except Exception as e:
                    LOG.error('目标计算机拒绝链接')
                else:
                    LOG.info(f'数据的插入详情为:{rq.text}')
        else:
            if flag is False:
                print('主动搜索:', info)
                try:
                    rq = self.session.post(python_config.POST_URL_SEARCH, json=info)
                except Exception as e:
                    LOG.error('目标计算机拒绝链接')
                else:
                    LOG.info(f'数据的插入详情为:{rq.text}')
            else:
                print('主动投递:', info)
                try:
                    rq = self.session.post(python_config.POST_URL, json=info)
                except Exception as e:
                    LOG.error('目标计算机拒绝链接')
                else:
                    LOG.info(f'数据的插入详情为:{rq.text}')

    def get_each_resume(self, resume_id, position_id, token, flag=None, inner=None):
        # flag 标志量 默认是空进行普通的下载简历和主动投递
        #            True 的时候是通过内部状态下载的简历
        time.sleep(random.uniform(1, 2))
        request_each_url = 'http://hr.91job.com/api/position/resume/getDetail?'
        verify_headers = {
            'Authorization': token
        }
        data = {
            'resumeId': resume_id,
            'positionId': position_id if position_id else '',
            't': int(time.time())
        }
        if flag:
            each_one_resume = self.session.get(request_each_url, params=data, headers=verify_headers)
            self.transfer_useful(each_one_resume.text, 'DOWN', inner)    # 这里是程序下载的简历
        else:
            if position_id:
                each_one_resume = self.session.get(request_each_url, params=data, headers=verify_headers)
                self.transfer_useful(each_one_resume.text)               # 这里是主动投递的简历
            else:
                each_one_resume = self.session.get(request_each_url, params=data, headers=verify_headers)
                self.transfer_useful(each_one_resume.text, True)         # 这里是主动下载的简历

    def handle_each_resume(self, resume_info, token):
        for resume_id, position_id in resume_info:
            self.get_each_resume(resume_id, position_id, token)

    def handle_resume_interest(self, token, action, pg=1):
        print(f'感兴趣的简历中当前页数为:{pg}页...')
        time.sleep(random.uniform(0, 1))
        verify_headers = {
            'Authorization': token
        }
        resume_auto_url = self.base_url + '/api/position/resume/list'
        data = {
            'action': action,
            'startDate': f'{time.strftime("%Y-%m-%d", time.localtime())} 00:00:00',
            'hrId': python_config.HR_ID,
            'pageNo': pg,
        }
        base_info = self.session.post(resume_auto_url, json=data, headers=verify_headers)
        base_data = json.loads(base_info.text).get('data')
        all_data = base_data.get('rows')
        total_resume = base_data.get('total')
        all_pg = total_resume // 10 + 1   # 获取到页数

        for each_data in all_data:
            resume_id = each_data.get('resumeId')
            position_id = each_data.get('positionId', None)
            yield (resume_id, position_id)

        if all_pg > pg:
            for p in range(pg+1, all_pg+1):
                resume_info_interest = self.handle_resume_interest(token, '0', p)
                self.handle_each_resume(resume_info_interest, token)

    # ========================================================== #

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
                each_data = self.session.get(request_each_url, params=data, headers=verify_headers)
                self.transfer_useful(each_data, False)

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
                'pageSize': 20      # 这里数据好像想写多少写多少，我就写20把 # 每天会跑3次数据,就是60条了。
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

    # ========================================================== #

    @staticmethod
    def get_resume_id_from_api():
        all_need_return = []
        api_get = requests.get(python_config.DOWN_RESUME_KEY)
        api_resume = json.loads(api_get.text)
        for each in api_resume:
            download_user = each.get('download_user', None)
            if download_user == python_config.DOWNLOAD_USER:
                external_resume_id = re.findall(r'91_(\d+)_', each.get('external_resume_id'))
                inner_resume_id = each.get('resume_id', '')
                one_resume = (external_resume_id, inner_resume_id)
                all_need_return.append(one_resume)

        return all_need_return

    def down_and_post_resume(self, ex_id, in_id, token):
        # 1. down
        down_url = f'http://hr.91job.com/api/position/resume/download/{ex_id}?recmd=0'
        verify_headers = {
            'Authorization': token
        }
        data = {
            'id': ex_id,
            'recmd': 0
        }
        response = self.session.post(down_url, json=data, headers=verify_headers).text
        response = json.loads(response)
        status = response.get('status', '500')
        phone_num = response.get('data', None)
        if (int(status) == 200) and phone_num:
            LOG.info(f'简历外部号为:91_{ex_id}_({phone_num},内部简历号为:{in_id}的简历下载成功...')
            self.get_each_resume(ex_id, '', token, True, in_id)

    def go_to_down_resume(self, token):
        all_need_down = self.get_resume_id_from_api()
        for ex_id, in_id in all_need_down:
            self.down_and_post_resume(ex_id, in_id, token)

    def run(self):
        token = self.get_token()    # 1,第一步获取到token尤为重要
        self.handle_fresh(token)    # 2 刷新职位
        time.sleep(random.uniform(2, 3))
        resume_info = self.handle_resume(token, '2')   # 3 主动投递的简历导入--获取一页的id来进行下一步获取
        self.handle_each_resume(resume_info, token)  # 4 处理好了主动投递后包括上传
        time.sleep(random.uniform(3, 5))
        resume_info_down = self.handle_resume(token, '3')  # 5 这里是下载的简历
        self.handle_each_resume(resume_info_down, token)   # 6 处理了下载的简历
        time.sleep(random.uniform(3, 5))
        resume_info_interest = self.handle_resume_interest(token, '0')   # 7 这里是对我感兴趣的简历
        self.handle_each_resume(resume_info_interest, token)             # 感兴趣的已经处理完毕
        time.sleep(random.uniform(3, 5))
        self.go_to_search(token)      # 8 这里处理搜索的简历
        self.go_to_down_resume(token)    # 9 这里是处理下载的简历


def run():
    app = HenXin()
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


