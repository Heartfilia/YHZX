import os
import random
import re
import json
import sys
# import threading
import autoit
from multiprocessing import Pool
import time
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException, \
    WebDriverException
from mytools.tools import get_oxylabs_proxy, get, post, create_proxyauth_extension, logger
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ProxyError
from selenium.webdriver.common.keys import Keys

date_ym = time.strftime('%Y%m', time.localtime())

logger = logger(f'review_us_{date_ym}')  # 后面补充了年月


class AliexpressReviewSpider():

    def __init__(self, task_id, task_info):
        self.task_id = task_id
        self.task_info = task_info
        self.target_id = self.task_info["asin"]["asin"]
        # OXY代理
        # self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        # Geosurf代理
        # self.proxy = 'http://10502+US+10502-%s:MilkyWay2018@us-30m.geosurf.io:8000' % random.randint(100000, 800000)
        # auth = self.proxy.split("@")[0][7:]
        # proxyid = self.proxy.split("@")[1]
        # proxyauth_plugin_path = create_proxyauth_extension(
        #     proxy_host=proxyid.split(":")[0],
        #     proxy_port=int(proxyid.split(":")[1]),
        #     proxy_username=auth.split(":")[0],
        #     proxy_password=auth.split(":")[1]
        # )
        self.options = webdriver.ChromeOptions()
        self.options.add_argument(
            'user-agent="%s"' % json.loads(self.task_info['account']['header'])['user-agent'])
        # 代理需要指定账户密码时，添加代理使用这种方式
        # self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)
        # headless模式
        # self.options.add_argument("--headless")
        # self.options.add_argument('--disable-gpu')
        # 设置不加载图片
        # self.options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(options=self.options)

    # 主实例方法，负责调用其他实例方法，完成收货留评的整个流程
    def run(self):
        try:
            self.driver.get('https://www.aliexpress.com/')
            # 过滤弹窗
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
            print('点击登录')
            # 点击登录
            self.driver.find_element_by_xpath('//span[@class="register-btn"]/a').click()
            # WebDriverWait(self.driver, 40).until(
            #     EC.frame_to_be_available_and_switch_to_it((By.ID,'alibaba-login-box'))
            # )
            time.sleep(10)
            # 切换到子iframe
            self.driver.switch_to.frame('alibaba-login-box')
            # 输入登录信息，此处需要特别注意，登录界面有两个，界面风格一致，但元素属性有变化
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="fm-login-id"]'))
            )
            time.sleep(random.uniform(4, 8))
            self.driver.find_element_by_id('fm-login-id').send_keys(self.task_info["account"]["login_aliexpress_email"])
            time.sleep(random.uniform(4, 8))
            self.driver.find_element_by_id('fm-login-password').send_keys(
                self.task_info["account"]["login_aliexpress_password"])
            time.sleep(random.uniform(4, 8))
            try:
                self.driver.find_element_by_id('fm-login-submit').send_keys(Keys.ENTER)
            except NoSuchElementException as e:
                print('no fm-login-submit')
                self.driver.find_element_by_xpath('//button[text()="Sign In"]').send_keys(Keys.ENTER)
            # self.driver.find_element_by_id('fm-login-submit').submit()
            # js = 'document.getElementByClassName("fm-button fm-submit password-login").click();'
            # self.driver.execute_script(js)
            # 此处判断登录过程中是否有滑块验证码，有则终止程序
            try:
                if 'display: block' in self.driver.find_element_by_id('fm-login-checkcode-title').get_attribute(
                        'style'):
                    logger.info('[taskid: %s]登录时发现滑块验证码，程序退出！' % self.task_id)
                    self.driver.quit()
                    # sys.exit(0)#fm-login-checkcode-title
            except NoSuchElementException as e:
                try:
                    if 'display: block' in self.driver.find_element_by_id('nocaptcha-password').get_attribute('style'):
                        logger.info('[taskid: %s]登录时发现滑块验证码，程序退出！' % self.task_id)
                        self.driver.quit()
                        # sys.exit(0)
                except NoSuchElementException:
                    pass

                    # 弹窗处理
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass

            # if self.driver.current_url == 'https://www.aliexpress.com/':
            if "Hi," in self.driver.page_source and 'noticed an unusual activity' not in self.driver.page_source:
                # 插入账号登录日志
                login_log_data = {
                    'data': {
                        "account_id": self.task_info["account"]["account_id"],
                        "header": self.task_info['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies()),
                        "login_status": "1",
                        "note": "登录成功"
                    }
                }
                self.insert_account_login_log(json.dumps(login_log_data))
                # 当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
                login_success_info_data = {
                    'data': {
                        "account_id": self.task_info["account"]["account_id"],
                        "header": self.task_info['account']['header'],
                        "cookies": json.dumps(self.driver.get_cookies())
                    }
                }
                self.update_account_login_success_info(json.dumps(login_success_info_data))

            elif 'passport.aliexpress.com' in self.driver.current_url:
                logger.info('[taskid: %s]登录后发现验证码，账户已被封！' % self.task_id)
                # 账户被封，也更新刷单状态
                brushing_data = {
                    str(self.task_id): {
                        "task_id": self.task_id,
                        "status": 10,
                    }
                }
                self.update_brushing_status(json.dumps(brushing_data))
                self.driver.quit()
                logger.info('[taskid: %s]程序退出！' % self.task_id)
                # sys.exit(0)
            # 先进入个人订单中心，再判断缓存文件的存在与否，避免多次进入订单中心，造成代码臃肿
            ## 点击首页中的"My Orders"，进入个人订单页面
            WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="user-benefits"]//ul/li[2]/a'))
            )

            self.driver.find_element_by_xpath('//div[@id="user-benefits"]//ul/li[2]/a').click()
            time.sleep(10)
            # 将浮动窗口拖开，免得影响点击 Pay Now
            if self.driver.find_element_by_id('J_xiaomi_dialog'):
                self.driver.execute_script("document.getElementById('J_xiaomi_dialog').style.right='1000px';")
            # 先检查cofirm_feedback_files文件夹下，是否存在一个taskid_xx.txt文件，xx为本次任务id
            # 若存在，则直接更新刷单状态，并删除该缓存文件，并结束当前线程！
            confirm_leavefeedback_dir = os.path.join(os.path.dirname(__file__), 'confirm_leavefeedback_files')
            confirm_leavefeedback_filename = confirm_leavefeedback_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            if os.path.exists(confirm_leavefeedback_filename):
                self.do_after_review_success()
                os.remove(confirm_leavefeedback_filename)
                logger.info('[taskid: %s]删除了一个文件:%s' % (self.task_id, confirm_leavefeedback_filename))
                logger.info('[taskid: %s]当前账户操作完毕，关闭当前浏览器,结束当前的留评线程！' % self.task_id)
                # sys.exit(0)
            # 若cofirm_feedback_files文件夹下不存在一个taskid_xx.txt文件，则检查cofirm_reveive_files文件夹下，是否存在一个taskid_xx.txt文件，xx为本次任务id。
            # 若存在，则点击‘Leave Feedback’，直接走留评流程，更新刷单状态,并删除该缓存文件。
            # 若不存在，则正常走收货留评流程。
            confirm_receive_dir = os.path.join(os.path.dirname(__file__), 'confirm_receive_files')
            confirm_receive_filename = confirm_receive_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
            if os.path.exists(confirm_receive_filename):
                logger.info(
                    '[taskid: %s]发现任务id: %d之前已点击确认收货，准备进入个人订单中心，确认是否留评状态，并进行相应的处理...' % (self.task_id, self.task_id))
                # 先找到所有的订单items，再根据订单号，定位到目标订单所在的item
                items = self.driver.find_elements_by_xpath('//*[@id="buyer-ordertable"]/tbody')
                for item in items:
                    print('接口中订单号:::', self.task_info["import_aliexpress_order"])
                    if item.find_element_by_xpath('./tr[1]/td[2]/p[1]/span[2]').text.strip() == self.task_info[
                        "import_aliexpress_order"]:
                        logger.info('=======[taskid: %s]找到目标订单所在的tbody!======' % self.task_id)
                        """
                        做一个订单是否关闭的判断
                        """
                        try:
                            print('now status::', item.find_element_by_xpath('./tr[2]/td[3]/span').text)
                        except:
                            pass
                        if "Closed" in item.find_element_by_xpath('./tr[2]/td[3]/span').text:
                            logger.info('order_closed')
                            self.do_after_order_close()
                        # 根据当前订单的状态做判断
                        elif item.find_element_by_xpath('./tr[2]/td[4]/button[3]').text.strip() == 'Leave Feedback':
                            logger.info('[taskid: %s]当前账户已收货，但未成功留评，准备执行留评的流程...' % self.task_id)
                            item.find_element_by_xpath('./tr[2]/td[4]/button[3]').send_keys(Keys.ENTER)
                            self.review(confirm_receive_filename)  # 需要传参

                        try:
                            if item.find_element_by_xpath('./tr[2]/td[4]/button[3]').text.strip() == 'Leave Feedback':
                                logger.info('[taskid: %s]当前账户已收货，但未成功留评，准备执行留评的流程...' % self.task_id)
                                item.find_element_by_xpath('./tr[2]/td[4]/button[3]').send_keys(Keys.ENTER)
                                self.review(confirm_receive_filename)  # 需要传参
                        except NoSuchElementException:
                            logger.info('[taskid: %s]已确认收货，但未找到review按键！' % self.task_id)
                        break
            else:
                # 先找到所有的订单items，再根据订单号，定位到目标订单所在的item
                items = self.driver.find_elements_by_xpath('//*[@id="buyer-ordertable"]/tbody')
                time.sleep(2)
                if len(self.driver.find_elements_by_xpath('//*[@id="buyer-ordertable"]/tbody/tr')) < 2:
                    logger.info('no_order')
                    self.do_after_order_close()
                for item in items:
                    if item.find_element_by_xpath('./tr[1]/td[2]/p[1]/span[2]').text == self.task_info[
                        "import_aliexpress_order"]:
                        logger.info('[taskid: %s]找到目标订单所在的tbody!' % self.task_id)
                        """
                        做一个订单是否关闭的判断
                        """
                        try:
                            print(item.find_element_by_xpath('./tr[2]/td[3]/span').text)
                        except:
                            pass
                        if "Closed" in item.find_element_by_xpath('./tr[2]/td[3]/span').text:
                            logger.info('order_closed')
                            self.do_after_order_close()

                        elif "Awaiting Payment" in item.find_element_by_xpath('./tr[2]/td[3]/span').text:
                            logger.info('order_closed')
                            self.do_after_order_close()
                        elif "Fund Processing" in item.find_element_by_xpath('./tr[2]/td[3]/span').text:
                            logger.info('order_closed')
                            self.do_after_order_close()
                        # time.sleep(360)
                        elif item.find_element_by_xpath(
                                './tr[2]/td[4]/button[2]').text.strip() == 'Confirm Goods Received':
                            logger.info('[taskid: %s]卖家已发货，正在执行收货的流程...' % self.task_id)
                            try:
                                button_order = self.driver.find_element_by_xpath(
                                    '//button[@button_action="confirmOrderReceived"]')
                            # item.find_element_by_xpath('./tr[2]/td[4]/button[2]').click()
                                print('准备点收货')
                                button_order.click()
                                print('已经点击了确认收货详情')
                            except:
                                logger.error('执行收货流程失败...')
                            # 进入订单明细页面，勾选目标商品所在的订单，再次点击确认收货
                            WebDriverWait(self.driver, 40).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="button-confirmOrderReceived"]'))
                            )
                            select_all = self.driver.find_element_by_id('select-all')
                            select_all.click()
                            # 将浮动窗口拖开，免得影响点击 Pay Now
                            # if self.driver.find_element_by_id('J_xiaomi_dialog'):
                            #     self.driver.execute_script(
                            #         "document.getElementById('J_xiaomi_dialog').style.right='1000px';")
                            # trs = self.driver.find_elements_by_xpath('//*[@id="confirm-receiving"]/tbody/tr')
                            # for tr in trs:
                            #     good_detail_url = tr.find_element_by_xpath('./td[4]/div[1]/a').get_attribute('href')
                            #     if re.search(self.target_id, good_detail_url):
                            #         tr.find_element_by_xpath('./td[2]/input').click()
                            # time.sleep(random.randint(1, 3))
                            self.driver.find_element_by_id('button-confirmOrderReceived').click()
                            # 点击弹出的“comfirm”按钮
                            WebDriverWait(self.driver, 40).until(
                                EC.element_to_be_clickable((By.ID, 'confirm_cpf'))
                            )
                            self.driver.find_element_by_id('confirm_cpf').click()
                            logger.info('[taskid: %s]点击了最终确认收货的按钮！' % self.task_id)
                            # 在项目的根目录下，新建一个文件夹confirm_receive_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
                            confirm_receive_dir = os.path.join(os.path.dirname(__file__), 'confirm_receive_files')
                            if not os.path.exists(confirm_receive_dir):
                                os.mkdir(confirm_receive_dir)
                            confirm_receive_filename = confirm_receive_dir + '/' + 'taskid_' + str(
                                self.task_id) + '.txt'
                            f = open(confirm_receive_filename, 'w', encoding='utf-8')
                            f.close()
                            logger.info('[taskid: %s]同时创建了一个文件：%s' % (self.task_id, confirm_receive_filename))
                            self.review(confirm_receive_filename)
                        elif item.find_element_by_xpath('./tr[2]/td[4]/button[1]').text.strip() == 'Add to Cart':
                            logger.info('Order has been closed!' % self.task_id)
                            self.do_after_order_close()
                            self.driver.quit()
                            # sys.exit(0)
                        elif 'Finished' in item.find_element_by_xpath('./tr[2]/td[3]/span').text:
                            logger.info('[taskid: %s]直接开始留评处理！' % self.task_id)
                            confirm_receive_dir = os.path.join(os.path.dirname(__file__), 'confirm_receive_files')
                            if not os.path.exists(confirm_receive_dir):
                                os.mkdir(confirm_receive_dir)
                            confirm_receive_filename = confirm_receive_dir + '/' + 'taskid_' + str(
                                self.task_id) + '.txt'
                            f = open(confirm_receive_filename, 'w', encoding='utf-8')
                            f.close()
                            click_into_review = self.driver.find_element_by_xpath('//*[@id="buyer-ordertable"]/tbody/tr[2]/td[4]/button[3]')
                            click_into_review.click()
                            self.review(confirm_receive_filename)
                            pass
                        else:
                            logger.info('[taskid: %s]卖家尚未发货，暂时不能留评，程序退出！' % self.task_id)
                            self.driver.quit()
                            # sys.exit(0)
                        break
            logger.info('[taskid: %s]当前账户操作完毕，关闭当前浏览器！' % self.task_id)
            self.driver.quit()
            # os._exit(0)
        except (TimeoutException, WebDriverException, NoSuchFrameException, NoSuchElementException):
            logger.info('[taskid: %s]等待超时,或者元素位未完全加载导致定位出错!' % self.task_id)
            logger.info('[taskid: %s]关闭当前浏览器，结束当前线程！' % self.task_id)
            logger.info('[taskid: %s]系统会自动生成新的线程来执行留评任务！' % self.task_id)
            self.driver.quit()
            # os._exit(0)

    # 留评的流程
    def review(self, confirm_receive_filename):
        """
        1105_LODGE: 修改对图片的支持...
        :param confirm_receive_filename:
        :return:
        """
        # 进入评论页面，走评论流程
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@name="eval_star_node"]/span[1]'))
            # EC.element_to_be_clickable((By.XPATH, '//*[@id="star_%s"]/span[1]' % '99723247396644'))
        )
        logger.info('[taskid: %s]进入评论填写页面...' % self.task_id)
        # logger.info('当前url:%s' % self.driver.current_url)
        # 此处需要根据接口数据，来判断好评与差评，再调整星级的点按位置（修改Xpath,使用占位符，设置星级数为一个变量）
        # 点星商品描述时，需要上传图片
        if self.task_info['review']["request_review"] == '1':
            stars_num = 1
        elif self.task_info['review']["request_review"] == '2':
            stars_num = 5
        self.driver.find_element_by_xpath('//div[@name="eval_star_node"]/span[%s]' % stars_num).click()
        time.sleep(10)
        # self.driver.find_element_by_xpath('//*[@id="image_uploader_99723247396644"]/div/button')
        # 处理评论内容中可能出现的中文标点'，'和'。'
        text_area = self.task_info['review']["content"]
        if text_area:
            if re.search(r'，', text_area):
                text_area = re.sub(r'，', ',', text_area)
            if re.search(r'。', text_area):
                text_area = re.sub(r'。', '.', text_area)
            if re.search(r'！', text_area):
                text_area = re.sub(r'！', '!', text_area)
            if re.search(r'’', text_area):
                text_area = re.sub(r'’', "'", text_area)
            self.driver.find_element_by_xpath('//div[@class="feedback-main"]/textarea').send_keys(text_area)
            time.sleep(random.randint(1, 5))
        img_url = self.task_info['review']["images"]
        if img_url:
            logger.info('[taskid: %s]发现图片链接，正在下载图片并将图片上传到评论页面中...' % self.task_id)
            # img_path_list = ' '#图片的绝对路径的列表
            img_path_list = self.get_img_path(img_url=img_url)
            try:
                for img_path in img_path_list:
                    try:
                        tId = self.task_info["import_aliexpress_order"]
                        self.driver.find_element_by_xpath(f'//*[@id="image_uploader_{tId}"]/div/button').click()
                        # self.driver.find_element_by_xpath('//div[@class="image_uploader"]/div[@class="ui-uploader"]/button[1]').click()
                        '//*[@id="image_uploader_8005672409594446"]/div/button'
                    except Exception as e:
                        print('点击上传按钮出错了...')
                        logger.info('[taskid: %s]点击上传图片出错...:%s' % (self.task_id, img_path))
                    else:
                        # 尽量保证里面有内容，否则很容易出问题的,要不然下面的容错处理都会出问题
                        try:
                            time.sleep(random.uniform(0, 1))
                            autoit.control_focus("打开", "[Class:Edit; instance:1]")
                            time.sleep(random.uniform(0, 1))
                            autoit.control_set_text("打开", "[Class:Edit; instance:1]", img_path)
                            time.sleep(random.uniform(1, 2))
                            autoit.control_click("打开", "[Class:Button; instance:1]")
                            logger.info('[taskid: %s]图片发送成功...' % self.task_id)
                        except Exception as e:
                            # 这里要发送rt一次,避免出了问题,卡在这里
                            logger.info('[taskid: %s]这里是出了错然后容错处理,不一定能解决,需要关注...:%s' % (self.task_id, img_path))
                            try:  # 再加一层错误处理，减少问题出错
                                print('发生错误，关闭窗口...')
                                autoit.control_click("打开", "[Class:Button; instance:1]")
                                time.sleep(0.5)
                                autoit.control_click("打开", "[Class:Button; instance:2]")
                                time.sleep(0.5)
                            except Exception as e:
                                autoit.control_click("打开", "[Class:Button; instance:1]")
                            finally:
                                time.sleep(random.uniform(0, 1))

                    time.sleep(2)

                    # self.driver.find_element_by_xpath('//div[@class="ui-uploader"]/button[1]').send_keys(
                    #     img_path)
                    # 时间延迟，使图片上传完,此处的时间延迟应该怎么做？多久合适？
            except:
                print('不上传图片了，垃圾服务器...')
                time.sleep(10)
        else:
            logger.info('[taskid: %s]未发现图片链接，将不上传图片到评论页面！' % self.task_id)
            time.sleep(random.randint(1, 3))
        # 服务态度
        self.driver.find_element_by_xpath(
            '//*[@id="j-leave-feedback-container"]/div/div[4]/div[2]/div/div[1]/span[%s]' % stars_num).click()
        # 物流速度
        time.sleep(random.randint(1, 3))
        self.driver.find_element_by_xpath(
            '//*[@id="j-leave-feedback-container"]/div/div[4]/div[3]/div/div[1]/span[%s]' % stars_num).click()

        # 差评时，设置匿名留评
        # if stars_num == 1:
        #     #勾选，设置为匿名评论
        # time.sleep(random.randint(1, 3))
        # self.driver.find_element_by_id('j-anonymous-feedback').click()
        # 点击按钮留下反馈
        time.sleep(random.randint(1, 3))
        self.driver.find_element_by_id('buyerLeavefb-submit-btn').click()
        logger.info('[taskid: %s]点击了评论页面的"Leave Feedback"按钮' % self.task_id)
        # 在项目的根目录下，新建一个文件夹confirm_leavefeedback_files,并在该文件夹下生成一个文件，文件名命名为'taskid_xx.txt'文件，‘xx’代表任务id
        confirm_leavefeedback_dir = os.path.join(os.path.dirname(__file__), 'confirm_leavefeedback_files')
        if not os.path.exists(confirm_leavefeedback_dir):
            os.mkdir(confirm_leavefeedback_dir)
        confirm_leavefeedback_filename = confirm_leavefeedback_dir + '/' + 'taskid_' + str(self.task_id) + '.txt'
        f = open(confirm_leavefeedback_filename, 'w', encoding='utf-8')
        f.close()
        logger.info('[taskid: %s]同时创建了一个文件：%s' % (self.task_id, confirm_leavefeedback_filename))
        # 留评后的url
        # 'https://feedback.aliexpress.com/management/leaveFeedback.htm?parentOrderId=99723247396644'
        time.sleep(20)
        # 评论完成时，url中没有'isOrderCompleted=Y'
        # if not 'isOrderCompleted=Y' in self.driver.current_url:
        if 'Your feedback has been submitted' in self.driver.page_source:
            self.do_after_review_success()
            os.remove(confirm_receive_filename)
            logger.info('[taskid: %s]删除了一个文件:%s' % (self.task_id, confirm_receive_filename))
            os.remove(confirm_leavefeedback_filename)
            logger.info('[taskid: %s]删除了一个文件:%s' % (self.task_id, confirm_leavefeedback_filename))
        else:
            self.do_after_review_failed(confirm_receive_filename, confirm_leavefeedback_filename)

    # 确定留评成功后要做的：更新刷单状态，插入刷单日志
    def do_after_review_success(self):
        logger.info('[taskid: %s]留评成功！' % self.task_id)
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
            'ip': self.get_ip_info()
        }
        self.create_task_order_log(json.dumps(log_data))

    # 订单已关闭:更新刷单状态，插入刷单日志
    def do_after_order_close(self):
        logger.info('[taskid: %s] 订单已关闭，无法留评!！' % self.task_id)
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
            'ip': self.get_ip_info()
        }
        self.create_task_order_log(json.dumps(log_data))

    # 确定留评失败后要做的：更新刷单状态，插入刷单日志，删除缓存文件
    def do_after_review_failed(self, confirm_receive_filename, confirm_leavefeedback_filename):
        logger.info('[taskid: %s]留评失败！' % self.task_id)
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
            'ip': self.get_ip_info()
        }
        self.create_task_order_log(json.dumps(log_data))
        self.driver.save_screenshot('LeaveFeedbackFailed.png')
        os.remove(confirm_receive_filename)
        logger.info('[taskid: %s]删除了一个文件:%s' % (self.task_id, confirm_receive_filename))
        os.remove(confirm_leavefeedback_filename)
        logger.info('[taskid: %s]删除了一个文件:%s' % (self.task_id, confirm_leavefeedback_filename))

    # 传入图片url，自动下载图片到项目根目录下的images文件下，返回图片的具体路径。
    def get_img_path(self, img_url):
        """
        1105_lodge: rewrite
        :param img_url:
        :return:
        """
        img_dir = os.path.join(os.path.dirname(__file__), 'images')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        img_url_list = img_url.split(',')
        img_path_list = []
        if len(img_url_list) == 1:
            img_name = 'FeedBack' + '_' + str(self.task_id) + '.' + img_url.split('.')[-1]
            img_path = os.path.join(img_dir, img_name)
            r = requests.get(img_url, stream=True)
            with open(img_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=512):
                    if chunk:
                        f.write(chunk)
            img_path_list.append(img_path)
        else:
            n = 1
            for img_url in img_url_list:
                img_name = 'FeedBack' + '_' + str(self.task_id) + '_' + str(n) + '.' + img_url.split('.')[-1]
                # img_name = f'FeedBack_{self.task_id}_{n}.{img_url.split('.')[-1]}'  # 这么简洁的方法竟然不用
                img_path = os.path.join(img_dir, img_name)
                r = requests.get(img_url, stream=True)
                with open(img_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=512):
                        if chunk:
                            f.write(chunk)
                img_path_list.append(img_path)
                n += 1

        return img_path_list  # 这里改成了返回一个列表

    # 插入账号登录日志
    def insert_account_login_log(self, data):
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=aliexpressInsertAccountLoginLog&inner_debug=1'
        post(requests.session(), url=url, post_data=data)
        logger.info('[taskid: %s]账户登录日志已成功插入！' % self.task_id)

    # 当账户成功登录时, 把登录的header和cookie修改对应账户表的字段
    def update_account_login_success_info(self, data):
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=aliexpressUpdateAccountLoginSuccessInfo&inner_debug=1'
        post(requests.session(), url=url, post_data=data)
        logger.info('[taskid: %s]对应账户的header和cookies字段已成功修改!' % self.task_id)

    # 更新刷单状态
    def update_brushing_status(self, data):
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus&inner_debug=1'
        resp = post(requests.session(), url=url, post_data=data)
        # print(resp.text)
        if resp.json()['msg'] == 'ok':
            logger.info('[taskid: %s]刷单状态更新成功！' % self.task_id)
        else:
            logger.info('[taskid: %s]刷单状态更新失败！' % self.task_id)

    # 新增刷单操作日志
    def create_task_order_log(self, data):
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog&inner_debug=1'
        resp = post(requests.session(), url=url, post_data=data)
        if resp.json()['status'] == 0:
            logger.info('[taskid: %s]新增刷单操作日志成功!' % self.task_id)
        else:
            logger.info('[taskid: %s]新增刷单操作日志失败!' % self.task_id)

    # 获取当前ip信息，返回字符串
    @staticmethod
    def get_ip_info(proxies=None):
        getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
        if getIpInfo:
            ipInfo = json.loads(getIpInfo.text)
            ip = ipInfo['ip']
        else:
            ip = '未获取到ip'
        return ip


