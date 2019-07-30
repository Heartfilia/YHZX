# -*- coding: utf-8 -*-
import re
import json
import time
import sys
import random
import datetime
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging import getLogger
import logging
import requests
from multiprocessing import Process
from mytools.tools_1 import get_oxylabs_proxy, create_proxyauth_extension, get, post
from user_agent import generate_user_agent


class Joon_Orders_spider(object):

    def __init__(self):

        # self.cookies = self.user_info["account"]["cookies"]
        # print('user_info:', self.user_info)
        self.find_number = 0
        self.number = 1
        self.login_num = 0
        # self.product_type = self.user_info["asin"]["keywords"]
        # self.pid = "5c7e2bba28fc71010165a9e5" #self.user_info["asin"]["asin"]

        self.product_type = "pins"
        self.pid = '5bcd933b36b54d01767b218a'

        self.switch = True
        self.cat_switch = True
        self.order_num = 0

        self.logger = getLogger()
        self.logger.setLevel(logging.DEBUG)
        filename = 'Log/log.log'
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
        # 添加请求头
        # # self.options.add_argument('user-agent="%s"' % self.user_info["account"]["header"])
        # self.options.add_argument('user-agent="%s"' % self.get_userinfo()["headers"])
        # 加user-agent 变成手机浏览器
        self.User_Agent = generate_user_agent(device_type="smartphone")
        self.headers = {
            "user-agent": self.User_Agent
        }
        self.options.add_argument('user-agent="%s"' % self.User_Agent)
        # 处理https 安全问题或者非信任站点
        self.options.add_argument('--ignore-certificate-errors')
        # 设置代理
        # 代理需要指定账户密码时，添加代理使用这种方式
        # self.options.add_extension(proxyauth_plugin_path)
        self.proxy = 'http://10502+HK+10502-%s:Y7aVzHabW@hk-30m.geosurf.io:8000' % random.randint(600000, 800000)
        # self.proxy = get_oxylabs_proxy('ru', _city=None, _session=random.random())['https']
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        self.logger.info("本次 ip 为: %s" % self.proxy)
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
        # self.driver = webdriver.Safari(self.url)

    """
    使用cookie登陆Joom
    """
    def Login(self):

        cookies = self.get_userinfo()
        # self.logger.info（cookies["cookie"])
        # 先打开一下浏览器 让cookie知道放在那里
        self.driver.get(self.url)
        time.sleep(3)
        # 添加cookie
        items = {}
        for li in cookies["cookie"]:
            items["name"] = li["name"]
            items["value"] = li["value"]
            self.driver.add_cookie({"name": items["name"], "value": items["value"]})

        self.driver.get(self.url)

        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="profile___2NGBH"]'))
        )
        time.sleep(4)
        self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
        time.sleep(3)
        if self.driver.find_element_by_xpath('//div[@class="item___a8qBu"]').text == "Выход":#"Sign Out":
            self.logger.info(u"登录成功")
            self.logger.info(u"登陆成功")
            time.sleep(2)
            self.search_items()
        else:
            self.logger.info(u"登陆失败---正在重新登录---")
            self.Login()
    """
       将用户信息从json文件中获取到
    """
    def get_userinfo(self):
        with open(r"D:\lodge\pack\pyfile\project\Joom_Orders\joom_userinfo.json", "r")as fp:
            cookies = fp.readline()
            cookies = json.loads(cookies)
            return cookies

    """ 
    账号密码登录
    """

    # def user_login(self):
    #
    #     # 获取网页的时候 要做一个超时判断
    #     self.driver.get(self.url, )
    #     # WebDriverWait(self.driver, timeout=3, poll_frequency=1, ignored_exceptions='超时').until(
    #     #     EC.presence_of_element_located((By.ID, "content"))
    #     # )
    #
    #     # 去掉广告
    #     WebDriverWait(self.driver, 30).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[@class="popup___ByDf3 "]'))
    #     )
    #     self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 "]//div[@class="close___zSRXA"]').click()
    #     self.login()
    #
    # # 登录操作
    # def login(self):
    #     WebDriverWait(self.driver, 30).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[@class="profile___2NGBH"]'))
    #     )
    #     self.driver.find_element_by_xpath('//div[@class="profile___2NGBH"]').click()
    #     time.sleep(3)
    #     self.driver.find_element_by_xpath('//div[@class="inner___2LYLS"]/div[5]').click()
    #     # time.sleep(5)
    #     # self.driver.find_element_by_name('email').click()
    #     WebDriverWait(self.driver, 30).until(
    #         EC.element_to_be_clickable((By.XPATH, '//form[@class="form___1qcS9"]/div[1]'))
    #     )
    #     self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]//input').send_keys(
    #        "cy45423582659@qq.com")  # self.user_info["account"]["login_joom_email"]
    #     # self.driver.find_element_by_name('email').send_keys('1933745428@qq.com')
    #     time.sleep(1)
    #     self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]//input').send_keys(
    #        "zhangsan123" )  #  self.user_info["account"]["login_joom_password"]
    #     # self.driver.find_element_by_name('password').send_keys('ZhanShen002')
    #     time.sleep(3)
    #     # 点击登陆  还需要做一个登陆成功判断
    #     self.driver.find_element_by_xpath('//button[@class="submit___3cAJx"]').click()
    #     time.sleep(5)
    #     if self.driver.find_elements_by_xpath('//form[@class="form___1qcS9"]/p').__len__() > 0:
    #         self.logger.info(u"登陆失败---正在重新登录---")
    #         self.driver.refresh()
    #         time.sleep(2)
    #         self.login_num += 1
    #         if self.login_num < 3:
    #             self.login()
    #         else:
    #             self.logger.info("登陆失败次数大于三次—退出程序")
    #             # self.login_log("登录失败", 2 , self.cookies)
    #             sys.exit(1)
    #     else:
    #         time.sleep(5)
    #         # 如果登陆出现 用户者协议 则点击我同意
    #         if self.driver.find_elements_by_xpath(
    #                 '//div[@class="inner___3uuBN"]//div[@class="positiveButton___1-fkP"]').__len__() > 0:
    #             self.driver.find_element_by_xpath(
    #                 '//div[@class="inner___3uuBN"]//div[@class="positiveButton___1-fkP"]').click()
    #             time.sleep(2)
    #             self.logger.info(u"出现了用户者协议")
    #             self.logger.info(u"登陆成功")
    #             # self.updata_cookies_headers_info()
    #             time.sleep(1)
    #             # self.login_log("登录成功", 1 ,json.dumps(self.driver.get_cookies()) )
    #             time.sleep(1)
    #             self.search_items()
    #         else:
    #
    #             self.logger.info(u"登陆成功")
    #             # self.updata_cookies_headers_info()
    #             time.sleep(1)
    #             # self.login_log("登录成功", 1, json.dumps(self.driver.get_cookies()))
    #             time.sleep(1)
    #             self.search_items()

    # 添加登录日志
    def login_log(self, login, status, cookies):
        data = {
            "data":{
                "account_id": self.user_info["account"]["account_id"], #"64",
                "header": self.user_info["account"]["header"], #"header info test",
                "cookies": cookies, #self.user_info["account"]["cookies"], #"cookies into test",
                "login_status": status, # "1","2"
                "login_ip": self.user_info["account"]["ip"], #"127.0.0.1",
                "note": login,
            }
        }
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomInsertAccountLoginLog"
        res = post(requests.Session(), url=url, post_data=json.dumps(data))
        if res:
            if res.status_code == 200:
                self.logger.info("账号登录日志添加成功")
            else:
                self.logger.info("账号登录日志添加失败")

    # 登陆成功 更新 headers 和 cookies 信息
    def updata_cookies_headers_info(self):
        data = {
            "data":{
                "account_id": self.user_info["account"]["account_id"],   #"64",
                "header": self.user_info["account"]["header"],
                "cookies": json.dumps(self.driver.get_cookies()),
            }
        }

        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomUpdateAccountLoginSuccessInfo"
        res = post(requests.Session(), url=url, post_data=json.dumps(data))
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
        self.driver.find_element_by_xpath('//input[@class="input___3wRUz"]').send_keys(self.product_type)
        print(self.product_type)
        self.logger.info(u'Я тебя люблю')
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="submit___3XMCO"]'))
        )
        self.logger.info(u"点击搜索")
        self.driver.find_element_by_xpath('//button[@class="submit___3XMCO"]').click()
        # self.find_to_shoppong()
        time.sleep(5)
        if self.driver.find_elements_by_xpath('//div[@class="productWrap___30WNd"]').__len__() > 0:
            self.logger.info(u"进入商品列表页")
            self.add_to_cart()
        else:
            self.driver.refresh()
            self.search_items()

    # 根据商品的pid来查找商品
    def find_to_shoppong(self):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH,
                                                     '//div[@class="productWrap___30WNd"]//div[@class="square___1fugM "]//a[@class="link___28nVD"]'))
            )
            # 判断商品数量
            shopping_number = self.driver.find_elements_by_xpath(
                '//div[@class="productWrap___30WNd"]//div[@class="square___1fugM "]//a[@class="link___28nVD"]').__len__()
            # self.logger.info(shopping_number)
            for i in range(self.number, shopping_number + 1):
                print("第{page}页，第{i}个".format(page = self.find_number + 1, i=i))
                shopping_url = self.driver.find_element_by_xpath(
                    '//div[@class="productWrap___30WNd"][%d]//div[@class="square___1fugM "]//a[@class="link___28nVD"]' % self.number).get_attribute(
                    'href')
                # print(self.pid)
                if self.pid in shopping_url:
                    self.logger.info(i)
                    self.logger.info(shopping_url)
                    print("###################")
                    print(i)
                    print(type(i))
                    print(self.find_number)
                    print(type(self.find_number))
                    print("###################")
                    # if self.find_number < 1:
                    #     # self.updata_postion(i)
                    # else:
                    #     row_num = i - 36 * (self.find_number)
                    #     print(row_num)
                    #     print("第:{row_num}个".format(row_num=row_num))
                    #     # self.updata_postion(row_num)

                    self.logger.info(u"找到了")
                    self.driver.find_element_by_xpath('//div[@class="productWrap___30WNd"][%d]' % self.number).click()
                    return
                else:
                    # self.logger.info(u"没有找到，正在重新查找")
                    self.number += 1
        except Exception as e:
            self.logger.info(e)
            sys.exit(1)

        # 查询 前多少页 的商品
        if self.find_number < 15:
            print(self.find_number)
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
            # self.updata_state(status=21, order_no="", payment_date="", actual_order_amount=0.00)
            time.sleep(2)
            sys.exit(1)

    # 更新当前页码和当前位置
    def updata_postion(self, row_num):
        data = {
            "data": {
                "page_num": self.find_number + 1,
                "row_num": row_num,
                "task_id": self.user_info["task_id"]
            }
        }
        print("第:{num}页".format(num=self.find_number + 1))
        print("第:{row_num}个".format(row_num=row_num))
        # print("------%s--------" % str(row_num))
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomUpdatePageAndRank"
        res = post(requests.Session(), url=url, post_data=json.dumps(data))
        print(json.loads(res.text)["code"])
        if res:
            if json.loads(res.text)["code"] == 200:
                self.logger.info(u"更新成功")
            else:
                self.logger.info(u"更新失败")

    # 将需要的商品添加至购物车里面
    def add_to_cart(self):
        # 搜索完成 等待商品加载出来
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="productWrap___30WNd"]'))
        )
        if self.switch:  # 1 True
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
                                    '//div[@class="attributes___iJZOP "]/div[%d]/div/h2/span' % i).__len__() > 0:
                                self.logger.info(u"选好了")
                                break
                            else:
                                self.driver.find_element_by_xpath(
                                    '//div[@class="attributes___iJZOP "]/div[%d]/div/div[%d]' % (i, j)).click()
                                break
                else:
                    self.logger.info(u"该参数已经选择好了")
        time.sleep(random.randint(3, 5))
        # 添加商品至购物车
        self.driver.find_element_by_xpath('//div[@class="button___1WAua"]').click()
        time.sleep(10)

        if len(self.driver.find_elements_by_xpath('//div["related___2Opz_"]')) > 0:
            self.logger.info(u"添加购物车成功")
            self.switch = False
            time.sleep(3)
            self.add_other_to_cart()
        else:
            self.logger.info(u"添加购物车失败")
            # 如果添加失败的话 先刷新当前网页 然后在 重新选择
            self.driver.refresh()
            self.add_to_cart()

    # 将不需要的商品添加至购物车里面，模拟认人为失误
    def add_other_to_cart(self):
        if self.cat_switch:
            self.driver.find_element_by_xpath('//div[@class="inner___2poSi"]/span[3]').click()
            self.cat_switch = False
            self.add_to_cart()
            time.sleep(3)
        else:
            self.delete_other_from_cart()

    # 将不需要的商品从购物车中删掉
    def delete_other_from_cart(self):
        self.driver.find_element_by_xpath('//div[@class="cart___3Shcs"]').click()
        time.sleep(3)
        # 取消需要的商品(根据pid)
        # self.driver.find_element_by_xpath('//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]').click()
        shop_num = self.driver.find_elements_by_xpath(
            '//div[@class="element___Zz7DL"]/div/div[2]/div[2]/div[@class=" item___1NoTC "]').__len__()
        self.logger.info(u'shop_num: %s' % shop_num)
        # 判断 如果只有一种商品 就直接判断商品的数量
        if shop_num < 3:
            self.check_quantity()
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
        self.driver.find_element_by_xpath(
            '//div[@class="content___Q0YRa "]/div[last()]//div[@class="container___3p3gG"]/div[1]').click()
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
        time.sleep(5)
        # # 判断信用卡额度 是不是够 支付商品价格
        # price = self.driver.find_element_by_xpath('//span[@class="buttonText___2_FiU"]/span/span[2]').get_attribute("content")
        # print(price)
        # print(self.user_info["payment"]["single_max_trade"])
        # time.sleep(2)
        # print(float(price) , float(self.user_info["payment"]["single_max_trade"]))
        # try:
        #     if float(price) < float(self.user_info["payment"]["single_max_trade"]):
        self.driver.find_element_by_xpath('//span[@class="buttonText___2_FiU"]').click()
        time.sleep(5)
        self.task_page()
        #     else:
        #          self.logger.info(u"商品价格大于信用卡额度")
        #          sys.exit(1)
        # except Exception as e :
        #     self.logger.info(e)

    # 判断该页面是哪个页面
    def task_page(self):
        if self.driver.find_elements_by_xpath('//div[@class="address___1MpYA"]/form').__len__() > 0:
            self.logger.info(u"进入添加填写收获地址界面")
            self.add_shipping_address()
        elif self.driver.find_element_by_xpath('//div[@class="payment___v_-wv"]/div/div[1]/div').text == "Новый вариант оплаты":#"New Payment Type":
            self.logger.info(u"进入填写银行卡号界面")
            if self.driver.find_elements_by_id("sub-frame-error").__len__() > 0:
                self.driver.refresh()
                time.sleep(random.randint(2, 5))
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
                # sys.exit(1)
                time.sleep(1)
                self.goto_myorder()
                self.order_page_whether_succeed()
            else:
                time.sleep(3)
                self.logger.info(u'判断是否支付成功')
                self.orders_whether_succeed()

    # 填写收货地址（填完保存直接调用 aad_payment_tpye() 方法）
    def add_shipping_address(self):
        street = self.user_info["address"]["AddressLine1"]
        city = self.user_info["address"]["City"]
        state = self.user_info["address"]["StateOrRegion"]
        zip_code = self.user_info["address"]["PostalCode"]
        phone_number = self.user_info["address"]["PhoneNumber"]
        apartment_no = random.randint(1,100)

        self.logger.info(u"正在填写地址………………")
        time.sleep(5)
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//form[@class="form___JoNlz"]/div[1]/div/div[2]'))
        # )
        # country
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[1]//select[@class="element___12f_-"]//optgroup[19]/option[3]').click()
        time.sleep(5)
        # street
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[4]').click()
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[4]//input').send_keys(street)
        time.sleep(5)
        # city
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[3]').click()
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[3]//input').send_keys(city)
        time.sleep(5)
        # state
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[2]//input').send_keys(state)  # //option[43]
        time.sleep(3)
        #house_no
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[5]//input').send_keys(zip_code)
        # #block
        # time.sleep(3)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[6]//input').send_keys(zip_code)
        # # building
        # time.sleep(3)
        # self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[7]//input').send_keys(zip_code)
        # # apartment_no
        time.sleep(3)
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[8]//input').send_keys(apartment_no)

        # zip_code

        time.sleep(3)
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[9]//input').send_keys(zip_code)
        time.sleep(5)
        # phone_number
        self.driver.find_element_by_xpath('//form[@class="form___JoNlz"]/div[2]/div/div[12]//input').send_keys(phone_number)
        self.logger.info(u"地址填写完成………………")
        time.sleep(5)
        # 保存地址
        self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
        time.sleep(10)
        # 判断地址信息有没有填好
        if self.driver.find_element_by_xpath(
                '//div[@class="payment___v_-wv"]//div[@class=" item___1NoTC "]').text == "Новый вариант оплаты":#New Payment Type":
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
        # get_ipinfo = get(requests.session(), 'https://ipinfo.io/')
        # self.logger.info(get_ipinfo)
        # if get_ipinfo:
        #     ipinfo = json.loads(get_ipinfo.text)
        #     ip = ipinfo["ip"]
        #     self.logger.info(u"ip城市为：{ip}".format(ip=ipinfo["city"]))
        #     self.logger.info(u"ip地址为：{ip}".format(ip=ip))
        #
        # time.sleep(5)
        # self.driver.find_element_by_xpath('//div[@class="tabs___svXx5"]/div[2]').click()
        # time.sleep(5)
        # self.driver.find_element_by_xpath('//button[@class="submit___2b4L0 "]').click()
        # # 判断是否弹出错误界面 如果弹出 把他叉掉 刷新网页 在重新点击
        # # self.create_cache_filer()
        # time.sleep(random.randint(3,5))
        # error_number = self.driver.find_elements_by_xpath('//div[@class="inner___3uuBN"]').__len__()
        # print(error_number)
        # if len(self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]')) > 0:
        #     self.logger.info(u"出现错误弹窗，刷新网页重试中")
        #     self.driver.refresh()
        #     time.sleep(3)
        #     self.aad_payment_tpye()
        #
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@class="inputField confidential cardNumber creditCardField ng-scope floatingLabel"]/input'))
        # )
        # self.logger.info(u"正在进入PayPal 支付")
        # card_number = 5329594837927602#int(self.user_info["payment"]["CreditCardNumber"])
        # self.driver.find_element_by_xpath(
        #     '//div[@class="inputField confidential cardNumber creditCardField ng-scope floatingLabel"]/input').send_keys(
        #     card_number)
        # time.sleep(2)
        # month = "06"#self.user_info["payment"]["ccMonth"]
        # year = "21"#self.user_info["payment"]["ccYear"]
        # centen = month + year
        # self.driver.find_element_by_id('expiry_value').send_keys(centen)
        # time.sleep(3)
        # CVC = 181#self.user_info["payment"]["cvv"]
        # self.driver.find_element_by_id('cvv').send_keys(CVC)
        # phone_number = 15797642529#self.user_info["address"]["PhoneNumber"]
        # self.driver.find_element_by_id('telephone').send_keys(phone_number)
        # # 邮箱
        # email = "15797642@qq.com" #self.user_info["account"]["login_joom_email"]
        # self.driver.find_element_by_id("email").send_keys(email)
        # # 邮编
        # zip_number = ""
        # for _ in range(6):
        #     zip_number += str(random.randint(1, 9))
        # self.driver.find_element_by_id("billingPostalCode").clear()
        # self.driver.find_element_by_id("billingPostalCode").send_keys(zip_number)
        # time.sleep(2)
        # self.driver.find_element_by_xpath('//div[@class="signupFieldsContainer ng-scope"]/fieldset/div[3]').click()
        # time.sleep(2)
        # self.driver.find_element_by_xpath(
        #     '//div[@class="signupFieldsContainer ng-scope"]/fieldset/xo-guest-options').click()
        # time.sleep(2)
        # # 做一个系统繁忙请重试的判断
        # self.foo()
        # time.sleep(30)
        # self.orders_whether_succeed()
        '''
        信用卡支付
        :return:
        '''
        card_number = 5329594837927602 #int(self.user_info["payment"]["CreditCardNumber"])
        month = 6  # int(self.user_info["payment"]["ccMonth"])
        month_index = month + 1
        year = 21 # int(self.user_info["payment"]["ccYear"])
        year_index = year - 17
        CVC = 181 # int(self.user_info["payment"]["cvv"])

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
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[1]//input').send_keys(card_number)
        time.sleep(random.randint(2, 5))

        # month
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]').click()
        self.driver.find_element_by_xpath(
            '//div[@class="form-inner"]/div[2]/label[1]//option[%d]' % month_index).click()
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[1]').click()
        time.sleep(random.randint(2, 5))

        # year
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]').click()
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]//option[%d]' % year_index).click()
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[2]/label[2]').click()
        time.sleep(random.randint(2, 5))

        # CVC
        self.driver.find_element_by_xpath('//div[@class="form-inner"]/div[3]//input').send_keys(CVC)
        time.sleep(random.randint(2, 5))
        self.logger.info(u"银行卡信息填写完成")
        time.sleep(2)
        # 点击支付-下单
        self.driver.find_element_by_xpath('//button[@class="form-submit"]').click()
        time.sleep(2)
        # 判断是否出现错误提示
        error_number = self.driver.find_elements_by_xpath('//div[@class="form-row form-globalError"]').__len__()
        if error_number > 0:
            self.logger.info(u"出现错误提示，刷新网页重试中")
            self.driver.refresh()
            time.sleep(3)
            self.aad_payment_tpye()
        self.logger.info(u"正在判断支付是否成功")
        self.driver._switch_to.default_content()
        time.sleep(30)
        self.orders_whether_succeed()

    # 做一个系统繁忙请重试的判断
    def foo(self):
        self.driver.find_element_by_id('guestSubmit').click()
        time.sleep(3)
        numbers = self.driver.find_elements_by_id("notifications").__len__()
        if numbers > 0:
            self.foo()

    # 判断订单是否成功
    def orders_whether_succeed(self):
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@class="inner___27ZuH"]/h1'))
        # )
        # time.sleep(5)
        # 这个判断有问题 错误弹窗 也有这个节点 需要重新修改 ： 2019-6-5
        if len(self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]/h1')) > 0:
            self.logger.info(u"Поздравляем, заказ выполнен успешно!")
            time.sleep(1)
            # self.add_order_log("下单成功日志")
            time.sleep(3)
            self.goto_myorder()
            time.sleep(3)
            self.get_orderinfo()
        else:
            if self.driver.find_element_by_xpath(
                    '//div[@class="payment___v_-wv"]//div[@class=" item___1NoTC "]').text == "New Payment Type":
                self.goto_myorder()
                self.order_page_whether_succeed()

    # 在订单界面判断有没有支付成功
    def order_page_whether_succeed(self):
        time.sleep(5)
        if self.driver.find_elements_by_xpath('//div[@class="inner___27ZuH"]/h1').__len__() > 0:
            self.logger.info(u'下单失败,订单中心没有任何订单')
            time.sleep(1)
            # self.add_order_log("下单失败日志")
            self.logger.info(u'退出程序')
            sys.exit(1)
            # self.driver.back()
            # self.task_page()
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
                # self.add_order_log("下单成功日志")
                # 下单————时间
                self.order_time  = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(self.order_time)
                time.sleep(3)
                self.get_orderinfo()
                time.sleep(3)
                # self.updata_state(status=1, order_no=self.order_number, payment_date=self.order_price, actual_order_amount=self.order_time )
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
                    # self.add_order_log("下单成功日志")
                    sys.exit(1)

    # 更新刷单状态
    def updata_state(self, status, order_no, payment_date, actual_order_amount):

        data = {
            "data": {
                "task_id": self.user_info["task_id"],
                "status": status,
                "order_no": order_no,
                "payment_date": payment_date,
                "actual_order_amount": actual_order_amount
            }
        }
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomModifyTaskOrderStatus"
        res = post(requests.Session(), url = url, post_data = json.dumps(data))
        if res:
            if json.loads(res.text)["status"] == 0:
                self.logger.info(u"订单刷新成功")
            else:
                self.logger.info(u"订单刷新失败")

    # 新增刷单日志
    def add_order_log(self, info):
        # 获取刷单的ip地址
        get_ipinfo = get(requests.Session(), 'http://ipinfo.io/')
        # print(get_ipinfo.text)
        if get_ipinfo:
            ipinfo = json.loads(get_ipinfo.text)
            ip = ipinfo["ip"]
            print(ip)
        data = {
                "task_id": self.user_info["task_id"],
                "info": info,  #"日志信息",
                "ip": ip
                }
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomCreateTaskOrderLog"
        res = post(requests.Session(), url=url, post_data=json.dumps(data))
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
            '$', '') + "美元"
        time.sleep(3)
        self.save_orderinfo()
        self.logger.info(u"订单号为：", self.order_number)
        self.logger.info(u"订单金额为:", self.order_price)
        self.logger.info(u"下单时间为：", self.order_time)

    # 将订单相关信息保存到json文件中
    def save_orderinfo(self):
        items = {}
        items["order_number"] = self.order_number
        items["order_time"] = self.order_time
        items["order_price"] = self.order_price
        content = json.dumps(items, ensure_ascii=False)
        with open('order_info.json', 'a', encoding="utf-8") as fp:
            fp.write(content + ",\n")


