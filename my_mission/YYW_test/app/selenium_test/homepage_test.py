#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 17:50
# @Author  : Lodge
import re
import json
import time
import random
import urllib3
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


from helper import python_config, tools


LOG = tools.log('yyw_test_item_home_page')

urllib3.disable_warnings()   # disabled requests' verify warning
# ========================================================================================== #


class Yyw(object):
    def __init__(self, driver):
        self.driver = tools.chose_driver(driver, LOG)
        if not self.driver:
            exit(0)
        else:
            pass

    def verify_whether_register(self, reg_info):
        """判断是否注册成功"""
        time.sleep(10)
        LOG.info('正在检验是否注册账号成功')
        c_url = self.driver.current_url
        if 'login' in c_url:
            LOG.error('注册账号状态:(失败),当前的注册信息为:' + str(reg_info))
            return False
        elif 'my' in c_url:
            LOG.info('注册账号:(成功),当前的注册信息为:' + str(reg_info))
            return True

    def test_register(self):
        """测试注册流程"""
        t_register_start = time.time()
        try:
            reg_cli = self.driver.find_element_by_xpath('//*[@id="Login_S"]/li[1]/a/span[2]')
        except expected_conditions.NoSuchElementException:
            LOG.error('没有找到注册节点')
        else:
            reg_cli.click()
        reg_info = tools.register(self.driver, LOG, 'hard')
        t_register_end = time.time()
        flag = self.verify_whether_register(reg_info)
        if flag:
            LOG.info(f'时间统计==>注册:{t_register_end - t_register_start:.2f} s')
            return reg_info
        else:
            return flag

    def verify_whether_login(self):
        """判断是否登录成功"""
        try:
            whether_login = self.driver.find_element_by_xpath('//*[@id="Login_S"]/li[1]/span').text
        except Exception as e:
            print(e)
        else:
            if whether_login and 'Hi,' in whether_login:
                LOG.info('注册的账号登录成功')

    def test_login(self, reg_info):
        """测试登录流程"""
        t_login_start = time.time()
        try:
            reg_cli = self.driver.find_element_by_xpath('//*[@id="Login_S"]/li[1]/a/span[1]')
        except expected_conditions.NoSuchElementException:
            LOG.error('没有找到登录节点')
        else:
            reg_cli.click()
        tools.login(self.driver, LOG, reg_info)
        t_login_end = time.time()
        LOG.info(f'时间统计==>登录:{t_login_end - t_login_start:.2f} s')
        self.verify_whether_login()

    def statistics_homepage_time(self):
        """统计进入登录页面所需的时间"""
        in_time_start = time.time()
        self.driver.get(python_config.GOAL_URL)
        in_time_end = time.time()
        LOG.info(f'进入主页面的时间统计为:{in_time_end - in_time_start:.2f} s')

    def run(self):
        """开始做事情啦"""
        self.statistics_homepage_time()
        reg_info = self.test_register()
        tools.reset_status(self.driver, LOG)
        if reg_info:
            self.test_login(reg_info)
        self.driver.quit()


def main(driver='Chrome'):
    # 可选驱动 Chrome  Firefox  IE   Edge
    app = Yyw(driver)
    app.run()


if __name__ == '__main__':
    main()

