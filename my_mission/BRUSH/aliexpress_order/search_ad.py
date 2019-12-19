#必须登录后，才能持续访问。

import random
import re
from multiprocessing import Process
import time
from user_agent import generate_user_agent
from lxml import etree
import requests
import sys
import json
from mytools.tools import logger, get, post, get_oxylabs_proxy

logger = logger('search_ad')
class AliexpressAdSearcher:

    def __init__(self, id, key_words):
        self.id = id
        self.key_words = key_words
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
        self.proxies= get_oxylabs_proxy('us', _city=None, _session=random.random())
        # self.proxies = {'https':'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(200000, 500000)}
        self.base_search_url = 'https://www.aliexpress.com/wholesale?SearchText=beads&page='
        self.AD_data = []
        # self.session = requests.session()

    def run(self):
        for i in range(1,5):
            url = self.base_search_url + self.key_words + "&page=" + str(i)
            logger.info('[%s] [%s] 正在搜索第 [%d] 页中的广告...' % (self.id, self.key_words, i))
            html = self.get_search_list_page(url)
            if html:
                num = self.parse_search_list_page(html, i)
                # print('第%d页中广告个数为%d' % (i, num))
                logger.info('[%s] [%s] 第 [%d] 页中广告个数为 [%d]' % (self.id, self.key_words, i, num))
                if num == 0:
                    logger.info('[%s] [%s] 第 [%d] 页未搜索到广告，停止搜索！' % (self.id, self.key_words, i))
                    break
            else:
                logger.info('[%s] [%s] 跳转到登录页，停止搜索！' % (self.id, self.key_words))
                break
        logger.info('[%s] [%s] 总共搜索到的广告个数：[%d]' % (self.id, self.key_words, len(self.AD_data)))
        print(json.dumps(self.AD_data))
        ad_data = {
            'data':{
                "id": self.id,
                "status": "1",
                "attack_result": json.dumps(self.AD_data)
            }
        }
        self.update_ad_data(json.dumps(ad_data))

    def get_search_list_page(self,url):
        resp = requests.get(url, headers=self.headers, proxies=self.proxies)
        # with open('xxxx.html', 'w', encoding='utf-8') as f:
        #     f.write(resp.text)
        if "<body data-spm='buyerloginandregister'>" in resp.text:
            # print('跳转到登录页，停止搜索！')
            return None
        return resp.text

    def parse_search_list_page(self,html,page):
        parseHtml = etree.HTML(html)
        lis = parseHtml.xpath('//ul[@id="hs-below-list-items"]/li')
        # print(len(lis))
        num = 0
        for li in lis:
            if li.xpath('.//i[@title="AD"]'):
                brand_name = li.xpath('//div[@class="store-name util-clearfix"]/a/text()')[0].strip()
                attack_url ='https:'+ li.xpath('.//h3/a/@href')[0]
                asin = re.search(r'.*?/item/.*?/(\d+).html', attack_url).group(1)
                # target_status = '1'
                # attack_clicks = '0'
                # log = '搜索到该广告，未进行点击'
                page = str(page)
                rank = str(lis.index(li) + 1)
                item = {
                    'brand_name': brand_name,
                    'attack_url': attack_url,
                    'asin': asin,
                    'target_status': '1',
                    'attack_clicks': '0',
                    'log': '搜索到该广告，未进行点击',
                    'page': page,
                    'rank': rank
                }
                # print(item)
                self.AD_data.append(item)
                num += 1
        return  num
        # print('广告个数：',len(self.AD_urls))
        # self.visit_ad_page()

    def update_ad_data(self, data):
        # url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=modifyAliexpressAdvertisingAttack'
        url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=modifyAliexpressAdvertisingAttack'
        resp = post(requests.session(), url=url, post_data=data)
        print("result", resp.text)
        if resp:
            if resp.json().get('msg') == "OK":
                logger.info('[%s] [%s] 搜索到的广告数据入库成功！' % (self.id, self.key_words))
            else:
                logger.info('[%s] [%s] 搜索到的广告数据入库失败！' % (self.id, self.key_words))

def main(id, key_words):
    spider = AliexpressAdSearcher(id, key_words)
    spider.run()

if __name__ == '__main__':
    while True:
        #测试地址
        url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=getAliexpressAdvertisingAttack'
        resp = get(requests.session(), url=url)
        if resp:
            try:
                if resp.json() == []:
                    logger.info('任务系统未获取到当前时间的任务，程序[sleep 10m]...')
                    time.sleep(60 * 10)
                else:
                    task_infos = resp.json()
                    all_tasks = []
                    for task in task_infos['data']:
                        id = task.get('id')
                        key_words = task.get("key_word")
                        all_tasks.append((id, key_words))
                    logger.info('成功获取到 [%d] 条待执行的广告搜索任务！' % len(all_tasks))
                    logger.info('正在创建 [%d] 个进程来分别执行广告搜索任务!' % len(all_tasks))
                    processes = []
                    for item in all_tasks:
                        p = Process(target=main, args=item)
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
