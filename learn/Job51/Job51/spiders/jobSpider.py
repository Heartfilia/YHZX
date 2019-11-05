# -*- coding: utf-8 -*-
import re

import scrapy
from urllib.parse import urlencode

from scrapy import Request

from Job51.items import Job51Item


class JobspiderSpider(scrapy.Spider):
    name = 'jobSpider'
    allowed_domains = ['51job.com']
    start_urls = ['http://search.51job.com/']

    def parse(self, response):
        _POS_ = self.get_pos()
        for pos in _POS_:
            base_url = f"https://search.51job.com/list/030200,000000,0000,00,9,99,{pos},2,1.html?"
            data = {
                "lang": "c",
                "postchannel": "0000",
                "workyear": "99",
                "cotype": "99",
                "degreefrom": "99",
                "jobterm": "99",
                "companysize": "99",
                "ord_field": "0",
                "dibiaoid": "0",
            }
            result = urlencode(data)
            url = base_url + result
            yield Request(
                url,
                callback=self.sure_page,
                dont_filter=True,
                meta={'result': result, 'pos': pos}
            )

    def sure_page(self, response):
        all_num = int(re.findall(r'共(\d+)条职位', response.body.decode(response.encoding))[0])
        result = response.meta['result']
        pos = response.meta['pos']
        if all_num != 0:
            page = all_num // 40
            for pg in range(1, page+1):
                base_url = f"https://search.51job.com/list/030200,000000,0000,00,9,99,{pos},2,{pg}.html?"
                url = base_url + result
                yield Request(
                    url,
                    callback=self.do_info,
                    dont_filter=True,
                    meta={'pg': pg}
                )

    def do_info(self, response):
        main_node = response.xpath('//div[@id="resultList"]/div')
        items = list()
        for node in main_node[2:]:
            item = Job51Item()
            item['posName'] = node.xpath('./p/span/a/@title').get()
            item['comName'] = node.xpath('./span[1]/a/@title').get()
            item['live'] = node.xpath('./span[2]/text()').get()
            item['publishTime'] = node.xpath('./span[4]/text()').get()
            item['nowPG'] = response.meta['pg']

            items.append(item)
        return items

    @staticmethod
    def get_pos():
        pos = ['python', 'php']
        for i in pos:
            yield i
