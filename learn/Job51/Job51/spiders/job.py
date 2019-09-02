# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class JobSpider(CrawlSpider):
    name = 'job'
    allowed_domains = ['search.51job.com']
    start_urls = ['https://search.51job.com']

    _pos_ = ['python', 'php']

    # for pos in _pos_:
    rules = (
        # Rule(LinkExtractor(allow=r'https://jobs.51job.com/all/co\d{7}.html'), callback='parse_item'),
        Rule(LinkExtractor(allow=rf'https://search.51job.com/list/030200,000000,0000,00,9,99,python,2,\d+.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='), callback='parse_item'),
        Rule(LinkExtractor(allow=rf'https://search.51job.com/list/030200,000000,0000,00,9,99,python,2,\d+.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='), follow=True),
    )

    def parse_item(self, response):
        item = dict()
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        # item['name'] = response.xpath('//div[@class="in img_on"]/h1/@title').extract_first()
        # print(item)
        item['ifo'] = re.findall('<span class="t4">.*？万/月</span>', response.body.decode())[0]
        print('item:', item)
        return item
