#必须登录后，才能持续访问。

import random
import time
from multiprocessing import Process
import requests
import json
from mytools.tools import logger, get, post, get_oxylabs_proxy

logger = logger('kill_ad')
class AliexpressKillAD:
    def __init__(self, task):
        self.task = task
        self.headers = {
            # "Host": "www.aliexpress.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            # "User-Agent": generate_user_agent(device_type='desktop'),
            "User-Agent": json.loads(self.task.get('header')),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "https://www.aliexpress.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.proxies=get_oxylabs_proxy('us', _city=None, _session=random.random())
        self.session = requests.session()
        cookie_list = json.dumps(self.task.get('cookies'))
        self.cookies = {}
        for cookie in cookie_list:
            self.cookies[cookie['name']] = cookie['value']

    def run(self):
        s = requests.session()
        for key in self.cookies:
            s.cookies.set(key, self.cookies[key])
        url = self.task.get('attack_url')
        res = get(s,url=url, headers=self.headers, proxies=self.proxies)
        if res and  'Add to Cart' in res.text:
            logger.info('成功点击广告 [1] 次!')
            attack_info = {
                "id": self.task.get("id"),
                "click_number": "1",
                "brand_name": self.task.get("attack_brand_name"),
                "asin": self.task.get("attack_asin"),
                "log": '成功点击广告1次！',
                "ip": self.get_ip_info(proxies=self.proxies)
            }
            kill_data = {
                'data':{
                    "master_id":self.task.get("master_id"),
                    "attack_info": json.dumps(attack_info)
                }
            }
            self.update_kill_data(json.dumps(kill_data))

    def update_kill_data(self, data):
        # url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=modifyAliexpressAdvertisingAttackURL'
        url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=modifyAliexpressAdvertisingAttackURL'
        resp = post(requests.session(), url=url, post_data=data)
        print("result", resp.text)
        if resp:
            if resp.json().get('msg') == "OK":
                logger.info('[master_id: %s] [id: %s] 广告点击的数据入库成功！' % (self.task.get("master_id"), self.task.get('id')))
            else:
                logger.info('[%s] [%s] 广告点击的数据入库失败！' % (self.task.get("master_id"), self.task.get('id')))

    # 获取当前ip信息，返回字符串
    @staticmethod
    def get_ip_info(proxies):
        getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        if getIpInfo:
            ipInfo = json.loads(getIpInfo.text)
            ip = ipInfo['ip']
        else:
            ip = '未获取到ip'
        return ip

    # def visit_ad_page(self):
    #     if self.AD_urls:
    #         for i in self.AD_urls:
    #             for j in range(1,31):
    #                 resp = requests.get(url=i, headers=self.headers,proxies=self.proxies)
    #                 if resp.status_code == 200 and 'Add to Cart' in resp.text:
    #                     print('成功点击%d次广告：%s'%(j, i) )
    #                     # if j == 10:
    #                     #     with open('10.html','w',encoding='utf-8') as f:
    #                     #         f.write(resp.text)
    #                 time.sleep(random.randint(1,4))

def main(task):
    spider = AliexpressKillAD(task)
    spider.run()

if __name__ == '__main__':
    while True:
        #测试地址
        url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=getAliexpressAdvertisingAttackURL'
        resp = get(requests.session(), url=url)
        if resp:
            try:
                if resp.json().get('error_msg'):
                    logger.info('未获任务出错，marketplace_id参数不能为空，程序[sleep 10m]...')
                    time.sleep(60 * 10)
                else:
                    task_infos = resp.json()
                    tasks = task_infos.get("attack_url")
                    logger.info('成功获取到 [%d] 条待执行的广告点击任务！' % len(tasks))
                    logger.info('正在创建 [%d] 个进程来分别执行广告点击任务!' % len(tasks))
                    processes = []
                    for task in tasks:
                        p = Process(target=main, args=(task,))
                        processes.append(p)
                        p.start()
                    # 回收线程
                    for p in processes:
                        p.join()
            except json.decoder.JSONDecodeError:
                pass
        else:
            logger.info('任务系统出错，程序[sleep 30s]...')
            time.sleep(30)