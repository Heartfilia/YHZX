#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 9:47
# @Author  : Lodge
import re
import os
import requests

from helper.Baidu_ocr.aip.ocr import AipOcr   # 这里根据情况需要修改位置

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 这个是定位到当前位置的
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上个位置

APP_ID = '17352180'
API_KEY = 'nXwvTLPhZll9jpRRYFf8E2ZM'
SECRET_KEY = '15FkboqNk0Kbrsm8vShCtZbu3V0GiwbG'
# 上面三个直接在百度开发者平台可以看见


def main_ocr():
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = dict()
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"

    with open(f'{BASE_DIR}\\fonts\\plt.png', 'rb') as fp:
        image = fp.read()
        # 上面这一条是打开需要识别的图片 位置看情况可能要修改

    return_info = client.basicGeneral(image, options)     # client 后面的就是功能:当前功能为 通用文字识别(高精度版)
    # return_info = client.handwriting(image, options)     # client 后面的就是功能:当前功能为 通用文字识别(高精度版)

    # print(return_info)
    f_key = ''
    for text in return_info.get('words_result'):
        f_key += text.get('words')

    print(f_key)
    return f_key


if __name__ == '__main__':
    try:
        main_ocr()
    except requests.exceptions.ProxyError:
        print('网络连接超时...')
