#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/1 11:24
# @Author  : Lodge
import os
import re
import sys
import time
import logging
import urllib3
from logging import getLogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from helper import python_config, exe_js, tools


LOG = tools.log('Ali_ADkill')
urllib3.disable_warnings()   # disabled requests' verify warning
# ========================================================================================== #
LOG.info('测试信息...')


class AliAdKill(object):
    def __init__(self):
        self.base_url = 'https://www.aliexpress.com'
        self.chat_url = self.base_url + ''

        self.options = webdriver.ChromeOptions()

        self.options.add_argument("--no-sandbox")
        # self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        # self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{python_config.CHROME_PORT}")  # connect
        self.driver = webdriver.Chrome(options=self.options)

    def search_keyword(self, items):
        time.sleep(0.5)
        for item in items:
            now_keyword = item.get('keyword')
            print(f'准备查找的内容为:{now_keyword}')
            homepage_box = self.driver.find_element_by_xpath('//*[@id="search-key"]')
            homepage_box.clear()
            homepage_box.send_keys(now_keyword)
            time.sleep(0.3)
            homepage_box.send_keys(Keys.ENTER)

            self.judge_whether_in(now_keyword)  # 判断是否搜索成功
            self.find_items_at_page_one(items, now_keyword)

    def close_search_page_ad(self):
        # js方案，管你有没有广告，我都点一下，反正又不会报错
        time.sleep(1.3)
        try:
            self.driver.execute_script(exe_js.JS_CLICK_AD2)
        except Exception as e:
            try:
                self.driver.execute_script(exe_js.JS_CLICK_AD)
            except Exception as e:
                pass

    def go_to_login(self):
        # 下面所有的内容都是用密码登录的,以后会改成cookie登录
        sign_in = self.driver.find_element_by_xpath('//*[@id="nav-user-account"]/div/div/p[3]/a[2]')
        self.driver.execute_script("arguments[0].click();", sign_in)
        time.sleep(5)
        self.driver.switch_to.frame('alibaba-login-box')

        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="fm-login-id"]')))
        except Exception as e:
            # 登录的窗口还是没有在规定的等待时间出来
            print('登录窗口的内容还不可以进行下一步操作...')
        else:
            print('登陆的窗口是可以进行下一步操作了...')
            account = self.driver.find_element_by_xpath('//*[@id="fm-login-id"]')
            account.send_keys('KiokoeJanaee160@nineboy.vip')
            time.sleep(0.2)
            password = self.driver.find_element_by_xpath('//*[@id="fm-login-password"]')
            password.send_keys('ZhanShen001')
            time.sleep(0.3)
            password.send_keys(Keys.ENTER)
            self.driver.switch_to.parent_frame()

    def judge_whether_in(self, keyword):
        # 判断是否搜索成功
        self.close_search_page_ad()  # 第二次判断广告
        try:
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     '//*[@id="root"]/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div[2]/span/span/span'
                     )))
        except Exception as e:
            # 没有搜索到内容,那么就跳过还是咋回事的,那就提醒一下嘛
            print(f'关键字为:{keyword}好像没有搜到内容, 可人为检查一下有没有问题...')
        else:
            goods = self.do_judge_now_keyword()
            flag = re.findall(keyword, goods)
            if flag:
                print(f'关键字为:{keyword}搜到内容了,可以接下来的处理操作了')
            else:
                print(f'关键字为:{keyword}好像没有搜到内容, 检查一下有没有问题...')
                input('>>>')

    def judge_whether_homepage(self, items):
        self.driver.delete_all_cookies()
        self.go_to_login()            # 现在是用账号密码,以后改成用cookie

        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//*[@id="nav-user-account"]/div/div/div/p/b')
                    # (By.XPATH, '//*[@id="header-categories"]')  # 这条为测试数据，不作任何验证效果，主要是为了忽略异常
                )
            )
        except Exception as e:
            # 这个操作就是没有登录成功
            print('登录失败,可能出现了滑动条需要拖动,尝试拖动...')
            html = self.driver.page_source
            tools.save_html(html, 'login_page')
        else:
            # print('>>登录成功了...')
            self.close_search_page_ad()  # 第一次判断广告
            self.search_keyword(items)  # 去搜索商品,现在还没添加从接口拿数据,(1101测试数据为死数据)

    def scroll_page(self):
        # 一定要拉到最下面才能找到全部商品
        time.sleep(2)
        top_num = 521
        for i in range(12):
            time.sleep(0.2)
            self.driver.execute_script(exe_js.JS_SCROLL % (i * top_num, (i + 1) * top_num))
        time.sleep(0.2)
        self.driver.execute_script(exe_js.JS_LAST_SCROLL % (12 * 382))
        time.sleep(0.3)

    def go_to_homepage(self, items):
        self.driver.get(self.base_url)  # 去首页
        # 判断是否进入首页,包含等待处理以及cookie登录(别问我为啥不直接get到商品类,要稳1101还未登录操作)
        self.judge_whether_homepage(items)

    def judge_country_info(self):
        try:
            text_info = self.driver.find_element_by_xpath('/html/body/div[10]/div/div/div/p[1]').text
        except Exception as e:
            print('没有让你判断国家问题...')
        else:
            if text_info == 'Confirm your country settings':
                print('碰到了要让你选择是否切换到美国或者其它地方进行处理操作...')
            else:
                print('text::', text_info)

    @staticmethod
    def back_asin(link):
        num = re.findall(r'com/item/(\d+).html', link)
        if num:
            return num[0]
        else:
            return None

    def do_judge_now_keyword(self):
        try:
            goods = self.driver.find_element_by_xpath(
                '//*[@id="root"]/div/div/div[2]/div[2]/div/div[1]/div[1]/div/div[2]/span/span/span'
            ).text
        except Exception as e:
            return ''
        else:
            return goods

    def browse_page(self):
        window = self.driver.window_handles
        self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
        try:
            WebDriverWait(self.driver, 20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/div[1]')))
        except Exception as e:
            # 没有搜索到内容,那么就跳过还是咋回事的,那就提醒一下嘛
            print('还没有已经切换到了商品详情页...')
        else:
            page_source = self.driver.page_source
            tools.save_html(page_source, 'product_detail_page')
            self.scroll_page()
        finally:
            # 最后成不成功都要关闭页面了
            time.sleep(2)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(1)

    def find_items_at_page_one(self, items, now_keyword):
        items_two = dict()
        for item in items:
            item_name = item.get('keyword')
            item_data = item.get('data')
            item_asin_s = []
            for dt in item_data:
                print('item_data::', item_data)
                if dt.get('page', 1) > python_config.LIMIT_PAGE:  # 如果超过限制的页数的就不再加入判断
                    continue
                item_asin = dt.get('asin')
                if item_asin in python_config.OUR_PRODUCT_ID:   # 避免杀到自家的广告,先排除
                    continue
                item_asin_s.append(item_asin)
            items_two[item_name] = item_asin_s

        # 解析页面之前需要处理判断你的国家的问题
        self.judge_country_info()
        # 滑动页面到最下面,让页面元素加载全部出来
        self.scroll_page()
        # 这里就是解析页面的内容了

        asin_list = items_two.get(now_keyword, None)
        if asin_list:
            pg = 1
            while True:
                if not asin_list:
                    break   # 为空了退出
                if pg == python_config.LIMIT_PAGE:   # 页数超过了限定页数退出(不包含)
                    break
                print('当前页(方便排查页数的问题):', pg)
                print('asin_list(需要处理的数据,处理一个减少一个,最后看剩哪一个没有处理):', asin_list)
                if pg != 1:
                    self.scroll_page()
                try:
                    time.sleep(5)
                    links = self.driver.find_elements_by_xpath(
                        '//div[@class="item-title-wrap"]//a[@class="item-title"]')
                except Exception as e:
                    print('查找页面的内容链接失败...')
                    fail_html = self.driver.page_source
                    tools.save_html(fail_html, 'find_links_fail')
                else:
                    print('all_nums(判断程序是否采集到的有链接数据):', len(links))
                    for link in links:
                        asin = self.back_asin(link.get_property('href'))
                        time.sleep(0.8)
                        if asin and (asin in asin_list):
                            print(f'{asin}:找到了,点进去浏览看看...')
                            goal_link = self.driver.find_element_by_xpath(
                                f'//div[@data-product-id="{asin}"]/div[1]/div[1]/a[1]')
                            self.driver.execute_script("arguments[0].click();", goal_link)
                            self.browse_page()
                            asin_list.remove(asin)
                            LOG.info(f'处理的asin为:{asin}')
                finally:
                    try:
                        time.sleep(0.8)
                        self.driver.execute_script(exe_js.NEXT_PAGE)
                    except Exception as e:
                        print('已经没有下一页可以点了')
                    finally:
                        pg += 1

    @staticmethod
    def get_goal_items():
        # 这里要从api拿数据,现在模拟一些数据
        items = [
            {'keyword': 'coat women autumn',
             'data': [
                 {'asin': '32962923195', 'page': 1},
             ]},
        ]

        return items

    def run(self):
        items = self.get_goal_items()
        self.go_to_homepage(items)
        # self.driver.quit()


def main():
    ad_app = AliAdKill()
    # ad_app.run()


if __name__ == '__main__':
    main()
