# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time


class DytiantangPipeline(object):
    def process_item(self, item, spider):
        now = time.strftime('%Y-%m-%d', time.localtime())
        filename = 'dy' + now + '.txt'
        with open(filename, 'a') as fp:
            fp.write(item['movieName'] + '\n' + 'https://www.dy2018.com' + item['movieUrl'] + '\n\n')

        return item
