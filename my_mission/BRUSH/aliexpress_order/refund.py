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
from mytools.tools import get_oxylabs_proxy, get, create_proxyauth_extension, logger

logger = logger('refund')
class AliexpressRefundSpider():

    def __init__(self,task_infos,task_id):
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

            self.refund()
            logger.info('当前账户操作完毕，关闭当前浏览器！')
            self.driver.quit()
        except NoSuchFrameException:
            logger.info('切换到登录的frame超时，正在重新请求主页，继续执行登录操作')
            self.run()

        except TimeoutException:
            # 在操作过程中等待超时，先退出当前登录状态，再重新执行run方法回调，重新走流程。也可直接结束程序，但更适合在多线程的情况下操作。
            logger.info('等待超时,正在检查登录状态，若已登录，则退出登录状态,重新走流程！')
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
            self.run()

    #点击首页中的"My Orders"，进入个人订单页面，走收货留评的流程
    def refund(self):
        # 点击首页中的"My Orders"，进入个人订单页面
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
        )
        self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()
        #搜索按钮可点击
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.ID, 'id="search-btn"'))
        )
        #先找到所有的订单items，再根据订单号或者商品asin，定位到目标订单所在的item
        items = self.driver.find_elements_by_xpath('//*[@id="buyer-ordertable"]/tbody')
        for item in items:
            if item.find_element_by_xpath('./tr[1]/td[2]/p[1]/span[2]').text == orderno:
                logger.info('找到目标订单所在的tbody!')
                #根据当前订单的状态做判断
                if item.find_element_by_xpath('./tr[2]/td[3]/span').text.strip() == 'Fund Processing':
                    #点击'Open Dispute',此时会打开一个新的页面，需要进行窗口的切换
                    item.find_element_by_xpath('./tr[2]/td[2]/span/a').click()
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(5)
                    #在新页面中执行下拉滚动条，再次点击'Open Dispute'
                    self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
                    WebDriverWait(self.driver, 40).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="TP_ProductTable"]/tbody/tr/td[5]/a'))
                    )
                    self.driver.find_element_by_xpath('//*[@id="TP_ProductTable"]/tbody/tr/td[5]/a').click()
                    #页面跳转,点击'Refund Only'按钮
                    WebDriverWait(self.driver, 40).until(
                        EC.element_to_be_clickable((By.ID, 'submit-ro'))
                    )
                    self.driver.find_element_by_id('submit-ro').click()
                    #页面跳转，进入refund页面
                    #url: https://trade.aliexpress.com/issue/fastissue/createIssueStep2.htm?orderId=99723247396644&issueId=400930414496644&solutionType=ro
                    #i want to apply for: 下拉列表选择默认即可，不操作
                    #Did you receive the item? 选择是
                    WebDriverWait(self.driver, 40).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@id="is_received_c"]/div[2]/div[1]/input'))
                    )
                    self.driver.find_element_by_xpath('//div[@id="is_received_c"]/div[2]/div[1]/input').click()
                    #选择否
                    # self.driver.find_element_by_xpath('//div[@id="is_received_c"]/div[2]/div[2]/input').click()
                    #做出选择后，下方会插入一个下拉选择，Reason for refund request
                    time.sleep(5)
                    self.driver.find_element_by_id('problem_type2').click()
                    time.sleep(3)
                    #点击'Product not as described'
                    self.driver.find_element_by_xpath('/html/body/div[9]/ul/li[2]').click()
                    time.sleep(5)
                    #点击'Please specify the reason'
                    time.sleep(3)
                    #点击'Style not as described'
                    self.driver.find_element_by_xpath('/html/body/div[10]/ul/li[2]').click()
                    time.sleep(random.randint(2,5))
                    #Refund Amount
                    self.driver.find_element_by_id('refund-amount').send_keys(actual_order_amount)
                    time.sleep(random.randint(2,5))
                    self.driver.find_element_by_id('request-detail-txt').send_keys('very bad qualiy,and the style is not as described')
                    #上传图片
                    time.sleep(random.randint(2,5))
                    self.driver.find_element_by_xpath('//*[@id="imageUploader"]/button').send_keys('图片路径')
                    time.sleep(10)
                    self.driver.find_element_by_id('videoUploader').send_keys('视频路径')
                    time.sleep(30)
                    #点击提交
                    self.driver.find_element_by_id('submit').submit()
                    #提交后的url:https://trade.aliexpress.com/issue/fastissue/Detail.htm?issueId=400930414496644&buyerAliid=1959146644
                    time.sleep(15)
                    if 'fastissue/Detail' in self.driver.current_url:
                        logger.info('已成功提交退款申请！')
            break
            self.driver.quit()
            logger.info('当前账户操作完毕，关闭当前浏览器！')

    #传入图片url，自动下载图片到项目根目录下的images文件下，返回图片的具体路径。
    @staticmethod
    def get_img_path(img_url):
        img_dir = os.path.join(os.path.dirname(__file__),'images')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        img_name = 'ReFund'+ '.' + img_url.split('.')[-1]
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

def main(task_infos, task_id):
    spider = AliexpressRefundSpider(task_infos, task_id)
    spider.run()

if __name__ == '__main__':
    # 多线程循环模式：默认一次最多获取5个待评论任务,自动根据获取到的任务数量创建相应数量的线程数，去执行各自分配到的刷单任务；当获取不到任务时，程序退出。
    #修改limit参数即可设置获取的任务数量，现在是1
    # while True:
    url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=3&limit=1&debug_list=0&debug_allot=0'
    resp = requests.get(url)
    try:
        if resp.json() == []:
            logger.info('未获取到待刷单列表的数据，程序结束！')
            sys.exit(0)
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

            # 回收线程
            for t in threads:
                t.join()
    except json.decoder.JSONDecodeError:
        pass