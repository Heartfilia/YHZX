#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/22 10:19
# @Author  : Lodge
import time
import urllib3

from helper import python_config, tools

LOG = tools.log('yyw_main_page_view')

urllib3.disable_warnings()   # disabled requests' verify warning
# 测试分类页数据加载是否正常
# ========================================================================================== #


class YywHomePage(object):
    def __init__(self, driver):
        self.driver_version = driver
        LOG.info(f'现在测试分类页状态任务开始,启动的驱动为:{self.driver_version}.')
        self.driver = tools.chose_driver(driver, LOG, True)
        # self.driver.maximize_window()
        if not self.driver:
            exit(0)

    def verify_whether_in(self, n):
        time.sleep(5)
        status = True
        try:
            if n <= 5:
                all_goods = self.driver.find_elements_by_xpath('/html/body/div[6]/div[1]/div[2]/ul/li')
            elif n in [6, 7]:
                all_goods = self.driver.find_elements_by_xpath('/html/body/div[6]/div[1]/div[3]/div[2]/ul/li')
            elif n == 8:
                all_goods = self.driver.find_elements_by_xpath('/html/body/div[6]/div[2]/ul/li')
            else:
                all_goods = []
            num = len(all_goods)
        except Exception as e:
            num = 0
            print(e)
            LOG.error('进入页面失败')
            status = False
        try:
            now_category = self.driver.find_element_by_xpath(f'/html/body/div[4]/div/ul/li[{n}]//span').text
        except Exception as e:
            print(e)
            now_category = '未找到'

        LOG.info(f'{now_category}:加载出来的商品数量有{num}个')
        log_status = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'status': status,
            'category': now_category,
            'goods_num': num
        }

        return log_status

    @tools.count_time
    def category_pages(self):
        """1,分类页是否正常打开"""
        t_in = time.time()
        self.driver.get(python_config.GOAL_URL)
        t_end = time.time()
        LOG.info(f'{self.driver_version}: 进入主页时间统计为{t_end - t_in:.2f}s')
        titles_nodes = self.driver.find_elements_by_xpath('/html/body/div[4]/div/ul/li')
        nodes_num = len(titles_nodes)
        tools.save_screen_shot(self.driver, 'V', f'{self.driver_version}_主页信息')
        time.sleep(3)
        for _ in range(1, nodes_num+1):
            title_node = self.driver.find_element_by_xpath(f'/html/body/div[4]/div/ul/li[{_}]')
            title_node.click()
            tools.save_screen_shot(self.driver, 'O', f'{self.driver_version}_点击节点{_}_')
            goods_info = self.verify_whether_in(_)
            LOG.info('当前页面的产品信息为:' + str(goods_info))
            time.sleep(3)

    def run(self):
        """开始做事情啦"""
        self.category_pages()
        tools.reset_status(self.driver, LOG)
        self.driver.quit()


def main(driver='Chrome'):
    # 可选驱动 Chrome  (后面几个没有添加驱动)Firefox  IE   Edge  Phantomjs(这个有问题)
    app = YywHomePage(driver)
    app.run()


if __name__ == '__main__':
    # main('Firefox')
    main()







