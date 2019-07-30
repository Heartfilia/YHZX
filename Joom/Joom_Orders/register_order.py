
# -*- coding: utf-8 -*-
import os
import json
import time
import sys
import random
import datetime
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import getLogger
import logging
import requests
from multiprocessing import Pool
from name_cfg import names_cfg
from name_cfg.config import Upper_Letter_List, Lower_Letter_List, Digit_List, Email_Domains
from mytools.tools import create_proxyauth_extension
from mytools.tools_1 import get_oxylabs_proxy, create_proxyauth_extension, get, post
from selenium.webdriver.common.action_chains import  ActionChains

class JoomRegisterSpider():

    def __init__(self, user_info, register_city, proxies):
        self.register_city = register_city
        self.user_info = user_info
        self.proxy = proxies
        # 屏蔽谷歌浏览器弹出的通知
        self.options = webdriver.ChromeOptions()
        self.prefs = {'profile.default_content_setting_values': {'notifications': 2}}
        self.options.add_experimental_option('prefs',self.prefs)

        # 加user-agent 变成手机浏览器
        self.User_Agent = generate_user_agent(device_type="smartphone")
        self.headers = {
            "user-agent": self.User_Agent
        }
        # self.chrome_options = Options()
        self.options.add_argument('user-agent="%s"' % self.User_Agent)
        # 设置静默模式
        # self.options.add_argument("--headless")
        # 设置不加载图片
        self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        # 设置代理
        # 代理需要指定账户密码时，添加代理使用这种方式
        # self.options.add_extension(proxyauth_plugin_path)
        # self.proxy = 'http://10502+RU+10502-%s:Y7aVzHabW@ru-30m.geosurf.io:8000' % random.randint(600000, 800000)

        # self.proxy = get_oxylabs_proxy('ru', _city=None, _session=random.random())['https']
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)

        # self.path = "chromedriver.exe"
        self.driver = webdriver.Chrome( chrome_options=self.options)
        self.index_url = "https://www.joom.com/ru"
        self.username = random.choice(names_cfg.names)
        # 密码
        self.password = ''.join(random.sample(Lower_Letter_List, 7)) + ''.join(
        random.sample(Digit_List, 3))
        # 邮箱
        self.email = self.user_info["data"]["email"]["login_joom_email"]

        # self.num = ""
        # for _ in range(11):
        #     self.num += str(random.randint(1, 9))
        # self.email = "cy"+self.num+"@qq.com"
        self.wait = random.randint(2,3)
        self.items = {}

    def witer_table(self):
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//form[@class="form___1qcS9"]//div[@class="caption___2klrn"]'))
        # )
        print("正在填写表单~~~")
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]/label/input').send_keys(self.username)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]/label/input').send_keys(self.username)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[3]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[3]/label/input').send_keys(self.email)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[4]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[4]/label/input').send_keys(self.password)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[5]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[5]/label/input').send_keys(self.password)
        time.sleep(self.wait)
        time.sleep(self.wait)
        # 提交表单
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[6]/button').click()
        print("填表完成~~~正在注册")

    def register(self):
        # 获取网页的时候 要做一个超时判断
        # self.driver.set_page_load_timeout(30)
        # try:
        self.driver.get(self.index_url)
        # except TimeoutException:
        #     self.logger.info(u"网页加载超时")
        #     sys.exit(1)


        # self.driver.maximize_window()
        WebDriverWait(self.driver,30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]//a[@class="button___X0gmy"]'))
        )
        if self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 "]') != -1:
            self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 "]//div[@class="close___zSRXA"]').click()

        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="content"]//a[@class="button___X0gmy"]').click()

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="content___ZmMAf"]'))
        )

        if self.driver.find_element_by_xpath('//div[@class="inner___2LYLS"]/div[1]/div/a').text == "VK":
            print("选择账号界面")
            time.sleep(5)
            button = self.driver.find_element_by_xpath('//a[text()="Нажмите здесь"]')
            self.driver.execute_script("arguments[0].click();", button)
            print("进入注册界面")
            time.sleep(2)
            self.witer_table()


        elif self.driver.find_element_by_xpath('//div[@class="caption___3L-qE"]').text == "Войти":
            print("登录界面")
            time.sleep(5)
            button = self.driver.find_element_by_xpath('//a[text()="Register"]')
            self.driver.execute_script("arguments[0].click();", button)
            print("进入注册界面")
            time.sleep(2)
            self.witer_table()

        else:
            print("注册界面")
            self.witer_table()


        """
             表单填写完成后还需要检测一下有没有漏填的 
             ***重新填写需要清空再写，该判断有bug***
        """
        try:
            print("正在检查表单是否填写完整——————")
            # self.driver.find_element_by_xpath('//div[@class="caption___2klrn"]/span') != -1
            self.driver.find_element('//div[@class="caption___2klrn"]/span')
            time.sleep(5)
            print("填写不完整")
            a = True
        except:
            a = False
            print("填写完整")

        if a == False:
            print("------正在判断账号有没有注册成功------")
            # 判断账号有没有注册成功
            time.sleep(5)
            if self.driver.find_element_by_xpath('//span[@class="text___2-0vG"]').text != "Sign in" :
                    print("~~~~~~账号注册成功~~~~~~~")
                    """
                    下单
                    """
                    self.order_main_1(2)
            else:
                print("账号注册失败")
                self.invalid_ip()
                self.driver.quit()
                return None
            time.sleep(3)
            self.driver.refresh()
            time.sleep(3)
            self.items["email"] = self.email
            self.items["password"] = self.password
            self.items['headers'] = self.headers
            self.items['cookie'] = self.driver.get_cookies()

            self.get_data_info()

            print("————————>保存数据中————————>")
            self.save_info()
            print("*********数据保存成功********")
            self.driver.quit()
            return

        elif a == True:
            print("第一个名字没有填，重新填写")
            self.witer_table()

    # 登录失败 就把地址改为无效
    def invalid_ip(self):
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomModifyOneAddress&address_id={addressId}&inner_debug=1"
        res = get(requests.session(), url=url.format(addressId=self.user_info["data"]["id"]))
        if res:
            if json.dumps(res.text)["code"] == 200:
                print("地址改为无效——操作成功")
            else:
                print("地址改为无效——操作失败")

    # 获取到需要上传的data信息
    def get_data_info(self):
        data = {
            'data':{
                "joom_password": self.password , #"密码",
                "email_id": self.user_info["data"]["email"]["id"], #"邮箱ID",
                "credit_id": self.user_info["data"]["credit"]["id"],#"信用卡ID",
                "address_id": self.user_info["data"]["address"]["id"],#"地址ID",
                "ip_id": self.user_info["data"]["ip"]["id"] ,#"IP的ID",
                "register_city": self.register_city,#self.user_info["data"]["address"]["city"],#"注册城市",
                "header": json.dumps(self.headers),#"头信息",
                "cookies": json.dumps(self.driver.get_cookies()),#"cookies信息",
                "status_code": 200,#"状态码，如200、1、2",
                # "device_type": 1,#"设备类型，如0 pc 1mobile"
            }
        }
        self.save_register_info(json.dumps(data))

    #把自动注册刷单账号存入数据库,
    def save_register_info(self, data):
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomAutoCreateAccountPost&inner_debug=1"
        response = post(requests.session(), url, post_data = data)
        print(response.text)
        print(response.status_code)
        if response:
            if response.text.strip() == "success" and response.status_code == 200:
                # print(resp.text)
                print('注册信息已成功入库！')
            else:
                print('注册信息入库失败！')

    #保存信息到本地文件
    def save_info(self):
        j = json.dumps(self.items)
        with open('joom_userinfo.json',"a")as fp:
            fp.write(j+",\n")

