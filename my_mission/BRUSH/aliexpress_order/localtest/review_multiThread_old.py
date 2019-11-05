import os
import random
import re
import json
import sys
import threading
import time
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException, \
    WebDriverException
from mytools.tools import get_oxylabs_proxy, get
from mytools.utils import logger

logger = logger('review')
class AliexpressReviewSpider():

    def __init__(self,task_infos,task_id):
        self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
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
        self.target_id = self.task_infos[str(self.task_id)]["asin"]["asin"]
        self.options.add_argument(
            'user-agent="%s"' % json.loads(self.task_infos[str(self.task_id)]['account']['header'])['user-agent'])
        self.options.add_extension(proxyauth_plugin_path)
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        # headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        # 设置不加载图片
        self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(options=self.options)

    #访问首页，并登录
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
            self.driver.find_element_by_id('fm-login-id').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_email"])
            time.sleep(random.randint(1, 5))
            self.driver.find_element_by_id('fm-login-password').send_keys(self.task_infos[str(self.task_id)]["account"]["login_aliexpress_password"])
            time.sleep(random.randint(1, 5))
            self.driver.find_element_by_id('fm-login-submit').submit()
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

            # 先检查cofirm_pay_file文件夹下，是否存在一个taskid_xx.txt文件，xx为本次任务id。
            # 若存在，则进入个人订单中心，获取订单号和定价总价等信息，更新刷单状态。并删除该文件。
            # 若不存在，则正常走流程。
            confirm_receive_dir = os.path.join(os.path.dirname(__file__), 'confirm_receive_files')
            confirm_receive_filename = confirm_receive_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            if os.path.exists(confirm_receive_filename):
                logger.info('发现任务id: %d之前已确认收货，准备进入个人订单中心，确认是否留评状态，并进行相应的处理...' % self.task_id)
                ## 点击首页中的"My Orders"，进入个人订单页面
                WebDriverWait(self.driver, 40).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
                )
                self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()
                # 搜索按钮可点击
                # WebDriverWait(self.driver, 40).until(
                #     EC.element_to_be_clickable((By.ID, 'id="search-btn"'))
                # )
                time.sleep(5)
                # 先找到所有的订单items，再根据订单号或者商品asin，定位到目标订单所在的item
                items = self.driver.find_elements_by_xpath('//*[@id="buyer-ordertable"]/tbody')
                for item in items:
                    if item.find_element_by_xpath('./tr[1]/td[2]/p[1]/span[2]').text == self.task_infos[str(self.task_id)]["import_aliexpress_order"]:
                        logger.info('找到目标订单所在的tbody!')
                        # 根据当前订单的状态做判断
                        if item.find_element_by_xpath('./tr[2]/td[4]/button[3]').text.strip() == 'Leave Feedback':
                            logger.info('当前账户已收货，但未成功留评，准备执行留评的流程...')
                            item.find_element_by_xpath('./tr[2]/td[4]/button[3]').click()
                            # 进入评论页面
                            WebDriverWait(self.driver, 60).until(
                                EC.element_to_be_clickable((By.XPATH, '//div[@name="eval_star_node"]/span[1]'))
                                # EC.element_to_be_clickable((By.XPATH, '//*[@id="star_%s"]/span[1]' % '99723247396644'))
                            )
                            logger.info('进入评论填写页面...')
                            logger.info('当前url:%s' % self.driver.current_url)
                            # 此处需要根据接口数据，来判断好评与差评，再调整星级的点按位置（修改Xpath,可使用占位符，设置星级数为一个实例属性，这样可以简化减少代码臃肿）
                            # 点星商品描述时，需要上传图片
                            if self.task_infos[str(self.task_id)]['review']['title'] == 'bad':
                                stars_num = 1
                            else:
                                stars_num = 5
                            self.driver.find_element_by_xpath(
                                '//div[@name="eval_star_node"]/span[%s]' % stars_num).click()
                            time.sleep(10)
                            # self.driver.find_element_by_xpath('//*[@id="image_uploader_99723247396644"]/div/button')
                            self.driver.find_element_by_xpath('//div[@class="feedback-main"]/textarea').send_keys(
                                self.task_infos[str(self.task_id)]['review']["content"])
                            time.sleep(random.randint(1, 5))
                            img_url = self.task_infos[str(self.task_id)]['review']["images"]
                            if img_url:
                                logger.info('发现图片链接，正在下载图片并将图片上传到评论页面中...')
                                # img_path = ' '#图片的绝对路径或者相对路径
                                img_path = self.get_img_path(img_url=img_url)
                                self.driver.find_element_by_xpath('//div[@class="ui-uploader"]/button[1]').send_keys(
                                    img_path)
                                # 时间延迟，使图片上传完,此处的时间延迟应该怎么做？多久合适？
                                time.sleep(30)
                            else:
                                logger.info('未发现图片链接，将不上传图片到评论页面！')
                                time.sleep(random.randint(1, 3))
                            # 服务态度
                            self.driver.find_element_by_xpath(
                                '//*[@id="j-leave-feedback-container"]/div/div[4]/div[2]/div/div[1]/span[%s]' % stars_num).click()
                            # 物流速度
                            time.sleep(random.randint(1, 3))
                            self.driver.find_element_by_xpath(
                                '//*[@id="j-leave-feedback-container"]/div/div[4]/div[3]/div/div[1]/span[%s]' % stars_num).click()
                            # 勾选，设置为匿名评论
                            time.sleep(random.randint(1, 3))
                            self.driver.find_element_by_id('j-anonymous-feedback').click()
                            # 点击按钮留下反馈
                            time.sleep(random.randint(1, 3))
                            self.driver.find_element_by_id('buyerLeavefb-submit-btn').click()
                            # 留评后的url
                            # 'https://feedback.aliexpress.com/management/leaveFeedback.htm?parentOrderId=99723247396644'
                            time.sleep(20)
                            # 评论完成时，url中没有'isOrderCompleted=Y'
                            # if not 'isOrderCompleted=Y' in self.driver.current_url:
                            if 'Your feedback has been submitted' in self.driver.page_source:
                                logger.info('留评成功！')
                                # 更新刷单状态
                                review_data = {
                                    str(self.task_id): {
                                        "task_id": self.task_id,
                                        "status": 6,
                                    }
                                }
                                self.update_brushing_status(json.dumps(review_data))
                                # 新增刷单操作日志
                                log_data = {
                                    "task_id": self.task_id,
                                    "info": "留评成功！",
                                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                                }
                                self.create_task_order_log(json.dumps(log_data))
                                os.remove(confirm_receive_filename)
                                logger.info('删除了一个文件:%s' % confirm_receive_filename)
                            else:
                                logger.info('留评失败！')
                                review_data = {
                                    str(self.task_id): {
                                        "task_id": self.task_id,
                                        "status": 61,
                                    }
                                }
                                # 更新刷单状态
                                self.update_brushing_status(json.dumps(review_data))
                                # 新增刷单操作日志
                                log_data = {
                                    "task_id": self.task_id,
                                    "info": "留评失败！",
                                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                                }
                                self.create_task_order_log(json.dumps(log_data))
                                os.remove(confirm_receive_filename)
                                logger.info('删除了一个文件:%s' % confirm_receive_filename)
                    break
            else:
                self.review()
            logger.info('当前账户操作完毕，关闭当前浏览器！')
            self.driver.quit()
        except NoSuchFrameException:
            logger.info('切换到登录的frame超时，正在重新请求主页，继续执行登录操作')
            self.run()
        except (TimeoutException, WebDriverException):
            logger.info('等待超时,或者元素位未完全加载导致定位出错!')
            logger.info('关闭当前浏览器，结束当前线程！')
            logger.info('系统会自动生成新的线程来执行下单任务！')
            self.driver.quit()
            sys.exit(0)

    #点击首页中的"My Orders"，进入个人订单页面，走收货留评的流程
    def review(self):
        # 点击首页中的"My Orders"，进入个人订单页面
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
        )
        self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()

        #点击确认收货
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//table[@id="buyer-ordertable"]/tbody/tr[2]/td[4]/button[2]'))
        )
        #此处先进行判断，如果卖家发货，则可以走留评的流程，否则，程序退出。
        if self.driver.find_element_by_xpath('//table[@id="buyer-ordertable"]/tbody/tr[2]/td[4]/button[2]').text.strip() == 'Confirm Goods Received':
            logger.info('卖家已发货，正在执行留评的流程...')
            self.driver.find_element_by_xpath('//table[@id="buyer-ordertable"]/tbody/tr[2]/td[4]/button[2]').click()

            # 进入订单明细页面，勾选目标商品所在的订单，再次点击确认收货
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="button-confirmOrderReceived"]'))
            )
            trs = self.driver.find_elements_by_xpath('//*[@id="confirm-receiving"]/tbody/tr')
            for tr in trs:
                good_detail_url = tr.find_element_by_xpath('./td[4]/div[1]/a').get_attribute('href')
                if  re.search(self.target_id, good_detail_url):
                    tr.find_element_by_xpath('./td[2]/input').click()
            time.sleep(random.randint(1, 3))
            self.driver.find_element_by_xpath('//*[@id="button-confirmOrderReceived"]').click()
            # 点击弹出的“comfirm”按钮
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.ID, 'confirm_cpf'))
            )
            self.driver.find_element_by_id('confirm_cpf').click()
            logger.info('点击了最终确认收货的按钮！')
            # 在项目的根目录下，新建一个文件夹confirm_receive_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
            confirm_receive_dir = os.path.join(os.path.dirname(__file__), 'confirm_receive_files')
            if not os.path.exists(confirm_receive_dir):
                os.mkdir(confirm_receive_dir)
            confirm_receive_filename = confirm_receive_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            f = open(confirm_receive_filename, 'w', encoding='utf-8')
            f.close()
            logger.info('同时创建了一个文件：%s' % confirm_receive_filename)
            #进入评论页面
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@name="eval_star_node"]/span[1]'))
                # EC.element_to_be_clickable((By.XPATH, '//*[@id="star_%s"]/span[1]' % '99723247396644'))
            )
            logger.info('进入评论填写页面...')
            logger.info('当前url:%s' % self.driver.current_url)
            #此处需要根据接口数据，来判断好评与差评，再调整星级的点按位置（修改Xpath,可使用占位符，设置星级数为一个实例属性，这样可以简化减少代码臃肿）
            #点星商品描述时，需要上传图片
            if self.task_infos[str(self.task_id)]['review']['title'] == 'bad':
                stars_num = 1
            else:
                stars_num = 5
            self.driver.find_element_by_xpath('//div[@name="eval_star_node"]/span[%s]' % stars_num).click()
            time.sleep(10)
            # self.driver.find_element_by_xpath('//*[@id="image_uploader_99723247396644"]/div/button')
            self.driver.find_element_by_xpath('//div[@class="feedback-main"]/textarea').send_keys(self.task_infos[str(self.task_id)]['review']["content"])
            time.sleep(random.randint(1, 5))
            img_url = self.task_infos[str(self.task_id)]['review']["images"]
            if img_url:
                logger.info('发现图片链接，正在下载图片并将图片上传到评论页面中...')
                # img_path = ' '#图片的绝对路径或者相对路径
                img_path = self.get_img_path(img_url=img_url)
                self.driver.find_element_by_xpath('//div[@class="ui-uploader"]/button[1]').send_keys(img_path)
                #时间延迟，使图片上传完,此处的时间延迟应该怎么做？多久合适？
                time.sleep(30)
            else:
                logger.info('未发现图片链接，将不上传图片到评论页面！')
                time.sleep(random.randint(1, 3))
            #服务态度
            self.driver.find_element_by_xpath('//*[@id="j-leave-feedback-container"]/div/div[4]/div[2]/div/div[1]/span[%s]' % stars_num).click()
            #物流速度
            time.sleep(random.randint(1, 3))
            self.driver.find_element_by_xpath('//*[@id="j-leave-feedback-container"]/div/div[4]/div[3]/div/div[1]/span[%s]' % stars_num).click()
            #勾选，设置为匿名评论
            time.sleep(random.randint(1, 3))
            self.driver.find_element_by_id('j-anonymous-feedback').click()
            #点击按钮留下反馈
            time.sleep(random.randint(1, 3))
            self.driver.find_element_by_id('buyerLeavefb-submit-btn').click()
            #留评后的url
            # 'https://feedback.aliexpress.com/management/leaveFeedback.htm?parentOrderId=99723247396644'
            time.sleep(20)
            #评论完成时，url中没有'isOrderCompleted=Y'
            # if not 'isOrderCompleted=Y' in self.driver.current_url:
            if 'Your feedback has been submitted' in self.driver.page_source:
                logger.info('留评成功！')
                # 更新刷单状态
                review_data = {
                    str(self.task_id): {
                        "task_id": self.task_id,
                        "status": 6,
                    }
                }
                self.update_brushing_status(json.dumps(review_data))
                # 新增刷单操作日志
                log_data = {
                    "task_id": self.task_id,
                    "info": "留评成功！",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(log_data))
                os.remove(confirm_receive_filename)
                logger.info('删除了一个文件:%s' % confirm_receive_filename)
            else:
                logger.info('留评失败！')
                review_data = {
                    str(self.task_id): {
                        "task_id": self.task_id,
                        "status": 61,
                    }
                }
                #更新刷单状态
                self.update_brushing_status(json.dumps(review_data))
                # 新增刷单操作日志
                log_data = {
                    "task_id": self.task_id,
                    "info": "留评失败！",
                    'ip': self.get_ip_info(proxies={'https': self.proxy})
                }
                self.create_task_order_log(json.dumps(log_data))
                os.remove(confirm_receive_filename)
                logger.info('删除了一个文件:%s' % confirm_receive_filename)
        else:
            logger.info('卖家尚未发货，暂时不能留评，程序退出！')
            self.driver.quit()
            sys.exit(0)

    #传入图片url，自动下载图片到项目根目录下的images文件下，返回图片的具体路径。
    @staticmethod
    def get_img_path(img_url):
        img_dir = os.path.join(os.path.dirname(__file__),'images')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        img_name = 'FeedBack'+ '.' + img_url.split('.')[-1]
        img_path = img_dir + '/' + img_name
        r = requests.get(img_url, stream=True)
        # f = open(img_abspath, "wb")
        with open(img_path,'wb') as f:
            for chunk in r.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
        return img_path

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

    # 更新刷单状态
    @staticmethod
    def update_brushing_status(data):
        # 测试机
        # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        # 线上
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
        resp = requests.post(url=url, data=data)
        # print(resp.text)
        if resp.json()['msg'] == 'ok':
            logger.info('刷单状态更新成功！')
        else:
            logger.info('刷单状态更新失败！')

    # 新增刷单操作日志
    @staticmethod
    def create_task_order_log(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
        resp = requests.post(url, data)
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

def main(task_infos, task_id):
    spider = AliexpressReviewSpider(task_infos, task_id)
    spider.run()

if __name__ == '__main__':
    # 多线程循环模式：默认一次最多获取5个待评论任务,自动根据获取到的任务数量创建相应数量的线程数，去执行各自分配到的刷单任务；当获取不到任务时，程序退出。
    #修改limit参数即可设置获取的任务数量，现在是1
    while True:
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=3&limit=2'
        resp = requests.get(url)
        try:
            if resp.json() == []:
                # logger.info('未获取到待评论列表的数据，程序结束！')
                # sys.exit(0)
                logger.info('当前未获取到待评论的数据，程序将启动休眠模式，60分钟后自动唤醒...')
                time.sleep(60 * 60)
            else:
                task_infos = resp.json()
                task_id_str_list = []
                for task_id_str in task_infos:
                    task_id_str_list.append(task_id_str)
                logger.info('成功获取到%d条待评论的数据！' % len(task_id_str_list))
                logger.info('将创建%d个线程来分别执行评论任务!' % len(task_id_str_list))
                threads = []
                for i in range(len(task_id_str_list)):
                    task_id = int(task_id_str_list[i])
                    t = threading.Thread(target=main, args=(task_infos, task_id))
                    threads.append(t)
                    t.start()
                    time.sleep(30)

                # 回收线程
                for t in threads:
                    t.join()
        except json.decoder.JSONDecodeError:
            pass