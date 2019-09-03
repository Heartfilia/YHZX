# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import time


class GztianqiPipeline(object):
    def process_item(self, item, spider):
        today = time.strftime('%Y%m%d', time.localtime())
        filename = today + '.txt'
        with open(filename, 'a') as fp:
            fp.write(
                f"{item['cityDate']}:{item['cityDay']} \n img_url:{item['img']} \n {item['temperature']} \n {item['wind']} \n")
        return item
