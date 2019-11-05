import os
import sys
import random
import re
import json
from user_agent import generate_user_agent
# import threading
from multiprocessing import Process
import time
import datetime
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException,TimeoutException,NoSuchFrameException,WebDriverException
from mytools.tools import get_oxylabs_proxy, get, post, create_proxyauth_extension, logger, load_json, save_json
from config import City_List

class AliexpressKillAd():
    def __init__(self):
        self.proxy = 'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(200000, 500000)
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="%s"' % generate_user_agent(device_type="desktop") )
        #代理需要指定账户密码时，添加代理使用这种方式
        self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        #headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        #设置不加载图片
        # self.options.add_experimental_option('prefs',{"profile.managed_default_content_settings.images":2})
        self.driver = webdriver.Chrome(options=self.options)
        #self.good_detail_urls属性，用于绑定目标商品所在列表页的所有商品的详情链接
        # self.good_detail_urls = ['https://www.aliexpress.com/item/32437358564.html']
        #self.target_good_detail_url属性，用于绑定目标商品的详情链接
        # self.target_good_detail_url = None

    def run(self):
        self.driver.get('http://www.aliexpress.com')
        sys.exit(0)

if __name__ == '__main__':
    spider = AliexpressKillAd()
    spider.run()