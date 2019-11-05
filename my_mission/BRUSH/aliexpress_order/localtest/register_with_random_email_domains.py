
import json,re
import os,sys
import random
import time
import requests
import threading
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from baiduOcr import BaiduOrc
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mytools import tools
from mytools.tools import logger
from selenium.webdriver.chrome.options import Options
from config import *
from urllib3.exceptions import NewConnectionError,MaxRetryError
from requests.exceptions import ProxyError


logger = logger('register')
User_Agent = generate_user_agent(device_type="desktop")
class AliexpressRegisterSpider():

    # def __init__(self,user_info,proxy):
        # # self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        # self.proxy = proxy
        # auth = self.proxy.split("@")[0][7:]
        # proxyid = self.proxy.split("@")[1]
        # proxyauth_plugin_path = self.create_proxyauth_extension(
        #     proxy_host=proxyid.split(":")[0],
        #     proxy_port=int(proxyid.split(":")[1]),
        #     proxy_username=auth.split(":")[0],
        #     proxy_password=auth.split(":")[1]
        # )
        # self.User_Agent = generate_user_agent(device_type="desktop")
        # self.options = webdriver.ChromeOptions()
        # self.options.add_extension(proxyauth_plugin_path)
        # self.options.add_argument('user-agent="%s"' % self.User_Agent)
        # # self.options.add_argument("--headless")
        # # self.options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(options=self.options)
        # # self.email = "".join(random.sample(self.digit_list,3)+random.sample(self.digit_list,3)+random.sample(self.digit_list,4)) + "@qq.com"
        # self.user_info = user_info
        # # print('当前正在注册的用户是',self.user_info['data']['email']["login_aliexpress_email"])
        # self.password = "ZhanShen001"
        # self.index_url = 'http://www.aliexpress.com/'
        # self.headers = {
        #     "user-agent": self.User_Agent
        # }
    def __init__(self,user_info,proxy):
        # self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        self.proxy = proxy
        self.user_info = user_info
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = tools.create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.chrome_options = Options()
        self.chrome_options.add_extension(proxyauth_plugin_path)
        self.chrome_options.add_argument('user-agent="%s"' % User_Agent)
        #设置无头模式
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # print('当前正在注册的用户是',self.user_info['data']['email']["login_aliexpress_email"])
        self.password = "ZhanShen001"
        self.index_url = 'http://www.aliexpress.com/'
        self.headers = {
            "user-agent": User_Agent
        }

    # 主实例方法，负责调用其他实例方法，完成注册的整个流程
    def run(self):
        #先请求主页，点击注册链接进行注册，需要判断是否有弹窗
        try:
            self.driver.get(self.index_url)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass
            self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
            time.sleep(3)

            element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.perform()
            # time.sleep(1)
            # self.driver.save_screenshot('before.png')
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="nav-user-account"]/div[2]/dl/dd/a'))
            )
            self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[2]/dl/dd/a').click()
            # time.sleep(1)
            # self.driver.save_screenshot('after.png')
            logger.info('当前正在注册的用户是%s' % self.user_info['data']['email']["login_aliexpress_email"])
            self.register(self.driver.current_url)
        except (TimeoutException,NoSuchElementException):
            #注册链接不可点击导致超时，设置回调，重新请求主页并进行相关操作
            logger.info('元素未加载，或者网络延迟导致超时,关闭当前浏览器，杀死当前线程，准备创建新的线程继续执行任务！')
            self.driver.quit()
            sys.exit(0)

    #访问注册页面并输入相关信息进行注册
    def register(self,url):
        self.driver.get(url)
        WebDriverWait(driver=self.driver, timeout=40).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="email-ipt"]'))
        )
        self.driver.find_element_by_id('email-ipt').send_keys(self.user_info['data']['email']["login_aliexpress_email"])
        truename = self.user_info['data']['address']['truename']
        if len(truename.split()) == 1:
            time.sleep(random.uniform(0.5,1.0))
            self.driver.find_element_by_id('first-name-ipt').send_keys(truename.split()[0])
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_id('last-name-ipt').send_keys(truename.split()[0])
        else:
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_id('first-name-ipt').send_keys(truename.split()[0])
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_id('last-name-ipt').send_keys(truename.split()[1])
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_id('password-ipt').send_keys(self.password)
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_id('confirm-password-ipt').send_keys(self.password)
        # time.sleep(5)
        #发现非法字符，自动让地址失效
        # if 'Please enter English characters only' in self.driver.page_source:
            # address_id = int(self.user_info['data']["address"]["id"])
            # self.modify_one_address_invalid(address_id)
        captcha_input = self.driver.find_element_by_id('checkcode-ipt')
        if captcha_input:
            #服务器上运行，网页加载仍有稍微延迟，此处应加上适当的时间延迟，使验证码加载完全，有利于截图并识别。
            time.sleep(3)
            captcha_img = self.driver.find_element_by_id('checkcode-img')
            captcha_img.screenshot('captcha.png')
            try:
                captcha = BaiduOrc().img_to_str()
                # print("百度OCR正在识别验证码：%s" % captcha)
                logger.info("百度OCR正在识别验证码：%s" % captcha)
                captcha_input.send_keys(captcha)
            except Exception:
                #识别不出任何内容,需要捕获该异常
                pass
        self.driver.find_element_by_id('submit-btn').submit()
        time.sleep(6) #此处时间该如何把握？
        if 'expressJoinSuccess' in self.driver.current_url:
            # print('%s用户注册成功！' % self.user_info['data']['email']["login_aliexpress_email"])
            logger.info('%s用户注册成功！' % self.user_info['data']['email']["login_aliexpress_email"])
            data = {
                'data':{
                    "aliexpress_password": self.password,
                    "email_id": self.user_info['data']['email']['id'],
                    "credit_id": self.user_info['data']["credit"]['id'],
                    "address_id": self.user_info['data']["address"]['id'],
                    "ip_id": self.user_info['data']["ip"]['id'],
                    "header": json.dumps(self.headers),
                    "cookies": json.dumps(self.driver.get_cookies()),
                    "status_code": "200"
                }
            }
            # print(json.dumps(data))
            self.save_success_register_info(json.dumps(data))
            self.driver.quit()
        else:
            #回调
            self.register(self.driver.current_url)

    #将成功注册的用户信息入库
    @staticmethod
    def save_success_register_info(data):
        # resp = requests.post(
        #     #测试机
        #     # url='http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountPost',
        #     # 线上
        #     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountPost',
        #     data=data
        # )
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountPost'
        resp = tools.post(requests.session(), url=url, post_data=data)
        if resp:
            if resp.text.strip() == "success" and resp.status_code == 200:
                # print(resp.text)
                logger.info('注册信息已成功入库！')
            else:
                logger.info('注册信息入库失败！')
            
    @staticmethod
    def modify_one_address_invalid(self, address_id):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyOneAddress&address_id=%s' % address_id
        resp = requests.get(url)
        if resp.json().get('code') == 200:
            logger.info('成功让地址失效！')
        else:
            logger.info('未能让地址失效')


