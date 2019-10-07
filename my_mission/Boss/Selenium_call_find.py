﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 9:53
# @Author  : Lodge
"""
特别注意,本文所有的xpath除了部分需要拼接的外,其余的均为浏览器生成,所以有些时候会出什么问题我也不知道,到时候再改就好了,主要还是xpath的问题
"""
import os
import re
import sys
import time
import json
import random
import base64
from PIL import Image

import urllib3
import logging
import importlib
from functools import wraps
from threading import Thread
from logging import getLogger


import requests
from lxml import etree
from selenium import webdriver
from fake_useragent import UserAgent
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import python_config   # 这里是导入配置文件
from Baidu_ocr import client

ua = UserAgent()     # fake useragent
LOG = getLogger()    # LOG recoder
LOG.setLevel(logging.DEBUG)  # Change the level of logging::
# You can modify the following code to change the location::
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
this_month = time.strftime('%Y%m', time.localtime())
filename = BASE_DIR + f'/utils/{this_month}.log'
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
class BossHello(object):
    """
    这里就是和别人沟通进行处理聊天信息的，看到这里写了这么多就知道这里是比较多逻辑的，还要判断很多状态来智能化处理各个情况。
    """
    def __init__(self):
        self.base_url = 'https://www.zhipin.com'
        self.chat_url = self.base_url + '/chat/im?mu=chat'
        self.pic_url = 'https://m.zhipin.com/wapi/zpgeek/resume/attachment/preview4boss?id='
        self.local_class = self.__class__.__name__

        self.session = requests.Session()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=8055 --user-data-dir="C:\selenium_boss_llfs\AutomationProfile"   # chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

    def handle_selenium_cookies(self):
        self.driver.get(self.chat_url)
        time.sleep(random.uniform(1, 2))
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="header"]/div/div/div[15]/div[4]/span/img'))
            )
        except Exception as e:
            local_def = sys._getframe().f_code.co_name
            write_exception(e, local_def, self.local_class)
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            LOG.warning('*=*=*=*= i need help to fresh the cookie =*=*=*=*')
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            msg = f"********* HR 数据自动化 *********\n负责人：{python_config.handler}\n状态原因：Boss程序登录状态发现异常" \
                  f"\n处理标准：请人为到服务器手动处理登陆状态后重启程序"
            # send_rtx_msg(msg)
            print(msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                expected_conditions.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="header"]/div/div/div[15]/div[4]/span/img')))

    # ===================================================================================== #

    def judge_whether_exchange(self):
        # False : 不用发送信息
        # None  : 不用回消息，是对方不会来的状态值
        # True  : 要发送信息的  >> 返回准确值--回对应的消息
        time.sleep(1)
        class_info = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[1]/a[3]').get_attribute('class')
        page_source = self.driver.page_source
        html_parser = etree.HTML(page_source)
        chat_info = html_parser.xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[1]/ul/li//text()')
        chat_info = ''.join(chat_info).replace(' ', '').strip()
        no_repeat = python_config.no_repeat  # some key words

        if '的手机号：' in chat_info:
            return False

        for judge in no_repeat:
            if judge in chat_info:
                # delete_that_guy = self.driver.find_element_by_xpath(
                #     f'//*[@id="container"]/div[1]/div[2]/div[3]/div[1]/ul[2]/li[{li}]/a/div[2]/div/div/div/span[3]')
                # self.driver.execute_script("arguments[0].click();", delete_that_guy)
                # self.sure_change()
                LOG.info(f'对方不来的原因是: {judge}')
                return None
        if 'disable' in class_info:
            LOG.info('disable: 未交换信息需要进一步验证')
            return True     # need to exchange
        else:
            LOG.info('changed: 已经互相发送信息尝试进一步验证')

            simple_chat = python_config.SIMPLE_CHAT
            situation_index = 0
            for each_situation in simple_chat:
                if situation_index == 0:
                    for i in each_situation:
                        if i in chat_info:
                            if '已发送' in chat_info:
                                return False
                            else:
                                return 'send_time'
                elif situation_index == 1:
                    for i in each_situation:
                        if i in chat_info:
                            if '已发送' in chat_info:
                                return False
                            else:
                                return 'go_on_chat'
                situation_index += 1

            if '对方想发送' or '您是否同意' in no_repeat:
                time.sleep(random.uniform(1, 2))
                try:
                    agree_button = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[3]/div[1]/span[2]')
                except Exception as e:
                    local_def = sys._getframe().f_code.co_name
                    write_exception(e, local_def, self.local_class)
                    return False
                else:
                    self.driver.execute_script("arguments[0].click();", agree_button)
                    return True
            else:
                return False

    def sure_change(self):
        time.sleep(random.uniform(1, 2))
        try:
            sure_change = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[3]/div/span[2]')
        except Exception as e:
            local_def = sys._getframe().f_code.co_name
            write_exception(e, local_def, self.local_class)
            sure_change = self.driver.find_element_by_xpath('/html/body/div[6]/div[2]/div[3]/div/span[2]')

        self.driver.execute_script("arguments[0].click();", sure_change)

    def exchange_information(self):
        time.sleep(random.uniform(1, 2))
        request_resume = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[1]/a[3]')
        self.driver.execute_script("arguments[0].click();", request_resume)
        self.sure_change()

        request_mobile = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[1]/a[4]')
        self.driver.execute_script("arguments[0].click();", request_mobile)
        self.sure_change()

        request_wechat = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[1]/a[5]')
        self.driver.execute_script("arguments[0].click();", request_wechat)    # get some trouble in change wechat

        self.sure_change()

    def request_base_info(self, data_uid):
        url = self.base_url + f'/wapi/zpboss/h5/chat/geek.json?uid={data_uid}'
        cookie = importlib.reload(python_config).cookie
        headers = {
            'Referer': self.chat_url,
            'Token': python_config.TOKEN,
            'User-Agent': ua.random,
            'Cookie': cookie
        }
        try:
            json_base_info = requests.get(url, headers=headers, verify=False).text
            json_status = json.loads(json_base_info)
            if json_status['zpData']['status'] == -1:
                return False   # get failed
            elif json_status['zpData']['status'] == 1:
                data = json_status['zpData']['data']
                age_char = re.findall(r'(\d+)', data['ageDesc'])
                if age_char:
                    age = int(age_char[0])
                    date_of_birth = time.localtime().tm_year - age
                else:
                    date_of_birth = time.localtime().tm_year

                weixin = data['weixin'] if data['weixin'] else ''
                phone = data['phone'] if data['phone'] else '123'
                if phone == '123':
                    if weixin.isdigit():
                        mobile_phone = weixin
                    else:
                        info_phone = re.findall(r'(1\d{10})', weixin)
                        if info_phone:
                            mobile_phone = info_phone[0]
                        else:
                            mobile_phone = phone
                else:
                    mobile_phone = phone

                json_info = {
                    'name': data['name'],
                    'mobile_phone': mobile_phone,
                    'company_dpt': 1,
                    'resume_key': '',
                    'gender': data['gender'] if int(data['gender']) == 1 else 2,
                    'date_of_birth': f'{date_of_birth}-01-01',
                    'current_residency': data['city'],
                    'years_of_working': data['year'],
                    'hukou': '',
                    'current_salary': '',
                    'politics_status': '',
                    'marital_status': 2,
                    'address': '',
                    'zip_code': '',
                    'email': '',
                    'home_telephone': '',
                    'personal_home_page': weixin,
                    'excecutiveneed': '',
                    'self_assessment': '',
                    'i_can_start': '',
                    'employment_type': 1,
                    'industry_expected': '',
                    'working_place_expected': '广州',
                    'salary_expected': data['price'],
                    'job_function_expected': 1,
                    'current_situation': data['positionStatus'],
                    'word_experience': [],
                    'project_experience': [],
                    'education': [],
                    'honors_awards': [],
                    'practical_experience': [],
                    'training': '',
                    'language': [],
                    'it_skill': [],
                    'certifications': [],
                    'is_viewed': 1,
                    'resume_date': data['addTime'],
                    'get_type': '',
                    'external_resume_id': data['encryptUid'],
                    'labeltype': 1,
                    'resume_logo': data['largeAvatar'],
                    'resume_from': 3,
                    'account_from': python_config.account_from,
                    'update_date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                }
                return json_info
        except Exception as e:
            local_def = sys._getframe().f_code.co_name
            write_exception(e, local_def, self.local_class)

    def request_detail_info(self, data_eid):
        html_url = self.base_url + f"/chat/geek/chatinfo?uid={data_eid}"
        cookie = importlib.reload(python_config).cookie
        headers = {
            'Referer': self.chat_url,
            'Token': python_config.TOKEN,
            'User-Agent': ua.random,
            'Cookie': cookie
        }
        html_detail_info = requests.get(html_url, headers=headers, verify=False).text
        return html_detail_info

    def save_message(self, name, phone, e_id, data_uid):
        """
        上传信息成功后需要把聊天记录上传到服务器
        :param name: 聊天的人的名字
        :param phone: 电话号码
        :param e_id: 简历id(虽然不能搜),但是可以保证唯一
        :param data_uid: 用来获取聊天信息的id
        :return:
        """
        messages = self.request_chat_msg(data_uid)
        base_chat = {
            'name': name,
            'phone': phone,
            'data': []
        }
        data = base_chat['data']
        for each in messages:
            info = each.get('pushText')
            time_info = each.get('time')
            if info:
                dict_chat = {
                    'chat_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_info) / 1000)),
                    'from_uid': each['from']['uid'],
                    'from_name': each['from']['name'],
                    'to_uid': each['to']['uid'],
                    'to_name': each['to']['name'],
                    'message': info,
                    'resume_id': e_id,
                }
                data.append(dict_chat)
        msg_url = python_config.MSG_URL
        print('聊天信息状态--准备写入聊天信息...')
        with open('./utils/chat_msg.json', 'a') as file:
            file.write(json.dumps(base_chat) + ',\n')
            # LOG.info(f'聊天信息--和{name}的聊天信息已经存储.')

        status = self.session.post(msg_url, json=base_chat)
        LOG.info(f'聊天信息--和{name}的聊天信息存储状态为{status.text}.')

    def request_chat_msg(self, gid):
        time.sleep(random.uniform(1, 3))
        url = f'https://www.zhipin.com/wapi/zpchat/boss/historyMsg?gid={gid}'
        cookie = importlib.reload(python_config).cookie
        headers = {
            'Referer': self.chat_url,
            'Token': python_config.TOKEN,
            'User-Agent': ua.random,
            'Cookie': cookie
        }
        response_text = requests.get(url, headers=headers, verify=False).text
        time.sleep(random.uniform(1, 2))
        data = json.loads(response_text)
        messages = data['zpData']['messages']
        return messages

    def post_resume(self, base_json, data_uid):
        time.sleep(random.uniform(2, 3))
        # 这里将那个图片转换为Base_64然后准备接下来的事情
        with open(BASE_DIR + '/Baidu_ocr/base.png', 'rb') as f:
            base64_data = base64.b64encode(f.read())
            base_img = base64_data.decode()  # 要处理这个base_img
            # print(f'data:image/png;base64,{base_img}')   # 这里是输出测试
        info = {
            'account': python_config.account,
            'boss_pic': f'data:image/jpeg;base64,{base_img}',
            'data': [base_json]
        }
        print(info)
        url = python_config.POST_URL   # api not sure
        mobile_phone = base_json['mobile_phone'] if base_json['mobile_phone'] != '123' else ''
        name = base_json['name']
        e_id = base_json['external_resume_id']
        if base_json and mobile_phone:
            # if base_json:
            with open('./utils/resume_info.txt', 'a') as json_file:
                json_file.write(str(info) + ',\n')
            try:
                response = self.session.post(url, json=info)
            except Exception as e:
                local_def = sys._getframe().f_code.co_name
                write_exception(e, local_def, self.local_class)
                LOG.error('目标计算机拒绝链接')
            else:
                LOG.info(f'沟通的数据插入详情为:{response.text}')
                if json.loads(response.text)['error_code'] == 0:
                    time.sleep(random.uniform(1, 2))
                    back_chat = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[1]/div[2]/span[1]'
                    )
                    self.driver.execute_script("arguments[0].click();", back_chat)
                    back_chat.click()
                    time.sleep(1)
                    msg_box = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[2]')
                    msg_box.send_keys(python_config.get_and_reply)
                    time.sleep(random.uniform(1, 2))
                    send_button = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[3]/button')
                    self.driver.execute_script("arguments[0].click();", send_button)
                    LOG.info(f'Reply信息状态:{name}:{mobile_phone}::的回复消息发送成功.')
                    time.sleep(random.uniform(1, 2))
                    self.save_message(name, mobile_phone, e_id, data_uid)
        else:
            LOG.info('reject: 对方还未回复关键信息,简历未能上传')

    def parse_detail_page(self, base_json, html_detail):
        time.sleep(random.uniform(1, 2))
        parser = etree.HTML(html_detail)
        self_assessment_xpt = parser.xpath('/html/body/div/div/div[1]/div[2]/div[2]//text()')
        base_json['self_assessment'] = ''.join(self_assessment_xpt)
        resume_key_xpt = parser.xpath('/html/body/div/div/div[2]/div/div/span[1]/text()')[0]
        base_json['resume_key'] = resume_key_xpt

        work_experience_xpt = parser.xpath('/html/body/div/div/div[3]/div/div/div')
        if work_experience_xpt:
            num_of_wex = len(work_experience_xpt)
            for i in range(1, num_of_wex+1):
                work_time_range = parser.xpath(f'/html/body/div/div/div[3]/div/div/div[{i}]/span/text()')[0]
                company_and_skill = parser.xpath(f'/html/body/div/div/div[3]/div/div/div[{i}]/h4//text()')
                company_info = ''.join(company_and_skill).replace(' ', '').strip()
                do_what = parser.xpath(f'/html/body/div/div/div[3]/div/div/div[{i}]/div/div//text()')
                do_what_info = ''.join(do_what).replace(' ', '').strip()
                work_info_one = {
                    '起止时间': work_time_range,
                    '公司信息': company_info,
                    '工作内容': do_what_info
                }
                base_json['word_experience'].append(work_info_one)

        if '项目经验' in html_detail:
            edu_code = 5
            project_experience_xpt = parser.xpath('/html/body/div/div/div[4]/div/div/div')
            if project_experience_xpt:
                num_of_pe = len(project_experience_xpt)
                for x in range(1, num_of_pe+1):
                    project_time_range = parser.xpath(f'/html/body/div/div/div[4]/div/div/div[{x}]/span/text()')[0]
                    project_and_skill = parser.xpath(f'/html/body/div/div/div[4]/div/div/div[{x}]/h4//text()')
                    project_info = ''.join(project_and_skill).replace(' ', '').strip()
                    done_what = parser.xpath(f'/html/body/div/div/div[4]/div/div/div[{x}]/div/div//text()')
                    done_what_info = ''.join(done_what).replace(' ', '').strip()
                    project_info_one = {
                        '起止时间': project_time_range,
                        '项目信息': project_info,
                        '项目内容': done_what_info
                    }
                    base_json['project_experience'].append(project_info_one)
        else:
            edu_code = 4

        education_xpt = parser.xpath(f'/html/body/div/div/div[{edu_code}]/div/div/div/span')
        if education_xpt:
            education_time_range = parser.xpath(f'/html/body/div/div/div[{edu_code}]/div/div/div[1]/span/text()')[0]
            school_and_class = parser.xpath(f'/html/body/div/div/div[{edu_code}]/div/div/div[1]/h4//text()')
            school_and_class_info = ''.join(school_and_class).replace(' ', '').strip()
            education_info = {
                '起止时间': education_time_range,
                '学校学历': school_and_class_info
            }
            base_json['education'].append(education_info)

        self.go_resume(base_json)

    def go_resume(self, base_json):
        """
        去到附件简历位置，先判断有吗 然后又再识别。
        :return:
        """
        resume_extra = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[1]/div[2]/span[3]'
        )
        attribute = resume_extra.get_attribute('class')
        if 'gray' in attribute:
            print('没有获取到附加简历...')
            return
        else:
            print('拿到了简历...')
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", resume_extra)
            time.sleep(2)
            self.driver.save_screenshot(BASE_DIR + '/Baidu_ocr/base.png')
            time.sleep(2)
            img = self.driver.find_element_by_xpath(
                '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[4]/div/div/img')
            location = img.location
            left = location['x']
            top = location['y']
            right = left + 860
            bottom = top + 650

            img = Image.open(BASE_DIR + '/Baidu_ocr/base.png')
            im = img.crop((left, top, right, bottom))
            im.save(BASE_DIR + '/Baidu_ocr/base.png')
            time.sleep(1)
            try:
                app_email = client.main()
            except Exception as e:
                LOG.error('图片识别转码网络连接超时...')
                write_exception(e, 'go_resume', 'BossHelll')
            else:
                if app_email:
                    base_json['email'] = app_email

            # resume_chat = self.driver.find_element_by_xpath(
            #     '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[1]/div[2]/span[1]'
            # )
            # time.sleep(2)
            # self.driver.execute_script("arguments[0].click();", resume_chat)

        time.sleep(3)

    def do_judge_who_is_last_one(self, gid):
        # False : 在需要发消息的情况里面非关键字的情况下 不需要发送信息
        # True  : 在需要发消息的情况里面非关键字的情况下 需要发送信息
        messages = self.request_chat_msg(gid)
        # if len(messages) < 5:
        #     return True
        # ================== 上面的这个容错判断很容易受到其它条件影响 ===================
        who_send = str(messages[-1]['from']['uid'])
        try:
            push_text = messages[-1]['pushText']
        except Exception as e:
            local_def = sys._getframe().f_code.co_name
            write_exception(e, local_def, self.local_class)
            return False
        else:
            if '牛人还没回复？' or '您的主页' not in push_text:
                if who_send != gid:  # we send
                    return False     # don't send request
                else:
                    return True      # need to send
            else:
                return False

    def ask_for_information(self):
        time.sleep(random.uniform(1, 2))

        all_people = self.driver.find_elements_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[1]/ul[2]/li')
        for each_person in all_people:
            time.sleep(random.uniform(2, 3))
            LOG.info('======================= 我是数据分割线 ========================')
            name_clickable = each_person.find_element_by_xpath('./a/div[2]/div/span[2]')
            self.driver.execute_script("arguments[0].click();", name_clickable)   # way two
            time.sleep(random.uniform(1, 2))
            flag = self.judge_whether_exchange()    # like the name
            gid = each_person.find_element_by_xpath('./a').get_attribute('data-uid')
            if flag:
                judge_pos = self.driver.find_element_by_xpath('//*[@id="header"]/div/div/div[1]/div[2]/span').text
                if flag == 'send_time':
                    LOG.info('当前状态-咨询时间')
                    msg_box = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[2]')
                    if 'php' or 'python' in judge_pos.lower():
                        msg_box.send_keys(python_config.send_time_tec)  # send msg  如果是程序员回复这条信息
                    else:
                        msg_box.send_keys(python_config.send_time_oth)
                    time.sleep(random.uniform(1, 2))
                    send_button = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[3]/button')
                    self.driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(random.uniform(1, 2))
                    self.exchange_information()
                    LOG.info('检查状态-已经回复咨询时间,如果回复再进行验证.')
                elif flag == 'go_on_chat':
                    LOG.info('当前状态-继续沟通')
                    msg_box = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[2]')
                    msg_box.send_keys(python_config.go_chat)  # send msg
                    time.sleep(random.uniform(1, 2))
                    send_button = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[3]/button')
                    self.driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(random.uniform(1, 2))
                    self.exchange_information()
                    LOG.info('检查状态-已经回复问候情况,如果回复再进行验证.')
                else:
                    LOG.info('当前状态-继续判断')
                    code_status = self.do_judge_who_is_last_one(gid)
                    if code_status:
                        msg_box = self.driver.find_element_by_xpath(
                            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[2]')
                        msg_box.send_keys(python_config.chat_msg)
                        time.sleep(random.uniform(1, 2))
                        send_button = self.driver.find_element_by_xpath(
                            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[2]/div[2]/div[3]/button')
                        self.driver.execute_script("arguments[0].click();", send_button)
                        time.sleep(random.uniform(1, 2))
                        self.exchange_information()
                        LOG.info('检查状态-已经请求消息,如果回复再进行验证.')
                    else:
                        LOG.info('检查状态-等待他人回复消息后再进行交换.')
            else:
                if flag is None:
                    LOG.info('检查状态-对方拒绝前来面试.')
                    continue
                else:
                    LOG.info('检查状态-对方回复了信息,尝试上传简历.')

            if flag is not None:
                url_node = each_person.find_element_by_xpath('./a')
                # suffix_url = url_node.get_attribute('data-url')
                data_uid = url_node.get_attribute('data-uid')     # base info
                data_eid = url_node.get_attribute('data-eid')     # detail info
                base_json = self.request_base_info(data_uid)      # return json-format dict file
                if base_json:
                    html_detail = self.request_detail_info(data_eid)
                    self.parse_detail_page(base_json, html_detail)

                    self.post_resume(base_json, data_uid)

    def chose_each_position(self):
        time.sleep(0.5)
        unread = self.driver.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/label/span')
        unread.click()
        time.sleep(random.uniform(0, 1))  # filter unread
        each_pos = self.driver.find_element_by_xpath('//*[@id="header"]/div/div/div[1]/div[2]/span')
        self.driver.execute_script("arguments[0].click();", each_pos)
        time.sleep(random.uniform(0, 1))
        all_pos = self.driver.find_elements_by_xpath('//*[@id="header"]/div/div/div[1]/div[2]/div/ul/li')[1:]
        for pos in all_pos:
            time.sleep(random.uniform(0, 1))
            self.driver.execute_script("arguments[0].click();", pos)
            time.sleep(random.uniform(1, 2))
            self.ask_for_information()  # To solve now 主要聊天信息处理(容错状态大致没有问题了)

    # ===================================================================================== #

    def test_msg(self):
        """
        开发的时候的调试状态，后面没有用到的...
        :return:
        """
        resume_extra = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[1]/div[2]/span[3]'
        )
        attribute = resume_extra.get_attribute('class')
        if 'gray' in attribute:
            print('没有获取到附加简历...')
            pass
        else:
            # resume_extra.click()
            print('拿到了简历...')
            time.sleep(2)
            self.driver.execute_script("arguments[0].click();", resume_extra)
            time.sleep(2)
            self.driver.save_screenshot(BASE_DIR + '/Baidu_ocr/base.png')
            time.sleep(4)
            img = self.driver.find_element_by_xpath(
                '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[4]/div/div/img')
            location = img.location
            left = location['x']
            top = location['y']
            right = left + 650
            bottom = top + 700

            img = Image.open(BASE_DIR + '/Baidu_ocr/base.png')
            im = img.crop((left, top, right, bottom))
            im.save(BASE_DIR + '/Baidu_ocr/base.png')
            time.sleep(1)

    # ===================================================================================== #

    def run(self):
        self.handle_selenium_cookies()     # about cookie 处理基础的页面状态(不用调)
        self.chose_each_position()
        time.sleep(3)
        self.driver.refresh()     # 消息处理完毕后，刷新哈，避免新消息被触发


# ========================================================================================== #
class CallForNiu(object):
    """
    这里是用来专门来处理给牛人打招呼的
    """
    def __init__(self):
        self.base_url = 'https://www.zhipin.com'
        self.chat_url = self.base_url + '/chat/im?mu=chat'
        self.local_class = self.__class__.__name__

        self.session = requests.Session()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=8055 --user-data-dir="C:\selenium_boss\AutomationProfile"   # start chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

    def select_salary_range(self):
        # //*[@id="wrap"]/div/div[2]/div[2]/div/div/span
        filter_button = self.driver.find_element_by_xpath('//*[@id="wrap"]/div/div[2]/div[2]/div/div/span')
        self.driver.execute_script("arguments[0].click();", filter_button)
        time.sleep(0.3)

        range_salary = self.driver.find_element_by_xpath(
            '//*[@id="wrap"]/div/div[2]/div[2]/div/div/div[2]/div[1]/div/dl[1]/dd/a[4]/span')
        self.driver.execute_script("arguments[0].click();", range_salary)
        time.sleep(0.3)

        sure_filter = self.driver.find_element_by_xpath(
            '//*[@id="wrap"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/span[2]'
        )
        self.driver.execute_script("arguments[0].click();", sure_filter)
        time.sleep(0.3)

    def chose_position_about_niu(self):
        time.sleep(random.uniform(1, 2))
        recommend_positions = self.driver.find_element_by_xpath('//*[@id="header"]/div/div/div[2]/div[2]/span')
        recommend_positions.click()
        time.sleep(random.uniform(1, 2))
        # self.driver.execute_script("arguments[0].click();", recommend_positions)  # way two
        all_positions = self.driver.find_elements_by_xpath('//*[@id="header"]/div/div/div[2]/div[2]/div/ul/li')[1:]
        for each_pos in all_positions:
            time.sleep(random.uniform(1, 2))
            self.driver.execute_script("arguments[0].click();", each_pos)  # way two
            time.sleep(random.uniform(1, 2))
            self.driver.switch_to.frame('syncFrame')
            self.select_salary_range()
            for _ in range(10):
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.uniform(2, 4))
            all_people = self.driver.find_elements_by_xpath('//*[@id="recommend-list"]/div/ul/li')[1:]
            default_pos = 0
            for each_people in all_people:

                time.sleep(random.uniform(0, 1))
                button_label = each_people.find_element_by_xpath('./div/div/div[2]/div/span/button').text
                if '继续沟通' in button_label:
                    LOG.info('打过招呼了,跳过这个人')
                    continue
                try:
                    say_hi = each_people.find_element_by_xpath('./div/div/div[2]/div/span/button')
                    self.driver.execute_script("arguments[0].click();", say_hi)  # way two
                except Exception as e:
                    local_def = sys._getframe().f_code.co_name
                    write_exception(e, local_def, self.local_class)
                    break

                try:
                    WebDriverWait(self.driver, 5).until(
                        expected_conditions.presence_of_element_located((
                            By.XPATH,
                            '//*[@id="recommend-list"]/div/ul/li[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]'))
                    )
                except Exception as e:
                    local_def = sys._getframe().f_code.co_name
                    write_exception(e, local_def, self.local_class)
                else:
                    # //*[@id="recommend-list"]/div/ul/li[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]//label
                    # //*[@id="recommend-list"]/div/ul/li[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]/button
                    no_notify_more = self.driver.find_element_by_xpath(
                        '//*[@id="recommend-list"]/div/ul/li[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]//label'
                    )
                    self.driver.execute_script("arguments[0].click();", no_notify_more)
                    sure_button = self.driver.find_element_by_xpath(
                        '//*[@id="recommend-list"]/div/ul/li[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]/button'
                    )
                    self.driver.execute_script("arguments[0].click();", sure_button)
                finally:
                    # 180px
                    self.driver.execute_script(f"window.scrollTo(0,{default_pos + 185})")
                    default_pos += 185
                    time.sleep(random.uniform(0, 1))

    def powerful_person_recommend(self):
        time.sleep(random.uniform(1, 3))
        niu = self.driver.find_element_by_xpath('//*[@id="main"]/div[1]/div/dl[2]/dt/a')
        niu.click()
        self.chose_position_about_niu()
        # self.driver.execute_script("arguments[0].click();", niu)   # way two
        time.sleep(random.uniform(1, 3))

    def run(self):
        self.powerful_person_recommend()   # niu people  向牛人打招呼(完成)