"""
下单
"""

class Joon_Orders_spider():

    def __init__(self, order_user_info):

        self.order_user_info = order_user_info
        self.cookies = self.order_user_info["account"]["cookies"]
        self.find_number = 0
        self.number = 1
        self.login_num = 0
        # self.product_type = "pins"
        self.pid = '1522305319996422210-45-1-709-2466191948'
        self.product_type = self.order_user_info["asin"]["keywords"]
        # self.pid = self.order_user_info["asin"]["asin"]
        self.switch = True
        self.cat_switch = True
        self.order_num = 0
        # 缓存文件相关变量
        self.dirPath = r"C:\myfiler\Joom\Joom_Orders\cache_file/"
        self.filername =  self.order_user_info["task_id"] + ".txt"
        self.paths = os.path.join(self.dirPath, self.filername)
        #  log日志
        self.logger = getLogger()
        self.logger.setLevel(logging.DEBUG)
        filename = 'Log/log_3.log'
        # 设置looger输出格式对象
        # %(asctime)s	字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
        # %(name)s 自定义的模块名
        formatter = logging.Formatter(
            "%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s - %(message)s")  # 定义日志输出格式
        # 文件日志
        # 向文件log.txt输出日志信息，encoding="utf-8",防止输出log文件中文乱码
        fh = logging.FileHandler(filename=filename, encoding="utf-8")
        fh.setFormatter(formatter)
        # 控制台日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        # 为logger 添加日志处理器
        self.logger.addHandler(fh)
        self.logger.addHandler(console_handler)
        # 设置日志等级
        self.logger.setLevel(logging.INFO)

        # 屏蔽谷歌浏览器弹出的通知
        self.options = webdriver.ChromeOptions()
        self.prefs = {'profile.default_content_setting_values': {'notifications': 2}}
        self.options.add_experimental_option('prefs', self.prefs)
        # 设置静默模式
        # self.options.add_argument("--headless")
        # 添加请求头
        self.options.add_argument('user-agent="%s"' % self.order_user_info["account"]["header"])
        self.logger.info( "请求头：{headers}".format(headers = self.order_user_info["account"]["header"]))
        # # 加user-agent 变成手机浏览器
        # self.User_Agent = generate_user_agent(device_type="smartphone")
        # self.headers = {
        #     "user-agent": self.User_Agent
        # }
        # self.logger.info( "请求头：{headers}".format(headers = self.headers))
        # self.options.add_argument('user-agent="%s"' % self.User_Agent)
        time.sleep(4)
        # 设置不加载图片
        # self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        # 设置代理
        # 代理需要指定账户密码时，添加代理使用这种方式
        # self.options.add_extension(proxyauth_plugin_path)
        # range_num = self.order_user_info["account"]["login_joom_email"].split("@")[0]
        # print("IP 端口号：",range_num)
        # self.proxy = 'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(600000,999999)
        self.proxy = get_oxylabs_proxy('ru', _city=None, _session=random.random())['https']
        self.proxies = {"https": self.proxy}
        # register_city = self.order_user_info["account"]["register_city"]
        # print("ip城市",register_city)
        # register_city_list = register_city.split()
        # print(register_city_list)
        # if len(register_city_list) > 1:
        #     register_city = '_'.join(register_city_list)
        #     print(register_city)
        # proxies = get_oxylabs_proxy('ru', _city=register_city, _session=random.random())
        # getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        # if getIpInfo:
        #     self.proxy = proxies['https']
        #     print('get ip!')
        # else:
        #     self.proxy = get_oxylabs_proxy('ru', _city=None, _session=random.random())['https']
        #     print('get ip failed!')
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        # self.logger.info("本次 ip 为: %s" % self.proxy)
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        # self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        self.url = "https://www.joom.com/ru"
        self.driver = webdriver.Chrome(chrome_options=self.options)

    """
    使用cookie登陆Joom
    """
    def Login(self):

        # 先打开一下浏览器 让cookie知道放在那里

        # 获取网页的时候 要做一个超时判断
        self.driver.set_page_load_timeout(30)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.logger.info(u"网页加载超时")
            sys.exit(1)

        time.sleep(3)
        # 添加cookie
        items = {}
        false = 1
        true = 0
        # cookies = self.get_userinfo()
        try:
            for li in eval(self.cookies): #cookies["cookie"]:#
                items["name"] = li["name"]
                items["value"] = li["value"]
                self.driver.add_cookie({"name": items["name"], "value": items["value"]})
                # self.driver.add_cookie(li)
            time.sleep(3)
            # self.driver.get(self.url)
            self.driver.refresh()
        except Exception as e:
            self.logger.info(e)
        time.sleep(10)
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="profile___2NGBH"]'))
        )
        time.sleep(4)
        self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
        time.sleep(3)
        if self.driver.find_element_by_xpath('//div[@class="item___a8qBu"]').text == "Выход":#"Sign Out":
            self.logger.info(u"登陆成功")

            # 　 检查ip是否发生变化
            get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
            print("正在检查ip是否发生变化")
            self.logger.info(get_ipinfo)
            if get_ipinfo:
                ipinfo = json.loads(get_ipinfo.text)
                ip = ipinfo["ip"]
                self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
                self.logger.info(u"ip地址为：{ip}".format(ip=ip))



            self.updata_cookies_headers_info()
            time.sleep(1)
            self.login_log("登录成功", 1, json.dumps(self.driver.get_cookies()))
            time.sleep(2)

            self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
            time.sleep(1)
            self.cache_islive()
        else:
            self.logger.info(u"登陆失败---正在重新登录---")
            self.Login()

    """
       将用户信息从json文件中获取到
    """
    def get_userinfo(self):
        with open("User_Info/joom.json", "r")as fp:
            cookies = fp.readline()
            cookies = json.loads(cookies)
            return cookies

    """
    账号密码登录
    """
    def user_login(self):

        # 获取网页的时候 要做一个超时判断
        self.driver.set_page_load_timeout(30)
        try:
            self.driver.get(self.url )
        except TimeoutException:
            self.logger.info(u"网页加载超时")
            self.driver.quit()
        # try:
    # 去掉广告
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="popup___ByDf3 "]'))
        )
        self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 "]//div[@class="close___zSRXA"]').click()
        self.login()
        # except Exception as e:
        #     self.logger.info(e)
        #     print(e)
        #     time.sleep(2)
        #     self.driver.quit()

    # 登录操作
    def login(self):
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="profile___2NGBH"]'))
        )
        self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
        time.sleep(3)
        self.driver.find_element_by_xpath('//div[@class="inner___2LYLS"]/div[5]').click()
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//form[@class="form___1qcS9"]/div[1]//input'))
        )
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]//input').send_keys(
        self.order_user_info["account"]["login_joom_email"])#
        time.sleep(1)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]//input').send_keys(
        self.order_user_info["account"]["login_joom_password"])
        time.sleep(3)
        # 点击登陆
        self.driver.find_element_by_xpath('//button[@class="submit___3cAJx"]').click()
        time.sleep(10)

        if self.driver.find_elements_by_xpath('//form[@class="form___1qcS9"]/p/span | //form[@class="form___1qcS9"]/p').__len__() > 0:
            self.logger.info(u"登陆失败---正在重新登录---")
            self.driver.refresh()
            time.sleep(2)
            self.login_num += 1
            if self.login_num < 3:
                self.login()
            else:
                self.logger.info("登陆失败次数大于三次—退出程序")
                self.login_log("登录失败", 2 , self.cookies)
                time.sleep(2)
                self.updata_state(status=10, order_no="", payment_date="", actual_order_amount=0.00)
                self.driver.quit()
        else:
            time.sleep(5)
            # 如果登陆出现 用户者协议 则点击我同意
            if self.driver.find_elements_by_xpath(
                    '//div[@class="inner___3uuBN"]//div[@class="positiveButton___1-fkP"]').__len__() > 0:
                self.driver.find_element_by_xpath(
                    '//div[@class="inner___3uuBN"]//div[@class="positiveButton___1-fkP"]').click()
                time.sleep(3)
                self.logger.info(u"出现了用户者协议")
                self.logger.info(u"登陆成功")
                self.updata_cookies_headers_info()
                time.sleep(1)
                self.login_log("登录成功", 1, json.dumps(self.driver.get_cookies()))
                time.sleep(1)
                self.cache_islive()
            else:
                self.logger.info(u"登陆成功")
                self.updata_cookies_headers_info()
                time.sleep(1)
                self.login_log("登录成功", 1, json.dumps(self.driver.get_cookies()))
                time.sleep(1)
                self.cache_islive()

    # 　根据缓存文件　来判断　该商品　有没有被下过单
    def cache_islive(self):
        print(self.paths)
        file_list = os.listdir(self.dirPath)
        if self.filername in file_list:
           self.logger.info(u"该商品被下过单")
           self.goto_myorder()
           time.sleep(5)
           if self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]/h1').__len__() > 0:
               self.logger.info(u'订单中心没有任何订单')
               time.sleep(1)
               self.logger.info(u'进入购物车， 查看是否有该商品')
               time.sleep(2)
               #  进入购物车 查看是否有 商品
               self.delete_other_from_cart()
           else:
               WebDriverWait(self.driver, 30).until(
                   EC.presence_of_all_elements_located(
                       (By.XPATH, '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="status___AN7Tv"]/span'))
               )
               order_type = self.driver.find_element_by_xpath(
                   '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="status___AN7Tv"]/span').text
               print(order_type)
               if order_type == "Оплачен":
                   self.logger.info(u"该商品已经被下过单,进行订单状态更新")
                   self.add_order_log("下单成功日志")
                   # 下单————时间
                   self.order_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                   self.logger.info(self.order_time)
                   time.sleep(3)
                   self.get_orderinfo()
                   time.sleep(3)
                   self.updata_state(status=2, order_no=self.order_number, payment_date=self.order_price, actual_order_amount=self.order_time )
                   self.detele_cache_filer()
                   time.sleep(2)
                   self.driver.quit()
               else:
                   self.delete_other_from_cart()
        else:
            self.search_items()

    # 添加登录日志
    def login_log(self, login, status, cookies):
        data = {
            "data":{
                "account_id": self.order_user_info["account"]["account_id"],
                "header": self.order_user_info["account"]["header"],
                "cookies": cookies, # self.order_user_info["account"]["cookies"],
                "login_status": status, # "1","2"
                "login_ip": self.order_user_info["account"]["ip"], #"127.0.0.1",
                "note": login,
            }
        }
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomInsertAccountLoginLog&inner_debug=1"
        res = post(requests.session(), url = url, post_data = json.dumps(data))
        if res:
            if res.status_code == 200:
                self.logger.info("账号登录日志添加成功")
            else:
                self.logger.info("账号登录日志添加失败")

    # 登陆成功 更新 headers 和 cookies 信息
    def updata_cookies_headers_info(self):
        data = {
            "data": {
                "account_id": self.order_user_info["account"]["account_id"],
                "header": self.order_user_info["account"]["header"],
                "cookies": json.dumps(self.driver.get_cookies()),
            }
        }
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomUpdateAccountLoginSuccessInfo&inner_debug=1"
        res = post(requests.session(), url=url, post_data=json.dumps(data))
        if res:
            if res.status_code == 200:
                self.logger.info("账号header和cookie更新成功")
            else:
                self.logger.info("账号header和cookie更新失败")

    # 搜索商品
    def search_items(self):

        time.sleep(5)
        # WebDriverWait(self.driver, 30).until(
        #     EC.presence_of_all_elements_located((By.XPATH, '//div[@class="searchIconOpen___2264C'))
        # )
        button = self.driver.find_element_by_xpath('//div[@class="searchIconOpen___2264C"]')
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
        self.driver.find_element_by_xpath('//input[@class="input___3wRUz"]').send_keys(self.product_type)
        print(self.product_type)
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="submit___3XMCO"]'))
        )
        self.logger.info(u"点击搜索")
        self.driver.find_element_by_xpath('//button[@class="submit___3XMCO"]').click()
        time.sleep(5)
        if self.driver.find_elements_by_xpath('//div[@class="productWrap___30WNd"]').__len__() > 0:
            self.logger.info(u"进入商品列表页")
            self.add_to_cart()
        else:
            self.driver.refresh()
            self.search_items()
            self.updata_state(status=25, order_no="", payment_date="", actual_order_amount=0.00)

    # 根据商品的pid来查找商品
    def find_to_shoppong(self):

        # 　 检查ip是否发生变化
        get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        self.logger.info(get_ipinfo)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
            self.logger.info(u"ip地址为：{ip}".format(ip=ip))


        # try:
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH,'//div[@class="productWrap___30WNd"]//div[@class="square___1fugM "]//a[@class="link___28nVD"]'))
        )
        # 判断商品数量
        shopping_number = self.driver.find_elements_by_xpath(
            '//div[@class="productWrap___30WNd"]//div[@class="square___1fugM "]//a[@class="link___28nVD"]').__len__()
        # self.logger.info(shopping_number)
        for i in range(self.number, shopping_number + 1):
            shopping_url = self.driver.find_element_by_xpath(
                '//div[@class="productWrap___30WNd"][%d]//div[@class="square___1fugM "]//a[@class="link___28nVD"]' % self.number).get_attribute(
                'href')
            # print(self.pid)
            if self.pid in shopping_url:
                self.logger.info(i)
                self.logger.info(shopping_url)
                if self.find_number < 1:
                    self.updata_postion(i)
                else:
                    row_num = i - 36 * (self.find_number)
                    print(row_num)
                    print("第:{row_num}个".format(row_num=row_num))
                    self.updata_postion(row_num)
                self.logger.info(u"找到了")
                self.logger.info("目标商品位于第:{page}页的第{i}个".format(page=self.find_number + 1, i= i - 36 * (self.find_number)))
                self.driver.find_element_by_xpath('//div[@class="productWrap___30WNd"][%d]' % self.number).click()
                return
            else:
                # self.logger.info(u"没有找到，正在重新查找")
                self.number += 1
        # except Exception as e:
        #     self.logger.info(e)
        #     time.sleep(2)
        #     self.driver.quit()

        # 在前多少页中查找目标商品
        if self.find_number < 15:
            if self.driver.find_elements_by_xpath('//div[@class="more___3SVAw"]/a[@class="button___2TwMH"]').__len__() > 0:
                self.driver.find_element_by_xpath('//div[@class="more___3SVAw"]/a[@class="button___2TwMH"]').click()
                self.find_number += 1
                time.sleep(random.randint(3, 5))
                self.find_to_shoppong()
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
                self.find_number += 1
                time.sleep(random.randint(3, 5))
                self.find_to_shoppong()
        else:
            self.logger.info(u"关键字查询了%s 页 都没找到，退出程序" % self.find_number)
            self.updata_state(status=21, order_no="", payment_date="", actual_order_amount=0.00)
            time.sleep(2)
            self.driver.quit()

    # 更新当前页码和当前位置
    def updata_postion(self, row_num):
        data = {
            "data": {
                "page_num": self.find_number + 1,
                "row_num": row_num,
                "task_id": self.order_user_info["task_id"]
            }
        }
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomUpdatePageAndRank&inner_debug=1"
        res = post(requests.session(), url=url, post_data=json.dumps(data))
        print(json.loads(res.text)["code"])
        if res:
            if json.loads(res.text)["code"] == 200:
                self.logger.info(u"更新成功")
            else:
                self.logger.info(u"更新失败")

    # 将需要的商品添加至购物车里面
    def add_to_cart(self):
        # 搜索完成 等待商品加载出来
        # WebDriverWait(self.driver, 30).until(
        #     EC.presence_of_all_elements_located((By.XPATH, '//div[@class="productWrap___30WNd"]'))
        # )
        time.sleep(3)
        if self.switch:
            self.find_to_shoppong()
        else:
            num = random.randint(1, 10)
            self.driver.find_element_by_xpath('//div[@class="productWrap___30WNd"][%d]' % num).click()

        self.logger.info(u"进入详情页成功")
        time.sleep(5)

        # 找出一共有几个需要选择的参数
        node_num = self.driver.find_elements_by_css_selector('.item___3x9Ra').__len__()
        self.logger.info(u"商品的样式数量有: %s 个" % node_num)
        if node_num < 2:
            self.logger.info(u"没有需要选择的样式")
        else:
            for i in range(2, node_num + 1):
                self.logger.info(i)
                time.sleep(5)
                if len(self.driver.find_elements_by_xpath(
                        '//div[@class="attributes___iJZOP "]/div[%d]/div/div' % i)) > 1:
                    # 根据具体的参数选择样式
                    # 判断该参数是否可选
                    style_num = self.driver.find_elements_by_xpath(
                        '//div[@class="attributes___iJZOP "]/div[%d]/div/div' % i).__len__()
                    for j in range(1, style_num + 1):
                        if self.driver.find_elements_by_xpath(
                                '//div[@class="attributes___iJZOP "]/div[%d]/div/div[%d]/div/span' % (
                                        i, j)).__len__() > 0:
                            self.logger.info(u'该样式没有了')
                        else:
                            if self.driver.find_elements_by_xpath(
                                    '//div[@class="attributes___iJZOP "]/div[%d]/div/h2/span[@class="headerSize___2osXA"]' % i).__len__() > 0:
                                self.logger.info(u"选好了")
                                break
                            else:
                                self.driver.find_element_by_xpath(
                                    '//div[@class="attributes___iJZOP "]/div[%d]/div/div[%d]/div' % (i, j)).click()
                                break
                else:
                    self.logger.info(u"该参数已经选择好了")
        time.sleep(random.randint(3, 5))
        # 添加商品至购物车
        self.driver.find_element_by_xpath('//div[@class="button___1WAua"]').click()
        time.sleep(10)

        if len(self.driver.find_elements_by_xpath('//div["related___2Opz_"]/div[2]/h2')) > 0:
            self.logger.info(u"添加购物车成功")
            self.switch = False
            time.sleep(3)
            self.add_other_to_cart()
        else:
            self.logger.info(u"添加购物车失败")
            # 如果添加失败的话 先刷新当前网页 然后在 重新选择
            self.driver.refresh()
            time.sleep(2)
            self.add_to_cart()

    # 将不需要的商品添加至购物车里面，模拟认人为失误
    def add_other_to_cart(self):
        if self.cat_switch:
            # self.driver.find_element_by_xpath('//div[@class="inner___2poSi"]/span[3]').click()
            button = self.driver.find_element_by_xpath('//div[@class="searchIconOpen___2264C"]')
            self.driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            self.driver.find_element_by_xpath('//input[@class="input___3wRUz"]').send_keys(self.product_type)
            print(self.product_type)
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="submit___3XMCO"]'))
            )
            self.logger.info(u"点击搜索")
            self.driver.find_element_by_xpath('//button[@class="submit___3XMCO"]').click()
            time.sleep(5)
            if self.driver.find_elements_by_xpath('//div[@class="productWrap___30WNd"]').__len__() > 0:
                self.logger.info(u"进入商品列表页")
            self.cat_switch = False
            self.add_to_cart()
            time.sleep(3)
        else:
            self.delete_other_from_cart()

    # 将不需要的商品从购物车中删掉
    def delete_other_from_cart(self):
        # 　 检查ip是否发生变化
        get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        self.logger.info(get_ipinfo)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
            self.logger.info(u"ip地址为：{ip}".format(ip=ip))


        self.driver.find_element_by_xpath('//div[@class="cart___3Shcs"]').click()
        WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="element___Zz7DL"]/div/div[2]/div[2]/div[@class=" item___1NoTC "]'))
            )
        # 取消需要的商品(根据pid)
        # self.driver.find_element_by_xpath('//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]').click()
        shop_num = self.driver.find_elements_by_xpath(
            '//div[@class="element___Zz7DL"]/div/div[2]/div[2]/div[@class=" item___1NoTC "]').__len__()
        self.logger.info(u'shop_num: %s' % shop_num)
        # 判断 如果只有一种商品 就直接判断商品的数量
        if 1 <shop_num < 3:
            self.driver.find_element_by_xpath(
                '//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]').click()
            self.check_quantity()
        elif shop_num < 2:
            self.search_items()
        else:
            for i in range(2, shop_num + 1):
                shop_pid = self.driver.find_element_by_xpath(
                    '//div[@class="content___Q0YRa "]/div[@class=" item___1NoTC "][%d]/div/div/table[1]//div[@class="imageParent___1iweV"]/a' % i).get_attribute(
                    'href')
                if self.pid in shop_pid:
                    self.logger.info(u'购物车中需要的商品找到了')
                    time.sleep(3)
                    self.logger.info(u"购物车里面的第%d个商品" % i)
                    self.driver.find_element_by_xpath(
                        '//div[@class="content___Q0YRa "]/div[@class=" item___1NoTC "][%d]/div/div/div/label/div/div' % i).click()
                    break
            time.sleep(4)
            # 删除键
            self.driver.find_element_by_xpath(
                '//div[@class="content___Q0YRa "]/div[1]//span[@class="remove___1BWDG"]').click()
            time.sleep(3)
            self.check_quantity()

    # 检查需要购买的商品 数量是不是正确的
    def check_quantity(self):
        time.sleep(3)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]'))
        )
        self.driver.find_element_by_xpath('//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]').click()
        quantity_number = int(self.driver.find_element_by_xpath('//div[@class="count___3LcYb"]').text)
        time.sleep(1)
        self.logger.info(u"商品数量为：%s" % quantity_number)
        time.sleep(3)
        # 判断商品数量是否为 1
        if quantity_number != 1:
            for i in range(quantity_number - 1):
                self.logger.info(u'第%d次按减号' % i)
                self.driver.find_element_by_xpath('//div[@class="counter___3YosS"]/div[1]').click()
                self.logger.info(u"商品数量 --> 减一")
                time.sleep(3)
            self.logger.info(u"商品数量一共有--%d--个，减去了--%d--个，还剩下--%d--个" % (quantity_number, quantity_number - 1, 1))
        # time.sleep(1)
        # self.driver.find_element_by_xpath('//span[@class="buttonText___2_FiU"]').click()
        # time.sleep(5)
        # self.task_page()
        # 判断信用卡额度 是不是够 支付商品价格
        price = self.driver.find_element_by_xpath('//span[@class="buttonText___2_FiU"]/span/span[2]').get_attribute("content")
        self.logger.info(price)
        card_price = float(self.order_user_info["payment"]["single_max_trade"]) * 64.537
        self.logger.info(card_price)
        time.sleep(2)
        # self.logger.info(float(price), float(self.order_user_info["payment"]["single_max_trade"]) * 64.537)
        # try:
        if float(price) < card_price:
            self.logger.info(u"信用卡额度够")
            time.sleep(3)
            self.driver.find_element_by_xpath('//span[@class="buttonText___2_FiU"]').click()
            time.sleep(5)
            self.task_page()
        else:
            self.logger.info(u"商品价格大于信用卡额度")
            self.driver.quit()
        # except Exception as e :
        #     self.logger.info(e)

    # 判断该页面是哪个页面
    def task_page(self):
        if self.driver.find_elements_by_xpath('//div[@class="address___1MpYA"]/form').__len__() > 0:
            self.logger.info(u"进入添加填写收获地址界面")
            self.add_shipping_address()
        elif self.driver.find_element_by_xpath(
                '//div[@class="payment___v_-wv"]/div/div[1]/div').text == "Новый вариант оплаты":#"New Payment Type":
            self.logger.info(u"进入填写银行卡号界面")
            if self.driver.find_elements_by_id("sub-frame-error").__len__() > 0:
                self.driver.refresh()
                time.sleep(random.randint(2, 5))
            self.aad_payment_tpye()
        elif self.driver.find_elements_by_xpath('//div[@class="number___3K0r4"]').__len__() > 0:
            #     # 直接点击支付-下单
            self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
            time.sleep(2)
            # 判断有没有错误的弹窗
            if self.driver.find_elements_by_xpath('//div[@class="inner___3uuBN"]').__len__() > 0:
                self.logger.info(u"支付时弹出出错窗口了哦")
                self.driver.find_element_by_xpath('//div[@class="inner___3uuBN"]/div[1]').click()
                time.sleep(1)
                self.goto_myorder()
                self.order_page_whether_succeed()
            else:
                time.sleep(3)
                self.logger.info(u'判断是否支付成功')
                self.orders_whether_succeed()

    # 填写收货地址（填完保存直接调用 aad_payment_tpye() 方法）
    #　俄罗斯　地址
    def add_shipping_address(self):
        # street = "&%"+self.order_user_info["address"]["AddressLine1"]
        # city = self.order_user_info["address"]["City"]
        # state = self.order_user_info["address"]["StateOrRegion"]
        # zip_code = self.order_user_info["address"]["PostalCode"]
        # phone_number = self.order_user_info["address"]["PhoneNumber"]
        # apartment_no = random.randint(1, 100)
        # 美国
        street = "2502 N Green St Detroit"
        city = "Detroit"
        zip_code = "482090" + "Detroit"
        phone_number = "13137046894"

        self.logger.info(u"正在填写地址………………")
        time.sleep(5)
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//form[@class="form___JoNlz"]/div[1]/div/div[2]'))
        # )
        # country
        # 　俄罗斯
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[1]//select[@class="element___12f_-"]//optgroup[19]/option[3]').click()
        #　　美国
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[1]//select[@class="element___12f_-"]//optgroup[17]/option[24]').click()
        time.sleep(5)

        # street
        # 　俄罗斯
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[4]').click()
        # time.sleep(1)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[4]//input').send_keys(street)
        # time.sleep(5)
        # 　美国
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[2]').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[2]//input').send_keys(street)
        time.sleep(5)

        # city
        # 　俄罗斯
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[3]').click()
        # time.sleep(1)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[3]//input').send_keys(city)
        # time.sleep(5)
        # 　美国
        time.sleep(1)
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[4]//input').send_keys(city)
        time.sleep(5)

        # state
        # 　俄罗斯
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[2]//input').send_keys(state)  # //option[43]
        time.sleep(3)
        # 　美国
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[5]//option[%d]'% random.randint(1,55)).click()
        time.sleep(3)

        # apartment_no
        # time.sleep(3)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[8]//input').send_keys(apartment_no)

        # zip_code
        # 　俄罗斯
        # time.sleep(3)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[9]//input').send_keys(zip_code)
        # time.sleep(5)
        # 美国
        time.sleep(3)
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[6]//input').send_keys(zip_code)
        time.sleep(5)

        # phone_number
        # 　俄罗斯
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[12]//input').send_keys(phone_number)
        # time.sleep(5)
        # 　美国
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[9]//input').send_keys(phone_number)
        time.sleep(5)


        self.logger.info(u"地址填写完成………………")
        # 保存地址
        self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
        time.sleep(1)
        if self.driver.find_elements_by_xpath('//div[@class="wrapper___1zU2T"]').__len__() > 0:
            self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
        time.sleep(10)
        # 判断地址信息有没有填好
        if self.driver.find_element_by_xpath(
                '//div[@class="payment___v_-wv"]//div[@class=" item___1NoTC "]').text == "Новый вариант оплаты":#"New Payment Type":
            time.sleep(2)
            self.aad_payment_tpye()
        else:
            self.logger.info(u"地址填写有问题 正在重新填写")
            self.driver.refresh()
            self.add_shipping_address()

    # 填写信用卡信息
    def aad_payment_tpye(self):

        """
         PayPal 支付
        """
        # # 　 检查ip是否发生变化
        # get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        # self.logger.info(get_ipinfo)
        # if get_ipinfo:
        #     ipinfo = json.loads(get_ipinfo.text)
        #     ip = ipinfo["ip"]
        #     self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
        #     self.logger.info(u"ip地址为：{ip}".format(ip=ip))
        #
        # time.sleep(10)
        # self.driver.find_element_by_xpath('//div[@class="tabs___svXx5"]/div[2]').click()
        # time.sleep(5)
        # self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
        # # 判断是否弹出错误界面 如果弹出 把他叉掉 刷新网页 在重新点击
        # self.create_cache_filer()
        # time.sleep(random.randint(3,5))
        # error_number = self.driver.find_elements_by_xpath('//div[@class="inner___3uuBN"]').__len__()
        # if  error_number > 0:
        #     self.logger.info(u"出现错误弹窗，刷新网页重试中")
        #     self.driver.refresh()
        #     time.sleep(3)
        #     self.aad_payment_tpye()
        # # if self.driver.find_elements_by_id("main-message").__len__() > 0:
        # #     self.logger.info(u"This page isn’t working, 退出程序")
        # #     self.driver.quit()
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH,'//div[@class="inputField confidential cardNumber creditCardField ng-scope floatingLabel"]/input'))
        # )
        # self.logger.info(u"正在进入PayPal 支付")
        # # 　选择国家--中国（中国可以不需要注册，直接信用卡支付）
        # self.driver.find_element_by_id("countryList").click()
        # time.sleep(3)
        # self.driver.find_element_by_xpath('//div[@id="countryList"]/div/select/option[38]').click()
        # time.sleep(3)
        # card_number = int(self.order_user_info["payment"]["CreditCardNumber"])
        # self.driver.find_element_by_xpath('//div[@class="inputField confidential cardNumber creditCardField ng-scope floatingLabel"]/input').send_keys(card_number)
        # month = self.order_user_info["payment"]["ccMonth"]
        # year = self.order_user_info["payment"]["ccYear"]
        # centen = month + year
        # time.sleep(2)
        # for i in centen:
        #     self.driver.find_element_by_id('expiry_value').send_keys(i)
        #     time.sleep(1)
        # time.sleep(3)
        # CVC = self.order_user_info["payment"]["cvv"]
        # time.sleep(2)
        # self.driver.find_element_by_id('cvv').send_keys(CVC)
        # phone_number = self.order_user_info["address"]["PhoneNumber"]
        # time.sleep(2)
        # self.driver.find_element_by_id('telephone').send_keys(phone_number)
        # #邮箱
        # email = self.order_user_info["account"]["login_joom_email"]
        # self.driver.find_element_by_id("email").send_keys(email)
        # #邮编
        # zip_number = ""
        # for _ in range(6):
        #     zip_number += str(random.randint(1, 9))
        # self.driver.find_element_by_id("billingPostalCode").clear()
        # self.driver.find_element_by_id("billingPostalCode").send_keys(zip_number)
        # time.sleep(2)
        # self.driver.find_element_by_xpath('//div[@class="signupFieldsContainer ng-scope"]/fieldset/div[3]').click()
        # time.sleep(2)
        # self.driver.find_element_by_xpath('//div[@class="signupFieldsContainer ng-scope"]/fieldset/xo-guest-options').click()
        # time.sleep(2)
        # # 做一个系统繁忙请重试的判断
        # self.foo()
        # time.sleep(30)
        # self.logger.info(u"支付成功")
        # self.orders_whether_succeed()
        """
         信用卡 支付
        # """
        # 检查 ip是否发生变化
        get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        self.logger.info(get_ipinfo)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
            self.logger.info(u"ip地址为：{ip}".format(ip = ip))

        card_number = self.order_user_info["payment"]["CreditCardNumber"]
        month = self.order_user_info["payment"]["ccMonth"]
        month_index = int(month) + 1
        year = self.order_user_info["payment"]["ccYear"]
        year_index = int(year) - 17
        CVC = self.order_user_info["payment"]["cvv"]
        print("CVC: ", CVC)
        self.logger.info(u"开始准备填写银行卡信息")
        time.sleep(random.randint(3, 5))

        card_iframe = self.driver.find_element_by_xpath('//iframe[@class="iframe___dxGbX "]')
        self.driver._switch_to.frame(card_iframe)

        time.sleep(random.randint(4, 6))
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@class="form-inner"]/div[1]//input'))
        # )
        # card_number
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[1]//input').click()
        time.sleep(random.randint(3, 5))
        for i in  card_number:
            self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[1]//input').send_keys(i)
            time.sleep(random.randint(1, 2))
        time.sleep(random.randint(3, 5))

        # month
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]').click()
        time.sleep(random.randint(3, 5))
        for i in range(1,12):
            if i == int(month):
                self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]//option[%d]' % month_index).click()
            else:
                month_1 = self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]//option[%d]' % i)
                ActionChains(self.driver).move_to_element(month_1).perform()
                time.sleep(1)
        time.sleep(random.randint(3, 5))
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]').click()
        time.sleep(random.randint(3, 5))

        # year
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]').click()
        time.sleep(random.randint(3, 5))
        for i in range(1,12):
            if i == year_index:
                self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]//option[%d]' % year_index).click()
            else:
                year_1 =  self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]//option[%d]' % i )
                ActionChains(self.driver).move_to_element(year_1).perform()
                time.sleep(1)
        time.sleep(random.randint(3, 5))
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]').click()
        time.sleep(random.randint(2, 5))

        # CVC
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[3]//input').send_keys(CVC)
        time.sleep(random.randint(3, 5))
        self.logger.info(u"银行卡信息填写完成")
        time.sleep(5)

        # 　 检查ip是否发生变化
        get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        self.logger.info(get_ipinfo)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
            self.logger.info(u"ip地址为：{ip}".format(ip=ip))


        # 点击支付-下单
        self.driver.find_element_by_xpath('//button[@class="form-submit"]').click()#send_keys(Keys.ENTER)
        time.sleep(2)
        self.create_cache_filer()
        # 判断是否出现错误提示
        # error_number = self.driver.find_elements_by_xpath('//div[@class="form-row form-globalError"]/div').__len__()
        # if error_number > 0:
        #     self.logger.info(u"出现错误提示，刷新网页重试中")
        #     self.driver.refresh()
        #     time.sleep(3)
        #     self.aad_payment_tpye()
        self.driver._switch_to.default_content()
        self.logger.info(u"正在判断支付是否成功")
        time.sleep(30)
        self.orders_whether_succeed()

    # 做一个系统繁忙请重试的判断
    def foo(self):
        self.driver.find_element_by_id('guestSubmit').click()
        time.sleep(3)
        numbers = self.driver.find_elements_by_id("notifications").__len__()
        if numbers > 0:
            self.foo()

    # 生成一个缓存文件 用于判断 该账号是否 下过单
    def create_cache_filer(self):
        with open(self.paths,"w",encoding="utf-8")as fp:
            fp.write("已经下过单的")
        fp.close()

    #  删除缓存文件
    def detele_cache_filer(self):
        if (os.path.exists(self.dirPath + self.filername)):
            os.remove(self.dirPath + self.filername)
            self.logger.info(u"已经删除缓存文件：{file}".format(file = self.filername))

    # 判断订单是否成功
    def orders_whether_succeed(self):
        if len(self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]/h1')) > 0:
            self.logger.info(u"Поздравляем, заказ выполнен успешно!")
            time.sleep(1)
            self.add_order_log("下单成功日志")
            # 下单————时间
            self.order_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(3)
            self.goto_myorder()
            time.sleep(3)
            self.get_orderinfo()
            self.updata_state(status=2, order_no=self.order_number, payment_date=self.order_time, actual_order_amount=self.order_price)
            self.detele_cache_filer()
            time.sleep(2)
            self.driver.quit()
        else:
            if self.driver.find_element_by_xpath(
                    '//div[@class="payment___v_-wv"]//div[@class=" item___1NoTC "]').text == "Новый вариант оплаты":#"New Payment Type":
                self.goto_myorder()
                self.order_page_whether_succeed()
        # try:
        # try:
        #     WebDriverWait(self.driver, 30).until(
        #         EC.presence_of_all_elements_located((By.XPATH, '//div[@class="inner___27ZuH"]/h1'))
        #     )
        # except TimeoutError as e:
        #     self.logger.info(e)
        #     self.driver.quit()
        # time.sleep(5)
        # 这个判断有问题 错误弹窗 也有这个节点 需要重新修改 ： 2019-6-13
        # content = self.driver.find_element_by_xpath('//div[@class="inner___27ZuH"]/h1').text
        # print(content)
        # time.sleep(5)
        # num = self.driver.find_elements_by_xpath('//div[@class="parent___3TKSF"]//div[@class=" item___1NoTC "]').__len__()
        # print(num)
        # if self.driver.find_elements_by_xpath('//div[@class="parent___3TKSF"]//div[@class=" item___1NoTC "]').__len__() > 0:
        #     self.loggrt.info(u"错误弹窗")
        #     self.goto_myorder()
        #     self.order_page_whether_succeed()
        # # if self.driver.find_element_by_xpath('//div[@class="inner___27ZuH"]/h1').text == "Thank you for your order!":
        # else:
        #     self.loggrt.info(u"成功页面")
        #     self.logger.info(u"Поздравляем, заказ выполнен успешно!")
        #     time.sleep(20)
        #     time.sleep(1)
        #     self.add_order_log("下单成功日志")
        #     # 下单————时间
        #     self.order_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #     time.sleep(3)
        #     self.goto_myorder()
        #     time.sleep(3)
        #     self.get_orderinfo()
        #     self.updata_state(status=2, order_no=self.order_number, payment_date=self.order_time, actual_order_amount=self.order_price)
        #     self.detele_cache_filer()
        #     time.sleep(2)
        #     self.driver.quit()

        # elif self.driver.find_element_by_xpath('//div[@class="inner___27ZuH"]/h1').text == "Oops! Something went wrong.":
        # elif self.driver.find_elements_by_xpath('//div[@class="parent___3TKSF"]//div[@class=" item___1NoTC "]').__len__() > 0:
        #     self.loggrt.info(u"错误弹窗")
        #     self.goto_myorder()
        #     self.order_page_whether_succeed()
        # else:
        #     # if self.driver.find_element_by_xpath('//div[@class="payment___v_-wv"]//div[@class=" item___1NoTC "]').text == "New Payment Type":
        #         self.loggrt.info(u"本页")
        #         self.goto_myorder()
        #         self.order_page_whether_succeed()
        # except Exception as e:
        #     self.logger.info(e)
        #     time.sleep(2)
        #     self.driver.quit()

    # 在订单界面判断有没有支付成功
    def order_page_whether_succeed(self):
        time.sleep(5)
        if self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]/h1').__len__() > 0:
            self.logger.info(u'下单失败,订单中心没有任何订单')
            time.sleep(1)
            self.add_order_log("下单失败日志")
            # self.updata_state(status=24, order_no="", payment_date="", actual_order_amount=0.00)
            # self.logger.info(u'退出程序')
            # time.sleep(2)
            # self.driver.quit()
            self.order_num += 1
            self.logger.info(u"下单失败第 %d 次" % self.order_num)
            if self.order_num < 3:
                self.logger.info(u'重试')
                self.driver.back()
                time.sleep(3)
                self.task_page()
            else:
                self.logger.info(u"下单次数大于三次了,退出程序")
                time.sleep(1)
                self.add_order_log("下单失败日志")
                self.updata_state(status=24, order_no="", payment_date="", actual_order_amount=0.00)
                self.driver.quit()
        else:
            WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="status___AN7Tv"]/span'))
            )
            order_type = self.driver.find_element_by_xpath(
                '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="status___AN7Tv"]/span').text
            print(order_type)
            if order_type == "Paid":
                self.logger.info(u"下单成功")
                self.add_order_log("下单成功日志")
                # 下单————时间
                self.order_time  = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(self.order_time)
                time.sleep(3)
                self.get_orderinfo()
                time.sleep(3)
                self.updata_state(status=2, order_no=self.order_number, payment_date=self.order_time, actual_order_amount=self.order_price )
                self.detele_cache_filer()
                time.sleep(2)
                self.driver.quit()
            else:
                self.order_num += 1
                self.logger.info(u"下单失败第 %d 次" % self.order_num)
                if self.order_num < 3:
                    self.logger.info(u'重试')
                    self.driver.back()
                    time.sleep(3)
                    self.task_page()
                else:
                    self.logger.info(u"下单次数大于三次了,退出程序")
                    time.sleep(1)
                    self.add_order_log("下单失败日志")
                    self.updata_state(status=24, order_no="", payment_date="", actual_order_amount=0.00)
                    self.driver.quit()

    # 更新刷单状态
    def updata_state(self, status, order_no, payment_date, actual_order_amount):

        data = {
            "data": {
                "task_id": self.order_user_info["task_id"],
                "status": status,
                "order_no": order_no,
                "payment_date": payment_date,
                "actual_order_amount": actual_order_amount
            }
        }
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomModifyTaskOrderStatus&inner_debug=1"
        res = post(requests.session(), url = url, post_data = json.dumps(data))
        if res:
            if json.loads(res.text)["status"] == 0:
                self.logger.info(u"订单刷新成功")
            else:
                self.logger.info(u"订单刷新失败")

    # 新增刷单日志
    def add_order_log(self, info):
        # 　 检查ip是否发生变化
        get_ipinfo = get(requests.session(), 'https://ipinfo.io/', proxies=self.proxies)
        self.logger.info(get_ipinfo)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
            self.logger.info(u"ip地址为：{ip}".format(ip=ip))
        data = {
                "task_id": self.order_user_info["task_id"],
                "info": info,  #"日志信息",
                "ip": ip
                }
        url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomCreateTaskOrderLog&inner_debug=1"
        res = post(requests.session(), url=url, post_data=json.dumps(data))
        print(json.loads(res.text)["status"])
        if res:
            if json.loads(res.text)["status"] == 0:
                self.logger.info(u"日志新增成功")
            else:
                self.logger.info(u"日志新增失败")

    # 进入我的订单
    def goto_myorder(self):
        time.sleep(4)
        self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
        time.sleep(3)
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="profile___2NGBH"]//div[@class="parent___AMaLV"]/div[2]/a[1]'))
        )
        self.driver.find_element_by_xpath(
            '//div[@class="profile___2NGBH"]//div[@class="parent___AMaLV"]/div[2]/a[1]').click()
        time.sleep(5)

    # 获取订单信息
    def get_orderinfo(self):
        self.order_number = self.driver.find_element_by_xpath(
            '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="id___OhKOl"]/span').text
        self.order_price = self.driver.find_element_by_xpath(
            '//div[@class="ordersList___b0dZw"]/div[1]//div[@class="info___IK2KI"]//td[@class="infoData___2tz3t"]/span[2]').text.replace(
            '$', '') + "卢比"
        time.sleep(3)
        self.save_orderinfo()
        self.logger.info(u"订单号为：{order_number}".format(order_number = self.order_number))
        self.logger.info(u"订单金额为:{order_price}".format(order_price = self.order_price))
        self.logger.info(u"下单时间为：{order_time}".format(order_time = self.order_time))

    # 将订单相关信息保存到json文件中
    def save_orderinfo(self):
        items = {}
        items["order_number"] = self.order_number
        items["order_time"] = self.order_time
        items["order_price"] = self.order_price
        content = json.dumps(items, ensure_ascii=False)
        with open('order_info.json', 'a', encoding="utf-8") as fp:
            fp.write(content + ",\n")

