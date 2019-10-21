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


class SendMsgAndDown(object):
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
    def judge_need_send():
        # 从接口中获取数据
        interview_url = python_config.JUDGE_SEND_URL
        send_info = requests.get(interview_url)
        if send_info:
            tic_dict = {
                '1': ' 10:00:00',
                '2': ' 11:00:00',
                '3': ' 14:00:00',
                '4': ' 15:00:00',
                '5': ' 16:00:00',
                '6': ' 14:30:00',
                '7': ' 15:30:00',
                '8': ' 16:30:00',
                '9': ' 09:30:00',
                '10': ' 10:30:00',
                '11': ' 11:30:00'
            }
            send_info = json.loads(send_info.text)
            need_send_info = []
            add_user = python_config.DOWNLOAD_USER
            for n_s_i in send_info:
                if n_s_i.get('add_user') == add_user:
                    ex_id = n_s_i.get('external_resume_id')
                    inner_id = n_s_i.get('resume_id')
                    date_time = n_s_i.get('interview_date')
                    ord_time = n_s_i.get('interview_time')
                    tic_time = date_time + tic_dict.get(ord_time, '14:00:00')
                    need_send_info.append((ex_id, inner_id, tic_time))

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

    def handle_interview(self, all_resume):
        send_msg_url = python_config.SEND_MSG_URL

        token = self.get_token()  # 2,第一步获取到token尤为重要
        verify_headers = {
            'Authorization': token
        }

        for ex_resume, inner_id, date in all_resume:
            phone_num = re.findall(r'_\((\d+)', ex_resume)
            resume_id = re.findall(r'91_(\d+)_', ex_resume)
            if phone_num:
                # date = self.judge_date()
                # "%Y-%m-%d 10:00:00'
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
                    msg = f'*********** HR程序自动化 ***********\n状态: {phone_num[0]}的短信邀约信息发送成功\n面试时间: {date}'
                    send_msg_tx(msg)
                    url_clear = python_config.CLEAR_URL_HEAD + inner_id
                    clear_info = requests.get(url_clear)
                    print(f'清除信息的状态为:{clear_info.text}')

    # ==================================================== #

    @staticmethod
    def judge_need_down():
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

    def transfer_useful(self, json_info, flag=None, inner=None):
        # flag 的状态量 True 的话是    下载的简历
        #              DOWN          程序下载的简历
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
            'self_assessment': data.get('description', ''),
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
            'ACCOUNT_FROM': python_config.ACCOUNT_FROM,
            'update_date': data.get('modifyDate'),
        }

        if flag:
            self.post_resume(json_info, flag, inner)

    def post_resume(self, json_info, flag, inner=None):
        info = {
            'account': python_config.EN_ACCOUNT,
            'add_user': python_config.EN_ACCOUNT,
            'data': [json_info]
        }
        # print(f'flag:{flag},info:{info}')
        if flag == 'DOWN':
            info['noneDlivery_resume_id'] = inner
            info['add_user'] = python_config.DOWNLOAD_USER
            print('程序下载的简历:', info)
            try:
                rq = self.session.post(python_config.POST_URL_DOWN, json=info)
            except Exception as e:
                LOG.error('目标计算机拒绝链接')
            else:
                LOG.info(f'程序下载数据的插入详情为:{rq.text}')

    @staticmethod
    def send_msg_own(status_msg):
        # 此处不重要,不是核心程序,是提供自己调试的内容
        handle_url = python_config.JUDGE_SEND_URL
        num_msg = len(status_msg)
        msg = f'自己的程序:{num_msg}\n查看链接:{handle_url}'
        my_ip = 'http://heartfilia.cn:5050/'
        data = {
            'sender': '系统机器人',
            'receiver': 'lodge',
            'info': msg
        }
        requests.post(my_ip, data=data)

    def run(self):
        status_msg = self.judge_need_send()     # # 1. 判断是否需要发送信息
        if status_msg:
            LOG.info('开始处理发送短信...')
            self.send_msg_own(status_msg)
            self.handle_interview(status_msg)

        status_down = self.judge_need_down()  # # 1. 判断是否有需要下载的简历
        if status_down:
            LOG.info('开始处理下载的简历...')
            token = self.get_token()  # 2,第一步获取到token尤为重要
            for ex_id, in_id in status_down:
                self.down_and_post_resume(ex_id, in_id, token)


def run():
    app = SendMsgAndDown()
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
