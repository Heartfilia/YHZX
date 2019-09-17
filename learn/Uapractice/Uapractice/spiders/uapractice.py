# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class UapracticeSpider(scrapy.Spider):
    name = 'uapractice'
    allowed_domains = ['exercise.kingname.info']
    start_urls = ['http://exercise.kingname.info/exercise_middleware_ua/']

    def parse(self, response):
        base_url = 'http://exercise.kingname.info/exercise_middleware_ua/'
        for i in range(1, 10):
            url = base_url + f'{i}'
            yield Request(
                url,
                callback=self.info
            )

    def info(self, response):
        print(f'{response.body.decode("utf-8")}')