# ========================================================================================== #
class ClearAllChat(object):
    """
    这里就是专门用来清理聊天信息的
    """
    def __init__(self):
        self.base_url = 'https://www.zhipin.com'
        self.chat_url = self.base_url + '/chat/im?mu=chat'
        self.local_class = self.__class__.__name__
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=8055 --user-data-dir="C:\selenium_boss\AutomationProfile"   # start chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

        # ===================================================================================== #

    def delete_all(self):
        LOG.info('== == 例行清除所有信息,等待有人回复信息的状态 == ==')
        self.driver.get(self.chat_url)
        time.sleep(random.uniform(5, 10))
        nums = self.driver.find_elements_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[1]/ul[2]/li')
        all_nums = len(nums)
        for _ in range(all_nums):
            try:
                self.delete_one()
            except Exception as e:
                local_def = sys._getframe().f_code.co_name
                write_exception(e, local_def, self.local_class)
                self.delete_one(True)

    def delete_one(self, flag=None):
        delete_one = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/div[2]/div[3]/div[1]/ul[2]/li[1]/a/div[2]/div/div/div/span[3]'
        )
        self.driver.execute_script("arguments[0].click();", delete_one)
        time.sleep(random.uniform(2, 3))
        if not flag:
            sure_that = self.driver.find_element_by_xpath(
                '/html/body/div[5]/div[2]/div[3]/div/span[2]'
            )
        else:
            sure_that = self.driver.find_element_by_xpath(
                '/html/body/div[6]/div[2]/div[3]/div/span[2]'
            )
        self.driver.execute_script("arguments[0].click();", sure_that)
        time.sleep(random.uniform(1, 2))

        # ===================================================================================== #
    def run(self):
        # 每天凌晨1点到4点清除所有消息(因为这个时候可能没有人回复消息,就不会错乱了,这个Boss消息是及时的就怕有人问然后改变处理消息的状态)
        self.delete_all()    # delete all contact # need to run at 01:00-04:00