def main(task_id, task_info):
    spider = AliexpressReviewSpider(task_id, task_info)
    spider.run()


if __name__ == '__main__':
    # 多线程循环模式：默认一次最多获取5个待评论任务,自动根据获取到的任务数量创建相应数量的线程数，去执行各自分配到的刷单任务；当获取不到任务时，程序退出或休眠。
    # 修改limit参数即可设置获取的任务数量，现在是2
    while True:
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=3&limit=1&inner_debug=1'
        resp = get(requests.session(), url=url)
        if resp:
            try:
                if ": 2001," in str(resp.json()) or ": 2002," in str(resp.json()):
                    # logger.info('未获取到待刷单列表的数据，程序结束！')
                    # sys.exit(0)
                    logger.info('任务系统未获取到当前时间的任务，程序[sleep 10m]...')
                    time.sleep(60 * 10)
                elif ": 3001," in str(resp.json()):  # or '2001' in str(resp.json()):
                    # logger.info('未获取到待刷单列表的数据，程序结束！')
                    # sys.exit(0)
                    logger.info('任务系统没有匹配的账户，程序[sleep 3s]...')
                    time.sleep(3)
                else:
                    pool = Pool(processes=1)
                    tasks_all = resp.json()
                    print("任务", tasks_all)
                    task_item_list = []
                    for task_id_str in tasks_all:
                        item = (int(task_id_str), tasks_all[task_id_str])
                        print(item)
                        task_item_list.append(item)
                    logger.info('成功获取到%d条待评论的数据！' % len(task_item_list))
                    for item in task_item_list:
                        # ==================== 临时跳过区 ====================
                        # if str(item[0]) in ['3697', '3894', '3899', '3901',
                        #                     '3902', '3905', '3909', '3912',
                        #                     '3929']:
                        #     print(f'跳过 {str(item[0])} 这个任务...')
                        #     continue
                        # ====================================================
                        # if str(item[0])[-1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:  # 只跑这些尾数
                        #     print(f'******* {str(item[0])} 该任务不该这台服务器处理 ******')
                        #     time.sleep(2)
                        #     continue
                        print(f'开始执行 {str(item[0])} 这个任务...')
                        pool.apply_async(func=main, args=item)
                    pool.close()
                    pool.join()
                    time.sleep(3)
                    logger.info('********************************pool sleep 3s************************************')
            except json.decoder.JSONDecodeError:
                pass
        else:
            logger.info('任务系统出错，程序[sleep 30s]...')
            time.sleep(30)