#主函数
def main(user_infos,proxy):
    spider = AliexpressRegisterSpider(user_infos,proxy)
    spider.run()

#思路：让主线程循环获取任务，每次获取一个任务，并创建一个子线程去跑注册流程，如果子线程网络出错或者其他原因导致的超时，则直接退出子线程。这样主线程又可以获取任务接着跑了。
if __name__ == '__main__':
    while True:

        s = requests.Session()
        try:
            # 获取地址ip
            r = tools.get(s, 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetOneValidAddress')
            html = json.loads(r.text)
            if int(html['code']) == 200:
                proxies = tools.get_oxylabs_proxy('us', None, random.random())
                getIpInfo = tools.get(requests.session(), 'https://ipinfo.io', proxies=proxies)
                if getIpInfo:
                    ipInfo = json.loads(getIpInfo.text)
                    ip = ipInfo['ip']
                    print(ip)
        except Exception:
            pass
        #邮箱规则：1位随机大写字母 + 7位随机小写字母 + 3位随机数字 + 随机邮箱域名
        Email = random.choice(Upper_Letter_List) + ''.join(random.sample(Lower_Letter_List,7)) + ''.join(random.sample(Digit_List,3)) + '@' + random.choice(Email_Domains)
        print(Email)
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet&validate_email={validateEmail}&dynamic_ip={dynamicIp}'.format(validateEmail=Email, dynamicIp=ip)
        resp = tools.get(s, url=url)
        if resp:
            if resp.json().get('code') == 200:
                user_infos = resp.json()
                #由于接口一次只返回一个待注册用户的数据，默认只创建一个子线程去执行注册流程
                for i in range(0,1):
                    t = threading.Thread(target=main, args=(user_infos, proxies['https']))
                    t.start()
                    t.join()
            else:
                # logger.info('未获取到待注册账户的数据，程序结束！')
                # sys.exit(0)
                logger.info('当前无注册任务，程序[sleep 10m]...')
                time.sleep(60 * 10)
        else:
            logger.info('任务系统出错，程序[sleep 10m]...')
            time.sleep(60 * 10)
