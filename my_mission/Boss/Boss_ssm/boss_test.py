#!/usr/bin/env python
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
from selenium.webdriver.common.keys import Keys
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
                    'resume_date': time.strftime("%Y-%m-%d", time.localtime()),
                    'get_type': '',
                    'external_resume_id': data['encryptUid'],
                    'labeltype': 1,
                    'resume_logo': data['largeAvatar'],
                    'resume_from': 3,
                    'account_from': python_config.account_from,
                    'update_date': data['addTime'],
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
        msg_url = python_config.TEST_MSG_URL
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
        url = python_config.TEST_POST_URL   # api not sure
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
            try:
                img = self.driver.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/div[2]/div[4]/div[2]/div[4]/div/div/img')
            except Exception as e:
                return
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
        self.position_url = self.base_url + '/chat/im?mu=%2Fbossweb%2Fjoblist.html'
        self.local_class = self.__class__.__name__
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=8055 --user-data-dir="C:\selenium_boss\AutomationProfile"   # start chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

        # ===================================================================================== #

    def go_post_position(self):
        self.driver.get(self.position_url)
        # 接下来就是切换子框架
        time.sleep(random.uniform(0, 1))
        self.driver.switch_to.frame('frameContainer')
        time.sleep(random.uniform(0, 1))
        self.judge_now_status()   # 判断当前页面状态
        time.sleep(random.uniform(1, 2))
        self.go_to_post()

    def go_to_post(self):
        self.driver.switch_to.frame('frameContainer')
        time.sleep(random.uniform(0, 1))
        # 这里要从api里面拿取需要处理的信息
        position_name = '买定离手'
        position_type = 'Java'
        exp_info = 3
        edu_info = 6
        salary_low = 5
        salary_high = 6 - salary_low
        position_desc = '测试数据'
        position_key = ['人工智能', '不知道能']

        b_name = self.driver.find_element_by_xpath('//*[@id="container"]/div[1]/form/div[3]/div[2]/span/input')
        b_name.clear()
        b_name.send_keys(position_name)

        b_type = self.driver.find_element_by_xpath('//*[@id="container"]/div[1]/form/div[4]/div[2]/span/input[1]')
        b_type.click()
        time.sleep(1)
        b_type_b = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[1]/h3/div/div[1]/input')
        b_type_b.send_keys(position_type)
        time.sleep(1)
        b_type_b_c = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[1]/h3/div/div[2]/div[1]/ul/li')
        b_type_b_c.click()

        exp_class = self.driver.find_element_by_xpath(
            f'//*[@id="container"]/div[1]/form/div[9]/div[2]/div[1]/div/ul/li[{exp_info}]'
        )
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", exp_class)

        edu_class = self.driver.find_element_by_xpath(
            f'//*[@id="container"]/div[1]/form/div[9]/div[2]/div[2]/div/ul/li[{edu_info}]')
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", edu_class)

        salary_l = self.driver.find_element_by_xpath(
            f'//*[@id="container"]/div[1]/form/div[10]/div[2]/div[1]/div/ul/li[{salary_low}]')
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", salary_l)

        salary_h = self.driver.find_element_by_xpath(
            f'//*[@id="container"]/div[1]/form/div[10]/div[2]/div[2]/div/ul/li[{salary_high}]')
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", salary_h)

        position_d = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/form/div[13]/div[2]/div/textarea')
        position_d.send_keys(position_desc)
        time.sleep(1)

        key_p = self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[1]/form/div[14]/div[2]/div/span/div/input')
        for pk in position_key:
            key_p.send_keys(pk)
            key_p.send_keys(Keys.ENTER)
            time.sleep(0.5)

    def judge_now_status(self):
        time.sleep(1)
        pos_btn = self.driver.find_element_by_xpath('//*[@id="container"]/div[1]/div/div[1]/div/a')
        pos_btn.click()
        time.sleep(random.uniform(1, 2))
        self.driver.refresh()   # 这里是保证页面有咩有数据都清除一下

    def run(self):
        self.go_post_position()


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