def main(order_user_info):
    spider = Joon_Orders_spider(order_user_info)
    spider.Login()#user_login()#

def main_1(limit):
    s = requests.session()
    url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomGetTaskOrdersList2&country_code={country_code}&limit={limit}&get_type={getType}&inner_debug=1"
    r = get(s, url=url.format(country_code="RU", getType=1, limit=limit))
    print(r.text)
    content = json.loads(r.text)
    print(content)
    if r:
        if len(content) != 0:
            for k in content.keys():
                print(k)
                ip = content[k]["account"]["ip"]
                order_user_info = content[k]
                print(ip)
                print("任务列表获取成功")
        else:
            # print('未获取到待注册账户的数据，程序结束！')
            # sys.exit(0)
            print('当前无下单任务，程序[sleep 10m]...')
            time.sleep(60 * 10)
    else:
        print('任务系统出错，程序[sleep 10m]...')
        time.sleep(60 * 10)
    try:
        url_ip = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomCheckLoginIp&login_ip={login_ip}&inner_debug=1"
        res = get(s, url=url_ip.format(login_ip=ip))
        print(res.text)
        if res:
            if json.loads(res.text)["code"] == 200:
                print("ip可用")
            else:
                print("ip不可用")
    except Exception as e:
        print(e)
    main(order_user_info)


