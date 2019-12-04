#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/29 11:25
# @Author  : Lodge
import os
import time
import requests
from selenium import webdriver
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from helper.tools import log
base_url = 'https://developers.google.com/speed/pagespeed/insights/?'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

urls = ['https://m.beads.us', 'https://www.beads.us']

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')

# 这里必须要外网才可以 我是本地 开了VPN, 要是本来就可以的话 就不用设置这个了                    <======
options.add_argument('--proxy-server=http://127.0.0.1:1080')

driver = webdriver.Chrome(options=options)

RECEIVERS = '陈镇泉;林伟鸿;全建誉'

LOG = log('google_页面分析检测')


def send_rtx_info(msg, receivers=RECEIVERS):
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def save_html(name):
    today_tic = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    save_info_dir = os.path.join(BASE_DIR, 'html', f'{name}{today_tic}.html')
    time.sleep(3)
    page_source = driver.page_source
    try:
        with open(save_info_dir, 'w', encoding='utf-8') as f:
            f.write(page_source)
    except Exception as e:
        print(e)
        LOG.error('网络连接失败,不能正常检测数据')


def go_to_test(url, goal, order):
    try:
        driver.get(url)
        WebDriverWait(driver, timeout=30).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//span[@class="lh-audit-group__title"]')))
    except Exception as e:
        print(e)
        save_html(f'{order}页面未找到')
        # driver.save_screenshot(fr'./img/{goal}.png')
        return False
    else:
        time.sleep(10)
        try:
            score = driver.find_elements_by_xpath('//div[@class="lh-gauge__percentage"]')[order].text
        except Exception as e:
            score = '网络连接超时,需要重新查看检测脚本'
        else:
            save_html(f'{order}检测情况')
            # driver.save_screenshot(fr'{goal}检测情况.png')

        if score.isdigit() and int(score) < 90:
            msg = f'== google 页面速度分析 ==\n评测网站: {goal}\n本次分数: {score}\n提醒标准: 分数低于90分触发\n查看连接: {url}'
            LOG.info(f'{goal}的评测分数为:{score}')
            send_rtx_info(msg)
        elif score.isdigit() and int(score) >= 90:
            LOG.info(f'{goal}的评测分数为:{score}')
        else:
            LOG.error(f'{goal}检测时候出现的问题为:{score}')
            msg = f'== google 页面速度分析 ==\n评测网站: {goal}\n状态原因: {score}'
            send_rtx_info(msg)


def run():
    for url in urls:
        test_url = urlencode({"url": url})
        order = urls.index(url)
        if urls.index(url) == 0:
            goal_url = base_url + f'{test_url}&tab=mobile'
        else:
            goal_url = base_url + f'{test_url}&tab=desktop'

        go_to_test(goal_url, url, order)

    driver.quit()


if __name__ == '__main__':
    run()
