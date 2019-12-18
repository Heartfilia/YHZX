# !/usr/bin/env python
# -*- coding:utf-8 -*-
 
 
"""
图片(文件)下载,核心方法是 urllib.urlrequest 模块的 urlretrieve()方法
    urlretrieve(url, filename=None, reporthook=None, data=None)
        url: 文件url
        filename: 保存到本地时,使用的文件(路径)名称
        reporthook: 文件传输时的回调函数
        data: post提交到服务器的数据
    该方法返回一个二元元组("本地文件路径",<http.client.HTTPMessage对象>)
"""
 
import requests
import urllib.request
from lxml import etree
 
 
def crawl():
    url='http://www.ivsky.com/tupian/haiyangshijie/'
    headers={
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        }
 
    resp=requests.get(url,headers=headers)
 
    if resp.status_code==200:
        resp.encoding='UTF-8'
        html=etree.HTML(resp.text)
 
        img_titles=html.xpath('//ul[@class="ali"]//a/@title')
        img_urls=html.xpath('//ul[@class="ali"]//a/img/@src')
 
        data=zip(img_titles,img_urls)
        for img_title,img_url in data:
            print('开始下载{title}.jpg'.format(title=img_title))
            url2 = 'http:' + img_url
            result=urllib.request.urlretrieve(url2,
                                       filename='./data/图片下载爬虫/{title}.jpg'.format(title=img_title),
                                       reporthook=loading,
                                       data=None)
            print()

 
def loading(blocknum,blocksize,totalsize):
    """
    回调函数: 数据传输时自动调用
    blocknum: 已经传输的数据块数目
    blocksize: 每个数据块字节
    totalsize: 总字节
    """
    percent=int(100*blocknum*blocksize/totalsize)
    if percent>100:
        percent=100
    print("\r正在下载>>>{}%".format(percent), end="")
    import time
    time.sleep(0.1)
 
 
if __name__ == '__main__':
    crawl()