# ========================================================================================== #
class CallForPosition(object):
    """
    发布职位的位置
    """

    def __init__(self):
        self.base_url = 'https://www.zhipin.com'
        self.position_url = self.base_url + '/chat/im?mu=%2Fbossweb%2Fjobedit%2F0.html'
        self.local_class = self.__class__.__name__
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=8055 --user-data-dir="C:\selenium_boss\AutomationProfile"   # start chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

        # ===================================================================================== #

    def run(self):
        pass


# ========================================================================================== #
def write_exception(e, local_def, local_class):
    """
    这里是写异常信息的，就是避免小黄线，我干脆把错误信息e写入文本算了，反正也能查看异常的状态信息
    :param e: 异常信息
    :param local_def: 发生异常的函数
    :param local_class: 发生异常的类
    :return: 不返回
    """
    # local_def = sys._getframe().f_code.co_name
    # self.local_class = self.__class__.__name__
    # write_exception(e, local_def, self.local_class)
    with open('./utils/error_log.txt', 'a', encoding='utf-8') as fl:
        t_now = time.strftime('%m-%d %H:%M:%S', time.localtime())
        fl.write(f'{t_now}:{local_class}>{local_def}::{str(e)}')


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
    requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


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
                print('\r清除程序开始了,正在休眠中...', end='')
                # print('清除程序开始了,正在休眠中...')
                time.sleep(60)
            else:
                print('\r不是清除程序运行的时间,继续休眠中...', end='')
                # print('不是清除程序运行的时间,继续休眠中...')
                time.sleep(60)

        return wrapper
    return work_time


