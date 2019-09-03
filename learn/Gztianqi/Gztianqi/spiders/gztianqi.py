# -*- coding: utf-8 -*-
import scrapy

from Gztianqi.items import GztianqiItem


class GztianqiSpider(scrapy.Spider):
    name = 'gztianqi'
    allowed_domains = ['tianqi.com']
    start_urls = ['http://www.tianqi.com/guangzhou/30/']

    def parse(self, response):
        all_day = response.xpath('//div[@class="box_day"]/div')
        items = list()
        for each_day in all_day:
            item = GztianqiItem()
            item['cityDate'] = each_day.xpath('./a/h3/b/text() | ./h3/b/text()').extract_first()
            item['cityDay'] = each_day.xpath('./a/h3/em/text() | ./a/h3/text() | ./h3/text()').extract()[-1].strip()
            item['img'] = each_day.xpath('./a/ul/li[1]/img/@src | ./ul/li[1]/img/@src').extract_first()
            item['temperature'] = ''.join(each_day.xpath('./a/ul/li[2]//text() | ./ul/li[2]//text()').extract())
            item['wind'] = each_day.xpath('./a/ul/li[3]/text() | ./ul/li[3]/text()').extract_first()
            items.append(item)
        return items
