import scrapy
from helper import tools


@tools.count_time
def ff():
    print('pass')


ff()
