#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/26 9:34
# @Author  : Lodge
import time
import random
import urllib3
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from helper import python_config, tools, exe_js

LOG = tools.log('yyw_pay_order_test')

urllib3.disable_warnings()   # disabled requests' verify warning
# 测试搜索商品相关流程
# ========================================================================================== #


class PayOrder(object):
    def __init__(self, driver):
        self.driver_version = driver
        LOG.info(f'现在测试主页订单购买以及支付任务开始,启动的驱动为:{self.driver_version}.')
        self.driver = tools.chose_driver(driver, LOG, True)
        # self.driver.maximize_window()
        if not self.driver:
            exit(0)

    def get_goods_info(self):
        goods_name = self.driver.find_element_by_xpath('//*[@id="proInfo_f"]/h1').text
        item_no = self.driver.find_element_by_xpath('//*[@id="proInfo"]/li[1]/em').text
        money = self.driver.find_element_by_xpath('//*[@id="cart_price"]').text
        quantity = self.driver.find_element_by_xpath('//*[@id="products_quantity"]').get_attribute('value')

        data = {
            'goods_name': goods_name,
            'item_no': item_no,
            'money': money,
            'quantity': quantity
        }
        return data

    def chose_random_category(self):
        n = random.randint(1, 5)
        category = self.driver.find_element_by_xpath(f'/html/body/div[4]/div/ul/li[{n}]/a/span')
        category.click()
        time.sleep(2)
        category_url = self.driver.current_url
        tools.save_screen_shot(self.driver, 'V', '1大类')
        goods_list = self.driver.find_elements_by_xpath('/html/body/div[6]/div[1]/div[2]/ul/li/a[1]')
        good_li = random.randint(1, len(goods_list))
        try:
            good = goods_list[good_li]
        except Exception as e:
            print(e)
            good = self.driver.find_element_by_xpath('/html/body/div[6]/div[1]/div[2]/ul/li/a[1]')

        good.click()
        time.sleep(2)
        goods_list_url = self.driver.current_url
        tools.save_screen_shot(self.driver, 'v', '2小类')
        self.driver.execute_script(exe_js.JS_LAST_SCROLL % 300)
        try:
            good_each = self.driver.find_elements_by_xpath('/html/body/div[6]/div[1]/div[3]/div[2]/ul/li/a[1]')
        except Exception as e:
            print(e)
            good_n = 1
            good_each = None
        else:
            try:
                good_n = random.randint(1, len(good_each))
            except Exception as e:
                print(e)
                good_n = 1
            print('当前点击的随机商品位数为:', good_n)

        if good_each:
            self.driver.execute_script("arguments[0].click();", good_each[good_n])
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            time.sleep(5)
            good_each_url = self.driver.current_url
            tools.save_screen_shot(self.driver, 'V', '3商品')
            goods_data = self.get_goods_info()

            data = {
                'driver': self.driver_version,
                'time': tools.get_now_time(),
                'category_url': category_url,
                'goods_list_url': goods_list_url,
                'each_good_url': good_each_url,
                'goods': goods_data
            }
            return data

    def pay_with_card(self):
        self.driver.find_element_by_id('createAccount').click()
        try:
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, 'countrySelector')))
        except Exception as e:
            print(e)
            LOG.error('还未能到达选择信用卡地区的位置界面...')
            tools.save_screen_shot(self.driver, 'e', 'payPal界面选择')
        else:
            time.sleep(10)
            self.driver.find_element_by_id('countrySelector').click()

        try:
            WebDriverWait(self.driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//*[@id="countrySelector"]/option[@value="US"]')))
        except Exception as e:
            print(e)
            LOG.error('未能找到美国的PayPal信息,退出后续流程')
            exit(0)
        else:
            time.sleep(2)
            us_btn = self.driver.find_element_by_xpath('//*[@id="countrySelector"]/option[@value="US"]')
            us_btn.click()
            # self.driver.execute_script("arguments[0].click();", us_btn)

        time.sleep(10)
        card_number = python_config.CREDIT_CARD.get('number')
        expire = python_config.CREDIT_CARD.get('expire')
        cvv = python_config.CREDIT_CARD.get('cvv')
        first_name = python_config.CREDIT_CARD.get('first_name')
        last_name = python_config.CREDIT_CARD.get('last_name')
        address1 = python_config.CREDIT_CARD.get('address1')
        postal = python_config.CREDIT_CARD.get('postal')
        city = python_config.CREDIT_CARD.get('city')

        try:
            card_number_input = self.driver.find_element_by_id('cc')
            expire_input = self.driver.find_element_by_id('expiry_value')
            csc_input = self.driver.find_element_by_id('cvv')
            first_name_input = self.driver.find_element_by_id('firstName')
            last_name_input = self.driver.find_element_by_id('lastName')
            address1_input = self.driver.find_element_by_id('billingLine1')
            postal_input = self.driver.find_element_by_id('billingPostalCode')
            city_input = self.driver.find_element_by_id('billingCity')
        except expected_conditions.NoSuchElementException:
            LOG.error('未能找到PayPal的相关页面元素设置...')
        else:
            try:
                card_number_input.send_keys(card_number)
                expire_input.send_keys(expire)
                csc_input.send_keys(cvv)
                first_name_input.send_keys(first_name)
                last_name_input.send_keys(last_name)
                address1_input.send_keys(address1)
                postal_input.send_keys(postal)
                city_input.send_keys(city)
            except Exception as e:
                print(e)
                LOG.error('当前页面不能选择到指定的元素,元素定位变动原因...(不同的国家,选择到其它国家的顺序不一致)')
                exit(0)

        # 还有的元素需要填写的放在了下面来处理
        try:
            time.sleep(2)
            self.driver.find_element_by_id('billingState').click()
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//*[@id="billingState"]/option[@value="string:CA"]').click()
            telephone = self.driver.find_element_by_id('telephone')
            telephone.send_keys(python_config.CREDIT_CARD.get('mobile'))
            email = self.driver.find_element_by_id('email')
            email.send_keys(python_config.CREDIT_CARD.get('email'))
        except Exception as e:
            print(e)
            tools.save_screen_shot(self.driver, 'e', '账单其它信息')

        time.sleep(3)
        tools.save_screen_shot(self.driver, 'o', 'PayPal信息填写')
        try:
            commit_btn = self.driver.find_element_by_id('guestSubmit')
        except expected_conditions.NoSuchElementException:
            commit_btn = self.driver.find_element_by_id('pomaSubmit')
        commit_btn.click()
        time.sleep(2)
        self.driver.execute_script(exe_js.JS_SCROLL % (0, 0))
        LOG.info(f'点击支付之后截图查看情况.')
        time.sleep(1)
        tools.save_screen_shot(self.driver, 'v', '点击支付之后')
        self.chose_pay_issue()

    def chose_pay_issue(self):
        xpt = '//*[@id="conversionContainer"]/div[2]/div[1]/form/xo-currency-conversion-lightbox-options/div/div/h1'
        try:
            WebDriverWait(self.driver, timeout=20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, xpt)))
        except Exception as e:
            LOG.error(f'不能定位到元素,支付未完成.')
        else:
            self.driver.execute_script(exe_js.JS_CHOSE_DOLLAR)
            try:
                self.driver.find_element_by_id('proceedButton')
            except Exception as e:
                print(e)
            LOG.info('支付成功')

    def go_to_cart(self):
        self.driver.get(python_config.CART_URL)
        now_money = self.driver.find_element_by_xpath('//*[@id="maindiv"]/div/div[4]/div[2]/p[1]/strong[2]').text
        LOG.info(f'当前购物车的金额为:{now_money}.')

        pay_pal = self.driver.find_element_by_id('bottomExpCheckout')
        pay_pal.click()

        try:
            WebDriverWait(self.driver, timeout=20).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     '//*[@id="root"]/div/main/div[5]/div/section/form/div/div/div/div[2]/div/div/div/div/button')))
        except Exception as e:
            print(e)
            LOG.error('当前状态不为已有PayPal账号,现在验证第二种情况..')
            tools.save_screen_shot(self.driver, 'e', '情况一')
            try:
                WebDriverWait(self.driver, timeout=20).until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, 'createAccount')))
            except Exception as e:
                print(e)
                LOG.error('当前状态错误位置,请查看错误截图')
                tools.save_screen_shot(self.driver, 'e', 'PayPal_错误')
            else:
                self.pay_with_card()
        else:
            input('卡在这里等待后续处理...')
            pass

    def add_to_cart(self):
        # self.driver.execute_script(exe_js.JS_ADD_TO_CART)
        try:
            add_ = self.driver.find_element_by_xpath('//div[@class="ruler_pic_left"]/div[@class="proBtnbuy ow"]/p[2]/a')
        except expected_conditions.NoSuchElementException:
            LOG.error('没有找到添加到购物车的按钮.')
        else:
            add_.click()
        time.sleep(5)

        try:
            WebDriverWait(self.driver, timeout=5).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//*[@id="resultShow"]')))
        except Exception as e:
            print(e)
            LOG.error(f'{self.driver_version}:没有获取到成功的状态.')
            status = False
        else:
            item_num = self.driver.find_element_by_id('topItemsNum').text.strip()
            print('item_num::', item_num)
            if item_num != '0':
                status = True
            else:
                status = False

        if status:
            self.go_to_cart()

    def login_in(self):
        self.driver.get(python_config.LOGIN_URL)
        reg_info = tools.register(self.driver, LOG, 'normal')
        tools.save_screen_shot(self.driver, 'o', '注册账号信息')
        time.sleep(2)
        if reg_info.get('status'):
            # tools.login(self.driver, LOG, reg_info=python_config.REG_INFO)
            tools.address(self.driver, LOG)
            tools.save_screen_shot(self.driver, 'o', '地址设置状态')
            self.driver.get(python_config.GOAL_URL)
            data = self.chose_random_category()
            print('data::', data)
            self.add_to_cart()
        else:
            LOG.error(f'注册账号失败,原因为:' + str(reg_info.get('error_info')))

    @tools.count_time
    def run(self):
        self.login_in()
        self.driver.quit()


def main(driver='Chrome'):
    app = PayOrder(driver)
    app.run()


if __name__ == '__main__':
    main()
