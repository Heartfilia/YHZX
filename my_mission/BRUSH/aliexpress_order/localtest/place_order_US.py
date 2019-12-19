import os
import sys
import random
import re
import json
# import threading
from multiprocessing import Process
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
from mytools.tools import get_oxylabs_proxy, get, post, create_proxyauth_extension, logger, load_json, save_json
from config import City_List

logger = logger('place_order_US')
class AliexpressOrderSpider():

    def __init__(self, task_id, task_info):
        self.task_id = task_id
        self.task_info = task_info
        #OXY代理
        # self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        #Geosurf代理
        self.proxy = 'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(300000, 400000)
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="%s"' % json.loads(self.task_info['account']['header'])['user-agent'] )
        #代理需要指定账户密码时，添加代理使用这种方式
        self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        #headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        #设置不加载图片
        self.options.add_experimental_option('prefs',{"profile.managed_default_content_settings.images":2})
        self.driver = webdriver.Chrome(options=self.options)
        self.target_id = self.task_info["asin"]["asin"]
        #self.good_detail_urls属性，用于绑定目标商品所在列表页的所有商品的详情链接
        # self.good_detail_urls = None
        self.good_detail_urls = ['https://www.aliexpress.com/item/32819259209.html']
        #self.target_good_detail_url属性，用于绑定目标商品的详情链接
        self.target_good_detail_url = None

    #主实例方法，负责调用其他实例方法，完成下单的整个流程
    def run(self):
        # if len(self.target_id) != 11:
        #     logger.info('ASIN无效，程序退出！')
        #     self.do_when_asin_is_invalid()
        #     self.driver.quit()
        #     sys.exit(0)
        try:
            self.driver.get('http://www.aliexpress.com')
            # self.driver.execute_script(
            #     '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
            # self.driver.execute_script('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            # self.driver.execute_script(
            #     '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            # self.driver.execute_script(
            #     '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            #过滤弹窗
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@class="register-btn"]/a'))
            )
            #点击登录
            self.driver.find_element_by_xpath('//span[@class="register-btn"]/a').click()
            # WebDriverWait(self.driver, 40).until(
            #     EC.frame_to_be_available_and_switch_to_it
            # )
            time.sleep(6)
            #切换到子iframe
            self.driver.switch_to.frame('alibaba-login-box')
            #输入登录信息
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="fm-login-id"]'))
            )
            time.sleep(random.uniform(1, 3))
            self.driver.find_element_by_id('fm-login-id').send_keys(self.task_info["account"]["login_aliexpress_email"])
            time.sleep(random.uniform(1, 3))
            self.driver.find_element_by_id('fm-login-password').send_keys(self.task_info["account"]["login_aliexpress_password"])
            time.sleep(random.uniform(1, 3))
            try:
                self.driver.find_element_by_id('fm-login-submit').send_keys(Keys.ENTER)
            except NoSuchElementException as e:
                print('no fm-login-submit')
                self.driver.find_element_by_xpath('//button[text()="Sign In"]').send_keys(Keys.ENTER)
            # js = 'document.getElementById("fm-login-submit").click();'
            # js = 'document.getElementByClassName("fm-button fm-submit password-login").click();'
            # self.driver.execute_script(js)
            time.sleep(1)
            # 此处判断登录过程中是否有滑块验证码，有则终止程序
            try:
                if 'display: block' in self.driver.find_element_by_id('fm-login-checkcode-title').get_attribute('style'):
                    logger.info('[taskid: %d] 登录时发现滑块验证码，程序退出！' % self.task_id)
                    self.driver.quit()
                    sys.exit(0)#fm-login-checkcode-title
            except NoSuchElementException as e:
                try:
                    if 'display: block' in self.driver.find_element_by_id('nocaptcha-password').get_attribute('style'):
                        logger.info('[taskid: %d] 登录时发现滑块验证码，程序退出！' % self.task_id)
                        self.driver.quit()
                        sys.exit(0)
                except NoSuchElementException:
                    pass
            #弹窗处理
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass

            # if self.driver.current_url == 'https://www.aliexpress.com/':
            if "Hi," in self.driver.page_source and 'noticed an unusual activity' not in self.driver.page_source:
                # logger.info('login_ip:%s' % self.get_ip_info({'https': self.proxy}))
                # logger.info('login_cookies: %s' % json.dumps(self.driver.get_cookies()))
                #插入账号登录日志
                login_log_data = {
                    'data':{
                        "account_id":self.task_info["account"]["account_id"],
                        "header":self.task_info['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies()),
                        "login_status": "1",
                        "note": "登录成功"
                    }
                }
                self.insert_account_login_log(json.dumps(login_log_data))
                #当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
                login_success_info_data = {
                    'data':{
                        "account_id": self.task_info["account"]["account_id"],
                        "header": self.task_info['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies())
                    }
                }
                self.update_account_login_success_info(json.dumps(login_success_info_data))
            elif 'passport.aliexpress.com' in self.driver.current_url:
                logger.info('[taskid: %d] 登录后发现验证码，账户已被封！' % self.task_id)
                #账户被封，也更新刷单状态
                brushing_data = {
                    str(self.task_id): {
                        "task_id": self.task_id,
                        "status": 10,
                    }
                }
                self.update_brushing_status(json.dumps(brushing_data))
                self.driver.quit()
                logger.info('[taskid: %d] 程序退出！' % self.task_id)
                sys.exit(0)
            #先检查cofirm_pay_file文件夹下，是否存在一个taskid_xx.txt文件，xx为本次任务id。
            # 若存在，则进入个人订单中心，获取订单号和定价总价等信息，更新刷单状态。并删除该文件。
            #若不存在，则正常走流程。
            confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
            confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            if os.path.exists(confirm_pay_filename):
                logger.info('[taskid: %d] 发现任务id: %d之前已支付过，准备进入个人订单中心，确认订单支付状态，并进行相应的处理...' % (self.task_id, self.task_id))
                ## 点击首页中的"My Orders"，进入个人订单页面
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()
                time.sleep(5)
                # 若未能获取指定元素，表明未成功下单！
                try:
                    self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]')
                except NoSuchElementException:
                    logger.info('[task_id: %s]未成功下单，删除缓存文件！' % self.task_id)
                    os.remove(confirm_pay_filename)
                    self.driver.quit()
                    sys.exit(0)
                #订单已关闭
                if self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').text.strip() == 'Add to Cart':
                    logger.info('[task_id: %s] Order has been closed!' % self.task_id)
                    os.remove(confirm_pay_filename)
                    logger.info('[task_id: %s] Remove one file: %s' % (self.task_id, confirm_pay_filename))
                    #解绑账号避免死循环
                    self.do_when_the_number_of_repyments_has_reached_three_times()
                    logger.info('[taskid: %d] 账号已解绑！'% self.task_id)
                    self.driver.quit()
                    sys.exit(0)
                #订单支付失败，则读取缓存文件confirm_pay_files/taskid_xx.txt中的再支付次数；
                #当再支付次数小于3次时，执行再支付流程；否则停止刷单，避免死循环。
                elif self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').text.strip() == 'Pay Now':
                    confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
                    confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
                    times = load_json(confirm_pay_filename, default={"times": 0})['times']
                    if times == 3:
                        logger.info('[taskid: %d] 再支付次数已达3次，终止刷单！' % self.task_id)
                        self.do_when_the_number_of_repyments_has_reached_three_times()
                        os.remove(confirm_pay_filename)
                        logger.info('[taskid: %d] Remove one file: %s' % (self.task_id, confirm_pay_filename))
                        self.driver.quit()
                        sys.exit(0)

                    logger.info('[taskid: %d] 确认订单未支付，正在尝试继续支付订单！' % self.task_id)
                    WebDriverWait(driver=self.driver, timeout=15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]'))
                    )
                    # 点击Pay Now
                    self.driver.find_element_by_xpath(
                        '//*[@id="buyer-ordertable"]/tbody[1]/tr[2]/td[4]/button[1]').click()
                    #由于支付信息填写的最后的done按钮与首次支付流程不一样，故此处需要再次写支付流程
                    self.fill_in_and_save_payment_information_again()
                    time.sleep(3)
                    WebDriverWait(driver=self.driver, timeout=15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//div[@class="checkout-button"]/button[1]'))
                    )
                    self.driver.find_element_by_xpath('//div[@class="checkout-button"]/button[1]').click()
                    logger.info('[taskid: %d] 点击了确认支付的按钮!' % self.task_id)
                    # 由于之前已支付过，但未成功，存在一个confirm_pay_files/taskid_xx.txt文件，且文件内容为空;;
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
                    # 订单支付成功
                    self.do_after_place_order_success(confirm_pay_filename)
            else:
                WebDriverWait(self.driver,15).until(
                    EC.element_to_be_clickable((By.ID,"search-key"))
                )
                search_btn = self.driver.find_element_by_id('search-key')
                for k in range(3):
                    search_btn.clear()
                    time.sleep(1)
                time.sleep(1)
                search_btn.send_keys(self.task_info["asin"]["keywords"].strip())
                time.sleep(random.uniform(2, 3))
                self.driver.find_element_by_class_name('search-button').send_keys(Keys.ENTER)

                for i in range(1,16):
                # for i in range(1,2):
                     #弹窗处理
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                        )
                        self.driver.find_element_by_class_name('close-layer').click()
                    except TimeoutException:
                        pass
                    # if 'did not match any products' in self.driver.page_source:
                    #     logger.info('搜索关键词有误，搜不到任何产品，终止刷单！')
                    #     self.do_when_good_off_shelf()
                    #     self.driver.quit()
                    #     sys.exit(0)
                    source = self.driver.page_source
                    result = self.parse_list_page(source,i)
                    if result:
                        self.get_detail_page_to_add(self.target_good_detail_url)
                        break
                    else:
                        try:
                            #此处处理列表搜索页少于3页的情况：只解析前两个列表搜索页，未找到目标商品时直接进行url拼接；
                            # if len(self.driver.find_elements_by_xpath('//*[@id="pagination-bottom"]/div[1]/a')) > 2:
                            if len(self.driver.find_elements_by_xpath('//*[@id="pagination-bottom"]/div[1]/a')) >= 2:
                                WebDriverWait(driver=self.driver, timeout=30).until(
                                    EC.element_to_be_clickable((By.XPATH, '//span[@class="ui-pagination-active"]/following-sibling::a[1]'))
                                )
                                self.driver.find_element_by_xpath('//span[@class="ui-pagination-active"]/following-sibling::a[1]').click()
                                logger.info('[taskid: %d] 第%d列表搜索页没找到目标商品，正在跳转到第%d列表搜索页...'% (self.task_id, i, i+1))
                                time.sleep(3)
                        except NoSuchElementException as e:
                            pass
                else:
                    # logger.info('[taskid: %d] 前4页中没有找到目标商品，正在拼接目标商品的详情url,进行特殊处理...' % self.task_id)
                    # page_and_rank_data = {
                    #     "data": {
                    #         "page_num": "5",
                    #         "row_num": "1",
                    #         "task_id": self.task_id
                    #     }
                    # }
                    # self.update_page_and_rank(json.dumps(page_and_rank_data))
                    # # logger.info('搜索页中没有找到目标商品，正在拼接目标商品的详情url,进行特殊处理...')
                    # self.target_good_detail_url = 'https://www.aliexpress.com/item/-a/'+ self.target_id + '.html'
                    # self.get_detail_page_to_add(self.target_good_detail_url)
                    logger.info('[taskid: %d] 前15个搜索页中没有找到目标商品，停止刷单！' % self.task_id)
                    self.do_when_asin_is_invalid()
                    self.driver.quit()
                    sys.exit(0)

                self.add_other_goods()
                try:
                    WebDriverWait(driver=self.driver, timeout=15).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"nav-cart nav-cart-box")]/a[1]'))
                    )
                    self.driver.find_element_by_xpath('//div[contains(@class,"nav-cart nav-cart-box")]/a[1]').send_keys(
                        Keys.ENTER)
                except TimeoutException:
                    # logger.info('[taskid: %d] 进入购物车等待超时，程序退出！' % self.task_id)
                    WebDriverWait(driver=self.driver, timeout=15).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="right-shopcart"]/a'))
                    )
                    self.driver.find_element_by_xpath('//div[@class="right-shopcart"]/a').send_keys(Keys.ENTER)
                    # sys.exit(0)
                time.sleep(5)
                if 'Shopping Cart (' in self.driver.page_source:
                    logger.info('[taskid: %d] This is a new cart！' % self.task_id)
                    self.do_new_cart_process()
                else:
                    logger.info('[taskid: %d] This is an old cart！' % self.task_id)
                    self.do_old_cart_process()
            #最后关闭浏览器，结束程序
            self.driver.quit()
            logger.info('[taskid: %d] 当前账户操作完毕，关闭当前浏览器！' % self.task_id)
        except (TimeoutException, WebDriverException, NoSuchElementException, NoSuchFrameException):
            # 在操作过程中等待超时，先退出当前登录状态，再重新执行run方法回调，重新走流程；也可直接结束程序，只适合在多线程的情况下操作。
            logger.info('[taskid: %d] 等待超时,或者元素位未完全加载导致定位出错!' % self.task_id)
            logger.info('[taskid: %d] 关闭当前浏览器，结束当前线程！' % self.task_id)
            logger.info('[taskid: %d] 系统会自动生成新的线程来执行下单任务！' % self.task_id)
            self.driver.quit()
            sys.exit(0)

    #解析搜索的列表页:若找到目标商品，则返回True,否则返回False
    def parse_list_page(self, html, page):
        parseHtml = etree.HTML(html)
        good_detail_urls = parseHtml.xpath('//ul[@id="hs-below-list-items"]/li/div[1]/div[1]/div/a/@href')
        #绑定当前页的所有商品详情链接
        # self.good_detail_urls += good_detail_urls
        if len(good_detail_urls) >= 2:
            self.good_detail_urls = good_detail_urls
        else:
            self.good_detail_urls += good_detail_urls
        for detail_url in good_detail_urls:
            if re.search(self.target_id, detail_url):
                rank_num = str(good_detail_urls.index(detail_url) + 1)
                detail_url = "https:" + detail_url
                self.target_good_detail_url = detail_url
                logger.info('[taskid: %d] 目标商品的详情链接是：%s' % (self.task_id, self.target_good_detail_url))
                #rank_num:目标商品在当前页中的排名，从1开始
                #找到目标商品以后，更新商品所在页数和排名
                page_and_rank_data = {
                    'data':{
                        'page_num': str(page),
                        'row_num': rank_num,
                        'task_id': str(self.task_id)
                    }
                }
                self.update_page_and_rank(json.dumps(page_and_rank_data))
                # self.good_detail_urls += good_detail_urls
                # logger.info('目标商品所在列表页的所有商品的详情链接是：%s' % self.good_detail_urls)
                return True
        return False

    #访问商品详情页，加入购物车
    def get_detail_page_to_add(self,url):
        self.driver.get(url)
        #页面刷新，即可过滤弹窗
        self.driver.refresh()
        #弹窗处理
        # try:
        #     WebDriverWait(self.driver, 15).until(
        #         EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
        #     )
        #     self.driver.find_element_by_class_name('close-layer').click()
        # except TimeoutException:
        #     self.driver.refresh()

        #旧详情页的商品规格颜色选择
        try:
            WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//ul[contains(@id, "j-sku-list")]/li'))
            )
            items_dls = self.driver.find_elements_by_xpath('//div[@id="j-product-info-sku"]/dl')
            # item_dl对应于颜色或者规格等，每个item_dl下面分几个选项choice_li,
            # 由于部分choice_li不可点击，没有“class属性”或者“class属性中有disabled”，需要遍历下，找到可点击的choice_li,点击后再break
            for item_dl in items_dls:
                choices_lis = item_dl.find_elements_by_xpath('.//ul[contains(@id, "j-sku-list-")]/li')
                for choice_li in choices_lis:
                    # print("class属性值：", choice_li.get_attribute('class'))
                    if (not choice_li.get_attribute('class')) or ('disabled' not in choice_li.get_attribute('class')):
                        choice_li.find_element_by_xpath('./a |./div').send_keys(Keys.ENTER)
                        # choice_li.send_keys(Keys.ENTER)
                        break
                time.sleep(random.uniform(1, 3))
        except (TimeoutException, NoSuchElementException):
            #有些商品没有颜色或者规格的选项
            pass

        # 新详情页的商品规格颜色选择
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[@class="sku-property-list"]/li'))
            )
            uls = self.driver.find_elements_by_xpath('//ul[@class="sku-property-list"]')
            for ul in uls:
                lis = ul.find_elements_by_xpath('./li')
                for li in lis:
                    value = li.get_attribute('class')
                    if 'selected' not in value and 'disabled' not in value:
                        div = li.find_element_by_xpath('./div')
                        action = ActionChains(self.driver)
                        action.move_to_element(div)
                        action.click()
                        action.perform()
                        time.sleep(random.uniform(1, 3))
                        break
        except (TimeoutException,NoSuchElementException) as e:
            # 有些商品没有颜色或者规格的选项
            print(e)
            pass
        time.sleep(random.uniform(1, 3))
        # 收藏商品
        if self.target_id in url and self.task_info["collection_goods"] == '1':
            try:
                #旧详情页中，点击收藏商品，对应元素的class属性中的collection将消失，再次点击则取消收藏，collection属性值又会出现
                collection_goods_div = self.driver.find_element_by_xpath('//div[@id="j-product-action-block"]/span[1]/div')
                #该div元素的class属性若有'collection'，则表示未收藏，否则为已收藏
                if 'collection' in collection_goods_div.get_attribute('class'):
                    ActionChains(self.driver).move_to_element(collection_goods_div).click().perform()
                    logger.info('[taskid: %d] Click on the Collection Goods!' % self.task_id)
            except (NoSuchElementException,Exception) as e:
                print(e)
                try:
                    #新详情页中，点击收藏商品，对应元素的class属性值的'favourite'将变成'favourited',再次点击则属性值反过来，取消了收藏。
                    collection_goods_i = self.driver.find_element_by_xpath('//div[@class="add-wishlist"]/i[1]')
                    if  'favourite' in collection_goods_i.get_attribute('class'):
                        ActionChains(self.driver).move_to_element(collection_goods_i).click().perform()
                        logger.info('[taskid: %d] Click on the Collection Goods!' % self.task_id)
                except NoSuchElementException:
                    pass
            try:
                # 旧详情页中，关闭收藏商品后的提示窗口
                WebDriverWait(driver=self.driver, timeout=5).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
                )
                self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
            except TimeoutException:
                # 新详情页中，关闭收藏商品后的提示窗口
                try:
                    WebDriverWait(driver=self.driver, timeout=5).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[@class="next-dialog-close"]'))
                    )
                    self.driver.find_element_by_xpath('//a[@class="next-dialog-close"]').click()
                except TimeoutException:
                    pass
        time.sleep(random.uniform(1, 3))
        # 收藏店铺
        if self.target_id in url and self.task_info["collection_store"] == '1':
            try:
                #旧详情页点击收藏店铺以后，再次点击并不会取消收藏
                # collection_store_a = self.driver.find_element_by_xpath('//a[@class="follow-store-btn"]')
                collection_store_span = self.driver.find_element_by_xpath('//span[@class="store-follow-btn"]')
                ActionChains(self.driver).move_to_element(collection_store_span).click().perform()
                logger.info('[taskid: %d] Click on the Collection Store!' % self.task_id)
            except NoSuchElementException:
                try:
                    #新详情页点击收藏店铺后，对应的span元素的class属性中的'follow'将变成'followed',再次点击则相反，取消了收藏
                    collection_store_span = self.driver.find_element_by_xpath('//div[@class="follow-container"]/span')
                    if 'follow' in collection_store_span.get_attribute('class'):
                        ActionChains(self.driver).move_to_element(collection_store_span).click().perform()
                        logger.info('[taskid: %d] Click on the Collection Store!' % self.task_id)
                except NoSuchElementException:
                    pass
            try:
                # 旧详情页中，关闭收藏店铺后的提示窗口
                WebDriverWait(driver=self.driver, timeout=5).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
                )
                self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
            except TimeoutException:
                try:
                    # 新详情页中，关闭收藏店铺后的提示窗口
                    WebDriverWait(driver=self.driver, timeout=5).until(
                        EC.element_to_be_clickable((By.XPATH, '//a[@class="next-dialog-close"]'))
                    )
                    self.driver.find_element_by_xpath('//a[@class="next-dialog-close"]').click()
                except TimeoutException:
                    pass
        time.sleep(random.uniform(1, 3))
        try:
            #旧购物车的“Add to Cart”按钮
            self.driver.find_element_by_id('j-add-cart-btn').send_keys(Keys.ENTER)
        except NoSuchElementException as e:
            try:
                #新购物车的“Add to Cart”按钮
                self.driver.find_element_by_xpath('//div[@class="product-action"]//button[text()="Add to Cart"]').send_keys(Keys.ENTER)
            except NoSuchElementException:
                if self.target_id in url:
                    logger.info('[taskid: %d] 商品已失效，无法添加到购物车！终止刷单!' % self.task_id)
                    self.do_when_good_off_shelf()
                    logger.info('[taskid: %d] 关闭当前浏览器，结束当前刷单任务！' % self.task_id)
                    self.driver.quit()
                    sys.exit(0)
                else:
                    pass

        if self.target_id in url:
            logger.info('[taskid: %d] 目标商品已成功添加到购物车！' % self.task_id)
        else:
            logger.info('[taskid: %d] 非目标商品已成功添加到购物车！' % self.task_id)

        try:
            # 关闭添加旧购物车后的提示窗口
            WebDriverWait(driver=self.driver, timeout=5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
            )
            self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
        except TimeoutException:
            try:
                # 关闭添加新购物车后的提示窗口
                WebDriverWait(driver=self.driver, timeout=5).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="next-dialog-close"]'))
                )
                self.driver.find_element_by_xpath('//a[@class="next-dialog-close"]').click()
            except TimeoutException:
                pass

    #购物车中添加其他非目标商品
    def add_other_goods(self):
        # self.driver.back()
        while True:
            url = random.choice(self.good_detail_urls)
            if not re.search(r'http', url):
                other_good_detail_url ='https:' + url 
            else:
                other_good_detail_url = url 
            # if other_good_detail_url != self.target_good_detail_url:
            #     break
            if not re.search(self.target_id, other_good_detail_url):
                break
        self.get_detail_page_to_add(other_good_detail_url)

    #删除旧购物车中的非目标商品
    def old_cart_delete_other_goods_from_cart(self):

        #(此缓存机制弃用！)此处判断是否为新的购物车，若是，将任务id写入缓存文件，data/new_cart_tasks.json,格式：{'task_list':['122',...]},并结束当前程序。
        # if  'Shopping Cart (' in self.driver.page_source:
        #     logger.info('购物车是新的页面布局！')
        #     # 先读取缓存文件
        #     cache_dir = os.path.join(os.path.dirname(__file__), 'data')
        #     if not os.path.exists(cache_dir):
        #         os.mkdir(cache_dir)
        #     _cache_file = cache_dir + '/' + 'new_cart_tasks.json'
        #     task_list = load_json(_cache_file, default={"task_list": []})["task_list"]
        #     if str(self.task_id) not in task_list:
        #         task_list.append(str(self.task_id))
        #         save_json(_cache_file, {"task_list": task_list})
        #         logger.info('[taskid: %s]已写入缓存文件，由另外的下单程序执行，本程序退出！' % self.task_id)
        #         self.driver.quit()
        #         sys.exit(0)

        items = self.driver.find_elements_by_class_name("item-group-wrapper")
        try:
            for item in items:
                good_detail_url = item.find_element_by_xpath('.//a[@target="_blank"]').get_attribute('href')
                if not re.search(self.target_id,good_detail_url):
                    #非目标商品，直接从购物车删除
                    item.find_element_by_xpath('.//div[@class="product-remove"]/form[1]/a').click()
                    logger.info('[taskid: %d] 非目标商品已从购物车中删除！' % self.task_id)
                    time.sleep(2)
        # 点击删除后，网页会刷新，元素已发生改变，需捕获异常并处理
        except StaleElementReferenceException:
            self.old_cart_delete_other_goods_from_cart()

    #旧购物车的下订单支付流程
    def old_cart_place_order(self):
        #页面刷新，可有可无
        # self.driver.refresh()
        WebDriverWait(driver=self.driver, timeout=20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="product-price-info3"]/a[1]'))
        )
        quantity = self.driver.find_element_by_xpath('//input[@readonly="readonly"]').get_attribute('value')
        # 发现一个有意思的情况，同一款商品同规格同颜色，多次添加到购物车，进入购物车查看时，商品数量依然为1。
        # 所以，商品数量的处理，可以简化。
        if quantity == '1':
            price_text = self.driver.find_element_by_xpath('//span[@class="total-price ui-cost notranslate"]/b').text
            price = re.sub(r'US \$','',price_text)
            #此处购物车中的待支付金额是否超出单笔最大额度，若超出，则终止刷单。
            logger.info('[taskid: %d] 删除非目标商品后，购物车中查看到的待支付金额：%s'% (self.task_id, price))
            if float(price) > float(self.task_info["payment"]["single_max_trade"]):
                logger.info('[taskid: %d] 删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!' % self.task_id)
                # 新增刷单操作日志
                data = {
                    "task_id": self.task_id,
                    "info": "删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(data))
                logger.info('[taskid: %d] 程序结束！' % self.task_id)
                # 商品超出单笔支付额度，更新刷单状态为无法加购物车
                self.do_when_good_off_shelf()
                self.driver.quit()
                sys.exit(0)
            #选择物流方式ePacket
            self.driver.find_element_by_xpath('//div[contains(@class, "product-shipping-select")]').click()
            time.sleep(random.uniform(2, 3))
            try:
                self.driver.find_element_by_xpath('//input[@value="EMS_ZX_ZX_US"]').click()
                time.sleep(random.uniform(2, 3))
            except NoSuchElementException:
                pass
            self.driver.find_element_by_xpath('//input[@value="OK"]').click()
            logger.info('[taskid: %d] 选择物流方式：ePacket!' % self.task_id)
            time.sleep(random.uniform(2, 3))
            self.driver.find_element_by_xpath('//div[@class="product-price-info3"]/a[1]').send_keys(Keys.ENTER)

            logger.info('[taskid: %d] 走下单流程！准备进入个人信息和支付信息的填写流程...' % self.task_id)
            #跳转到个人信息填写页面,需要加以判断，是否已有地址信息
            WebDriverWait(driver=self.driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="page"]/div[1]/div[1]/ol/li[1]'))
            )
            try:
                default_address_info_element = self.driver.find_element_by_xpath('//*[@id="address-main"]/div[2]/ul/li/div/div[1]')
                if 'selected' in default_address_info_element.get_attribute('class'):
                    logger.info('[taskid: %d] 已有默认收货地址！' % self.task_id)
                    time.sleep(3)
                    self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                    time.sleep(3)
                    try:
                        # if self.driver.find_element_by_xpath('//*[@id="j-payment-method"]/div[4]/ul/li[1]/span/span'):
                        if self.driver.find_element_by_xpath('//ul[@class="pay-method-list"]/li[1]/span/span'):
                            logger.info('[taskid: %d] 已有默认支付信息!' % self.task_id)
                    except NoSuchElementException:
                        # 找不到对应的元素，即没有默认支付信息，则继续走支付信息的填写流程
                        self.old_cart_fill_in_payment_information()
            except NoSuchElementException as e:
                logger.info('[taskid: %d] 没有默认收货地址，将新建收货地址...' % self.task_id)
                self.old_cart_fill_in_address_information()
                time.sleep(random.uniform(2, 3))
                # self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                self.old_cart_fill_in_payment_information()

            WebDriverWait(driver=self.driver, timeout=15).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="place-order-button"]/button[1]'))
            )
            #点击"Confirm & Pay"
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_xpath('//div[@class="place-order-button"]/button[1]').click()
            logger.info('[taskid: %d] 点击了确认支付的按钮!' % self.task_id)
            #在项目的根目录下，新建一个文件夹confirm_pay_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
            confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
            if not os.path.exists(confirm_pay_dir):
                os.mkdir(confirm_pay_dir)
            confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_'+ str(self.task_id) + '.txt'
            f = open(confirm_pay_filename,'w',encoding='utf-8')
            f.close()
            logger.info('[taskid: %d] 同时创建了一个文件：%s' % (self.task_id, confirm_pay_filename))
            WebDriverWait(driver=self.driver, timeout=15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/a'))
            )
            time.sleep(20)
            #下单成功有两种不同的页面风格，此处需要兼容
            if 'payOnlineSuccess' in self.driver.current_url or 'Thank you for your payment' in self.driver.page_source:
                self.driver.save_screenshot('PaySuccess.png')
                logger.info('[taskid: %d] 下单成功！' % self.task_id)
                # logger.info("成功下单后的url:%s" % self.driver.current_url)
                # self.driver.back()
                time.sleep(2)
                self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
                WebDriverWait(driver=self.driver, timeout=15).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="nav-user-account"]/div[1]'))
                )
                element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
                # print(element)
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                time.sleep(1)
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//ul[@class="flyout-quick-entry"]/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//ul[@class="flyout-quick-entry"]/li[2]/a').click()
                time.sleep(4)
                self.do_after_place_order_success(confirm_pay_filename)

            elif 'payOnlineFailure' in self.driver.current_url:
                self.driver.save_screenshot('PayFailed.png')
                self.do_after_place_order_failed(confirm_pay_filename)

    #旧购物车的收货地址信息的创建流程
    def old_cart_fill_in_address_information(self):
        logger.info('[taskid: %d] 正在创建收货地址信息...' % self.task_id)
        WebDriverWait(driver=self.driver, timeout=15).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="sa-btn-group"]/a'))
        )
        FullName = self.task_info["address"]["FullName"]
        # 将Fullname中的非英文字符去除掉
        if re.search(r"[^A-Za-z\s]", FullName):
            FullName = re.sub(r"[^A-Za-z\s]", '', FullName)
        self.driver.find_element_by_name('contactPerson').send_keys(FullName)
        time.sleep(random.uniform(1, 2))
        country_selectBtn = Select(self.driver.find_element_by_name('country'))
        country_selectBtn.select_by_visible_text('United States')
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('address').send_keys(self.task_info["address"]["AddressLine1"])
        if self.task_info["address"]["AddressLine2"]:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('address2').send_keys(self.task_info["address"]["AddressLine2"])
        state_selectBtn = Select(
            self.driver.find_element_by_xpath('//input[@name="province"]/following-sibling::select[1]'))
        try:
            time.sleep(random.uniform(1, 2))
            state_selectBtn.select_by_visible_text(self.task_info["address"]["StateOrRegion"])
        except Exception:
            logger.info('[taskid: %d] 从接口获取的StateOrRegion信息对应不上，默认为下拉列表的第一个州或地区！' % self.task_id)
            StateOrRegion = self.driver.find_element_by_xpath(
                '//input[@name="province"]/following-sibling::select[1]/option[2]').text
            print(StateOrRegion)
            time.sleep(random.uniform(1, 2))
            state_selectBtn.select_by_visible_text(StateOrRegion)
        # 此处需要时间延迟，来加载城市的下拉列表
        time.sleep(6)
        city_selectBtn = Select(
            self.driver.find_element_by_xpath('//input[@name="city"]/following-sibling::select[1]'))
        # amazon的城市信息与速卖通的城市信息不一定匹配，比如大小写不一致，需要做异常处理
        try:
            time.sleep(random.uniform(1, 2))
            city_selectBtn.select_by_visible_text(self.task_info["address"]["City"])
        except Exception:
            logger.info('[taskid: %d] 从接口获取的城市信息对应不上，正在进行异常处理...' % self.task_id)
            try:
                city_text = self.task_info["address"]["City"].split()
                city_text[-1] = city_text[-1].lower()
                city = " ".join(city_text)
                print(city)
                time.sleep(random.uniform(1, 2))
                city_selectBtn.select_by_visible_text(city)
            except Exception:
                logger.info('[taskid: %d] 大小写处理失败，默认为下拉列表的第一个城市!' % self.task_id)
                city = self.driver.find_element_by_xpath(
                    '//input[@name="city"]/following-sibling::select[1]/option[2]').text
                # print(city)
                time.sleep(random.uniform(1, 2))
                city_selectBtn.select_by_visible_text(city)
        # city_selectBtn.select_by_visible_text('Jersey city')
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('zip').send_keys(self.task_info["address"]["PostalCode"].strip())
        # 电话号码需要处理，若有"+1"前缀，则去掉"+1"前缀
        PhoneNumber = self.task_info["address"]["PhoneNumber"]
        if re.search(r'\+1|\s|\(|\)|Â', PhoneNumber):
            PhoneNumber = re.sub(r'\+1|\s|\(|\)|Â', '', PhoneNumber)
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('mobileNo').send_keys(PhoneNumber)
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('isDefault').click()
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_xpath('//div[@class="sa-btn-group"]/a[1]').click()
        logger.info('[taskid: %d] 完成收货地址信息的创建！' % self.task_id)

    #旧购物车的支付信息的创建流程
    def old_cart_fill_in_payment_information(self):
        logger.info('[taskid: %d] 正在进入支付信息的填写流程...' % self.task_id)
        WebDriverWait(driver=self.driver, timeout=15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="cardNum"]'))
        )
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('cardNum').send_keys(self.task_info["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('dateM').send_keys(self.task_info["payment"]["ccMonth"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('dateY').send_keys(self.task_info["payment"]["ccYear"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('cvv2').send_keys(self.task_info["payment"]["cvv"])
        # 切割全名并判断长度
        FullName = self.task_info["address"]["FullName"]
        # 将Fullname中的非英文字符去除掉
        if re.search(r"[^A-Za-z\s]", FullName):
            FullName = re.sub(r"[^A-Za-z\s]", '', FullName)
        FullName_text = FullName.split()
        if len(FullName_text) == 1:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[0])
        else:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[1])
        # time.sleep(random.uniform(0.5, 1.0))
        # self.driver.find_element_by_name('saveinfo').click()
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_xpath('//div[@class="payment-line"]/button[1]').click()
        logger.info('[taskid: %d] 完成支付信息的填写!' % self.task_id)

    #删除新购物车中的非目标商品
    def new_cart_delete_other_goods_from_cart(self):
        items = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')
        # print(len(items))
        try:
            for item in items:
                good_detail_url = item.find_element_by_xpath('.//div[@class="product-title"]/a').get_attribute(
                    'href')
                if not re.search(self.target_id, good_detail_url):
                    # 非目标商品，直接从购物车删除
                    item.find_element_by_xpath('.//div[@class="opt-group"]/button[2]').click()
                    time.sleep(2)
                    # print('[taskid: %d] 点击删除！' % self.task_id)
                    # 点击ok
                    WebDriverWait(driver=self.driver, timeout=20).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//div[@class="next-dialog-footer next-align-left"]/button[1]'))
                    )
                    self.driver.find_element_by_xpath(
                        '//div[@class="next-dialog-footer next-align-left"]/button[1]').send_keys(
                        Keys.ENTER)
                    logger.info('[taskid: %d] 点击OK,确认删除非目标商品！' % self.task_id)
                    logger.info('[taskid: %d] 非目标商品已从购物车中删除！' % self.task_id)
                    time.sleep(5)
        # 点击删除后，网页会刷新，元素已发生改变，需捕获异常并处理
        except StaleElementReferenceException:
            self.new_cart_delete_other_goods_from_cart()

    #新购物车的下订单支付流程
    def new_cart_place_order(self):
        # 页面刷新，可有可无
        # self.driver.refresh()
        WebDriverWait(driver=self.driver, timeout=15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="SearchText"]'))
        )
        # 虽有只有一个商品，但是有两个<div class="store-list single"></div>,第一个为空
        try:
            item = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')[1]
        except IndexError:
            item = self.driver.find_elements_by_xpath('//div[@class="store-list single"]')[0]
        # print('item',item)
        good_detail_url = item.find_element_by_xpath('.//div[@class="product-title"]/a').get_attribute('href')
        # print(good_detail_url)
        if re.search(self.target_id, good_detail_url):
            input_elements = item.find_elements_by_xpath('.//input')
            # print('len(input_elements)',len(input_elements))
            quantity = input_elements[2].get_attribute('value')
            print('quantity', quantity)
            input_elements[1].click()
        # 发现一个有意思的情况，同一款商品同规格同颜色，多次添加到购物车，进入购物车查看时，商品数量依然为1。
        # 所以，商品数量的处理，可以简化。
        time.sleep(5)
        if quantity == '1':
            price_text = self.driver.find_element_by_xpath('//div[@class="total-price"]/dl/dd').text
            price = re.sub(r'US \$', '', price_text).strip()
            # 此处购物车中的待支付金额是否超出单笔最大额度，若超出，则终止刷单;但有时获取不到，为“”，捕获该异常并让程序继续运行；
            logger.info('[taskid: %d] 删除非目标商品后，购物车中查看到的待支付金额：%s' % (self.task_id, price))
            try:
                if float(price) > float(self.task_info["payment"]["single_max_trade"]):
                    logger.info('[taskid: %d] 删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!' % self.task_id)
                    # 新增刷单操作日志
                    data = {
                        "task_id": self.task_id,
                        "info": "删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!",
                        'ip': self.get_ip_info(proxies={'https': self.proxy})
                    }
                    self.create_task_order_log(json.dumps(data))
                    logger.info('[taskid: %d] 程序结束！' % self.task_id)
                    # 商品超出单笔支付额度，更新刷单状态为无法加购物车
                    self.do_when_good_off_shelf()
                    self.driver.quit()
                    sys.exit(0)
            except ValueError:
                logger.info('[taskid: %d] 获取订单金额出错，go on running!' % self.task_id)

            # self.driver.find_element_by_xpath('//button[@id="checkout-button"]').send_keys(Keys.ENTER)
            self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
            time.sleep(1)
            js = 'document.getElementById("checkout-button").click();'
            self.driver.execute_script(js)
            logger.info('[taskid: %d] 走下单流程！准备进入个人信息和支付信息的填写流程...' % self.task_id)
            time.sleep(6)
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
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="switch-to-full"]/a'))
                )
                # url = self.driver.find_element_by_xpath('//div[@class="switch-to-full"]/a').get_attribute('href')
                # print(url)
                # self.driver.get(url)
                # time.sleep(3)
                # 切换到全屏模式
                js = 'document.querySelector("div[class=switch-to-full] > a").click();'
                self.driver.execute_script(js)
                # self.driver.find_element_by_xpath('//div[@class="switch-to-full"]/a').send_keys(Keys.ENTER)
                time.sleep(5)
            except NoSuchFrameException:
                # logger.info('切换到收货信息填写的子iframe超时，程序退出！')
                logger.info('[taskid: %d] 不需切换到收货信息填写的子iframe!正在创建收货信息...' % self.task_id)
                # sys.exit(0)
            try:
                if "checked" in self.driver.find_element_by_xpath(
                        '//div[@role="radiogroup"]/div[1]/label[@dir="ltr"]').get_attribute('class'):
                    logger.info('[taskid: %d] 该用户已有默认收货信息！' % self.task_id)
            except NoSuchElementException:
                logger.info('[taskid: %d] 该用户无默认收货信息，正在创建收货信息...' % self.task_id)
                self.new_cart_fill_in_address_infomation()
            self.new_cart_fill_in_payment_information()
            time.sleep(5)
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@id="checkout-button"]'))
            )
            # "点击placc order"
            # self.driver.find_element_by_xpath('//button[@id="checkout-button"]').click()
            js = 'document.getElementById("checkout-button").click();'
            self.driver.execute_script(js)
            logger.info('[taskid: %d] 点击了确认支付的按钮!' % self.task_id)
            # 在项目的根目录下，新建一个文件夹confirm_pay_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
            confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
            if not os.path.exists(confirm_pay_dir):
                os.mkdir(confirm_pay_dir)
            confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            f = open(confirm_pay_filename, 'w', encoding='utf-8')
            f.close()
            logger.info('[taskid: %d] 同时创建了一个文件：%s' % (self.task_id, confirm_pay_filename))
            WebDriverWait(driver=self.driver, timeout=15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/a'))
            )
            time.sleep(20)
            # logger.info('last_ip:%s' % self.get_ip_info({'https': self.proxy}))
            # logger.info('last_cookies: %s' % json.dumps(self.driver.get_cookies()))
            if 'payOnlineSuccess' in self.driver.current_url or 'Thank you for your payment' in self.driver.page_source:
                self.driver.save_screenshot('PaySuccess.png')
                logger.info('[taskid: %d] 下单成功！' % self.task_id)
                # logger.info("成功下单后的url:%s" % self.driver.current_url)
                # self.driver.back()
                time.sleep(2)
                self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
                WebDriverWait(driver=self.driver, timeout=15).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="nav-user-account"]/div[1]'))
                )
                element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
                # print(element)
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                time.sleep(1)
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//ul[@class="flyout-quick-entry"]/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//ul[@class="flyout-quick-entry"]/li[2]/a').click()
                time.sleep(4)
                self.do_after_place_order_success(confirm_pay_filename)

            elif 'payOnlineFailure' in self.driver.current_url:
                self.driver.save_screenshot('PayFailed.png')
                self.do_after_place_order_failed(confirm_pay_filename)

    #新购物车收货地址信息的创建流程
    def new_cart_fill_in_address_infomation(self):
        # self.driver.refresh()
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'contactPerson'))
        )
        FullName = self.task_info["address"]["FullName"]
        #将Fullname中的非英文字符去除掉
        if re.search(r"[^A-Za-z\s]", FullName):
            FullName = re.sub(r"[^A-Za-z\s]", '', FullName)
        self.driver.find_element_by_id('contactPerson').send_keys(FullName)
        time.sleep(random.uniform(1, 2))
        # 电话号码需要处理，若有"+1"前缀，则去掉"+1"前缀
        PhoneNumber = self.task_info["address"]["PhoneNumber"]
        if re.search(r'\+1|\s|\(|\)|-|\+', PhoneNumber):
            PhoneNumber = re.sub(r'\+1|\s|\(|\)|-|\+', '', PhoneNumber)
        self.driver.find_element_by_id('mobileNo').send_keys(PhoneNumber)
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('address').send_keys(self.task_info["address"]["AddressLine1"])
        time.sleep(random.uniform(1, 2))
        if self.task_info["address"]["AddressLine2"]:
            self.driver.find_element_by_name('address2').send_keys(self.task_info["address"]["AddressLine2"])
        # else:
        #     self.driver.find_element_by_name('address2').send_keys("Al Bada'a Park 1")
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_xpath(
            '//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[1]/span/span/span/span[1]/span/input').click()
        time.sleep(random.uniform(2, 3))
        # 显示7个
        # self.driver.find_element_by_xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[1]/span/div/div/div/ul/li[5]').click()
        self.driver.find_element_by_xpath('//li[text()="California"]').click()
        time.sleep(random.uniform(2, 3))
        self.driver.find_element_by_xpath(
            '//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[2]/span/span/span/span[1]/span/input').click()
        # self.driver.find_element_by_xpath('//li[text()="3 points"]').click()
        time.sleep(random.uniform(2, 3))
        # self.driver.find_element_by_xpath(
        # '//*[@id="main"]/div[1]/div/div/div[2]/div/div[2]/div[3]/div/div/div[2]/span/div/div/div/ul/li[5]').click()
        # self.driver.find_element_by_xpath('//li[text()="3 points"]').click()
        self.driver.find_element_by_xpath('//li[text()="%s"]' % random.choice(City_List)).click()
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('zip').send_keys(self.task_info["address"]["PostalCode"].strip())
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_xpath('//input[@type="checkbox"]').click()
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_xpath('//div[@class="save"]/button[@type="button"]').click()
        logger.info('[taskid: %d] 完成收货地址信息的填写！' % self.task_id)

    #新购物车的支付信息的创建流程
    def new_cart_fill_in_payment_information(self):
        logger.info('[taskid: %d] 正在创建支付信息...' % self.task_id)
        # WebDriverWait(self.driver, 40).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@class="payment-info mini"]/div[@class="mini-title"]'))
        # )
        # self.driver.find_element_by_xpath('//div[@class="payment-info mini"]/div[@class="mini-title"]').click()
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'cardNo'))
        )
        # logger.info('payment_ip:%s' % self.get_ip_info({'https': self.proxy}))
        # logger.info('payment_cookies: %s' % json.dumps(self.driver.get_cookies()))
        self.driver.find_element_by_id('cardNo').send_keys(self.task_info["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(1, 2))
        # 卡持有者强制用空格隔开firstname 与 lastname
        # 切割全名并判断长度
        FullName = self.task_info["address"]["FullName"]
        # 将Fullname中的非英文字符去除掉
        if re.search(r"[^A-Za-z\s]", FullName):
            FullName = re.sub(r"[^A-Za-z\s]", '', FullName)
        FullName_text = FullName.split()
        print(FullName_text[0] + ' ' + FullName_text[0])
        if len(FullName_text) == 1:
            self.driver.find_element_by_id('cardHolder').send_keys(FullName_text[0] + ' ' + FullName_text[0])
            time.sleep(random.uniform(1, 2))
        else:
            self.driver.find_element_by_id('cardHolder').send_keys(FullName)
            time.sleep(random.uniform(1, 2))
        expireDate = self.task_info["payment"]["ccMonth"] + \
                     self.task_info["payment"]["ccYear"]
        self.driver.find_element_by_id('expire').send_keys(expireDate)
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_id('cvc').send_keys(self.task_info["payment"]["cvv"])
        time.sleep(2)
        # //*[@id="main"]/div[2]/div/div/div[2]/div[2]/div[2]/button
        self.driver.find_element_by_xpath('//div[@class="save"]/button[@type="button"]').click()
        logger.info('[taskid: %d] 完成支付信息的创建！' % self.task_id)

    #支付失败后再次填写支付信息，与首次下单时的支付信息填写流程相比，仅最后一个按钮有差异！
    def fill_in_and_save_payment_information_again(self):
        logger.info('[taskid: %d] 正在进入支付信息的填写流程...' % self.task_id)
        WebDriverWait(driver=self.driver, timeout=15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="cardNum"]'))
        )
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('cardNum').send_keys(
            self.task_info["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('dateM').send_keys(self.task_info["payment"]["ccMonth"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('dateY').send_keys(self.task_info["payment"]["ccYear"])
        time.sleep(random.uniform(1, 2))
        self.driver.find_element_by_name('cvv2').send_keys(self.task_info["payment"]["cvv"])
        # 切割全名并判断长度
        FullName_text = self.task_info["address"]["FullName"].split()
        if len(FullName_text) == 1:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[0])
        else:
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(1, 2))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[1])
        time.sleep(random.uniform(1, 2))
        try:
            self.driver.find_element_by_xpath('//div[@class="checkout-button"]/button[2]').send_keys(Keys.ENTER)
            logger.info('[taskid: %d] 完成支付信息的填写!' % self.task_id)
        except Exception as e:
            print(e)

    #当目标商品下架无法加入购物车，或者asin无效时，更新刷单状态，并退出。
    def do_when_good_off_shelf(self):
        # 更新刷单状态
        brushing_data = {
            str(self.task_id): {
                "task_id": self.task_id,
                "status": 26,
            }
        }
        self.update_brushing_status(json.dumps(brushing_data))
        # 新增刷单操作日志
        log_data = {
            "task_id": self.task_id,
            "info": "商品异常，无法添加至购物车，刷单终止",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(log_data))

    # 当ASIN无效时，更新刷单状态，终止刷单
    def do_when_asin_is_invalid(self):
        # 更新刷单状态
        brushing_data = {
            str(self.task_id): {
                "task_id": self.task_id,
                "status": 21,
            }
        }
        self.update_brushing_status(json.dumps(brushing_data))
        # 新增刷单操作日志
        log_data = {
            "task_id": self.task_id,
            "info": "ASIN无效，找不到指定产品，终止刷单！",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(log_data))

    #当再支付次数达到3次时，更新刷单状态，自动失效当前账户，并解绑
    def do_when_the_number_of_repyments_has_reached_three_times(self):
        # 更新刷单状态
        brushing_data = {
            str(self.task_id): {
                "task_id": self.task_id,
                "status": 24,
            }
        }
        self.update_brushing_status(json.dumps(brushing_data))
        # 新增刷单操作日志
        log_data = {
            "task_id": self.task_id,
            "info": "再支付次数已达三次，自动失效当前账号，并解绑！",
            'ip': self.get_ip_info(proxies={'https': self.proxy})
        }
        self.create_task_order_log(json.dumps(log_data))

    #确认订单支付成功后，获取订单信息，更新刷单状态，插入刷单日志，最后删除缓存文件
    def do_after_place_order_success(self,confirm_pay_filename):
        logger.info('[taskid: %d] 确认订单已成功支付，正在获取订单的相关信息，更新刷单状态...' % self.task_id)
        order_no = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]//tr[1]/td[2]/p[1]/span[2]').text
        logger.info("[taskid: %d] 订单号为：%s" % (self.task_id, order_no))
        price_text = self.driver.find_element_by_xpath(
            '//*[@id="buyer-ordertable"]/tbody[1]/tr[1]/td[4]/div/p[2]').text.strip()
        actual_order_amount = re.sub(r'\$ ', '', price_text)
        logger.info('[taskid: %d] 订单总价：%s' % (self.task_id, actual_order_amount))
        payment_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info('[taskid: %d] 下单时间：%s' % (self.task_id, payment_date))
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
        logger.info('[taskid: %d] 删除了一个文件：%s' % (self.task_id, confirm_pay_filename))

    #确认订单支付失败后，插入刷单日志
    def do_after_place_order_failed(self, confirm_pay_filename):
        logger.info('[taskid: %d] 支付失败！' % self.task_id)
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

    #新购物车的流程，包括购物车中的商品剔除，以及后续下单的整个流程
    def do_new_cart_process(self):
        self.new_cart_delete_other_goods_from_cart()
        self.new_cart_place_order()

    # 旧购物车的流程，包括购物车中的商品剔除，以及后续下单的整个流程
    def do_old_cart_process(self):
        self.old_cart_delete_other_goods_from_cart()
        self.old_cart_place_order()

    # 插入账号登录日志
    def insert_account_login_log(self, data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressInsertAccountLoginLog'
        post(requests.session(), url=url, post_data=data)
        logger.info('[taskid: %d] 账户登录日志已成功插入！' % self.task_id)

    # 当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
    def update_account_login_success_info(self, data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressUpdateAccountLoginSuccessInfo'
        post(requests.session(), url=url, post_data=data)
        logger.info('[taskid: %d] 对应账户的header和cookies字段已成功修改!' % self.task_id)

    # 更新刷单状态
    def update_brushing_status(self, data):
        # 测试机
        # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        # 线上
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        resp = post(requests.session(), url=url, post_data=data)
        if resp.json()['msg'] == 'ok':
            logger.info('[taskid: %d] 刷单状态更新成功！' % self.task_id)
        else:
            logger.info('[taskid: %d] 刷单状态更新失败！' % self.task_id)

    # 新增刷单操作日志
    def create_task_order_log(self, data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
        resp = post(requests.session(), url=url, post_data=data)
        if resp.json()['status'] == 0:
            logger.info('[taskid: %d] 新增刷单操作日志成功!' % self.task_id)
        else:
            logger.info('[taskid: %d] 新增刷单操作日志失败!' % self.task_id)

    #更新商品排名(所在的page和rank)
    def update_page_and_rank(self, data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressUpdatePageAndRank'
        resp = post(requests.session(), url=url, post_data=data)
        print(resp.text)
        if resp.json()['code'] == 200:
            logger.info('[taskid: %d] 更新商品排名成功!' % self.task_id)
        else:
            logger.info('[taskid: %d] 更新商品排名失败!' % self.task_id)


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


def main(task_id, task_info):
    spider = AliexpressOrderSpider(task_id, task_info)
    spider.run()


if __name__ == '__main__':
    # 多线程循环模式：默认一次最多获取2个待刷单任务,自动根据获取到的任务数量创建相应数量的线程数，去执行各自分配到的刷单任务；当获取不到任务时，程序休眠10分钟。
    while True:
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=1&limit=8'
        resp = get(requests.session(), url=url)
        if resp:
            try:
                if resp.json() == []:
                    # logger.info('未获取到待刷单列表的数据，程序结束！')
                    # sys.exit(0)
                    logger.info('任务系统未获取到当前时间的任务，程序[sleep 10m]...')
                    time.sleep(60 * 10)
                else:
                    tasks_all = resp.json()
                    task_item_list = []
                    for task_id_str in tasks_all:
                        item = (int(task_id_str), tasks_all[task_id_str])
                        task_item_list.append(item)
                    logger.info('成功获取到%d条待刷单的数据！' % len(task_item_list))
                    logger.info('将创建%d个进程来分别执行刷单任务!' % len(task_item_list))
                    processes = []
                    for item in task_item_list:
                        p = Process(target=main, args=item)
                        processes.append(p)
                        p.start()
                        #每个进程创建间隔30秒
                        # time.sleep(10)
                    # 回收线程
                    for p in processes:
                        p.join()
            except json.decoder.JSONDecodeError:
                pass
        else:
            logger.info('任务系统出错，程序[sleep 30s]...')
            time.sleep(30)