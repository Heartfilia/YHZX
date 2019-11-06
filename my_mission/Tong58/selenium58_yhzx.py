#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 15:08
# @Author  : Lodge
import os
import re
# from threading import Thread

import cv2
import sys
import json
import time
import base64
import random
import logging
import urllib3
import importlib
# from functools import wraps
from logging import getLogger
import matplotlib.pyplot as plt
from fontTools.ttLib import TTFont
from skimage.measure import compare_ssim
# from helper.Baidu_ocr.client import main_ocr

import requests
from lxml import etree
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions   # 不用EC 因为EC会有小黄下划线 不好看

from helper import python_config   # 这里是导入配置文件
# 这个可以做成完全不用自动化的程序,但是设计之初是有可能需要沟通交流功能,所以做成半自动化的

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
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # chrome.exe --remote-debugging-port=58580 --user-data-dir="C:\selenium_58_yh\AutomationProfile"  # start chrome
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.chrome_port}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

    def post_data_down(self, info_json):
        if info_json['mobile_phone'].isdigit():
            info = {
                'account': python_config.account_from,
                'data': [info_json]
            }
            url = python_config.POST_URL_DOWN
            print('info:', info)
            try:
                response = self.session.post(url, json=info)
            except Exception as e:
                LOG.error('目标计算机拒绝链接')
            else:
                LOG.info(f'数据插入详情为:{response.text}')
        else:
            print('解码失败:', info_json)

    @staticmethod
    def down_compare_img():
        image_dynamic = BASE_DIR + r"\helper\fonts\plt.png"   # 这就是动态的图片,通过前面程序保存的

        # print('开始比较图片中...')
        for i in range(10):  # 意思就是识别图片0 到 9
            time.sleep(0.1)
            image1 = BASE_DIR + rf"\helper\fonts\digit_{i}.png"     # 待识别的字符图片
            image_a = cv2.imread(image1)
            image_b = cv2.imread(image_dynamic)
            gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
            gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
            (score, diff) = compare_ssim(gray_a, gray_b, full=True)
            # print(f'当前秒为{time.localtime().tm_sec}:图片比较中...和{i}的相似度为{score:.3f}...')

            if score > 0.86:    # 应该这个 魔法 数字比较好用
                return str(i)   # 返回的就是那个数字
            else:
                continue
        return None

    def handle_num(self, key, flag=None):
        key_code = re.findall(r'(&#x.*?);', key)
        if flag:
            # print('是年龄...')
            key_1 = None
            key = key
        else:
            if len(key_code) == 11:
                # print('是手机号....')
                key_1 = key_code[0]   # 1
                key = key.replace(f'{key_1};', '1')
            else:
                # print('是薪资....')
                key_1 = key_code[-1]  # 0
                key = key.replace(f'{key_1};', '0')

        xml = etree.parse(BASE_DIR + r'\helper\fonts\b64.xml')
        root = xml.getroot()
        font_dict = {}
        all_data = root.xpath('//glyf/TTGlyph')
        for index, data in enumerate(all_data):
            font_key = data.attrib.get('name')[3:].lower()
            contour_list = list()
            if index == 0:
                continue
            for contour in data:
                for pt in contour:
                    contour_list.append(dict(pt.attrib))
            font_dict[font_key] = json.dumps(contour_list, sort_keys=True)

        for each_value in key_code:
            if each_value == key_1:
                print('跳过了指定字符为:0/1:')
                continue
            else:
                each_value = each_value.replace('&#x', '')
                print('当前需要处理的数据为:', each_value)
                for v in font_dict:
                    # print('当前的', v, '有跑到这里...')
                    if v == each_value:
                        value = font_dict[v]
                        value = json.loads(value)
                        x = []
                        y = []
                        time.sleep(0.1)
                        for al in value:
                            x_e = int(al['x'])
                            y_e = int(al['y'])
                            x.append(x_e)
                            y.append(y_e)
                        plt.figure(figsize=(1, 1))  # 设置保存图片的大小 (n x 100px)
                        plt.fill_between(x, y, facecolor='black')  # 填充图片,使用黑色
                        # plt.grid(True)
                        plt.plot(x, y)  # 这里可以额外添加很多属性比如线型,线色('-k')这个表示实线黑色  线宽(linewidth)
                        plt.axis('off')  # 关闭坐标
                        plt.savefig(BASE_DIR + r"\helper\fonts\plt.png")
                        plt.close()
                        # plt.show()   # 这个和上面那个功能会重置坐标 如果两个都要显示的话 不要放上句前面

                        # print('准备比较相似程度...')
                        sub_key = self.down_compare_img()
                        # sub_key = main_ocr()   # 调用百度的识别，发现很慢

                        if sub_key:
                            key = key.replace(f'&#x{each_value};', sub_key)
                        else:
                            key = key.replace(f'&#x{each_value};', '*')
        return key

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

    def transfer_useful(self, handled_data, order_list):
        # 这里是最后要处理数据的地方，在这之前还有很多地方的数据需要处理（解码为主）
        data_s = handled_data
        for _ in range(order_list):
            data = data_s[_]
            gender_judge = data['sex']
            work_exp = data['experiences']
            if work_exp:
                work_experience = []
                for each_work in work_exp:
                    work_info = {
                        '起止时间': each_work['startDate'] + each_work['endDate'],
                        '公司信息': each_work['company'],
                        '工作内容': each_work['positionName'] + ":" + each_work['description']
                    }
                    work_experience.append(work_info)
            else:
                work_experience = []
            phone_num = self.handle_num(data['mobile'])
            name = self.handle_name(data)
            work_year = self.handle_num(data['workYear'])
            salary = self.handle_num(data['targetSalary']) if '面议' not in data['targetSalary'] else '面议'

            age = self.handle_num(data['ageText'], True)
            try:
                now_year = time.localtime().tm_year - int(age)
            except Exception as e:
                now_year = time.localtime().tm_year

            json_info = {
                'name': name + '(号码3天有效)',
                'mobile_phone': phone_num,
                'company_dpt': 2,
                'resume_key': data['expectCateName'],
                'gender': 2 if gender_judge == '0' else 1,
                'date_of_birth': f'{now_year}-01-01',
                'current_residency': data['expectArea'] if data['expectArea'] else '广州',
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
                'get_type': 2,
                'external_resume_id': data['resumeid'][-49:],
                'labeltype': 1,
                'resume_logo': data['picUrl'],
                'resume_from': 4,           # 来源
                'account_from': python_config.account_from,
                'update_date': time.strftime("%Y-%m-%d", time.localtime(int(data['addtime']) / 1000)),
            }

            yield json_info

    def click_get_code(self, num):
        time.sleep(0.5)
        if num != 0:
            time.sleep(0.2)
            for i in range(1, num+1):
                time.sleep(0.2)
                each_pos = self.driver.find_element_by_xpath(
                    f'/html/body/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li[{i}]/div[1]/div[3]/section[1]'
                )
                each_pos_text = each_pos.text
                if each_pos_text == '获取密号':
                    each_pos_c = self.driver.find_element_by_xpath(
                        f'/html/body/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li[{i}]/div[1]/div[3]/section[1]/a'
                    )
                    self.driver.execute_script("arguments[0].click();", each_pos_c)
                    time.sleep(0.2)
                    try:
                        click_sure = self.driver.find_element_by_xpath(
                            '/html/body/div[14]/div[2]/div/div[2]/div/div/a[2]')
                    except Exception as e:
                        pass
                    else:
                        self.driver.execute_script("arguments[0].click();", click_sure)

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

    def download_page_all_detail(self, referer_url, people_num):
        # 4.开始爬基础数据。
        headers = self.requests_headers(referer_url)
        pgs = people_num // 50 + 1
        for pg in range(1, pgs+1):
            LOG.info(f'当前下载页为:{pg}(请求次数), 页面数据有{people_num}条')
            page_source = self.driver.page_source
            font_key = re.findall('var ____json4fe = {fontKey: "(.*?)"', page_source)[0]
            time.sleep(random.uniform(0, 1))
            try:
                now_pg_data = requests.get(self.down_url_api,
                                           params={'pageindex': pg,
                                                   'fontKey': font_key},
                                           headers=headers)
            except Exception as e:
                print(e)
                msg = '***** 58 程序自动化 *****\n触发原因: cookie失效\n处理标准: 重新处理页面状态'
                send_rtx_msg(msg)
            else:
                new_data = now_pg_data.text.lstrip('(').rstrip(')')
                new_data = json.loads(new_data)
                resume_data = new_data['data']['resumeList']
                yield resume_data

    def download_page_people_each(self, today_all_num):
        # 3.这里是点击每一个人 然后...
        # /html/body/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li/div[1]/div[1]/div[3]/p[1]/span[1]
        now_page_referer = self.driver.current_url
        pages = today_all_num   # 总共的数量(后面两个调用函数意思不一样)
        time.sleep(random.uniform(1, 2))
        # 下面是好一点的办法,速度快,但是需要处理的地方有点多
        resume_data = self.download_page_all_detail(now_page_referer, pages)  # 这里的pages是该函数拿来确定页数的

        tttt1 = time.time()
        page_source = self.driver.page_source
        self.handle_font(page_source)
        time.sleep(0.1)

        for each_data in resume_data:
            data_info_down = self.transfer_useful(each_data, pages)   # 这里的pages是用来保留几条数据的

            for post_data_down in data_info_down:                   # 这里是异步处理
                time.sleep(0.5)
                self.post_data_down(post_data_down)
        tttt2 = time.time()
        print(f'总用时: {tttt2 - tttt1:.2f}')

    @staticmethod
    def handle_font(page_source):
        bs64_str = re.findall(
            r'@font-face{font-family:"customfont"; src:url\(data:application/font-woff;charset=utf-8;base64,(.*?)\)  format',
            page_source)[0]
        temp_str = base64.b64decode(bs64_str)
        with open(BASE_DIR + '/helper/fonts/b64.woff', 'wb') as fl:
            fl.write(temp_str)
            print('数据写入成功...')
        time.sleep(1)
        font = TTFont(BASE_DIR + '/helper/fonts/b64.woff')
        font.saveXML(BASE_DIR + '/helper/fonts/b64.xml')

    def download_page_people(self):
        # 2.这里先判断今天有没有人
        today_tik = time.strftime('%Y-%m-%d', time.localtime())
        # today_tik = '2018-12-13'                                             # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        LOG.info(f'今天日期为{today_tik},下载任务开始查询...')
        # page_source = self.driver.page_source
        # self.handle_font(page_source)
        try:
            today_all = self.driver.find_elements_by_xpath(
                f'/html/body/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li/div[1]/div[text()="{today_tik}"]')
        except Exception as e:
            print(e)
            today_all_num = 0
        else:
            today_all_num = len(today_all)

        self.click_get_code(today_all_num)  # 这里是处理页面的数据，让每一个都变成可以识别的密令

        if today_all_num != 0:
            self.download_page_people_each(today_all_num)
        else:
            return

    def download_page(self):
        # 1.只是去下载页面而已
        self.driver.get(self.down_url)
        try:
            WebDriverWait(self.driver, 86400, poll_frequency=10).until(
                expected_conditions.presence_of_element_located((
                    By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li[1]/div[1]/div[1]/div[3]/p[1]/span[1]'
                )))
        except Exception as e:
            print(e)
            msg = '******* 58数据自动化 *******\n触发原因: 账号登录状态过期\n处理标准: 重新登录处理,存入新的cookie\n触发账号: 银河在线'
            send_rtx_msg(msg)
        else:
            self.download_page_people()

    # =============================================================== # 上面是关于下载简历的部分,里面的加密暂时还未处理
    # =============================================================== # 下面的程序已经单独提取变成了非自动化处理

    # def post_data_auto(self, resume_data):
    #     info = {
    #         'account': python_config.account_from,
    #         'data': [resume_data]
    #     }
    #     print(info)
    #     url = python_config.POST_URL
    #     try:
    #         response = self.session.post(url, json=info)
    #     except Exception as e:
    #         LOG.error('目标计算机拒绝链接')
    #     else:
    #         LOG.info(f'数据插入详情为:{response.text}')
    #
    # def all_auto_get(self, nums):
    #     referer_url = self.driver.current_url
    #     headers = self.requests_headers(referer_url)
    #     pgs = nums // 50 + 1
    #     for pg in range(1, pgs+1):
    #         time.sleep(random.uniform(1, 3))
    #         now_pg_data = requests.get(self.auto_resume_api, params={'pageindex': pg}, headers=headers, verify=False)
    #         new_data = now_pg_data.text.lstrip('(').rstrip(')')
    #         new_data = json.loads(new_data)
    #         resume_data = new_data['data']['resumeList']
    #         yield resume_data
    #
    # def auto_resume(self):
    #     # 1. 到主动投递的页面去拿到 当天 的简历的数量
    #     self.driver.get(self.auto_resume_url)
    #     today_tic = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
    #     xpath_today = f'投递时间：{today_tic}'
    #     time.sleep(0.5)
    #     all_auto = self.driver.find_elements_by_xpath(f'//span[text()="{xpath_today}"]')
    #     all_nums_auto = len(all_auto)
    #     if all_nums_auto == 0:
    #         LOG.info(f'{today_tic}检测的时候没有简历投递进来...')
    #     else:
    #         LOG.info(f'{xpath_today}为这天的简历有:{all_nums_auto}条')
    #         auto_resume_data = self.all_auto_get(all_nums_auto)
    #         for each_data in auto_resume_data:
    #             need_post = self.transfer_useful_auto(each_data)
    #             for post_resume in need_post:
    #                 self.post_data_auto(post_resume)
    #
    # def transfer_useful_auto(self, handled_data):
    #     # 这里是最后要处理数据的地方，在这之前还有很多地方的数据需要处理（解码为主）
    #     data_s = handled_data
    #     for _ in range(len(data_s)):
    #         data = data_s[_]
    #         gender_judge = data['sex']
    #         work_exp = data['experiences']
    #         if work_exp:
    #             work_experience = []
    #             for each_work in work_exp:
    #                 work_info = {
    #                     '起止时间': each_work['startDate'] + '-' + each_work['endDate'],
    #                     '公司信息': each_work['company'],
    #                     '工作内容': each_work['positionName'] + ":" + each_work['description']
    #                 }
    #                 work_experience.append(work_info)
    #         else:
    #             work_experience = []
    #         phone_num = data['mobile']
    #         name = self.handle_name(data)
    #         work_year = data['workYear']
    #         salary = data['targetSalary'] if '面议' not in data['targetSalary'] else '面议'
    #         age = int(data['age'])
    #         now_year = int(time.strftime('%Y', time.localtime()))
    #
    #         json_info = {
    #             'name': name,
    #             'mobile_phone': phone_num,
    #             'company_dpt': 1,  # 不确定写啥
    #             'resume_key': data['targetPosition'] if data['targetPosition'] else '',
    #             'gender': 2 if gender_judge == '0' else 1,
    #             'date_of_birth': f'{now_year - age}-01-01',
    #             'current_residency': data['expectArea'],
    #             'years_of_working': work_year,
    #             'hukou': '',
    #             'current_salary': '',
    #             'politics_status': '',
    #             'marital_status': 2,
    #             'address': '',
    #             'zip_code': '',
    #             'email': '',
    #             'home_telephone': '',
    #             'personal_home_page': '',
    #             'excecutiveneed': '',
    #             'self_assessment': data['letter'],
    #             'i_can_start': '',
    #             'employment_type': 1,
    #             'industry_expected': '',
    #             'working_place_expected': data['expectArea'],
    #             'salary_expected': salary,
    #             'job_function_expected': 1,
    #             'current_situation': '',
    #             'word_experience': work_experience,
    #             'project_experience': [],
    #             'education': [],
    #             'honors_awards': [],
    #             'practical_experience': [],
    #             'training': '',
    #             'language': [],
    #             'it_skill': [],
    #             'certifications': [],
    #             'is_viewed': 1,
    #             'resume_date': time.strftime("%Y-%m-%d", time.localtime()),
    #             'get_type': 1,
    #             'external_resume_id': data['resumeid'][-49:],
    #             'labeltype': 1,
    #             'resume_logo': data['picUrl'],
    #             'resume_from': 4,  #
    #             'account_from': python_config.account_from,
    #             'update_date': time.strftime("%Y-%m-%d", time.localtime(int(data['updateDate']) / 1000)),
    #         }
    #
    #         yield json_info

    # ================================================================ #

    def run_down(self):
        self.download_page()    # 获取下载的简历信息 (涉及到加密,正在处理中)

    # def run_auto(self):
    #     self.auto_resume()   # 获取主动投递的简历信息,这里的数据就不这里跑了,换另外的地方跑


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


def main():
    app = TongCheng()
    app.run_down()


if __name__ == '__main__':
    main()