def test_main():
    a = {'account': 'Ling', 'data': [{'name': '伍鑫1', 'mobile_phone': '18594226629', 'company_dpt': 1, 'source_file': '3_a5adad659136c70222HN72N24GV0~.jpg', 'resume_key': 'Python', 'gender': 1, 'date_of_birth': '1996-01-01', 'current_residency': '广州', 'years_of_working': '2年', 'hukou': '', 'current_salary': '', 'politics_status': '', 'marital_status': 2, 'address': '', 'zip_code': '', 'email': 'xx8848@qq.com', 'home_telephone': '', 'personal_home_page': '13037494129', 'excecutiveneed': '', 'self_assessment': '简单', 'i_can_start': '', 'employment_type': 1, 'industry_expected': '', 'working_place_expected': '广州', 'salary_expected': '面议', 'job_function_expected': 1, 'current_situation': '离职-随时到岗', 'word_experience': [{'起止时间': '2018.03-至今', '公司信息': '长沙世速网络科技有限公司Python', '工作内容': '1、参与网站的平台开发，架构设计和维护参与需求分析和产品设计2、撰写Python，Django进行后台及API的开发3、负责客户需求的数据采集，不断提升客户需求的后台数据量。4、负责对底层数据进行清洗后的针对具体问题的数据分析，并将数据分析报告提交。5、不断学习新技术和研发反爬，并处理工作过程中的问题。'}], 'project_experience': [{'起止时间': '2018.02-2019.03', '项目信息': '抖音数据收集抖音数据收集', '项目内容': '该项目收集热门的视频和抖音用户，流量，并且分析视频最受人喜爱，判断对广告投入是否有价值；项目职责：1、负责该项目的Spider的编写，研究网页各类反爬机制，抓取数据，清洗分析和入库。2、对抖音进行反爬处理，加了SSL的验证，通过Appium模拟人工分享链接。3、对抖音的css字体静态加密，在模拟发送请求遇到sign加密。找到加密的js文件，并对其进行解密，使用'}, {'起止时间': '2018.06-2018.10', '项目信息': '回头鱼商城开发', '项目内容': '回头鱼商城专注于国外原装进口保健品的电商网站，主要包括常用模块，如商品管理模块，登陆注册模块，订单管理模块，购物车管理模块和支付等。项目职责：1、用python的Django框架实现对项目的管理，用pymysql模块实现后台数据库的连接与ORM操作'}], 'education': [{'起止时间': '2014-2018', '学校学历': '永州职业技术学院\n计算机\n大专'}], 'honors_awards': [], 'practical_experience': [], 'training': '', 'language': [], 'it_skill': [], 'certifications': [], 'is_viewed': 1, 'resume_date': '2019-10-18', 'get_type': 1, 'external_resume_id': 'a5adad659136c70222HN72N24GV0~', 'labeltype': 1, 'resume_logo': 'https://img.bosszhipin.com/boss/avatar/avatar_14.png', 'resume_from': 3, 'account_from': '广州外宝电子商务有限公司', 'update_date': '2019-10-11'}]}

    boss_pic = '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mZmZBAcHM3DgQPR6Pfn5+Xz99dfcf//92o9Pr9fTp08f3nrrLWpra5udgOw3y97e3tTX13P8+HFSUlK04MLVyTMwMFBbzvfff88zzzzDvffey3XXXYePj48WbN100028+OKL2gWloqKC3NxcIiMjueiiizh48CCHDx9m+/btXHjhhXTt2pXg4GDKysp47rnnePrpp7UybNiwgS+++IKff/65xYDLlRtvvJHZs2eTmprKhg0buPTSS7Wnak0TPtir80NDQ3F3dycxMZGEhATGjBnjFJRYLBb27NnD999/z/PPP4/BYKBLly506tQJRVHo3r07FouF7OxsevbsSXFxMUePHiUiIkKrNRw7diwDBgzgxx9/1ALX9PR0rr76ampra7FarRiNRmbNmqWVy1FxcTGdO3dm27ZtDB06FA8PD7Zv3651rLbz9vYmNTWVgQMHap1zU1JS+Oqrr7j44ou54YYb+Otf/0ppaSnPPPMMQ4cOJTQ0lLKyMsrLy3Fzc+P999/niSeeYO7cubzwwgtawFVXV0dOTg5hYWGsWbOGr776itTUVO68806mTp2KoigsWbKEiy++mLKyMlavXk2XLl2cnpo+/vjj3Hjjjdx///3ceeed2vFmtVrp3LmzFjw1PQ6HDRvG/PnziYmJYeLEiVp/ud69e/PTTz85XaCfe+45brvtNoKDg8nPz+fYsWOMGjWKrl274u7uzg033EB1dTXPP/88H3zwAWDrj+Hj48MNN9yg3SC8/fbbko5XCNGiN998k0OHDjF9+nSGDh3K559/jtVqpaKigttuu00LTsB2U9/0webTTz/NkCFD+PrrrwHbA9P//Oc/VFdXO03neO0yGo1ERUUxaNAg9uzZA9iuYQMHDqSgoMCpr9PJmsDdd999XHrppVqipdbcfffdJCcns2HDhtPqS7RgwQJyc3OZPn26y4yyp+LEiRPa9X3w4MEsXLiQTz/9lOjo6HZJumW/5+nSpQv33HMPhw8fpl+/fixevLjZtAaDQftePT09tWuyqqrU1NRw+PBh6uvrtXu0hQsX0rt3b6eMilVVVbz88suEhYU5Lfeqq67Czc0NnU7H8uXL2bx5M//6178wm80u+y0L4UiOkNPk5ubmlLoU4L333mPGjBn06dMHNzc3Nm3axPjx49Hr9YSEhJxWE6imzfnsJ+yKigo++eQTHnzwQW6+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H3D11VdTVVVFcnIyDz/8MIqiUFFRwYUXXkhAQADV1dUUFRURERHhVI6IiAg6depETk4OcXFx3H///YwePRqwBXcHDhzQAmv7e3bXXXcdc+bM0T6z27dvHytXrqRTp06tbq8QQoiTk4DrPOXqqe3SpUt57733iIiIYOzYsdpnrdWGtVVubi4//vgj119/PWPGjAHg+PHjvPvuu7zyyitUVFRw/PhxoqKinOYbO3YsS5cuZc6cOYAtmCooKEBVVe0G4MCBA4wYMUK7+TGbzezbt4/77ruPu+++m61bt/L3v/+d3r17a0+EAbp168bWrVuJiIigc+fOzfbP559/TnV1tXaTFhERQXZ2NoqiaDeEEyZM0AKurKwszGYzW7duZfv27bi5uREYGMiOHTsA6N27N5WVlURHR7N9+3Z69uwJ2G46ExIStKY+9ptH+824r68vbm5uREVFsXPnThYtWsTDDz/M0KFDAXj++efZvXs3Pj4+gK0Z0Oeff67dxD333HOALTAZN24c//znP4mOjmbXrl1UVFQwbdo0du3aRW5uLseOHeP48eMcOXKEfv36sX//fm3elJQUHn74YcrLyzly5AgHDhwgPT2d//u//6Nfv36UlZWxdetW/Pz8UBSF+vp6jh496lSTEhgYyI033sizzz6Lp6cnI0eOZPjw4TzzzDOUlpZy1VVXsW3bNrp168aQIUOcnqrX19ezbNkyjh07xq233sr48eMB+OCDDxg2bBjDhg3Tpu3duzfFxcXaMdKW2q22fG42m0lISGDz5s3ceOONJ11GaGgooaGhzJs3j6FDh+Lj48N9993Hjz/+qH1/jmpra1m+fDlffvklx48fx8vLi2+//ZYHH3wQgP/85z/a91xQUMDMmTOdtm/s2LFs3boVsP3mWmp621RNTQ0ZGRk88sgj3HTTTaxbt46HHnqIKVOmMHPmTK3muEuXLsTHxxMWFkZMTEyz7f7f//6Ht7c3er1eqwXLy8tDURQKCwsJCgpixowZWsB17NgxTCYT69evZ+/evZhMJnx8fFi/fj2BgYFER0dTU1NDbGws69at02rfKioqSEpK0pq62c9RJ06cICEhQQvUwsLC2LFjB7/88gt33303AwYMAODee++luLgYk8nE559/ztGjR3njjTfIy8sjISGBp59+GoD09HRmzJjBSy+95HQc9+rVi/fff18L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'

    purl = f"/var/www/html/upfile/ebay/3_{a['data'][0]['external_resume_id']}.jpg"
    data = {
        'pdata': base64.b64decode(boss_pic),
        'filesize': 0,
        'purl': purl,
        'SUBMIT': 'Send'
    }
    requests.post('http://pic.fbeads.cn/curl_phase_cn.php', data=data)

    print(requests.post(python_config.POST_URL, json=a).text)


def development_mode():
    # 开发者模块，调试的时候用的
    # find_app = BossHello()
    # find_app = CallForPosition()
    # find_app.run()
    test_main()
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
