# -*- coding: utf-8 -*-
import scrapy


class Job51Spider(scrapy.Spider):
    name = 'job51'
    allowed_domains = [''ehire.51job.com'']
    start_urls = ['http://'ehire.51job.com'/']

    def parse(self, response):
        pass
