import random
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from mysql_helper import Mysql_helper
from selenium.webdriver.common.keys import Keys
from lxml import etree
from selenium.common.exceptions import StaleElementReferenceException
from mytools.utils import logger

mysql_helper = Mysql_helper()
item = mysql_helper.query4One()

class AliexpressSpider():
    def __init__(self,keyword,id):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="%s"' % json.loads(item[4])['user-agent'] )
        self.driver = webdriver.Chrome(options=self.options)
        self.keyword = keyword
        self.id = id
        #self.good_detail_urls属性，用于存放目标商品所在列表页的所有商品的详情链接
        self.good_detail_urls = None
        #self.target_good_detail_url属性，用于绑定目标商品的详情链接
        self.target_good_detail_url = None
        # print('user-agent="%s"' % json.loads(item[4])['user-agent'])
        self.logger = logger('order')

    def run(self):
        self.driver.get('http://www.aliexpress.com/')
        try:
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
            )
            self.driver.find_element_by_class_name('close-layer').click()
        except Exception:
            pass
        # for cookie in json.loads(item[3]):
        #     self.driver.add_cookie(cookie)
        #页面刷新
        # self.driver.refresh()
        # try:
        #     WebDriverWait(self.driver, 40).until(
        #         EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
        #     )
        #     self.driver.find_element_by_class_name('close-layer').click()
        # except Exception:
        #     pass
        # self.driver.execute_script('window.scrollTo(document.body.scrollWidth,0 );')
        # WebDriverWait(self.driver, 40).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@id="nav-user-account"]/div[1]/div[1]/span[1]/a[1]'))
        # )
        # self.driver.find_element_by_xpath('/div[@id="nav-user-account"]/div[1]/div[1]/span[1]/a[1]').click()
        # element = self.driver.find_element_by_xpath('//div[@id="nav-user-account"]/div[1]')
        # print(element)
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element)
        # actions.perform()
        # time.sleep(1)
        # WebDriverWait(self.driver, 40).until(
        #     EC.element_to_be_clickable((By.XPATH, '//div[@id="nav-user-account"]/div[2]/div[2]/p[2]/a'))
        # )
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="register-btn"]/a'))
        )
        #点击登录
        self.driver.find_element_by_xpath('//span[@class="register-btn"]/a').click()
        # WebDriverWait(self.driver, 40).until(
        #     EC.frame_to_be_available_and_switch_to_it
        # )
        time.sleep(3)
        #切换到子iframe
        self.driver.switch_to.frame('alibaba-login-box')
        #输入登录信息
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="fm-login-id"]'))
        )
        self.driver.find_element_by_id('fm-login-id').send_keys(item[1])
        self.driver.find_element_by_id('fm-login-password').send_keys(item[2])
        self.driver.find_element_by_id('fm-login-submit').click()

        #弹窗处理
        try:
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
            )
            self.driver.find_element_by_class_name('close-layer').click()
        except Exception:
            pass

        WebDriverWait(self.driver,40).until(
            EC.element_to_be_clickable((By.ID,"search-key"))
        )
        self.driver.find_element_by_id('search-key').send_keys(self.keyword)
        self.driver.find_element_by_class_name('search-button').send_keys(Keys.ENTER)
        for i in range(1,6):
            source = self.driver.page_source
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@class="ui-pagination-active"]/following-sibling::a[1]'))
            )
            result = self.parse_list_page(source)
            if result:
                self.get_detail_page_to_add(self.target_good_detail_url)
                self.add_other_goods()
                self.delete_other_goods_from_cart()
                self.place_order()
                break
            else:
                next_page_btn = self.driver.find_element_by_xpath('//span[@class="ui-pagination-active"]/following-sibling::a[1]')
                next_page_btn.click()
                # print('第%d列表搜索页没找到目标商品，正在跳转到第%d列表搜索页'% (i,i+1))
                self.logger.info('第%d列表搜索页没找到目标商品，正在跳转到第%d列表搜索页'% (i,i+1))
                time.sleep(3)

    def parse_list_page(self,html):
        parseHtml = etree.HTML(html)
        good_detail_urls = parseHtml.xpath('//ul[@id="hs-below-list-items"]/li/div[1]/div[1]/div/a/@href')
        # print("当前页所有商品的详情链接是",good_detail_urls)
        self.logger.info("当前页所有商品的详情链接是:%s" % good_detail_urls)
        for detail_url in good_detail_urls:
            if re.search(self.id,detail_url):
                detail_url = "https:" + detail_url
                self.target_good_detail_url = detail_url
                # print('目标商品的详情链接是：',self.target_good_detail_url)
                self.logger.info('目标商品的详情链接是：%s' % self.target_good_detail_url)
                self.good_detail_urls = good_detail_urls
                # print('目标商品所在列表页的所有商品的详情链接是：',self.good_detail_urls)
                self.logger.info('目标商品所在列表页的所有商品的详情链接是：%s' % self.good_detail_urls)
                # self.get_detail_page(detail_url)
                return True
        return False

    def get_detail_page_to_add(self,url):
        self.driver.get(url)
        try:
            #有些商品是没有颜色可选的，需要做异常处理
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[@id="j-sku-list-1"]/li[1]/a/img'))
            )
            self.driver.find_element_by_xpath('//ul[@id="j-sku-list-1"]/li[1]/a/img').click()
        except Exception:
            pass
        time.sleep(random.randint(1,4))
        self.driver.find_element_by_xpath('//ul[@id="j-sku-list-2"]/li[1]/a').click()
        time.sleep(random.randint(1,4))
        self.driver.find_element_by_id('j-add-cart-btn').send_keys(Keys.ENTER)
        if self.id in url:
            # print('目标商品已成功添加到购物车')
            self.logger.info('目标商品已成功添加到购物车')
        else:
            # print('非目标商品已成功添加到购物车')
            self.logger.info('非目标商品已成功添加到购物车')
        #关闭添加购物车后的提示窗口
        try:
            WebDriverWait(driver=self.driver, timeout=10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="ui-window-close"]'))
            )
            self.driver.find_element_by_xpath('//a[@class="ui-window-close"]').click()
        except Exception:
            pass

    def add_other_goods(self):
        self.driver.back()
        while True:
            other_good_detail_url ='https:' + random.choice(self.good_detail_urls)
            if other_good_detail_url != self.target_good_detail_url:
                break
        self.get_detail_page_to_add(other_good_detail_url)

    def delete_other_goods_from_cart(self):
        WebDriverWait(driver=self.driver, timeout=20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="nav-cart nav-cart-box"]/a[1]'))
        )
        self.driver.find_element_by_xpath('//div[@class="nav-cart nav-cart-box"]/a[1]').send_keys(Keys.ENTER)
        items = self.driver.find_elements_by_class_name("item-group-wrapper")
        # print(len(items))
        try:
            for item in items:
                good_detail_url = item.find_element_by_xpath('.//a[@target="_blank"]').get_attribute('href')
                if not re.search(self.id,good_detail_url):
                    #非目标商品，直接从购物车删除
                    item.find_element_by_xpath('.//div[@class="product-remove"]/form[1]/a').click()
                    # print('非目标商品已从购物车中删除！')
                    self.logger.info('非目标商品已从购物车中删除！')
                    time.sleep(2)
        except StaleElementReferenceException:
            self.delete_other_goods_from_cart()

    def place_order(self):
        #页面刷新，可有可无
        self.driver.refresh()
        WebDriverWait(driver=self.driver, timeout=20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="product-price-info3"]/a[1]'))
        )
        quantity = self.driver.find_element_by_xpath('//input[@readonly="readonly"]').get_attribute('value')
        if quantity == '1':
            price_text = self.driver.find_element_by_xpath('//span[@class="total-price ui-cost notranslate"]/b').text
            price = re.sub(r'US \$','',price_text)
            # print('订单总价：',price)
            self.logger.info('订单总价：%s' % price)
            self.driver.find_element_by_xpath('//div[@class="product-price-info3"]/a[1]').click()

            #可能先跳转到用户登录的ifame，但登录成功后需要进行刮图验证码和手机验证码的双重验证，暂无有效识别方法。具体原因可能是同一IP注册用户数量的过多，导致的验证。
            # try:
            #     time.sleep(3)
            #     self.driver.switch_to.frame('alibaba-login-box')
            #     #输入登录信息
            #     WebDriverWait(self.driver, 40).until(
            #         EC.element_to_be_clickable((By.XPATH, '//input[@id="fm-login-id"]'))
            #     )
            #     self.driver.find_element_by_id('fm-login-id').send_keys(item[1])
            #     self.driver.find_element_by_id('fm-login-password').send_keys(item[2])
            #     self.driver.find_element_by_id('fm-login-submit').click()
            # except Exception:
            #     pass

            # 跳转到个人信息填写页面
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="sa-btn-group"]/a'))
            )
            self.driver.find_element_by_name('contactPerson').send_keys('xiaoqiang')
            country_selectBtn = Select(self.driver.find_element_by_name('country'))
            country_selectBtn.select_by_visible_text('United States')
            self.driver.find_element_by_name('address').send_keys('42TH STREET')
            self.driver.find_element_by_name('address2').send_keys('910 1FL')
            state_selectBtn = Select(
                self.driver.find_element_by_xpath('//input[@name="province"]/following-sibling::select[1]'))
            state_selectBtn.select_by_visible_text('New York')
            # 此处需要时间延迟，来加载城市的下拉列表
            time.sleep(2)
            city_selectBtn = Select(
                self.driver.find_element_by_xpath('//input[@name="city"]/following-sibling::select[1]'))
            city_selectBtn.select_by_visible_text('Brooklyn')
            self.driver.find_element_by_name('zip').send_keys('11219')
            self.driver.find_element_by_name('mobileNo').send_keys('13729005200')
            self.driver.find_element_by_name('isDefault').click()
            self.driver.find_element_by_xpath('//div[@class="sa-btn-group"]/a[1]').click()
            # 填写支付信息
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@name="cardNum"]'))
            )
            self.driver.find_element_by_name('cardNum').send_keys('5329598063750158')
            self.driver.find_element_by_name('dateM').send_keys('03')
            self.driver.find_element_by_name('dateY').send_keys('21')
            self.driver.find_element_by_name('cvv2').send_keys('140')
            self.driver.find_element_by_name('cardHolderF').send_keys('xiaoqiang')
            self.driver.find_element_by_name('cardHolderL').send_keys('huang')
            self.driver.find_element_by_name('saveinfo').click()
            self.driver.find_element_by_xpath('//div[@class="payment-line"]/button[1]').click()
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="place-order-button"]/button[1]'))
            )
            self.driver.find_element_by_xpath('//div[@class="place-order-button"]/button[1]').click()
            # print('下单成功！')
            self.logger.info('下单成功！')
            time.sleep(2)
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
            time.sleep(2)
            orderId = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]//tr[1]/td[2]/p[1]/span[2]').text
            # print("订单号为：",orderId)
            self.logger.info("订单号为：%s" % orderId)

if __name__ == '__main__':
    spider = AliexpressSpider("Running Top Tees Mens Clothing",'32965410914')
    spider.run()
