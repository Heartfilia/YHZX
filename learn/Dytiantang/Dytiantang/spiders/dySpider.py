# -*- coding: utf-8 -*-
import scrapy

from Dytiantang.items import DytiantangItem


class DyspiderSpider(scrapy.Spider):
    name = 'dySpider'
    allowed_domains = ['dy2018.com']
    start_urls = ['http://www.dy2018.com/']

    def parse(self, response):
        sub_selector = response.xpath("//div[@class='co_content222']/ul/li")
        items = list()
        for sub in sub_selector:
            item = DytiantangItem()
            item['movieName'] = sub.xpath('./a/text()').extract_first()
            item['movieUrl'] = sub.xpath('./a/@href').extract_first()
            items.append(item)
        return items

