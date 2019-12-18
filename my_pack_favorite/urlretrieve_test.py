# !/usr/bin/env python
# -*- coding:utf-8 -*-
 
 
"""
ͼƬ(�ļ�)����,���ķ����� urllib.urlrequest ģ��� urlretrieve()����
    urlretrieve(url, filename=None, reporthook=None, data=None)
        url: �ļ�url
        filename: ���浽����ʱ,ʹ�õ��ļ�(·��)����
        reporthook: �ļ�����ʱ�Ļص�����
        data: post�ύ��������������
    �÷�������һ����ԪԪ��("�����ļ�·��",<http.client.HTTPMessage����>)
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
            print('��ʼ����{title}.jpg'.format(title=img_title))
            url2 = 'http:' + img_url
            result=urllib.request.urlretrieve(url2,
                                       filename='./data/ͼƬ��������/{title}.jpg'.format(title=img_title),
                                       reporthook=loading,
                                       data=None)
            print()

 
def loading(blocknum,blocksize,totalsize):
    """
    �ص�����: ���ݴ���ʱ�Զ�����
    blocknum: �Ѿ���������ݿ���Ŀ
    blocksize: ÿ�����ݿ��ֽ�
    totalsize: ���ֽ�
    """
    percent=int(100*blocknum*blocksize/totalsize)
    if percent>100:
        percent=100
    print("\r��������>>>{}%".format(percent), end="")
    import time
    time.sleep(0.1)
 
 
if __name__ == '__main__':
    crawl()
