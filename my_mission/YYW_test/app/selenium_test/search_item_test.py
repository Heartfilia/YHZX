#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/23 10:04
# @Author  : Lodge
import time
import random
import urllib3
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from helper import python_config, tools, range_config

LOG = tools.log('yyw_search_item_test')

urllib3.disable_warnings()   # disabled requests' verify warning
# 测试搜索商品相关流程
# ========================================================================================== #


class YywSearchItem(object):
    def __init__(self, driver):
        self.driver_version = driver
        LOG.info(f'现在测试搜索商品信息状态任务开始,启动的驱动为:{self.driver_version}.')
        self.driver = tools.chose_driver(driver, LOG, True)
        # self.driver.maximize_window()
        if not self.driver:
            exit(0)

    def search_item(self):
        item = random.choice(range_config.RANDOM_GOODS_ITEM)
        flag = self.search(item)

        status = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'search_item': item,
            'status': flag
        }

        return status

    def search(self, item):
        try:
            input_box = self.driver.find_element_by_class_name('new_yyw_input')
            input_box.clear()
            input_box.send_keys(item)
            input_box.send_keys(Keys.ENTER)
        except expected_conditions.NoSuchElementException:
            flag = False
        else:
            flag = True
            time.sleep(5)
            tools.save_screen_shot(self.driver, 'V', f'搜索{item}关键字_')
            time.sleep(2)

        try:
            WebDriverWait(self.driver, timeout=30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '/html/body/div[7]/div[1]/div/div[2]/div/ul/li')))
        except Exception as e:
            print(e)
            LOG.error(f'{self.driver_version}:页面数据未搜索到..')
            flag = False

        return flag

    def search_item_id(self):
        item = random.choice(range_config.RANDOM_GOODS_ITEM)
        flag = self.search(item)

        status = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'search_id': item,
            'status': flag
        }

        return status

    def run(self):
        self.driver.get(python_config.GOAL_URL)
        search_info = self.search_item()
        LOG.info(f'{self.driver_version}:搜索关键字的详情为' + str(search_info))

        search_item_info = self.search_item_id()
        LOG.info(f'{self.driver_version}:搜索id的详情为' + str(search_item_info))


def main(driver='Chrome'):
    app = YywSearchItem(driver)
    app.run()


if __name__ == '__main__':
    main('Chrome')