def hello_timer(set_time):
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
                print('\r招呼和主动找牛人程序开始了,正在休眠中...', end='')
                time.sleep(60)
            else:
                print('\r不是招呼和主动找牛人程序运行的时间,继续休眠中...', end='')
                time.sleep(60)

        return wrapper
    return work_time


# 数据扫描时间为指定每小时，因为避免以后数据过多的问题 每十分钟扫描一次
@hello_timer(python_config.time_tic)
def thread_one_hello():
    """
    抓们拿一个线程来处理打招呼，时间到了指定的时间就开始处理信息
    :return: 不返回
    """
    try:
        find_app = BossHello()
        find_app.run()
    except Exception as e:
        write_exception(e, 'thread_one_hello', '需要重新登录')
        msg = f"********* HR 数据自动化 *********\n负责人：{python_config.handler}\n状态原因：其它地方登录,程序已经离线" \
              f"\n处理标准：请重新登录账号,并替换本地的cookie"
        send_rtx_msg(msg)


@clear_timer(['04:30'])
def thread_two_clear():
    """
    专门开了第二个线程来处理多余的聊天信息,保证聊天界面的简洁,每天大家都睡着了的情况下，不会有新信息来的情况下就要删除了
    :return: 不返回
    """
    try:
        delete_app = ClearAllChat()
        delete_app.run()
    except Exception as e:
        write_exception(e, 'thread_two_clear', '需要重新登录')
        msg = f"********* HR 数据自动化 *********\n负责人：{python_config.handler}\n状态原因：其它地方登录,程序已经离线" \
              f"\n处理标准：请重新登录账号,并替换本地的cookie"
        send_rtx_msg(msg)


