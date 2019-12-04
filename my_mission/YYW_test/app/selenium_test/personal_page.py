#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/2 10:45
# @Author  : Lodge
import time
import random
import urllib3
from selenium.webdriver.common.by import By
from helper import python_config, tools, range_config
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

LOG = tools.log('yyw_personal_page')

urllib3.disable_warnings()   # disabled requests' verify warning
# 测试分类页数据加载是否正常
# ========================================================================================== #


class PersonalHomePage(object):
    def __init__(self, driver):
        self.driver_version = driver
        LOG.info(f'现在测试个人中心状态任务开始,启动的驱动为:{self.driver_version}.')
        self.driver = tools.chose_driver(driver, LOG, True)
        # self.driver.maximize_window()
        if not self.driver:
            exit(0)

    # ===========================================================================

    def test_profile_change_profile(self):
        try:
            last_name = self.driver.find_element_by_id('lastname')
            first_name = self.driver.find_element_by_id('firstname')
            telephone = self.driver.find_element_by_id('telephone')
            save_one = self.driver.find_element_by_id('changB')
        except expected_conditions.NoSuchElementException:
            LOG.error('改变个人信息出错,可能是没有找到页面元素')
        else:
            try:
                test_name = random.choice(range_config.NAMES)
                last_name.clear()
                last_name.send_keys(test_name)
                first_name.clear()
                first_name.send_keys(random.choice(range_config.NAMES))
                telephone.clear()
                telephone.send_keys(range_config.PHONE)
                save_one.click()
            except Exception as e:
                LOG.error(f'错误类型为{str(e)}')
            else:
                time.sleep(2)
                sure = self.driver.find_element_by_xpath('//*[@id="_ButtonCancel_0"]')
                sure.click()
                LOG.info('名字信息更换成功,等待验证中...')
                self.driver.refresh()
                time.sleep(2)
                try:
                    last_name = self.driver.find_element_by_id('lastname')
                    last_name_text = last_name.get_attribute('value')
                    if last_name_text == test_name:
                        LOG.info('修改个人信息==>成功')
                    else:
                        LOG.info('修改个人信息==>失败')
                except Exception as e:
                    LOG.error(f'错误状态的原因是:{str(e)}')

    def test_profile_change_email(self):
        try:
            self.driver.get('https://my.yyw.com/accountManage.php')
            tag_1 = self.driver.find_element_by_id('tag1')
            email_password = self.driver.find_element_by_id('email_passwd')
            change_button = self.driver.find_element_by_id('changeE')
        except expected_conditions.NoSuchElementException:
            LOG.error('不能定位到 个人信息>>改变邮箱 的位置')
        else:
            tag_1.click()
            time.sleep(2)
            email_password.clear()
            email_password.send_keys(python_config.REG_INFO.get('password'))
            LOG.info('尝试修改邮箱中...')
            change_button.click()
            time.sleep(5)
            tips = self.driver.find_element_by_xpath('//*[@id="Message_undefined"]')
            sure = self.driver.find_element_by_xpath('//*[@id="_ButtonCancel_0"]')
            LOG.info(f'修改密码的状态原因为:{tips.text}')
            sure.click()

    def test_profile_change_password(self):
        try:
            self.driver.get('https://my.yyw.com/accountManage.php')
            tag_2 = self.driver.find_element_by_id('tag2')
            old_password = self.driver.find_element_by_id('old_pwd')
            new_pwd = self.driver.find_element_by_id('new_pwd')
            pwd1 = self.driver.find_element_by_id('pwd1')
            changeP = self.driver.find_element_by_id('changeP')
        except expected_conditions.NoSuchElementException:
            LOG.error('不能定位到 个人信息>>改变密码 的位置')
        else:
            tag_2.click()
            time.sleep(2)
            old_pwd = python_config.REG_INFO.get('password')
            old_password.clear()
            old_password.send_keys(old_pwd)
            LOG.info('尝试修改密码中...')
            # new_password = range_config.PASSWORD.get('hard')
            new_password = old_pwd
            new_pwd.clear()
            new_pwd.send_keys(new_password)
            pwd1.clear()
            pwd1.send_keys(new_password)
            time.sleep(2)
            changeP.click()
            time.sleep(1.5)
            tips = self.driver.find_element_by_xpath('//*[@id="Message_undefined"]')
            LOG.info(f'修改密码的状态原因为:{tips.text} 新的密码为:{new_password}')

    def test_profile(self):
        try:
            self.driver.get('https://my.yyw.com/accountManage.php')
        except Exception as e:
            print(e)
            exit(0)
        else:
            self.test_profile_change_profile()
            self.test_profile_change_email()
            self.test_profile_change_password()

    # ===========================================================================

    def test_address(self):
        try:
            self.driver.get('https://my.yyw.com/accountManage.php')
        except Exception as e:
            print(e)
            status = False
            exit(0)
        else:
            address_link = self.driver.find_element_by_id('addressManage.php')
            address_link.click()
            try:
                WebDriverWait(self.driver, timeout=10).until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, 'addAddress')))
            except Exception as e:
                print(e)
                LOG.error(f'{self.driver_version}:未能定位到元素或者地址信息设置已经到达上限.')
                status = False
            else:
                add_address = self.driver.find_element_by_id('addAddress')
                add_address.click()
                tools.address(self.driver, LOG)
                status = True

        data = {
            'driver': self.driver_version,
            'time': tools.get_now_time(),
            'address_status': status
        }

        LOG.info(f'设置地址信息的情况是:{str(data)}')

    # ===========================================================================

    def test_wish(self):
        try:
            self.driver.get('https://my.yyw.com/wishLists_dir.php')
        except Exception as e:
            print(e)
            status = False
            exit(0)
        else:
            num_list = self.driver.find_elements_by_xpath('//*[@id="container"]/div[2]/div[3]/div/div[2]/ul/li')
            num_l = len(num_list)
            if num_l > 2:
                LOG.info('当前已经存在了愿望单,不用再添加了.')
            else:
                create_list = self.driver.find_element_by_id('creatItemBtn')
                create_list.click()
                time.sleep(3)
                wish_name = self.driver.find_element_by_id('name')
                wish_description = self.driver.find_element_by_id('itemDescription')
                time.sleep(2)
                wish_name.clear()
                wish_name.send_keys(random.choice(range_config.NAMES) + 'wishes')
                wish_description.clear()
                wish_description.send_keys('this is a test description!')
                sure = self.driver.find_element_by_id('creatBtn')
                sure.click()

            data = self.test_wish_add_goods()
            self.test_wish_check_in(data)

    def test_wish_add_goods(self):
        self.driver.get('https://www.yyw.com/product/Polyester-Sexy-Harness-Bra_p66198.html')  # 去这个固定商品位置
        item_no = self.driver.find_element_by_xpath('//*[@id="proInfo"]/li[1]/em')
        price = self.driver.find_element_by_xpath('//*[@id="cart_price"]/span')
        item_name = self.driver.find_element_by_xpath('//*[@id="proInfo_f"]/h1')

        add_wish = self.driver.find_element_by_id('addWishListBtn')
        add_wish.click()
        time.sleep(2)

        add_now_js = 'document.querySelector("#wish-dir-button").click()'
        self.driver.execute_script(add_now_js)
        data = {
            'item_name': item_name.text.strip(),
            'item_no': item_no.text.strip(),
            'item_price': price.text.strip().replace(' ', '')
        }
        LOG.info(f'添加到愿望单成功,{str(data)},等待下一步验证.')

        return data

    def test_wish_check_in(self, data):
        self.driver.get('https://my.yyw.com/wishLists_dir.php')
        wish_info = self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/div[3]/div/div[2]/ul/li[1]/p[3]')
        wish_info.click()

        time.sleep(10)
        item_no_price = self.driver.find_element_by_xpath('//*[@id="mywishlistForm"]/div[3]/div[2]/ul/li[3]/dl/dd[1]')

        item_no_price_info = item_no_price.text.replace(' ', '')

        if data.get('item_no') in item_no_price_info and data.get('item_price') in item_no_price_info:
            LOG.info(f'指定商品添加==>成功')
        else:
            LOG.error(f'指定商品添加==>失败')

        time.sleep(2)
        self.driver.execute_script(
            'document.querySelector("#mywishlistForm > div.be2c > div:nth-child(1) > span.fl > input").click()')   # 全选
        time.sleep(0.5)
        rm_js = 'document.querySelector("#mywishlistForm > div.be2c > div:nth-child(1) > img.fl.ml10.removeWishList.hand").click()'
        self.driver.execute_script(rm_js)
        time.sleep(1)
        from selenium.webdriver.common.alert import Alert
        alert = Alert(self.driver)
        alert.accept()
        time.sleep(3)
        LOG.info('删除指定商品成功.')
        del alert

    # ===========================================================================
    def test_tickets(self):
        self.driver.get('https://my.yyw.com/app/ticket.php')
        search_btn = self.driver.find_element_by_id('submitBtn')
        search_btn.click()
        try:
            time.sleep(3)
            num = self.driver.find_element_by_xpath('//span[@class="page1Num"]')
        except expected_conditions.NoSuchElementException:
            LOG.error('tickets 分类查找数据失败.')
        else:
            num = num.text
            LOG.info(f'tickets 查找到的数据为 {num}条.')

    # ============================================================================

    def test_orders(self):
        self.driver.get('https://my.yyw.com/app/myorder.php')
        try:
            search_btn = self.driver.find_element_by_id('submitbtn')
            search_btn.click()
            time.sleep(2)
            num = self.driver.find_element_by_xpath('//span[@class="page1Num"]')
        except Exception as e:
            print(e)
            LOG.error(f'个人订单信息查询==>失败')
        else:
            LOG.info(f'Orders 查到了的数据为 {num.text}条')

    # ============================================================================

    def test_finance(self):
        self.driver.get('https://my.yyw.com/financeManage.php')
        try:
            search_btn = self.driver.find_element_by_id('Submitbtn')
            search_btn.click()
            time.sleep(2)
            num = self.driver.find_element_by_xpath('//span[@class="page1Num"]')
            account_credit = self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/div[3]/div/p/em')
        except Exception as e:
            print(e)
            LOG.error('金融信息管理查询==>失败')
        else:
            LOG.info(f'Finance 查询到的数据条数为:{num.text}条, 账户信用为:{account_credit.text}.')

    # ============================================================================

    def test_arrive(self):
        self.driver.get('https://my.yyw.com/arriveManage.php')
        try:
            search_btn = self.driver.find_element_by_id('searchbtn')
            search_btn.click()
            time.sleep(2)
            num = self.driver.find_element_by_xpath('//span[@class="page1Num"]')
        except Exception as e:
            print(e)
            LOG.error('邮寄位置管理查询==>失败')
        else:
            LOG.info(f'Arrive 查询到的数据条数为:{num.text}条.')

    # ============================================================================

    def test_coupons(self):
        self.driver.get('https://my.yyw.com/couponManage.php')
        try:
            enter_code = self.driver.find_element_by_id('requestcode')
            search_btn = self.driver.find_element_by_id('submitbtn')
        except Exception as e:
            print(e)
            LOG.error('优惠券管理查询==>失败')
        else:
            enter_code.send_keys(random.sample(range_config.Digit_List, 8))
            time.sleep(0.5)
            search_btn.click()
            time.sleep(3)
            from selenium.webdriver.common.alert import Alert
            alert = Alert(self.driver)
            info = alert.text.strip()
            alert.accept()
            time.sleep(1)
            LOG.info(f'查询优惠券功能正常,本次随机查询的数据为:{info}.')
            del alert

    # ============================================================================

    def test_support(self):
        self.driver.get('https://my.yyw.com/Submit_ticket.php')
        try:
            order_id = self.driver.find_element_by_id('orders_id')
            subject = self.driver.find_element_by_id('message_title')
            message = self.driver.find_element_by_id('message_msg')
            submit = self.driver.find_element_by_id('autoSub')
        except expected_conditions.NoSuchElementException:
            LOG.error(f'support 功能里面查找页面元素==>错误.')
        else:
            order_id_random = random.sample(range_config.Digit_List, 8)
            order_id.send_keys(order_id_random)
            subject.send_keys('this is an inner test file')
            message.send_keys('this is an inner test file')
            time.sleep(2)
            submit.click()

            try:
                time.sleep(2)
                message_msg = self.driver.find_element_by_id('message_msg')
                submit_msg = self.driver.find_element_by_name('Submit_reply')
            except expected_conditions.NoSuchElementException:
                LOG.info('这个页面继续留数据出错.')
            else:
                time.sleep(2)
                message_msg.send_keys('this is an inner test file')
                time.sleep(0.5)
                submit_msg.click()

            try:
                time.sleep(5)
                all_file = self.driver.find_elements_by_xpath('//div[@id="ticket_reply"]/p')
            except Exception as e:
                print(e)
                LOG.error('不能定位到反馈支持的相关回馈信息.')
            else:
                if len(all_file) > 0:
                    LOG.info(f'support 当前有{len(all_file)}条主题信息.')
                else:
                    LOG.info(f'留言貌似没有成功,需要留意.')

    # ============================================================================

    def increase_fault_tolerance(self):
        """这个函数只是为了处理容错的"""
        try:
            self.test_profile()
        except Exception as e:
            print(e)
            LOG.error('个人信息设置处理==>错误')

        try:
            self.test_address()
        except Exception as e:
            print(e)
            LOG.error('地址管理设置处理==>错误')

        try:
            self.test_wish()
        except Exception as e:
            print(e)
            LOG.error('个人心愿单情况处理==>错误')

        try:
            self.test_tickets()
        except Exception as e:
            print(e)
            LOG.error('票据查询处理==>错误')

        try:
            self.test_orders()
        except Exception as e:
            print(e)
            LOG.error('订单查询相关处理==>错误')

        try:
            self.test_finance()
        except Exception as e:
            print(e)
            LOG.error('个人金融相关处理==>错误')

        try:
            self.test_arrive()
        except Exception as e:
            print(e)
            LOG.error('物流信息相关处理==>错误')

        try:
            self.test_coupons()
        except Exception as e:
            print(e)
            LOG.error('优惠券相关处理==>错误')

        try:
            self.test_support()
        except Exception as e:
            print(e)
            LOG.error('辅助支持相关处理==>错误')

    @tools.count_time
    def run(self):
        self.driver.get('https://my.yyw.com/login.php')
        tools.login(self.driver, LOG, python_config.REG_INFO)
        self.increase_fault_tolerance()
        self.driver.quit()


def main(driver='Chrome'):
    app = PersonalHomePage(driver)
    app.run()


if __name__ == '__main__':
    main()
