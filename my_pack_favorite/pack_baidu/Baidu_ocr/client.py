#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 9:47
# @Author  : Lodge
import re, os
import requests

from aip.ocr import AipOcr   # 这里根据情况需要修改位置

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
# 上面三个直接在百度开发者平台可以看见


def main():
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = dict()
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"

    with open(f'{BASE_DIR}\\base.png', 'rb') as fp:
        image = fp.read()
        # 上面这一条是打开需要识别的图片

    return_info = client.basicAccurate(image, options)     # client 后面的就是功能:当前功能为 通用文字识别(高精度版)

    # print(return_info)
    f_key = ''
    for text in return_info.get('words_result'):
        f_key += text.get('words')

    last_one = re.findall(r'([a-zA-Z0-9_]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_]+)+', f_key)

    # print(f_key)
    if last_one:
        print('email', last_one[0])
        return last_one[0]
    else:
        return None


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ProxyError:
        print('网络连接超时...')