@clear_timer(['06:00'])
def thread_three_niu():
    """
    专门开了第三个线程来处理给牛人打招呼,就是主动要人来聊天,每个职位每次打招呼10页牛人,大概有100个,每天打招呼一次[根据业务数据量只能减少]
    :return: 不返回
    """
    try:
        niu_app = CallForNiu()
        niu_app.run()
    except Exception as e:
        write_exception(e, 'thread_three_niu', '需要重新登录')
        msg = f"********* HR 数据自动化 *********\n负责人：{python_config.handler}\n状态原因：其它地方登录,程序已经离线" \
              f"\n处理标准：请重新登录账号,并替换本地的cookie"
        send_rtx_msg(msg)


@hello_timer(['02:00'])
def thread_four_position():
    """
        专门开了第四个线程来处理职位发布信息
        :return: 不返回
        """
    try:
        post_app = CallForPosition()
        post_app.run()
    except Exception as e:
        write_exception(e, 'thread_three_niu', '需要重新登录')
        msg = f"********* HR 数据自动化 *********\n负责人：{python_config.handler}\n状态原因：其它地方登录,程序已经离线" \
              f"\n处理标准：请重新登录账号,并替换本地的cookie"
        send_rtx_msg(msg)


def development_mode():
    # 开发者模块，调试的时候用的
    find_app = BossHello()
    find_app.run()
    # find_app.test_msg()
    # time.sleep(100)  # 等待功能二
    # delete_app = ClearAllChat()
    # delete_app.run()
    # time.sleep(100)  # 等待功能三
    # niu_app = CallForNiu()
    # niu_app.run()


def main():
    """
    程序的主要启动入口，就是这里来开启各个线程，让每个线程去做事。
    :return: 不返回
    """
    development_mode()
    print('调试的时候 要卡在这里...')
    time.sleep(10000)
    while True:
        hello_t = Thread(target=thread_one_hello)
        clear_t = Thread(target=thread_two_clear)
        call_t = Thread(target=thread_three_niu)

        hello_t.start()
        clear_t.start()
        call_t.start()

        hello_t.join()
        clear_t.join()
        call_t.join()


if __name__ == '__main__':
    main()
