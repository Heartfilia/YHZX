#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 17:50
# @Author  : Lodge
# import os
# import re
# import json
import time
# import random
import urllib3
# import requests
from threading import Thread
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains


from helper import python_config, tools, exe_js


LOG = tools.log('yyw_homepage_test')

urllib3.disable_warnings()   # disabled requests' verify warning
# 测试主页相关数据业务与登录注册功能
# ========================================================================================== #


class Yyw(object):
    def __init__(self, driver):
        self.driver_version = driver
        LOG.info(f'现在测试主页以及登录注册状态任务开始,启动的驱动为:{self.driver_version}.')
        self.driver = tools.chose_driver(driver, LOG)
        self.driver.maximize_window()
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
            LOG.error(f'{self.driver_version}:没有找到注册节点')
        else:
            reg_cli.click()
        reg_info = tools.register(self.driver, LOG, 'hard')
        t_register_end = time.time()
        flag = self.verify_whether_register(reg_info)
        if flag:
            LOG.info(f'{self.driver_version}:时间统计==>注册:{t_register_end - t_register_start:.2f} s')
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
            try:
                account_id = self.driver.find_element_by_xpath(
                    '//*[@id="container"]/div[2]/div[2]/div[1]/ul/li[2]').text
            except expected_conditions.NoSuchElementException:
                my_account = self.driver.find_element_by_xpath('//*[@id="Login_S"]/li[2]/a')
                my_account.click()
                time.sleep(10)
                try:
                    WebDriverWait(self.driver, timeout=30).until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, '//*[@id="Login_S"]/li[1]/span')))
                except Exception as e:
                    print(e)
                    LOG.error('页面元素为查找到,现在退出当前流程..')
                    account_id = 0
                    exit(0)
                else:
                    account_id = self.driver.find_element_by_xpath(
                        '//*[@id="container"]/div[2]/div[2]/div[1]/ul/li[2]').text
            if whether_login and 'Hi,' in whether_login:
                # tools.save_csv('login', ['测试名', '时间', '描述', '备注'])
                if account_id != 0:
                    account_status = '成功'
                else:
                    account_status = '失败'
                LOG.info(f'{self.driver_version}:注册的账号登录状态为:{account_status},id为:{account_id}')
                return True if account_status == '成功' else False

    def test_login(self, reg_info):
        """测试登录流程"""
        t_login_start = time.time()
        try:
            reg_cli = self.driver.find_element_by_xpath('//*[@id="Login_S"]/li[1]/a/span[1]')
        except expected_conditions.NoSuchElementException:
            LOG.error(f'{self.driver_version}:没有找到登录节点')
        else:
            reg_cli.click()
        tools.login(self.driver, LOG, reg_info)
        t_login_end = time.time()
        LOG.info(f'{self.driver_version}:时间统计==>登录:{t_login_end - t_login_start:.2f} s')
        login_status = self.verify_whether_login()

        status = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'task': 'login',
            'status': login_status
        }
        return status

    def statistics_homepage_time(self):
        """统计进入登录页面所需的时间"""
        in_time_start = time.time()
        self.driver.get(python_config.GOAL_URL)
        in_time_end = time.time()
        LOG.info(f'{self.driver_version}:进入主页面的时间统计为:{in_time_end - in_time_start:.2f} s')

    def page_first_class_view(self):
        """在主页上浏览然后随机点进去查询"""
        LOG.info(f'{self.driver_version}:准备去到主页测试页面功能流程')
        self.driver.get(python_config.GOAL_URL)
        time.sleep(3)
        for _ in range(8):
            self.driver.execute_script(exe_js.JS_SCROLL % (_ * 200, (_ + 1) * 200))
            time.sleep(0.3)
        tools.save_screen_shot(self.driver, 'V')
        LOG.info(f'{self.driver_version}:浏览数据的情况图片已经截图...')
        time.sleep(1)
        self.driver.execute_script(exe_js.JS_SCROLL % (0, 0))
        print('现在准备随机点击商品菜单进入查看...')
        for first_class_random_choice in range(1, 8):
            LOG.info(f'{self.driver_version}:选择第{first_class_random_choice}类进入查看信息')
            on_click_node = self.driver.find_element_by_xpath(
                f'/html/body/div[4]/div/ul/li[{first_class_random_choice}]')
            ActionChains(self.driver).move_to_element(on_click_node).perform()
            tools.save_screen_shot(self.driver, 'O', f'{first_class_random_choice}类不点击查看')
            time.sleep(2)
            on_click_node.click()
            time.sleep(5)   # 等待页面加载五秒
            now_status = self.judge_whether_done(first_class_random_choice)
            tools.save_screen_shot(self.driver, 'O', f'{first_class_random_choice}类点击后查看')
            LOG.info(f'{self.driver_version}:点击操作的时候的截图,状态信息为:{str(now_status)}')

    def judge_whether_done(self, node):
        print(f'当前所在节点为:{node},主要判断页面元素有没有加载出来')
        status = True
        try:
            WebDriverWait(self.driver, timeout=10).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//ul[@class="hkICon"]/li/a[1]/img')))
        except Exception as e:
            print(e)
            try:
                WebDriverWait(self.driver, timeout=10).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, '//ul[@class="contentGrid clearfix"]/li/a[1]/img')))
            except Exception as e:
                print(e)
                LOG.error(f'{self.driver_version}:当前页面的节点:{node}数据加载异常.')
                status = False

        loading_status = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'status': '成功' if status else '失败'
        }

        return loading_status

    def test_view_goods(self):
        """这里是测试登录上之后浏览东西的详情"""
        self.page_first_class_view()  # 测试一级界面的稳定性以及速度

    @tools.count_time
    def with_login_test(self):
        # way 1: 包含登录信息的测试流程
        self.statistics_homepage_time()
        reg_info = self.test_register()
        tools.reset_status(self.driver, LOG)
        if reg_info:
            status = self.test_login(reg_info)
            print('当前是登录上后渠道主页然后进行一些操作...')
            print(str(status))
            self.test_view_goods()

        self.driver.quit()

    @tools.count_time
    def without_login_test(self):
        # way 2: 无登录信息的测试流程
        LOG.warning(f'{self.driver_version}:现在准备处理《无登录》信息的的测试流程')
        self.test_view_goods()
        self.driver.quit()

    def run(self):
        """开始做事情啦"""
        pass


def start_threading(driver):
    # app_login = Yyw(driver)
    # app_without_login = Yyw(driver)
    # with_login = Thread(target=app_login.with_login_test)
    # without_login = Thread(target=app_without_login.without_login_test)
    # with_login.start()
    # without_login.start()
    # with_login.join()
    # without_login.join()
    app_login = Yyw(driver)
    app_login.with_login_test()


def main(driver='Chrome'):
    # 可选驱动 Chrome  Firefox  IE   Edge
    start_threading(driver)


if __name__ == '__main__':
    # main('Firefox')
    main()
