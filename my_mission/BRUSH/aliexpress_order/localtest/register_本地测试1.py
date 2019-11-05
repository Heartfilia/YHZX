import os
import random
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from baiduOcr1 import Captcha
import json
from mysql_helper import Mysql_helper
from user_agent import generate_user_agent
from selenium.webdriver import ActionChains
from mytools.utils import logger


class AliexpressSpider():
    # letter_digit_list =[chr(x) for x in range(48,58)] + [chr(x) for x in range(65,91)] + [chr(x) for x in range(97,123)]
    digit_list = [chr(x) for x in range(48,58)]
    def __init__(self):
        # self.proxy = get_oxylabs_proxy('us',_city=None,_session=random.random())['https']
        self.logger = logger('register')
        self.User_Agent = generate_user_agent(device_type="desktop")
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--start-maximized') #窗口最大化
        self.options.add_argument('user-agent="%s"' % self.User_Agent)
        # print('user-agent="%s"' % self.User_Agent)
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=self.options)
        self.email = "".join(random.sample(self.digit_list,3)+random.sample(self.digit_list,3)+random.sample(self.digit_list,4)) + "@qq.com"
        # print('当前正在注册的用户是',self.email)
        self.logger.info('当前正在注册的用户是:%s' % self.email)
        self.password = "zhanshen001"
        self.index_url = 'http://www.aliexpress.com/'
        self.headers = {
            "user-agent": self.User_Agent
            # "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"

        }
        self.mysql_helper = Mysql_helper()

    def run(self):
        #先请求主页，点击注册链接进行注册，需要判断是否有弹窗
        self.driver.get(self.index_url)
        try:
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
            )
            self.driver.find_element_by_class_name('close-layer').click()
        except Exception:
            pass
        self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
        time.sleep(1)
        element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
        # print(element)
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
        # time.sleep(1)
        # self.driver.save_screenshot('before.png')
        try:
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="nav-user-account"]/div[2]/dl/dd/a'))
            )
            self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[2]/dl/dd/a').click()
            # time.sleep(1)
            # self.driver.save_screenshot('after.png')
            self.register(self.driver.current_url)
        except TimeoutException:
            #超时，设置回调
            self.run()

    #访问注册页面并输入相关信息进行注册
    def register(self,url):
        self.driver.get(url)
        WebDriverWait(driver=self.driver, timeout=40).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="email-ipt"]'))
        )
        self.driver.find_element_by_id('email-ipt').send_keys(self.email)
        self.driver.find_element_by_id('first-name-ipt').send_keys('xiaoqiang')
        self.driver.find_element_by_id('last-name-ipt').send_keys('huang')
        self.driver.find_element_by_id('password-ipt').send_keys(self.password)
        self.driver.find_element_by_id('confirm-password-ipt').send_keys(self.password)
        captcha_input = self.driver.find_element_by_id('checkcode-ipt')
        if captcha_input:
            captcha_img = self.driver.find_element_by_id('checkcode-img')
            captcha_img.screenshot('captcha.png')
            try:
                captcha = Captcha().get_captcha()
                # print("百度OCR正在识别验证码：", captcha)
                self.logger.info("百度OCR正在识别验证码：%s" % captcha)
                captcha_input.send_keys(captcha)
            except Exception:
                #识别不出任何内容,需要捕获该异常
                # self.register(self.driver.current_url)
                pass
        self.driver.find_element_by_id('submit-btn').submit()
        time.sleep(4)
        if 'expressJoinSuccess' in self.driver.current_url:
            # print('%s用户注册成功！' % self.email)
            self.logger.info('%s用户注册成功！' % self.email)
            cookies = json.dumps(self.driver.get_cookies())
            # print(cookies)
            item = {
                'email':self.email,
                'password':self.password,
                'cookies':cookies,
                'headers':json.dumps(self.headers),
                'credit_card':'5329598063750158'
            }
            # print(item)
            self.mysql_helper.process_item(item)
            # print('注册信息已成功入库！')
            self.logger.info('注册信息已成功入库！')
            self.driver.quit()
        else:
            #回调
            self.register(self.driver.current_url)

def main():
    i = 1
    while i <= 10:
        spider = AliexpressSpider()
        spider.run()
        # print('已成功注册%d个用户' % i )
        i += 1

if __name__ == '__main__':
    main()
