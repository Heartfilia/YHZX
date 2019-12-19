import os
import sys
import random
import re
import json
import threading
import time
import datetime
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException,TimeoutException,NoSuchFrameException,WebDriverException
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ProxyError
from mytools.tools import get_oxylabs_proxy, get, post, create_proxyauth_extension, logger, load_json, save_json
from config import City_List

logger = logger('place_order_new_US')
class AliexpressOrderSpider():

    def __init__(self,task_infos,task_id):
        self.task_infos = task_infos
        self.task_id = task_id
        # register_city = self.task_infos[str(self.task_id)]["account"].get("register_city")
        # register_city_list = register_city.split()
        # if len(register_city_list) > 1:
        #     register_city = '_'.join(register_city_list)
        # proxies = get_oxylabs_proxy('us', _city=register_city, _session=random.random())
        # getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        # if getIpInfo:
        #     self.proxy = proxies['https']
        #     print('get ip!')
        # else:
        #     self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        #     print('get ip failed!')
        self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="%s"' % json.loads(self.task_infos[str(self.task_id)]['account']['header'])['user-agent'] )
        self.options.add_extension(proxyauth_plugin_path)
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        #headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        #设置不加载图片
        self.options.add_experimental_option('prefs',{"profile.managed_default_content_settings.images":2})
        self.driver = webdriver.Chrome(options=self.options)
        self.target_id = self.task_infos[str(self.task_id)]["asin"]["asin"]
        #self.good_detail_urls属性，用于绑定目标商品所在列表页的所有商品的详情链接
        self.good_detail_urls = None
        #self.target_good_detail_url属性，用于绑定目标商品的详情链接
        self.target_good_detail_url = None

    # 主实例方法，负责调用其他实例方法，完成下单的整个流程
    def run(self):
        try:
            self.driver.get('http://www.aliexpress.com/')
            self.driver.execute_script(
                '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
            self.driver.execute_script('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            self.driver.execute_script('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            self.driver.execute_script(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            #过滤弹窗
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@class="register-btn"]/a'))
            )
            #点击登录
            self.driver.find_element_by_xpath('//span[@class="register-btn"]/a').click()
            # WebDriverWait(self.driver, 40).until(
            #     EC.frame_to_be_available_and_switch_to_it
            # )
            time.sleep(10)
            #切换到子iframe
            self.driver.switch_to.frame('alibaba-login-box')
            #输入登录信息
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="fm-login-id"]'))
            )
            time.sleep(random.uniform(4, 8))
            self.driver.find_element_by_id('fm-login-id').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_email"])
            time.sleep(random.uniform(4, 8))
            self.driver.find_element_by_id('fm-login-password').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_password"])
            time.sleep(random.uniform(4, 8))
            # self.driver.find_element_by_id('fm-login-submit').click()
            js = 'document.getElementById("fm-login-submit").click();'
            self.driver.execute_script(js)
            time.sleep(1)
            # 此处判断登录过程中是否有滑块验证码，有则终止程序
            if 'display: block' in self.driver.find_element_by_id('fm-login-checkcode-title').get_attribute('style'):
                logger.info('登录时发现滑块验证码，程序退出！')
                self.driver.quit()
                sys.exit(0)
            #弹窗处理
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass

            if self.driver.current_url == 'https://www.aliexpress.com/':
                #插入账号登录日志
                login_log_data = {
                    'data':{
                        "account_id":self.task_infos[str(self.task_id)]["account"]["account_id"],
                        "header":self.task_infos[str(self.task_id)]['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies()),
                        "login_status": "1",
                        "note": "登录成功"
                    }
                }
                self.insert_account_login_log(json.dumps(login_log_data))
                #当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
                login_success_info_data = {
                    'data':{
                        "account_id": self.task_infos[str(self.task_id)]["account"]["account_id"],
                        "header": self.task_infos[str(self.task_id)]['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies())
                    }
                }
                self.update_account_login_success_info(json.dumps(login_success_info_data))
            elif 'passport.aliexpress.com' in self.driver.current_url:
                logger.info('登录后发现验证码，账户已被封！')
                #账户被封，也更新刷单状态
                brushing_data = {
                    str(self.task_id): {
                        "task_id": self.task_id,
                        "status": 10,
                    }
                }
                self.update_brushing_status(json.dumps(brushing_data))
                self.driver.quit()
                logger.info('程序退出！')
                sys.exit(0)
            #先检查cofirm_pay_file文件夹下，是否存在一个taskid_xx.txt文件，xx为本次任务id。
            # 若存在，则进入个人订单中心，获取订单号和定价总价等信息，更新刷单状态。并删除该文件。
            #若不存在，则正常走流程。
            confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
            confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            if os.path.exists(confirm_pay_filename):
                logger.info('发现任务id: %d之前已支付过，准备进入个人订单中心，确认订单支付状态，并进行相应的处理...' % self.task_id)
                ## 点击首页中的"My Orders"，进入个人订单页面
                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()
                time.sleep(5)
                #若未能获取指定元素，表明未成功下单！
                try:
                    self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]')
                except NoSuchElementException:
                    logger.info('[task_di: %s]未成功下单，删除缓存文件！'% self.task_id)
                    os.remove(confirm_pay_filename)
                #订单支付成功
                if self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').text.strip() != 'Pay Now':
                    self.do_after_place_order_success(confirm_pay_filename)
                # 订单支付失败，则读取缓存文件confirm_pay_files/taskid_xx.txt中的再支付次数；
                # 当再支付次数小于3次时，执行再支付流程；否则停止刷单，避免死循环。
                elif self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').text.strip() == 'Pay Now':
                    confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
                    confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
                    times = load_json(confirm_pay_filename, default={"times": 0})['times']
                    if times == 3:
                        logger.info('再支付次数已达3次，终止刷单！')
                        self.do_when_good_off_shelf()
                        self.driver.quit()
                        sys.exit(0)

                    logger.info('确认订单未成功支付，正在尝试继续支付订单！')
                    WebDriverWait(driver=self.driver, timeout=40).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]'))
                    )
                    # 点击Pay Now
                    self.driver.find_element_by_xpath(
                        '//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').click()
                    #再次支付流程,页面布局与首次支付不一致
                    self.fill_in_payment_information2()
                    time.sleep(3)
                    WebDriverWait(driver=self.driver, timeout=30).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//div[@class="checkout-button"]/button[1]'))
                    )
                    self.driver.find_element_by_xpath('//div[@class="checkout-button"]/button[1]').click()
                    logger.info('点击了确认支付的按钮!')
                    # 由于之前已支付过，但未成功，存在一个confirm_pay_files/taskid_xx.txt文件，且文件内容为空;
                    # 读取文件内容，若为空，则写入再支付次数;若不为空，则更新支付次数, 格式：{“times”: 1}
                    confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
                    confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
                    times = load_json(confirm_pay_filename, default={"times": 0})['times']
                    times += 1
                    save_json(confirm_pay_filename, json_data={"times": times})
                    # WebDriverWait(driver=self.driver, timeout=30).until(
                    #     EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/a'))
                    # )
                    time.sleep(20)
                    if 'payOnlineSuccess' in self.driver.current_url or 'Thank you for your payment' in self.driver.page_source:
                        self.driver.save_screenshot('PaySuccess.png')
                        # self.driver.back()
                        time.sleep(2)
                        self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
                        WebDriverWait(driver=self.driver, timeout=30).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="nav-user-account"]/div[1]'))
                        )
                        element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
                        # print(element)
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element)
                        actions.perform()
                        time.sleep(1)
                        WebDriverWait(self.driver, 40).until(
                            EC.element_to_be_clickable((By.XPATH, '//ul[@class="flyout-quick-entry"]/li[2]/a'))
                        )
                        self.driver.find_element_by_xpath('//ul[@class="flyout-quick-entry"]/li[2]/a').click()
                        time.sleep(4)
                        self.do_after_place_order_success(confirm_pay_filename)

                    elif 'payOnlineFailure' in self.driver.current_url:
                        self.driver.save_screenshot('PayFailed.png')
                        self.do_after_place_order_failed(confirm_pay_filename)
            else:
                WebDriverWait(self.driver,40).until(
                    EC.element_to_be_clickable((By.ID,"search-key"))
                )
                self.driver.find_element_by_id('search-key').send_keys(self.task_infos[str(self.task_id)]["asin"]["keywords"])
                time.sleep(random.uniform(0.5, 1.5))
                self.driver.find_element_by_class_name('search-button').send_keys(Keys.ENTER)

                for i in range(1,2):
                     #弹窗处理
                    try:
                        WebDriverWait(self.driver, 15).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                        )
                        self.driver.find_element_by_class_name('close-layer').click()
                    except TimeoutException:
                        pass
                    source = self.driver.page_source
                    result = self.parse_list_page(source)
                    if result:
                        self.get_detail_page_to_add(self.target_good_detail_url)
                        break
                    # else:
                    #     try:
                    #         #此处处理列表搜索页少于3页的情况：只解析第一个列表搜索页，未找到目标商品时直接进行url拼接；
                    #         if len(self.driver.find_elements_by_xpath('//*[@id="pagination-bottom"]/div[1]/a')) > 2:
                    #             WebDriverWait(driver=self.driver, timeout=30).until(
                    #                 EC.element_to_be_clickable((By.XPATH, '//span[@class="ui-pagination-active"]/following-sibling::a[1]'))
                    #             )
                    #             self.driver.find_element_by_xpath('//span[@class="ui-pagination-active"]/following-sibling::a[1]').click()
                    #             logger.info('第%d列表搜索页没找到目标商品，正在跳转到第%d列表搜索页...'% (i,i+1))
                    #             time.sleep(3)
                    #     except NoSuchElementException as e:
                    #         pass
                else:
                    logger.info('搜索页中没有找到目标商品，正在拼接目标商品的详情url,进行特殊处理...')
                    self.target_good_detail_url = 'https://www.aliexpress.com/item/-a/'+ self.target_id + '.html'
                    self.get_detail_page_to_add(self.target_good_detail_url)
                self.add_other_goods()
                self.delete_other_goods_from_cart()
                self.place_order()
            #最后关闭浏览器，结束程序
            self.driver.quit()
            logger.info('当前账户操作完毕，关闭当前浏览器！')
        except (TimeoutException, WebDriverException, NoSuchElementException, NoSuchFrameException):
            # 在操作过程中等待超时，先退出当前登录状态，再重新执行run方法回调，重新走流程；也可直接结束程序，只适合在多线程的情况下操作。
            logger.info('等待超时,或者元素位未完全加载导致定位出错!')
            logger.info('关闭当前浏览器，结束当前线程！')
            logger.info('系统会自动生成新的线程来执行下单任务！')
            self.driver.quit()
            sys.exit(0)

    #解析搜索的列表页:若找到目标商品，则返回True,否则返回False
    def parse_list_page(self,html):
        parseHtml = etree.HTML(html)
        good_detail_urls = parseHtml.xpath('//ul[@id="hs-below-list-items"]/li/div[1]/div[1]/div/a/@href')
        #绑定当前页的所有商品详情链接
        self.good_detail_urls = good_detail_urls
        for detail_url in good_detail_urls:
            if re.search(self.target_id,detail_url):
                detail_url = "https:" + detail_url
                self.target_good_detail_url = detail_url
                logger.info('目标商品的详情链接是：%s' % self.target_good_detail_url)
                # logger.info('搜索页中找到了目标商品！')
                self.good_detail_urls = good_detail_urls
                # logger.info('目标商品所在列表页的所有商品的详情链接是：%s' % self.good_detail_urls)
                return True
        return False

    # 访问商品详情页，加入购物车
    def get_detail_page_to_add(self, url):
        self.driver.get(url)
        # 弹窗处理
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
            )
            self.driver.find_element_by_class_name('close-layer').click()
        except TimeoutException:
            pass
        # try:
        #     WebDriverWait(driver=self.driver, timeout=10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-1"]/li[1]/a'))
        #     )
        #     self.driver.find_element_by_xpath('//ul[@id="j-sku-list-1"]/li[1]/a').send_keys(Keys.ENTER)
        # except TimeoutException:
        #     pass
        # time.sleep(random.randint(1,4))
        # try:
        #     #有些商品是没有颜色可选的，需要做异常处理
        #     WebDriverWait(driver=self.driver, timeout=10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-2"]/li[1]/a'))
        #     )
        #     self.driver.find_element_by_xpath('//ul[@id="j-sku-list-2"]/li[1]/a').send_keys(Keys.ENTER)
        # except TimeoutException:
        #     pass
        # time.sleep(random.randint(1,4))
        #
        # try:
        #     #有些商品是没有规格可选的，需要做异常处理
        #     WebDriverWait(driver=self.driver, timeout=10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-3"]/li[1]/a'))
        #     )
        #     self.driver.find_element_by_xpath('//ul[@id="j-sku-list-3"]/li[1]/a').send_keys(Keys.ENTER)
        # except TimeoutException:
        #     pass
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[contains(@id, "j-sku-list-")]/li'))
            )
            items_dls = self.driver.find_elements_by_xpath('//div[@id="j-product-info-sku"]/dl')
            # item_dl对应于颜色或者规格等，每个item_dl下面分几个选项choice_li,
            # 由于部分choice_li不可点击，没有“class属性”或者“class属性中有disabled”，需要遍历下，找到可点击的choice_li,点击后再break
            for item_dl in items_dls:
                choices_lis = item_dl.find_elements_by_xpath('.//ul[contains(@id, "j-sku-list-")]/li')
                for choice_li in choices_lis:
                    # print("class属性值：", choice_li.get_attribute('class'))
                    if (not choice_li.get_attribute('class')) or (
                            'disabled' not in choice_li.get_attribute('class')):
                        choice_li.find_element_by_xpath('./a').send_keys(Keys.ENTER)
                        # choice_li.send_keys(Keys.ENTER)
                        break
                time.sleep(random.uniform(3, 6))
        except (TimeoutException, NoSuchElementException):
            # 有些商品没有颜色或者规格的选项
            pass

        try:
            self.driver.find_element_by_id('j-add-cart-btn').send_keys(Keys.ENTER)
            if self.target_id in url:
                logger.info('目标商品已成功添加到购物车！')
            else:
                logger.info('非目标商品已成功添加到购物车！')
        except NoSuchElementException as e:
            logger.info('商品已失效，无法添加到购物车！终止刷单!')
            self.do_when_good_off_shelf_or_asin_is_invalid()
            logger.info('关闭当前浏览器，结束当前刷单任务！')
            self.driver.quit()
            sys.exit(0)

        # 关闭添加购物车后的提示窗口
        try:
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
            )
            self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
        except TimeoutException:
            pass

    #购物车中添加其他非目标商品
    def add_other_goods(self):
        # self.driver.back()
        while True:
            other_good_detail_url ='https:' + random.choice(self.good_detail_urls)
            # if other_good_detail_url != self.target_good_detail_url:
            #     break
            if not re.search(self.target_id, other_good_detail_url):
                break
        self.get_detail_page_to_add(other_good_detail_url)

    #删除购物车中的非目标商品
    def delete_other_goods_from_cart(self):
        try:
            WebDriverWait(driver=self.driver, timeout=20).until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"nav-cart nav-cart-box")]/a[1]'))
            )
            self.driver.find_element_by_xpath('//div[contains(@class,"nav-cart nav-cart-box")]/a[1]').send_keys(Keys.ENTER)
        except TimeoutException:
            logger.info('进入购物车等待超时，程序退出！')
            sys.exit(0)
        time.sleep(10)
        items = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')
        # print(len(items))
        try:
            for item in items:
                good_detail_url = item.find_element_by_xpath('.//div[@class="product-title"]/a').get_attribute('href')
                if not re.search(self.target_id,good_detail_url):
                    #非目标商品，直接从购物车删除
                    item.find_element_by_xpath('.//div[@class="opt-group"]/button[2]').click()
                    time.sleep(2)
                    print('点击删除！')
                    #点击ok
                    WebDriverWait(driver=self.driver, timeout=20).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="next-dialog-footer next-align-left"]/button[1]'))
                    )
                    self.driver.find_element_by_xpath('//div[@class="next-dialog-footer next-align-left"]/button[1]').send_keys(
                        Keys.ENTER)
                    logger.info('点击OK,确认删除非目标商品！')
                    logger.info('非目标商品已从购物车中删除！')
                    time.sleep(2)
        # 点击删除后，网页会刷新，元素已发生改变，需捕获异常并处理
        except StaleElementReferenceException:
            self.delete_other_goods_from_cart()

    #下订单支付流程
    def place_order(self):
        #页面刷新，可有可无
        # self.driver.refresh()
        WebDriverWait(driver=self.driver, timeout=20).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="SearchText"]'))
        )
        #虽有只有一个商品，但是有两个<div class="store-list single"></div>,第一个为空
        try:
            item = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')[1]
        except IndexError:
            item = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')[0]
        # print('item',item)
        good_detail_url = item.find_element_by_xpath('.//div[@class="product-title"]/a').get_attribute('href')
        # print(good_detail_url)
        if  re.search(self.target_id,good_detail_url):
            input_elements = item.find_elements_by_xpath('.//input')
            # print('len(input_elements)',len(input_elements))
            quantity = input_elements[2].get_attribute('value')
            print('quantity',quantity)
            input_elements[1].click()
        # 发现一个有意思的情况，同一款商品同规格同颜色，多次添加到购物车，进入购物车查看时，商品数量依然为1。
        # 所以，商品数量的处理，可以简化。
        time.sleep(20)
        if quantity == '1':
            price_text = self.driver.find_element_by_xpath('//div[@class="total-price"]/dl/dd').text
            price = re.sub(r'US \$','',price_text).strip()
            #此处购物车中的待支付金额是否超出单笔最大额度，若超出，则终止刷单。
            logger.info('删除非目标商品后，购物车中查看到的待支付金额：%s'% price)
            # if float(price) > float(self.task_infos[str(self.task_id)]["payment"]["single_max_trade"]):
            #     logger.info('删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!')
            #     # 新增刷单操作日志
            #     data = {
            #         "task_id": self.task_id,
            #         "info": "删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!",
            #         'ip': self.get_ip_info(proxies={'https': self.proxy})
            #     }
            #     self.create_task_order_log(json.dumps(data))
            #     logger.info('程序结束！')
            #     self.driver.quit()
            #     sys.exit(0)

            # self.driver.find_element_by_xpath('//button[@id="checkout-button"]').send_keys(Keys.ENTER)
            self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
            time.sleep(1)
            js = 'document.getElementById("checkout-button").click();'
            self.driver.execute_script(js)
            logger.info('走下单流程！准备进入个人信息和支付信息的填写流程...')
            time.sleep(10)
            # 切换到收货信息填写的子iframe
            try:
                # self.driver.switch_to.frame('poplay-order')
                # WebDriverWait(self.driver, 40).until(
                #     EC.element_to_be_clickable((By.XPATH, '//div[@class="shipping-info mini"]/div[@class="mini-title"]'))
                # )
                # if 'checked' in self.driver.find_element_by_xpath('//label[@dir="ltr" and aria-checked="true"]').get_attribute('class'):
                #     logger.info('该用户已有默认收货信息！')
                #     self.fill_in_pament_information()
                # else:
                #     logger.info('该用户无默认收货信息，正在创建收货信息...')
                #     self.driver.find_element_by_xpath('//div[@class="shipping-info mini"]/div[@class="mini-title"]').click()
                self.driver.switch_to.frame('poplay-order')
                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="switch-to-full"]/a'))
                )
                # url = self.driver.find_element_by_xpath('//div[@class="switch-to-full"]/a').get_attribute('href')
                # print(url)
                # self.driver.get(url)
                # time.sleep(3)
                js = 'document.querySelector("div[class=switch-to-full] > a").click();'
                self.driver.execute_script(js)
                # self.driver.find_element_by_xpath('//div[@class="switch-to-full"]/a').send_keys(Keys.ENTER)
                time.sleep(10)
            except NoSuchFrameException:
                # logger.info('切换到收货信息填写的子iframe超时，程序退出！')
                logger.info('不需切换到收货信息填写的子iframe!正在创建收货信息...')
                # sys.exit(0)
            try:
                if "checked" in self.driver.find_element_by_xpath('//div[@role="radiogroup"]/div[1]/label[@dir="ltr"]').get_attribute('class'):
                    logger.info('该用户已有默认收货信息！')
            except NoSuchElementException:
                logger.info('该用户无默认收货信息，正在创建收货信息...')
                self.fill_in_address_infomation()
            self.fill_in_pament_information()
            time.sleep(5)
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@id="checkout-button"]'))
            )
            #"点击placc order"
            # print('下一步即时点击操作...')
            # print('此处点击支付...')
            # self.driver.find_element_by_xpath('//button[@id="checkout-button"]').click()
            js = 'document.getElementById("checkout-button").click();'
            self.driver.execute_script(js)
            # logger.info('点击了确认支付的按钮!')
            # 在项目的根目录下，新建一个文件夹confirm_pay_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
            confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
            if not os.path.exists(confirm_pay_dir):
                os.mkdir(confirm_pay_dir)
            confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_'+ str(self.task_id) + '.txt'
            f = open(confirm_pay_filename,'w',encoding='utf-8')
            f.close()
            logger.info('同时创建了一个文件：%s' % confirm_pay_filename)
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/a'))
            )
            time.sleep(20)
            if 'payOnlineSuccess' in self.driver.current_url or 'Thank you for your payment' in self.driver.page_source:
                self.driver.save_screenshot('PaySuccess.png')
                logger.info('下单成功！')
                # logger.info("成功下单后的url:%s" % self.driver.current_url)
                # self.driver.back()
                time.sleep(2)
                self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
                WebDriverWait(driver=self.driver, timeout=30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="nav-user-account"]/div[1]'))
                )
                element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
                # print(element)
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                time.sleep(1)
                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, '//ul[@class="flyout-quick-entry"]/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//ul[@class="flyout-quick-entry"]/li[2]/a').click()
                time.sleep(4)
                self.do_after_place_order_success(confirm_pay_filename)

            elif 'payOnlineFailure' in self.driver.current_url:
                self.driver.save_screenshot('PayFailed.png')
                self.do_after_place_order_failed(confirm_pay_filename)

    #创建收货地址信息
    def fill_in_address_infomation(self):
        # self.driver.refresh()
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.ID, 'contactPerson'))
        )
        self.driver.find_element_by_id('contactPerson').send_keys(
            self.task_infos[str(self.task_id)]["address"]["FullName"])
        time.sleep(random.uniform(2, 4))
        # 电话号码需要处理，若有"+1"前缀，则去掉"+1"前缀
        PhoneNumber = self.task_infos[str(self.task_id)]["address"]["PhoneNumber"]
        if re.search(r'\+1|\s|\(|\)|-', PhoneNumber):
            PhoneNumber = re.sub(r'\+1|\s|\(|\)|-', '', PhoneNumber)
        self.driver.find_element_by_id('mobileNo').send_keys(PhoneNumber)
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('address').send_keys(
            self.task_infos[str(self.task_id)]["address"]["AddressLine1"])
        time.sleep(random.uniform(2, 4))
        if self.task_infos[str(self.task_id)]["address"]["AddressLine2"]:
            self.driver.find_element_by_name('address2').send_keys(
                self.task_infos[str(self.task_id)]["address"]["AddressLine2"])
        # else:
        #     self.driver.find_element_by_name('address2').send_keys("Al Bada'a Park 1")
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_xpath( '//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[1]/span/span/span/span[1]/span/input').click()
        time.sleep(5)
        #显示7个
        # self.driver.find_element_by_xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[1]/span/div/div/div/ul/li[5]').click()
        self.driver.find_element_by_xpath('//li[text()="California"]').click()
        time.sleep(4)
        self.driver.find_element_by_xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[2]/span/span/span/span[1]/span/input').click()
        # self.driver.find_element_by_xpath('//li[text()="3 points"]').click()
        time.sleep(5)
        # self.driver.find_element_by_xpath(
            # '//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[2]/span/div/div/div/ul/li[5]').click()
        # self.driver.find_element_by_xpath('//li[text()="3 points"]').click()
        self.driver.find_element_by_xpath('//li[text()="%s"]' % random.choice(City_List)).click()
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('zip').send_keys(
            self.task_infos[str(self.task_id)]["address"]["PostalCode"].strip())
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_xpath('//input[@type="checkbox"]').click()
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_xpath('//div[@class="save"]/button[@type="button"]').click()
        logger.info('完成收货地址信息的填写！')

    #创建支付信息
    def fill_in_pament_information(self):
        logger.info('正在创建支付信息...')
        # WebDriverWait(self.driver, 40).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@class="payment-info mini"]/div[@class="mini-title"]'))
        # )
        # self.driver.find_element_by_xpath('//div[@class="payment-info mini"]/div[@class="mini-title"]').click()
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.ID, 'cardNo'))
        )
        self.driver.find_element_by_id('cardNo').send_keys(self.task_infos[str(self.task_id)]["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(2, 4))
        #卡持有者强制用空格隔开firstname 与 lastname
        # 切割全名并判断长度
        FullName_text = self.task_infos[str(self.task_id)]["address"]["FullName"].split()
        print(FullName_text[0] + ' ' + FullName_text[0])
        if len(FullName_text) == 1:
            self.driver.find_element_by_id('cardHolder').send_keys(FullName_text[0] + ' ' + FullName_text[0])
            time.sleep(random.uniform(2, 4))
        else:
            self.driver.find_element_by_id('cardHolder').send_keys(self.task_infos[str(self.task_id)]["address"]["FullName"])
            time.sleep(random.uniform(2, 4))
        expireDate = self.task_infos[str(self.task_id)]["payment"]["ccMonth"] + self.task_infos[str(self.task_id)]["payment"]["ccYear"]
        self.driver.find_element_by_id('expire').send_keys(expireDate)
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_id('cvc').send_keys(self.task_infos[str(self.task_id)]["payment"]["cvv"])
        time.sleep(2)
        #//*[@id="main"]/div[2]/div/div/div[2]/div[2]/div[2]/button
        self.driver.find_element_by_xpath('//div[@class="save"]/button[@type="button"]').click()
        logger.info('完成支付信息的创建！')

    #支付失败后，进行再支付时的支付信息创建
    def fill_in_payment_information2(self):
        logger.info('正在进入支付信息的填写流程...')
        WebDriverWait(driver=self.driver, timeout=60).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="cardNum"]'))
        )
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('cardNum').send_keys(
            self.task_infos[str(self.task_id)]["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('dateM').send_keys(self.task_infos[str(self.task_id)]["payment"]["ccMonth"])
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('dateY').send_keys(self.task_infos[str(self.task_id)]["payment"]["ccYear"])
        time.sleep(random.uniform(2, 4))
        self.driver.find_element_by_name('cvv2').send_keys(self.task_infos[str(self.task_id)]["payment"]["cvv"])
        # 切割全名并判断长度
        FullName_text = self.task_infos[str(self.task_id)]["address"]["FullName"].split()
        if len(FullName_text) == 1:
            time.sleep(random.uniform(2, 4))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(2, 4))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[0])
        else:
            time.sleep(random.uniform(2, 4))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(2, 4))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[1])
        time.sleep(random.uniform(3, 5))
        try:
            self.driver.find_element_by_xpath('//div[@class="checkout-button"]/button[2]').send_keys(Keys.ENTER)
            logger.info('完成支付信息的填写!')
        except Exception as e:
            print(e)

    #当商品下架，无法加入购物车时，更新刷单状态，终止刷单
    def do_when_good_off_shelf(self):
        # 更新刷单状态
        brushing_data = {
            str(self.task_id): {
                "task_id": self.task_id,
                "status": 23,
            }
        }
        self.update_brushing_status(json.dumps(brushing_data))
        # 新增刷单操作日志
        log_data = {
            "task_id": self.task_id,
            "info": "商品失效，无法添加到购物车，终止刷单！",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(log_data))

    #确认订单支付成功后，获取订单信息，更新刷单状态，插入刷单日志，最后删除缓存文件
    def do_after_place_order_success(self,confirm_pay_filename):
        logger.info('确认订单已成功支付，正在获取订单的相关信息，更新刷单状态...')
        order_no = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]//tr[1]/td[2]/p[1]/span[2]').text
        logger.info("订单号为：%s" % order_no)
        price_text = self.driver.find_element_by_xpath(
            '//*[@id="buyer-ordertable"]/tbody[1]/tr[1]/td[4]/div/p[2]').text.strip()
        actual_order_amount = re.sub(r'\$ ', '', price_text)
        logger.info('订单总价：%s' % actual_order_amount)
        payment_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info('下单时间：%s' % payment_date)
        brushing_data = {
            str(self.task_id): {
                "task_id": self.task_id,
                "status": 2,
                "order_no": order_no,
                "payment_date": payment_date,
                "actual_order_amount": float(actual_order_amount)
            }
        }
        self.update_brushing_status(json.dumps(brushing_data))
        # 新增刷单操作日志
        data = {
            "task_id": self.task_id,
            "info": "下单成功！",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(data))
        os.remove(confirm_pay_filename)
        logger.info('删除了一个文件：%s' % confirm_pay_filename)

    #确认订单支付失败后，插入刷单日志
    def do_after_place_order_failed(self, confirm_pay_filename):
        logger.info('支付失败！')
        self.driver.save_screenshot('PayFailed.png')
        # logger.info('支付失败的url:%s' % self.driver.current_url)
        # 新增刷单操作日志
        data = {
            "task_id": self.task_id,
            "info": "支付失败！导致下单失败！",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(data))
        # 支付失败，也要删除confirm_pay_filename
        # os.remove(confirm_pay_filename)
        # logger.info('删除了一个文件：%s' % confirm_pay_filename)

    # 插入账号登录日志
    @staticmethod
    def insert_account_login_log(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressInsertAccountLoginLog'
        post(requests.session(), url=url, post_data=data)
        logger.info('账户登录日志已成功插入！')

    # 当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
    @staticmethod
    def update_account_login_success_info(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressUpdateAccountLoginSuccessInfo'
        post(requests.session(), url=url, post_data=data)
        logger.info('对应账户的header和cookies字段已成功修改!')

    # 更新刷单状态
    @staticmethod
    def update_brushing_status(data):
        # 测试机
        # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        # 线上
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        resp = post(requests.session(), url=url, post_data=data)
        if resp.json()['msg'] == 'ok':
            logger.info('刷单状态更新成功！')
        else:
            logger.info('刷单状态更新失败！')

    # 新增刷单操作日志
    @staticmethod
    def create_task_order_log(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
        resp = post(requests.session(), url=url, post_data=data)
        if resp.json()['status'] == 0:
            logger.info('新增刷单操作日志成功!')
        else:
            logger.info('新增刷单操作日志失败!')

    # 获取当前ip信息，返回字符串
    @staticmethod
    def get_ip_info(proxies):
        getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        if getIpInfo:
            ipInfo = json.loads(getIpInfo.text)
            ip = ipInfo['ip']
        else:
            ip = '未获取到ip'
        return ip


def main(task_infos, task_id):
    spider = AliexpressOrderSpider(task_infos, task_id)
    spider.run()


if __name__ == '__main__':
    # 多线程循环模式：默认一次最多获取2个待刷单任务,自动根据获取到的任务数量创建相应数量的线程数，去执行各自分配到的刷单任务；当获取不到任务时，程序退出。
    while True:
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=1&limit=2'
        resp = get(requests.session(), url=url)
        if resp:
            try:
                if resp.json() == []:
                    # logger.info('未获取到待刷单列表的数据，程序结束！')
                    # sys.exit(0)
                    logger.info('任务系统未获取到当前时间的任务，程序[sleep 10m]...')
                    time.sleep(60 * 10)
                else:
                    # 先读取缓存文件
                    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
                    if not os.path.exists(cache_dir):
                        os.mkdir(cache_dir)
                    _cache_file = cache_dir + '/' + 'new_cart_tasks.json'
                    cache_task_list = load_json(_cache_file, default={"task_list": []})["task_list"]

                    #先读取缓存文件
                    # cache_dir = os.path.dirname(__file__)
                    # _cache_file = cache_dir + "/data/new_cart_tasks.json"
                    # if not os.path.exists(os.path.dirname(_cache_file)):
                    #     os.makedirs(os.path.dirname(_cache_file))
                    # cache_task_list = load_json(_cache_file, default={"task_list": []})["task_list"]

                    task_infos = resp.json()
                    task_id_str_list = []

                    for task_id_str in task_infos:
                        if task_id_str in cache_task_list:
                            task_id_str_list.append(task_id_str)
                    # 未获取到任务时，休眠1分钟，避免频繁请求任务接口
                    if len(task_id_str_list) == 0:
                        logger.info('缓存文件中没有可执行的任务，程序[sleep 60s]...')
                        time.sleep(60)
                    else:
                        logger.info('成功获取到%d条待刷单的数据！' % len(task_id_str_list))
                        logger.info('将创建%d个线程来分别执行刷单任务!' % len(task_id_str_list))
                        threads = []
                        for i in range(len(task_id_str_list)):
                            task_id = int(task_id_str_list[i])
                            t = threading.Thread(target=main, args=(task_infos, task_id))
                            threads.append(t)
                            t.start()
                            #每个线程创建间隔30秒
                            time.sleep(30)

                        # 回收线程
                        for t in threads:
                            t.join()
            except json.decoder.JSONDecodeError:
                pass
        else:
            logger.info('任务系统出错，程序[sleep 30s]...')
            time.sleep(30)
