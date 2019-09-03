# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class Job51Pipeline(object):
    def process_item(self, item, spider):
        posName = item['posName']
        if posName:
            comName = item['comName']
            live = item['live']
            publishTime = item['publishTime']
            nowPG = item['nowPG']

            with open('job.txt', 'a') as f:
                f.write(f'{posName}:::{comName}:{live}:{publishTime}::{nowPG} \n')

        return item