if __name__ == '__main__':
    p = Pool()
    for i in range(1):
        p.apply_async(main_1(1))
    p.close()
    p.join()



def main(user_info, register_city, proxies):
    spider = JoomRegisterSpider(user_info, register_city, proxies)
    spider.register()

def main_1():

    s = requests.session()

    #邮箱规则：1位随机大写字母 + 7位随机小写字母 + 3位随机数字 + 邮箱域名[按索引轮询]
    email = random.choice(Upper_Letter_List) + ''.join(random.sample(Lower_Letter_List, 7)) + ''.join(
        random.sample(Digit_List, 3)) + '@' + random.choice(Email_Domains)
    print(email)
    # oxy代理
    proxies = get_oxylabs_proxy('ru', None, '0.1234564846502153')["https"]
    # 住宅代理
    # proxies = 'http://10502+RU+10502-%s:Y7aVzHabW@ru-30m.geosurf.io:8000' % random.randint(100000, 200000)
    #　指定某个城市的ｉｐ
    # city = "Yoshkar-ola"
    # proxies = "http://customer-rdby111-cc-ru-city-%s-sessid-0.1234564846502153:4G5wTzP5rj@ru-pr.oxylabs.io:40000" % city
    # # try:
    url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomGetOneValidAddress&country_code=RU&inner_debug=1"
    r = get(s, url)
    html = json.loads(r.text)
    print(html['code'])
    if html['code'] == 200:
        print(proxies)
        proxie = {"https": proxies }
        get_ipinfo = get(s, 'https://ipinfo.io/', proxies=proxie)
        print(get_ipinfo.text)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            print("ip信息",ipinfo)
            local_ip = ipinfo["ip"]
            print("调试")
            print(local_ip)
            register_city = ipinfo["city"]
            print("注册ip城市为：",register_city)
    # 获取自动注册账号所需要的 邮箱, 地址, IP, 信用卡
    url = "http://third.gets.com/api/index.php?sec=20171212getscn&act=joomAutoCreateAccountGet&country_code={country_code}&validate_email={validateEmail}&dynamic_ip={dynamicIp}&inner_debug=1"
    res = get(s, url.format(country_code="RU", validateEmail=email, dynamicIp=local_ip))
    content = json.loads(res.text)
    print(content['code'])
    if res:
        if content["code"] == 200:
            user_info = content
            print("收获地址城市：",user_info["data"]["address"]["city"])
            print(user_info)
            main(user_info, register_city, proxies)
        else:
            # print('未获取到待注册账户的数据，程序结束！')
            # sys.exit(0)
            print('当前无注册任务，程序[sleep 10m]...')
            time.sleep(60 * 10)
    else:
        print('任务系统出错，程序[sleep 10m]...')
        time.sleep(60 * 10)

if __name__ == '__main__':

    p = Pool()
    for i in range(1):
        p.apply_async(main_1)
    p.close()
    p.join()

