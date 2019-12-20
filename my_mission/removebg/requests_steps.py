#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/31 14:08
# @Author  : Lodge
import os
import re
import time
import random
import urllib3
import requests

cwd = os.getcwd()
UTILS_DIR = os.path.join(cwd, 'utils')
urllib3.disable_warnings()


class RemoveBg(object):
    def __init__(self):
        self.base_url = 'https://www.remove.bg'
        self.sign_up_url = self.base_url + '/users/sign_up'
        self.session = requests.Session()

    @staticmethod
    def write_page(page, html_name):
        with open(os.path.join(UTILS_DIR, f'{html_name}.html'), 'w') as html_file:
            html_file.write(page)

    @staticmethod
    def get_important_items(html):
        application_js = re.findall('<script src="(/packs/application.*?)"></script>', html)[0]
        csrf_token = re.findall('meta name="csrf-token" content="(.*?)"', html)[0]
        v3_cfg = re.findall('"g-recaptcha-v3-cfg" data-sitekey="(.*?)"', html)[0]
        v2_checkbox_cfg = re.findall('checkbox-cfg" data-sitekey="(.*?)"', html)[0]

        info = {
            "application_js": application_js,
            "csrf_token": csrf_token,
            "v3_cfg": v3_cfg,  # 关注一下"
            "v2_checkbox_cfg": v2_checkbox_cfg,
        }
        return info

    def sign_up_page(self):
        register_page = self.session.get(self.sign_up_url, verify=False)
        self.write_page(register_page.text, 'register_page')

        base_info = self.get_important_items(register_page.text)
        return base_info

    @staticmethod
    def judge_whether_done(html):
        if 'Please follow the link to activate your account' in html:
            return True
        else:
            return False

    def register_now(self, info):
        register_url = self.base_url + '/users'
        data = {
            'utf8': '✓',
            'authenticity_token': info.get('csrf_token'),
            'user[email]': info.get('email'),
            'user[password]': info.get('password'),
            'user[password_confirmation]': info.get('password'),
            # 'user[terms_of_service]': '0',
            'user[terms_of_service]': '1',
            'user[receive_newsletter]': '0',
            'g-recaptcha-response': info.get('recaptcha_response'),
        }
        done_html = self.session.post(register_url, data=data)
        status = self.judge_whether_done(done_html.text)
        if status is True:
            print('成功了...')
        else:
            print('失败了...')

    @staticmethod
    def add_email_password():
        # list1 = [chr(i) for i in range(65, 91)] + [chr(x) for x in range(97, 123)] + [str(o) for o in range(10)]
        list1 = [str(o) for o in range(10)]
        # user = random.sample(list1, random.randint(6, 10))
        user = random.sample(list1, 6)
        i = ''.join(user)
        # user_name = i + '@dersses.store'  # 整个邮箱
        user_name = i + '@qq.store'  # 整个邮箱
        # my_mongo.mongo_user_add(user_name=user_name)
        password = 'gets.com123'
        add_info = {
            'email': user_name,
            'password': password
        }
        return add_info
            
    def handle_some_key_value(self, base_info):
        add_info = self.add_email_password()
        second_info = dict(base_info, **add_info)


        return {}

    def run(self):
        base_info = self.sign_up_page()
        info = self.handle_some_key_value(base_info)

        self.register_now(info)


if __name__ == '__main__':
    app = RemoveBg()
    app.run()

