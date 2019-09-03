# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GztianqiItem(scrapy.Item):
    # define the fields for your item here like:
    cityDate = scrapy.Field()
    cityDay = scrapy.Field()
    img = scrapy.Field()
    temperature = scrapy.Field()
    wind = scrapy.Field()
