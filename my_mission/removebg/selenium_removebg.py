#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/30 15:42
# @Author  : Lodge
import time
import random
from selenium import webdriver
from threading import Thread
from helper import my_mongo


# options = webdriver.ChromeOptions()
# options.add_argument('--incognito')
# options.add_argument('--disable-gpu')
# options.add_argument('--blink-settings=imagesEnabled=false')
# options.add_experimental_option("debuggerAddress", f"127.0.0.1:65432")
# driver = webdriver.Chrome(options=options)

class Reg(object):
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.options)

    def go_go_go(self, eml):
        time.sleep(1)
        self.driver.get('https://www.remove.bg/users/sign_up')
        time.sleep(8)
        self.driver.delete_all_cookies()
        time.sleep(1)
        self.driver.refresh()
        time.sleep(random.uniform(1, 3))

        email = self.driver.find_element_by_xpath('//*[@id="user_email"]')
        email.send_keys(eml)

        password = self.driver.find_element_by_xpath('//*[@id="user_password"]')
        re_password = self.driver.find_element_by_xpath('//*[@id="user_password_confirmation"]')
        password_info = 'getscom123'
        password.send_keys(password_info)
        re_password.send_keys(password_info)

        sure = self.driver.find_element_by_xpath('//*[@id="user_terms_of_service"]')
        sure.click()

        time.sleep(random.uniform(1, 2))

        sign_up = self.driver.find_element_by_xpath('//*[@id="new_user"]/div[8]/button')
        sign_up.click()
        time.sleep(random.uniform(3, 5))

    @staticmethod
    def sign_up():
        """注册账号"""
        # list1 = [chr(i) for i in range(65, 91)] + [chr(x) for x in range(97, 123)] + [str(o) for o in range(10)]
        list1 = [str(o) for o in range(10)]
        # user = random.sample(list1, random.randint(6, 10))
        user = random.sample(list1, 7)
        i = ''.join(user)
        user_name = i + '@dersses.store'   # 整个邮箱
        # my_mongo.mongo_user_add(user_name=user_name)
        return user_name

    def get_email(self):
        # 搞一个生成器玩玩
        pass

    def judge_success(self):
        time.sleep(2)
        try:
            successfully = self.driver.find_element_by_xpath('//*[@id="page-content"]/div[1]/div').text
        except Exception as e:
            print('失败了...')
        else:
            if 'Please follow the link to activate your account' in successfully:
                print('成功了.....成功了....')
            else:
                print('结果还是失败了...')

    def run(self):
        eml = self.sign_up()
        self.go_go_go(eml)
        self.judge_success()


def go():
    app = Reg()
    app.run()


def main():
    tl = []
    for t in range(5):
        t1 = Thread(target=go)
        t1.start()
        tl.append(t1)

    for tk in tl:
        tk.join()


if __name__ == '__main__':
    main()