def main():
    spider = Joon_Orders_spider()
    spider.Login()


if __name__ == '__main__':
    # s = requests.Session()
    #
    # url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomGetTaskOrdersList2&country_code={country_code}&get_type={getType}"
    # r = get(s, url = url.format(country_code = "RU", getType = 1 ))
    # print(r.text)
    # content = json.loads(r.text)
    # print(content)
    # if r:
    #     if len(content) != 0 :
    #         for k in content.keys():
    #             print(k)
    #             ip = content[k]["account"]["ip"]
    #             user_info = content[k]
    #             print(ip)
    #             print("任务列表获取成功")
    #     else:
    #         # print('未获取到待注册账户的数据，程序结束！')
    #         # sys.exit(0)
    #         print('当前无下单任务，程序[sleep 10m]...')
    #         time.sleep(60 * 10)
    # else:
    #     print('任务系统出错，程序[sleep 10m]...')
    #     time.sleep(60 * 10)
    # try:
    #     url_ip = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomCheckLoginIp&login_ip={login_ip}"
    #     res = get(s, url = url_ip.format(login_ip = ip))
    #     print(res.text)
    #     if res:
    #         if json.loads(res.text)["code"] == 200:
    #             print("ip可用")
    #         else:
    #             print("ip不可用")
    # except Exception as e:
    #     print(e)


    process_list = []
    for i in range(1):
        print(u"主线程开始")
        p = Process(target=main)
        p.start()
        process_list.append(p)
        time.sleep(30)
    for i in range(len(process_list)):
        p.join()