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
        position_data = requests.get(python_config.POSITION_URL).text
        # print(position_data)
        local_account = python_config.phone_num.replace('-', '')
        position_data = json.loads(position_data)
        for each_pos in position_data:
            each_id = each_pos['id']
            account = each_pos['account']

            if account == local_account:
                position_name = each_pos['job_name']
                position_type = each_pos['job_type']
                exp_info = each_pos['experience']
                edu_info = each_pos['edu']
                salary_low = int(each_pos['salary_min'])
                salary_high = int(each_pos['salary_max']) - salary_low
                position_desc = each_pos['job_desc']
                position_key = each_pos['job_keywords'].split(',')

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
                self.driver.execute_script("arguments[0].click();", edu_class)
                time.sleep(0.5)

                salary_l = self.driver.find_element_by_xpath(
                    f'//*[@id="container"]/div[1]/form/div[10]/div[2]/div[1]/div/ul/li[{salary_low}]')
                self.driver.execute_script("arguments[0].click();", salary_l)
                time.sleep(0.5)

                salary_h = self.driver.find_element_by_xpath(
                    f'//*[@id="container"]/div[1]/form/div[10]/div[2]/div[2]/div/ul/li[{salary_high}]')
                self.driver.execute_script("arguments[0].click();", salary_h)
                time.sleep(0.5)

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

                post_position = self.driver.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/form/div[15]/div[2]/button'
                )
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", post_position)

                time.sleep(1)
                try:
                    self.driver.switch_to.parent_frame()
                    self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[1]/div[1]/h3')
                except Exception as e:
                    requests.get(python_config.POSITION_URL_CLEAR + each_id)
                    LOG.info('职位发布成功, 现在消除的id为:', each_id)
                else:
                    requests.get(python_config.POSITION_FAIL_CLEAR + each_id)
                    LOG.error('职位发布失败, 现在消除的id为:', each_id)
                finally:
                    self.driver.refresh()

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
    with open(os.path.join(BASE_DIR, 'utils', 'error_log.txt'), 'a', encoding='utf-8') as fl:
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
    position_app = CallForPosition()
    position_app.run()


def main():
    """
    程序的主要启动入口，就是这里来开启各个线程，让每个线程去做事。
    :return: 不返回
    """
    development_mode()
    # print('调试的时候 要卡在这里...')
    # time.sleep(10000)
    # while True:
    #     hello_t = Thread(target=thread_one_hello)
    #     clear_t = Thread(target=thread_two_clear)
    #     call_t = Thread(target=thread_three_niu)
    #
    #     hello_t.start()
    #     clear_t.start()
    #     call_t.start()
    #
    #     hello_t.join()
    #     clear_t.join()
    #     call_t.join()


if __name__ == '__main__':
    main()
