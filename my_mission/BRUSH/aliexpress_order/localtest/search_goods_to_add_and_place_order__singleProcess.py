import os
import random
import re
import json
import sys
import time
import  datetime
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, \
    NoSuchFrameException, WebDriverException
from mytools.tools import get_oxylabs_proxy, get
from mytools.utils import logger

logger = logger('place_order')

class AliexpressOrderSpider():
    def __init__(self,task_infos,task_id):
        self.proxy = get_oxylabs_proxy('us',_city=None,_session=random.random())['https']
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = self.create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.options = webdriver.ChromeOptions()
        self.task_infos = task_infos
        self.task_id = task_id
        self.options.add_argument('user-agent="%s"' % json.loads(self.task_infos[str(self.task_id)]['account']['header'])['user-agent'] )
        self.options.add_extension(proxyauth_plugin_path)
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        #headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        # 设置不加载图片
        self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(options=self.options)
        self.target_id = self.task_infos[str(self.task_id)]["asin"]["asin"]
        #self.good_detail_urls属性，用于绑定目标商品所在列表页的所有商品的详情链接
        self.good_detail_urls = None
        #self.target_good_detail_url属性，用于绑定目标商品的详情链接
        self.target_good_detail_url = None

    def run(self):
        try:
            self.driver.get('http://www.aliexpress.com/')
            #过滤弹窗
            try:
                WebDriverWait(self.driver, 40).until(
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
            # time.sleep(random.randint(1,3))
            self.driver.find_element_by_id('fm-login-id').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_email"])
            time.sleep(random.randint(1,5))
            self.driver.find_element_by_id('fm-login-password').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_password"])
            time.sleep(random.randint(1,5))
            self.driver.find_element_by_id('fm-login-submit').click()
            #此处判断登录过程中是否有滑块验证码，有则终止程序
            if 'display: block' in self.driver.find_element_by_id('fm-login-checkcode-title').get_attribute('style'):
                logger.info('登录时发现滑块验证码，程序退出！')
                self.driver.quit()
                sys.exit(0)
            #弹窗处理
            try:
                WebDriverWait(self.driver, 40).until(
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
                        # "order_no": '',
                        # "payment_date": '',
                        # "actual_order_amount": 0.00
                    }
                }
                self.update_brushing_status(json.dumps(brushing_data))
                self.driver.quit()
                logger.info('程序退出！')
                sys.exit(0)

            WebDriverWait(self.driver,40).until(
                EC.element_to_be_clickable((By.ID,"search-key"))
            )
            self.driver.find_element_by_id('search-key').send_keys(self.task_infos[str(self.task_id)]["asin"]["keywords"])
            time.sleep(random.uniform(0.5, 1.5))
            self.driver.find_element_by_class_name('search-button').send_keys(Keys.ENTER)

            for i in range(1,3):
                 #弹窗处理
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                    )
                    self.driver.find_element_by_class_name('close-layer').click()
                except TimeoutException:
                    pass
                WebDriverWait(driver=self.driver, timeout=30).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@class="ui-pagination-active"]/following-sibling::a[1]'))
                )
                source = self.driver.page_source
                result = self.parse_list_page(source)
                if result:
                    self.get_detail_page_to_add(self.target_good_detail_url)
                    break
                else:
                    next_page_btn = self.driver.find_element_by_xpath('//span[@class="ui-pagination-active"]/following-sibling::a[1]')
                    next_page_btn.click()
                    logger.info('第%d列表搜索页没找到目标商品，正在跳转到第%d列表搜索页...'% (i,i+1))
                    time.sleep(3)
            else:
                logger.info('前2页中没有找到目标商品，正在拼接目标商品的详情url,进行特殊处理...')
                self.target_good_detail_url = 'https://www.aliexpress.com/item/-a/'+ self.target_id + '.html'
                self.get_detail_page_to_add(self.target_good_detail_url)

            self.add_other_goods()
            self.delete_other_goods_from_cart()
            brushing_data = self.place_order()
            # 更新刷单状态. place_order（）成功下单时返回json数据，否则返回None.
            if brushing_data:
                self.update_brushing_status(brushing_data)
                # 新增刷单操作日志
                data = {
                    "task_id": self.task_id,
                    "info": "下单成功！",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(data))
            self.driver.quit()
            logger.info('当前账户操作完毕，关闭当前浏览器！')
        except NoSuchFrameException:
            logger.info('切换到登录的frame超时，正在重新请求主页，继续执行登录操作')
            self.run()
        # except NoSuchElementException:
        #     logger.info('定位不到对应的元素，将重新访问首页，继续走流程！')
        #     self.run()
        # except WebDriverException:
        #     logger.info('点击下一页连接时出错，将重新访问首页，继续走流程！')
        #     self.run()
        except (TimeoutException,WebDriverException) as e:
            # 在操作过程中等待超时，先退出当前登录状态，再重新执行run方法回调，重新走流程。也可直接结束程序，只适合在多线程的情况下操作。
            logger.info('等待超时,或者元素位未完全加载导致点击出错，正在检查登录状态，若已登录，则退出登录状态,重新走流程！')
            self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
            time.sleep(3)
            try:
                element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
                actions = ActionChains(self.driver)
                actions.move_to_element(element)
                actions.perform()
                WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="nav-user-account"]/div[2]/div[1]/a'))
                )
                self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[2]/div[1]/a').click()
                time.sleep(4)
                # 此处必须有关闭浏览器的操作，否则登录状态退出不彻底，不能正常run回调
                self.driver.close()
            except NoSuchElementException:
                pass
            #是否需要close?
            self.run()

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
                self.good_detail_urls = good_detail_urls
                # logger.info('目标商品所在列表页的所有商品的详情链接是：%s' % self.good_detail_urls)
                return True
        return False

    #访问商品详情页，加入购物车
    def get_detail_page_to_add(self,url):
        self.driver.get(url)
        #弹窗处理
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
            )
            self.driver.find_element_by_class_name('close-layer').send_keys(Keys.ENTER)
        except TimeoutException:
            pass
        try:
            #有些商品是没有颜色可选的，需要做异常处理
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-1"]/li[1]/a'))
            )
            self.driver.find_element_by_xpath('//ul[@id="j-sku-list-1"]/li[1]/a').send_keys(Keys.ENTER)
        except TimeoutException:
            pass
        time.sleep(random.randint(1,4))

        try:
            #有些商品是没有规格可选的，需要做异常处理
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-2"]/li[1]/a'))
            )
            self.driver.find_element_by_xpath('//ul[@id="j-sku-list-2"]/li[1]/a').click()
        except TimeoutException:
            pass
        time.sleep(random.randint(1,4))
        self.driver.find_element_by_id('j-add-cart-btn').send_keys(Keys.ENTER)
        if self.target_id in url:
            logger.info('目标商品已成功添加到购物车！')
        else:
            logger.info('非目标商品已成功添加到购物车！')
        #关闭添加购物车后的提示窗口
        try:
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
            )
            self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
        except TimeoutException:
            pass

    #购物车中添加其他非目标商品
    def add_other_goods(self):
        self.driver.back()
        while True:
            other_good_detail_url ='https:' + random.choice(self.good_detail_urls)
            # if other_good_detail_url != self.target_good_detail_url:
            #     break
            if not re.search(self.target_id, other_good_detail_url):
                break
        self.get_detail_page_to_add(other_good_detail_url)

    #删除购物车中的非目标商品
    def delete_other_goods_from_cart(self):
        WebDriverWait(driver=self.driver, timeout=20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="nav-cart nav-cart-box"]/a[1]'))
        )
        self.driver.find_element_by_xpath('//div[@class="nav-cart nav-cart-box"]/a[1]').send_keys(Keys.ENTER)
        items = self.driver.find_elements_by_class_name("item-group-wrapper")
        try:
            for item in items:
                good_detail_url = item.find_element_by_xpath('.//a[@target="_blank"]').get_attribute('href')
                if not re.search(self.target_id,good_detail_url):
                    #非目标商品，直接从购物车删除
                    item.find_element_by_xpath('.//div[@class="product-remove"]/form[1]/a').click()
                    logger.info('非目标商品已从购物车中删除！')
                    time.sleep(2)
        #点击删除后，网页会刷新，元素已发生改变，需捕获异常并处理
        except StaleElementReferenceException:
            self.delete_other_goods_from_cart()

    #下订单支付流程
    def place_order(self):
        #页面刷新，可有可无
        self.driver.refresh()
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
            logger.info('删除非目标商品后，购物车中查看到的待支付金额：%s'% price)
            if float(price) > float(self.task_infos[str(self.task_id)]["payment"]["single_max_trade"]):
                logger.info('删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!')
                # 新增刷单操作日志
                data = {
                    "task_id": self.task_id,
                    "info": "删除非目标商品后，购物车中查看到的待支付金额超出单笔最大额度，终止刷单!",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(data))
                logger.info('程序结束！')
                sys.exit(0)
            self.driver.find_element_by_xpath('//div[@class="product-price-info3"]/a[1]').send_keys(Keys.ENTER)

            logger.info('走下单流程！准备进入个人信息和支付信息的填写流程...')
            #跳转到个人信息填写页面,需要加以判断，是否已有地址信息
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="page"]/div[1]/div[1]/ol/li[1]'))
            )
            try:
                default_address_info_element = self.driver.find_element_by_xpath('//*[@id="address-main"]/div[2]/ul/li/div/div[1]')
                if 'selected' in default_address_info_element.get_attribute('class'):
                    logger.info('已有默认收货地址！')
                    self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                    time.sleep(3)
                    try:
                        # if self.driver.find_element_by_xpath('//*[@id="j-payment-method"]/div[4]/ul/li[1]/span/span'):
                        if self.driver.find_element_by_xpath('//ul[@class="pay-method-list"]/li[1]/span/span'):
                            logger.info('已有默认支付信息!')
                    except NoSuchElementException:
                        # 找不到对应的元素，即没有默认支付信息，则继续走支付信息的填写流程
                        self.fill_in_and_save_payment_information()
            except NoSuchElementException as e:
                logger.info('没有默认收货地址，正在新建收货地址...')
                WebDriverWait(driver=self.driver, timeout=30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="sa-btn-group"]/a'))
                )
                self.driver.find_element_by_name('contactPerson').send_keys(self.task_infos[str(self.task_id)]["address"]["FullName"])
                time.sleep(random.uniform(0.5, 1.0))
                country_selectBtn = Select(self.driver.find_element_by_name('country'))
                country_selectBtn.select_by_visible_text('United States')
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.find_element_by_name('address').send_keys(self.task_infos[str(self.task_id)]["address"]["AddressLine1"])
                if self.task_infos[str(self.task_id)]["address"]["AddressLine2"]:
                    time.sleep(random.uniform(0.5, 1.0))
                    self.driver.find_element_by_name('address2').send_keys(self.task_infos[str(self.task_id)]["address"]["AddressLine2"])
                state_selectBtn = Select(
                    self.driver.find_element_by_xpath('//input[@name="province"]/following-sibling::select[1]'))
                try:
                    time.sleep(random.uniform(0.5, 1.0))
                    state_selectBtn.select_by_visible_text(self.task_infos[str(self.task_id)]["address"]["StateOrRegion"])
                except Exception:
                    logger.info('从接口获取的StateOrRegion信息对应不上，默认为下拉列表的第一个州或地区！')
                    StateOrRegion = self.driver.find_element_by_xpath('//input[@name="province"]/following-sibling::select[1]/option[2]').text
                    print(StateOrRegion)
                    time.sleep(random.uniform(0.5, 1.0))
                    state_selectBtn.select_by_visible_text(StateOrRegion)
                # 此处需要时间延迟，来加载城市的下拉列表
                time.sleep(12)
                city_selectBtn = Select(
                    self.driver.find_element_by_xpath('//input[@name="city"]/following-sibling::select[1]'))
                #amazon的城市信息与速卖通的城市信息不一定匹配，比如大小写不一致，需要做异常处理
                try:
                    time.sleep(random.uniform(0.5, 1.0))
                    city_selectBtn.select_by_visible_text(self.task_infos[str(self.task_id)]["address"]["City"])
                except Exception:
                    logger.info('从接口获取的城市信息对应不上，正在进行异常处理...')
                    try:
                        city_text = self.task_infos[str(self.task_id)]["address"]["City"].split()
                        city_text[-1] = city_text[-1].lower()
                        city = " ".join(city_text)
                        print(city)
                        time.sleep(random.uniform(0.5, 1.0))
                        city_selectBtn.select_by_visible_text(city)
                    except Exception:
                        logger.info('大小写处理失败，默认为下拉列表的第一个城市!')
                        city = self.driver.find_element_by_xpath('//input[@name="city"]/following-sibling::select[1]/option[2]').text
                        # print(city)
                        time.sleep(random.uniform(0.5, 1.0))
                        city_selectBtn.select_by_visible_text(city)
                # city_selectBtn.select_by_visible_text('Jersey city')
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.find_element_by_name('zip').send_keys(self.task_infos[str(self.task_id)]["address"]["PostalCode"])
                #电话号码需要处理，若有"+1"前缀，则去掉"+1"前缀
                PhoneNumber = self.task_infos[str(self.task_id)]["address"]["PhoneNumber"]
                if re.match(r'\+1',PhoneNumber):
                    PhoneNumber = re.sub(r'\+1','',PhoneNumber)
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.find_element_by_name('mobileNo').send_keys(PhoneNumber)
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.find_element_by_name('isDefault').click()
                time.sleep(random.uniform(0.5, 1.0))
                self.driver.find_element_by_xpath('//div[@class="sa-btn-group"]/a[1]').click()
                self.fill_in_and_save_payment_information()

            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="place-order-button"]/button[1]'))
            )
            #点击"Confirm & Pay"
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_xpath('//div[@class="place-order-button"]/button[1]').click()
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div[1]/a'))
            )
            time.sleep(15)
            if 'payOnlineSuccess' in self.driver.current_url:
                self.driver.save_screenshot('PaySuccess.png')
                logger.info('下单成功！')
                # logger.info("成功下单后的url:%s" % self.driver.current_url)
                payment_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info('下单时间：%s' % payment_date)
                self.driver.back()
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
                order_no = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]//tr[1]/td[2]/p[1]/span[2]').text
                logger.info("订单号为：%s" % order_no)
                price_text = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody[1]/tr[1]/td[4]/div/p[2]').text.strip()
                actual_order_amount = re.sub(r'\$ ', '', price_text)
                logger.info('订单总价：%s' % actual_order_amount)
                brushing_data = {
                    str(self.task_id):{
                        "task_id":self.task_id,
                        "status":2,
                        "order_no":order_no,
                        "payment_date":payment_date,
                        "actual_order_amount":float(actual_order_amount)
                    }
                }
                # print(json.dumps(data))
                return json.dumps(brushing_data)
            else:
                logger.info('支付失败！')
                self.driver.save_screenshot('PayFailed.png')
                logger.info('支付失败的url:%s' % self.driver.current_url)
                #新增刷单操作日志
                data = {
                    "task_id": self.task_id,
                    "info": "支付失败！导致下单失败！",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(data))

    # 填写并保存支付信息
    def fill_in_and_save_payment_information(self):
        logger.info('正在进入支付信息的填写流程...')
        WebDriverWait(driver=self.driver, timeout=60).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@name="cardNum"]'))
        )
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_name('cardNum').send_keys(self.task_infos[str(self.task_id)]["payment"]["CreditCardNumber"])
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_name('dateM').send_keys(self.task_infos[str(self.task_id)]["payment"]["ccMonth"])
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_name('dateY').send_keys(self.task_infos[str(self.task_id)]["payment"]["ccYear"])
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_name('cvv2').send_keys(self.task_infos[str(self.task_id)]["payment"]["cvv"])
        # 切割全名并判断长度
        FullName_text = self.task_infos[str(self.task_id)]["address"]["FullName"].split()
        if len(FullName_text) == 1:
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[0])
        else:
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_name('cardHolderF').send_keys(FullName_text[0])
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_name('cardHolderL').send_keys(FullName_text[1])
        # time.sleep(random.uniform(0.5, 1.0))
        # self.driver.find_element_by_name('saveinfo').click()
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_xpath('//div[@class="payment-line"]/button[1]').click()
        logger.info('完成支付信息的填写!')

    # 插入账号登录日志
    @staticmethod
    def insert_account_login_log(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressInsertAccountLoginLog'
        requests.post(url, data)
        logger.info('账户登录日志已成功插入！')

    # 当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
    @staticmethod
    def update_account_login_success_info(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressUpdateAccountLoginSuccessInfo'
        requests.post(url, data)
        logger.info('对应账户的header和cookies字段已成功修改!')

    #更新刷单状态
    @staticmethod
    def update_brushing_status(data):
        # 测试机
        # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        # 线上
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        resp = requests.post(url=url,data=data)
        print(resp.text)
        if resp.json()['msg'] == 'ok':
            logger.info('刷单状态更新成功！')
        else:
            logger.info('刷单状态更新失败！')

    #新增刷单操作日志
    @staticmethod
    def create_task_order_log(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
        resp = requests.post(url,data)
        if resp.json()['status'] == 0:
            logger.info('新增刷单操作日志成功!')
        else:
            logger.info('新增刷单操作日志失败!')

    #获取当前ip信息，返回字符串
    @staticmethod
    def get_ip_info(proxies):
        getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        if getIpInfo:
            ipInfo = json.loads(getIpInfo.text)
            ip = ipInfo['ip']
        else:
            ip = '未获取到ip'
        return ip

    def create_proxyauth_extension(self, proxy_host, proxy_port,
                                   proxy_username, proxy_password,
                                   scheme='http', plugin_path=None):
        import string
        import zipfile

        if plugin_path is None:
            plugin_path = os.path.abspath(os.path.dirname(__file__)) + "/vimm_chrome_proxyauth_plugin.zip"

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com"]
                    }
                  };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """
        ).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )
        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        zipf = zipfile.ZipFile(plugin_path)
        # print(zipf.namelist())
        return plugin_path

def main():
    #单进程模式：循环获取待刷单任务，一次获取一个；若获取不到任务，程序退出。
    while True:
        #测试机地址，获取刷单任务，返回字典格式的json串
        # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=1&limit=1&debug_list=0&debug_allot=0'
        #线上地址，获取刷单任务，返回字典格式的json串
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=1&limit=1'
        resp = requests.get(url)
        # if json.loads(resp.text,strict=False) == []:
        try:
            # if 'status' in resp.json():
            if resp.json() == []:
                logger.info('未获取到待刷单列表的数据，程序结束！')
                sys.exit(0)
            else:
                logger.info('成功获取到一条待刷单的数据！')
                task_infos = resp.json()
                # print(task_infos)
                for key in task_infos.keys():
                    task_id = int(key)
                spider = AliexpressOrderSpider(task_infos,task_id)
                spider.run()
        except json.decoder.JSONDecodeError:
            pass 


if __name__ == '__main__':
    main()