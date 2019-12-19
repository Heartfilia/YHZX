#必须登录后，才能持续访问。

import random
import threading
import time
from user_agent import generate_user_agent
from lxml import etree
import requests
import json
from mytools import tools


class AliexpressKillAD:
    def __init__(self):
        self.headers = {
            # "Host": "www.aliexpress.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": generate_user_agent(device_type='desktop'),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "https://www.aliexpress.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",

        }
        self.proxies=self.get_oxylabs_proxy('us', _city=None, _session=random.random())
        # self.proxies = {'https':'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(200000, 500000)}

        self.AD_urls = []
        self.session = requests.session()
        cookie_list = json.dumps(cookies)
        self.cookies = {}
        for cookie in cookies:
            self.cookies[cookie['name']] = cookie['value']


    def run(self):
        s = requests.session()
        for key in self.cookies:
            s.cookies.set(key, self.cookies[key])
        for url in self.AD_urls:
            res = tools.get(s, url)
            if res and 'Add to Cart' in res.text:
                print('成功点击了广告！')

    def visit_ad_page(self):
        if self.AD_urls:
            for i in self.AD_urls:
                for j in range(1,31):
                    resp = requests.get(url=i, headers=self.headers,proxies=self.proxies)
                    if resp.status_code == 200 and 'Add to Cart' in resp.text:
                        print('成功点击%d次广告：%s'%(j, i) )
                        # if j == 10:
                        #     with open('10.html','w',encoding='utf-8') as f:
                        #         f.write(resp.text)
                    time.sleep(random.randint(1,4))

    @staticmethod
    def get_oxylabs_proxy(_country, _city, _session):
        # def get_oxylabs_proxy(_country,_session):
        # 端口10000随机
        # 端口10001 - 19999 美国端口
        username = 'rdby111'
        password = '4G5wTzP5rj'
        country = _country
        city = _city
        session = _session
        port = 10000
        if _country == 'gb':
            port = 20000
        if _country == 'ca' or _country == 'cn' or _country == 'de':
            port = 30000

        if city:
            entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
                     (username, country, city, session, password, country, port))
        else:
            entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
                     (username, country, session, password, country, port))
        proxies = {
            'http': entry,
            'https': entry,
        }
        return proxies

def main():
    spider = AliexpressKillAD()
    spider.run()

if __name__ == '__main__':
    threads = []
    for i in range(1):
        t = threading.Thread(target=main)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()