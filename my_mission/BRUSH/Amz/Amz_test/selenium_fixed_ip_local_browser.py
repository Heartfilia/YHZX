import os
import re
import sys
import json
import time
import random
import logging
import requests
import traceback
import us.tools as tools
from us import change_proxy
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.webdriver.common.keys import Keys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# 重连
# tools.reconnect()
process_id = len(sys.argv) > 1 and int(sys.argv[1]) or 1
asin = "amazon_add_card"
img_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "screenshot")

if not os.path.isdir(img_dir):
    os.mkdir(img_dir)


class AmazonBrush(object):
    def __init__(self):
        change_proxy.disable_proxy()
        time.sleep(5)
        self.flag, self.row = change_proxy.compare_task()
        if self.flag != "DONTNEXT":
            self.proxies_full = change_proxy.use_fixed_ip(self.row)
            if self.proxies_full:
                self.proxies, self.header, self.no, self.sip, self.header = change_proxy.add_proxy(self.proxies_full,
                                                                                                   self.row)
                self.options = webdriver.ChromeOptions()
                # proxy = webdriver.Proxy()
                # proxy.http_proxy = self.proxies.replace("http://", '')
                new_ip = self.proxies.replace("http://", '')
                change_proxy.main(new_ip)   # 这里替换了ip后要等好久好久才可以处理 后面可能需要处理一下页面访问后的数据判断
                print('等待环境能够切换好...')
                time.sleep(10)     # 等待久一点,然后再继续后面的操作
                # proxy.add_to_capabilities(webdriver.DesiredCapabilities.CHROME)
                # self.options.add_argument(f'--proxy-server=192.16.213.81:8800')
                self.options.add_argument(f'--user-agent="{self.header}"')
                # self.options.add_argument("--headless")
                self.options.add_argument("--disable-gpu")
                self.options.add_experimental_option("debuggerAddress", "127.0.0.1:62486")

                self.browser = webdriver.Chrome(options=self.options)
                # self.browser.start_session(webdriver.DesiredCapabilities)
                self.session = requests.Session()

    def goods_index_handle(self, goal_asin=None):
        """
        商品搜索处理....
        :param goal_asin: ASIN
        :return:
        """
        time.sleep(random.uniform(3, 5))
        self.browser.execute_script('window.scrollTo(0, %s)' % random.randint(100, 400))
        # time.sleep(random.randint(3,10))
        # 增加selected_size码数字段
        try:
            size_chose = self.browser.find_element_by_id("dropdown_selected_size_name")
        except Exception as e:
            pass
        else:
            size_chose.click()

            n = len(self.browser.find_elements_by_class_name("a-dropdown-item"))
            time.sleep(random.uniform(3, 10))
            if goal_asin:
                for i in range(0, n):
                    size_name = self.browser.find_elements_by_class_name("a-dropdown-item")
                    click_size = size_name[i].click()
                    if goal_asin in self.browser.current_url:
                        break
                    else:
                        size_name.click()
                        time.sleep(random.uniform(3, 8))
            else:
                i = random.uniform(1, n)
                size_name = self.browser.find_element_by_class_name("a-dropdown-item")
                size_name[i].click()

        time.sleep(random.randint(3, 5))
        self.browser.execute_script('window.scrollTo(0, %s)' % random.randint(500, 1000))

        # 进入跟卖页面
        old_feature_div = self.browser.find_element_by_id("olp_feature_div")
        aok_float_right = self.browser.find_element_by_class_name("aok-float-right")
        print('下面的内容需要重构....')
        if old_feature_div:
            old_feature_div.find_by_tag("a").click()
        elif aok_float_right and aok_float_right.get_attribute("a"):
            aok_float_right.get_attribute("a").click()
        else:
            self.browser.get("https://www.amazon.com/gp/offer-listing/" + goal_asin)

    def found_page(self):
        # 打开浏览器，访问登陆页
        self.browser.set_window_size(1200, 820)
        delta = process_id % 5
        self.browser.set_window_position(400 * (delta - 1), 8)

        try:
            self.browser.get("https://www.amazon.com/")
        except:
            print('超时')
            # 出现异常，重新启动
            # reply_log(row["task_id"], "出现异常，重新启动刷单", getIpInfo_ip, row['account']['register_city'])
            url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
            res = tools.get(requests, url=url.format(TASK_ID=self.row["task_id"]))
            print(res.text)
            if 'ok' in res.text:
                print('账号任务解绑成功_ok_ok_ok')
            traceback.print_exc()
            self.browser.quit()
            exit()

        print('dierge tianjia cookie zhong')
        self.browser.delete_all_cookies()

        if self.row['account']['cookies']:
            self.browser.delete_all_cookies()
            listCookies = json.loads(self.row['account']['cookies'])

            cookie_jar = [{"name": key, "value": listCookies[key]} for key in listCookies]
            for cookie_j in cookie_jar:
                self.browser.add_cookie(cookie_j)
            self.browser.get("https://www.amazon.com/")
            time.sleep(random.randint(3, 10))
        else:
            os._exit(0)

    def search_items(self):
        print("搜索关键字 ===>>> 添加中")
        input('>>')
        for KEY in self.row['asin']["keywords"].split(","):
            time.sleep(3)
            input_box = self.browser.find_element_by_id("twotabsearchtextbox")
            input_box.send_keys(self.row['asin']["keywords"])
            input_box.send_keys(Keys.ENTER)
            numb = 0
            while True:
                time.sleep(random.randint(3, 10))
                if self.browser.find_element_by_class_name('sg-col-inner'):
                    break
                elif numb > 5:
                    # 加入一个解绑任务账号(不把账号设为无效)的api接口
                    time.sleep(random.randint(3, 10))
                    exit()
                numb += 1
            print(f'商品列表页标题为: {self.browser.title}')
            time.sleep(random.randint(3, 10))
            page_num = 1
            max_page_num = 3
            while page_num < max_page_num:
                time.sleep(3)
                self.browser.execute_script('window.scrollTo(0, 0);')
                for h in range(6):
                    self.browser.execute_script(
                        f'window.scrollTo({500 * h}, {500 * (h + 1)});')
                    time.sleep(random.randint(1, 2))
                asins = self.browser.find_elements_by_xpath('//a[@class="a-link-normal a-text-normal"]')
                print('asins::', len(asins))
                self.do_another_thing(asin, page_num, KEY, max_page_num)
                page_num += 1
                print("翻页查找%s" % page_num)
                # reply_log(row["task_id"], "翻页查找", getIpInfo_ip, row['account']['register_city'])
                try:
                    next_btn = self.browser.find_element_by_xpath(
                        '//*[@id="search"]/div[1]/div[2]/div/span[8]/div/span/div/div/ul/li[7]/a')
                except Exception as e:
                    print('没有下一页了...')
                else:
                    next_btn.click()
                time.sleep(random.randint(3, 8))
            if page_num == max_page_num:
                msg = "关键词%s没找到商品id" % KEY
                print(msg)
                # reply_log(row["task_id"], msg, getIpInfo_ip, row['account']['register_city'])
                # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                # print(res.text)
                # if 'ok' in res.text:
                #     print('账号任务解绑成功_ok_ok_ok')
        else:
            # 找不到指定产品，刷单终止 直接找改产品链接
            print("找不到指定产品，刷单终止")
            # reply_log(row["task_id"], "找不到指定产品，刷单终止", getIpInfo_ip, row['account']['register_city'])
            # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
            # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
            # print(res.text)
            # if 'ok' in res.text:
            #     print('账号任务解绑成功_ok_ok_ok')
            # self.browser.delete_cookie()
            exit()

    def delete_other_item(self):
        """
        删除购物车多余的商品
        :return:
        """
        print("删除购物车多余的商品")
        # reply_log(row["task_id"], "删除购物车多余的商品", getIpInfo_ip, row['account']['register_city'])
        # 更新
        num = int(
            self.browser.find_element_by_id('sc-subtotal-label-activecart').text.split('(')[1].split(' ')[0])
        print(f'商品数量一共有{num} 个')
        sameAsin = 1
        for i in range(num):
            data_asin = self.browser.find_elements_by_class_name("sc-list-item-border")[i]._element.get_attribute(
                "data-asin")
            if data_asin not in self.row["asin"]["asin"]:
                time.sleep(random.randint(3, 10))
                print(i)
                print('delete this shopping')
                time.sleep(random.randint(3, 10))
                print('刷新网页')
                self.browser.refresh()
                time.sleep(random.randint(3, 10))
                try:
                    self.browser.find_element_by_xpath(
                        '//div[@class="a-row sc-list-item sc-list-item-border sc-java-remote-feature"][1]/div[4]/div/div[1]/div/div/div[2]/div/span[2]/span/input').click()
                    print('已经按下删除键')
                except:
                    print('删除键没触发')
                    # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                    # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                    # print(res.text)
                    # if 'ok' in res.text:
                    #     print('账号任务解绑成功_ok_ok_ok')
            else:
                if sameAsin > 1:
                    self.browser.find_elements_by_class_name(
                        "sc-list-item-border")[i].find_elements_by_class_name("sc-action-delete").click()
                else:
                    sameAsin += 1

            # 网络连接出错 重试
            # if browser.find_element_by_id('reload-button'):
            #     print('This site can’t provide a secure connection')
            #     browser.find_element_by_id('reload-button').click()
            #     time.sleep(random.randint(3, 10))

            # time.sleep(random.randint(3, 10))

        time.sleep(random.randint(3, 10))
        print("选择商品数量，准备去一键支付")
        # reply_log(row["task_id"], "选择商品数量，准备去一键支付", getIpInfo_ip, row['account']['register_city'])
        sc_subtobal_label = self.browser.find_element_by_xpath('sc-subtotal-label-activecart')
        if int(sc_subtobal_label.text.split('(')[1].split(' ')[0]) == 1:
            try:
                self.browser.find_elements_by_class_name("a-dropdown-container")[-1].click()
                # 做一个判断（下拉菜单 第一个可能是 0）
                page_num = self.browser.find_element_by_class_name("a-popover-wrapper")[-1].find_self.by_tag(
                    "li").first.text
                if page_num in '1':
                    self.browser.find_elements_by_class_name("a-popover-wrapper")[-1].find_by_tag("li").first.click()
                else:
                    self.browser.find_elements_by_class_name("a-popover-wrapper")[-1].find_by_tag("li")[1].click()
            except:
                pass
            try:
                quantity_box = self.browser.find_element_by_name('quantityBox')
                quantity_box.click()
                quantity_box.clear()
                quantity_box.send_keys(1)
                self.browser.find_element_by_class_name("sc-update-link").click()
            except:
                pass
            time.sleep(random.randint(1, 3))
            self.browser.find_element_by_id("sc-buy-box-ptc-button").click()
            time.sleep(random.randint(3, 10))
            helper = '测试信息线上有对应的功能需要修改的'
            input('到helper这里需要看情况修改>>>>')
            helper = tools.sign_in_password(self.row['account']['login_amazon_email'],
                                            self.row['account']["login_amazon_password"],
                                            "https://www.amazon.com/gp/message", helper, self.row["task_id"], 1)

            if self.row['account']['amazon_account_type'] == 3 or self.row['account']['amazon_account_type'] == 2:
                if self.browser.find_element_by_class_name("a-button-primary"):
                    self.browser.find_element_by_class_name("a-button-primary").click()

            self.reload_reconnect()  # 网络连接出错 重试

            # 去掉会员广告弹窗
            try:
                vip_ad_box = self.browser.find_element_by_class_name("prime-nothanks-button")
            except Exception as e:
                pass
            else:
                print('出现广告弹窗')
                vip_ad_box.click()
            # 网络连接出错 重试
            self.reload_reconnect()

            # 出现手机号码验证
            if self.browser.find_element_by_id("authportal-center-section"):
                time.sleep(5)
                print('出现手机号码验证')
                self.browser.find_element_by_id("ap-account-fixup-phone-skip-link").click()

            # 网络连接出错 重试
            self.reload_reconnect()

            isClickPrime = 0
            # 选择免费物流 如果任务为会员 则点击会员申请
            if 'request_amazon_account_type' in self.row:
                if int(self.row['request_amazon_account_type']) == 2:
                    prime_fake_radio = self.browser.find_element_by_class_name('prime-fake-radio')
                    if prime_fake_radio:
                        prime_fake_radio.click()
                        # 选择免费物流且注册会员后的弹窗处理 点击申请会员
                        try:
                            prime_signup_button = self.browser.find_element_by_id('primeSignupButton')
                            prime_acquistition = self.browser.find_element_by_id('prime-acquisition-spc-popover-submit-button')
                        except Exception as e:
                            print('上面两个链接说不定都有问题,不知道是哪一个出了问题...:::')
                        else:
                            if prime_signup_button:
                                prime_signup_button.click()
                                isClickPrime = 1
                            elif prime_acquistition:
                                prime_acquistition.click()
                                isClickPrime = 1

            time.sleep(random.uniform(2, 5))
            return isClickPrime

    def do_another_thing(self, asins, page_num, KEY, max_page_num=3):
        for asin in asins:
            goods_url = asin.get_attribute("href")
            for goal_asin in self.row['asin']["asin"].split(','):
                # 下面是购物车数量
                cart_num = self.browser.find_element_by_id('nav-cart-count')
                if cart_num and int(cart_num.text.replace("+", "")) == 0:
                    if page_num < max_page_num - 1 and goal_asin in goods_url:
                        self.browser.get(goods_url)
                    elif page_num >= max_page_num - 1:
                        self.browser.get(f'https://www.amazon.com/dp/{goal_asin}?psc=1')
                        title_now = self.browser.title
                        print('当前的页面标题为:', title_now)
                        if title_now in ['找不到页面', 'Page Not Found']:
                            print('找不到指定产品，刷单终止')
                            dic = dict()
                            dic[self.row["task_id"]] = {}
                            dic[self.row["task_id"]]["task_id"] = self.row["task_id"]
                            dic[self.row["task_id"]]["status"] = 21
                            dic[self.row["task_id"]]["order_no"] = ''

                            our_url = "http://third.gets.com/api/index.php"
                            params = {"act": "modifyTaskOrderStatus",
                                      "sec": "20171212getscn"}

                            response = tools.post(requests.session(), our_url, params=params, post_data=json.dumps(dic))
                            self.browser.delete_all_cookies()
                            exit()
                    else:
                        break

                    self.check_agent_city_options()
                    # 商品详情页操作
                    self.goods_index_handle(goal_asin)
                    # 判断跟卖页
                    self.judge_follow_sale_page(goal_asin)
                    # 增加订单类型 order_type
                    self.add_order_type(self.row, KEY)
                    # 随机挑选商品
                    self.add_random_item()

                # 下单流程
                print('到了下单流程了...:::')
                ord_cart = self.browser.find_element_by_id("nav-cart")
                ord_cart.click()
                time.sleep(random.randint(3, 10))

                # self.reload_reconnect()  网络连接出错 重试
                '''
                做一检察代理ip和城市是否发生的操作
                params proxy_ip: getIpInfo_ip:: 这个参数可以不要，所以最上面没有导进去
                '''
                # tools.proxy_check(proxies=self.proxies, proxy_city=self.row['account']['register_city'],
                #                   proxy_ip=getIpInfo_ip, task_id=self.row["task_id"])

                isClickPrime = self.delete_other_item()  # 删除购物车多余的商品

                # 点击会员后，币种发生改变，需要再次点击marketplaceRadio
                market_place_radio = self.browser.find_element_by_id("marketplaceRadio")
                if market_place_radio:
                    market_place_radio.click()

                time.sleep(random.uniform(3, 10))
                # 获取金额
                try:
                    print('估计这里会找不到元素出问题，具体是点哪儿还需要看看...:::')
                    text_price = self.browser.find_element_by_css_selector(
                        "#subtotals-marketplace-table .grand-total-price").text
                    print(f'金额为::{text_price}')
                    print(text_price.split())
                except Exception as e:
                    # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                    # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                    # print(res.text)
                    # if 'ok' in res.text:
                    #     print('帐号任务解绑成功')
                    input('这里是因为找元素出了问题,先卡这里然后看看页面的操作,如何修改情况:::')
                    self.browser.delete_all_cookies()  # 退出，改了
                    time.sleep(random.randint(3, 10))
                    text_price = ''
                    exit()
                order_price = text_price.split()
                if len(order_price) == 1:
                    order_price = text_price.split("$")[1]
                else:
                    order_price = text_price.split()[1]
                if float(order_price) > float(self.row['payment']['single_max_trade']):
                    print("订单金额大于50美金")
                    # reply_log(row["task_id"], "订单金额大于50美金", getIpInfo_ip, row['account']['register_city'])
                    dic = dict()
                    dic[self.row["task_id"]] = {}
                    dic[self.row["task_id"]]["task_id"] = self.row["task_id"]
                    dic[self.row["task_id"]]["status"] = 25
                    dic[self.row["task_id"]]["order_no"] = '',
                    url = "http://third.gets.com/api/index.php"
                    params = {"act": "modifyTaskOrderStatus",
                              "sec": "20171212getscn"}
                    response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
                    self.browser.delete_all_cookies()   # 退出，改了
                    exit()

                img_file_name = self.browser.save_screenshot(img_dir + self.no)
                print("保存浏览器截图:%s" % os.path.basename(img_file_name))
                order_button_link = self.browser.find_element_by_class_name("place-order-button-link")
                order_button_link.click()

                time.sleep(random.randint(3, 10))
                print("付款成功")
                # reply_log(row["task_id"], "付款成功", getIpInfo_ip, row['account']['register_city'])
                print('这里也有问题需要处理的...:::')
                order_number_count = len(self.browser.find_elements_by_css_selector(".a-span7 h5"))
                if order_number_count == 1:
                    order_number = self.browser.find_element_by_css_selector(".a-span7 h5 .a-text-bold").text
                else:
                    order_index = 0
                    for order_dom in self.browser.find_elements_by_css_selector(".s-span7 h5"):
                        print('这里也要出现问题的,还需要修改的哦:::')
                        if self.browser.find_elements_by_css_selector(
                                ".a-span7 ul[class='a-unordered-list a-vertical']"
                        )[order_index].find_element_by_tag_name("span[class='wrap-item-title']"):
                            order_number = order_dom.find_element_by_class_name("a-text-bold").text
                            break
                        else:
                            order_index += 1

                # helper.logger.info("Order Number: %s" % order_number)
                self.do_some_cookies_info(order_number, order_price, order_number_count, isClickPrime)

            # img_file_name = browser.screenshot(img_dir + no)
            # helper.logger.info("保存浏览器截图:%s" % os.path.basename(img_file_name))
            '''
            加入一个解绑任务账号(不把账号设为无效)的api接口
            '''
            # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
            # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
            # print(res.text)
            # if 'ok' in res.text:
            #     print('帐号任务解绑成功')
            self.browser.delete_all_cookies()   # 退出，已改
            time.sleep(random.uniform(3, 10))
            exit()

    def do_some_cookies_info(self, order_number, order_price, order_number_count, isClickPrime):
        cookies = self.browser.get_cookies()
        cookies1 = {}
        for cookie in cookies:
            cookies1[cookie['name']] = cookie['value']
        jsonCookies = json.dumps(cookies1)
        payment_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        payment_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
        status = 2
        if int(self.row['feedback']['request_feedback']) == 0 and int(self.row['review']['request_review']) == 0:
            status = 6
        elif int(self.row['feedback']['request_feedback']) == 0 and int(
                self.row['review']['request_review']) != 0:
            status = 4
        dic = dict()
        dic[self.row["task_id"]] = {}
        dic[self.row["task_id"]]["task_id"] = self.row["task_id"]
        dic[self.row["task_id"]]["status"] = status
        dic[self.row["task_id"]]["order_no"] = order_number
        dic[self.row["task_id"]]["payment_date"] = payment_date + ' ' + payment_time
        dic[self.row["task_id"]]["actual_order_amount"] = order_price
        # 如果有两个订单号 则开通会员
        if order_number_count == 2 or isClickPrime == 1:
            dic[self.row["task_id"]]["is_open_prime"] = 1
        # 保存一下订单信息 防止post失败
        tools.save_file("%s.txt" % self.row["task_id"], json.dumps(dic), 'order')

        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyTaskOrderStatus",
                  "sec": "20171212getscn"}
        response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
        # 下单时间
        # order_num = int(row["order_num"]) + 1
        # 提交账号信息
        cookies = self.browser.get_cookies()
        cookies1 = {}
        for cookie in cookies:
            cookies1[cookie['name']] = cookie['value']
        jsonCookies = json.dumps(cookies1)
        postDateUser = {
            'data': {
                'account_id': self.row['account']['account_id'],
                'header': self.header,
                'cookie': cookie
            }
        }
        url = "http://third.gets.com/api/index.php"
        params = {"act": "updateAccountLoginSuccessInfo",
                  "sec": "20171212getscn"}
        response = tools.post(requests.session(), url, params=params, post_data=jsonCookies)
        img_file_name = self.browser.save_screenshot(img_dir + order_number)
        # helper.logger.info("保存浏览器截图:%s" % os.path.basename(img_file_name))
        self.browser.quit()
        os._exit(0)

    def add_random_item(self):
        n = len(self.browser.find_elements_by_class_name("s-result-item"))
        i = random.uniform(0, n)

        random_asin = self.browser.find_elements_by_class_name("s-result-item")[i].get_attribute("data-asin")
        print('random_asin:::', random_asin)
        s_color_title_link_class_name = self.browser.find_element_by_class_name("s-color-twister-title-link")
        s_color_title_links_class_name = self.browser.find_elements_by_class_name("s-color-twister-title-link")
        s_color_title_link_xpath = self.browser.find_element_by_xpath("//a[@class='a-link-normal a-text-normal']")
        s_color_title_links_xpath = self.browser.find_elements_by_xpath("//a[@class='a-link-normal a-text-normal']")
        if s_color_title_link_class_name:
            asins = s_color_title_link_class_name
        else:
            asins = s_color_title_link_xpath

        if random_asin not in self.row["asin"]["asin"]:
            if s_color_title_link_class_name:
                other_url = s_color_title_links_class_name[i].get_attribute("href")
            else:
                other_url = s_color_title_links_xpath[i].get_attribute("href")
        else:
            if s_color_title_link_class_name:
                other_url = s_color_title_links_class_name[i].get_attribute("href")
            else:
                other_url = s_color_title_links_xpath[i].get_attribute("href")

        self.browser.get(other_url)

        self.reload_reconnect()   # 网络连接出错 重试
        self.goods_index_handle(random_asin)  # 商品详情页操作
        # self.reload_reconnect()   # 网络连接出错 重试
        print('下面的点击属性需要重新调试...')
        time.sleep(random.randint(3, 6))
        self.browser.find_element_by_class_name("olpOffer").get_attribute("a-button-input").click()
        # self.reload_reconnect()   # 网络连接出错 重试

        # 过滤安装费 添加数码产品时候会提示需不需要上面安装
        filter_fee = self.browser.find_element_by_id('btnVasModalSkip')
        if filter_fee:
            filter_fee.click()

        print("其他商品添加到购物车成功")

    def reload_reconnect(self):
        # 网络连接出错 重试
        if self.browser.find_element_by_id('reload-button'):
            print('This site can’t provide a secure connection')
            self.browser.find_element_by_id('reload-button').click()
            time.sleep(random.randint(3, 10))

    def add_order_type(self, row, KEY):
        print('增加订单类型这里面,下面的数据也需要重构呢:这里是浩大的工程')
        for shop in self.browser.find_elements_by_class_name("olpOffer"):
            a_icon_popover = shop.find_element_by_class_name("a-icon-popover")
            olp_seller_name = shop.find_element_by_class_name("olpSellerName")
            a_button_input = shop.find_element_by_class_name("a-button-input")
            if row["asin"]["order_type"].upper() == "FBA":
                # browser.find_element_by_**(".olpOffer")[1].find_by_css(".a-icon-popover")
                if a_icon_popover:  # 订单为FBA订单
                    # 判断店家
                    print('判断店家中...:::')
                    if olp_seller_name.text.lower() == row["asin"]["shop_name"].lower():
                        a_button_input.click()
                        time.sleep(random.uniform(3, 10))
                        break

            elif row["asin"]["order_type"].upper() == "FBM":
                if not a_icon_popover:
                    if olp_seller_name.text.lower() == row["asin"]["shop_name"].lower():
                        a_button_input.click()
                        time.sleep(random.uniform(3, 10))
                        break

            elif row["asin"]["order_type"].upper() == "FBA 或 FBM":
                if olp_seller_name.text.lower() == row["asin"]["shop_name"].lower():
                    a_button_input.click()
                    time.sleep(random.uniform(3, 10))
                    break

        else:
            if self.browser.find_element_by_id('olpProduct'):
                dic = dict()
                dic[row["task_id"]] = {}
                dic[row["task_id"]]["task_id"] = row["task_id"]
                dic[row["task_id"]]["status"] = 23
                dic[row["task_id"]]["order_no"] = row['account']["first_order_no"]
                url = "http://third.gets.com/api/index.php"
                params = {"act": "modifyTaskOrderStatus",
                          "sec": "20171212getscn"}
                response = tools.post(requests, url, params=params, post_data=json.dumps(dic))
                print("没有找到店铺")
                # reply_log(row["task_id"], "没有找到店铺", getIpInfo_ip, row['account']['register_city'])
            '''
            加入一个解绑任务账号(不把账号设为无效)的api接口
            '''
            url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
            res = tools.get(requests, url=url.format(TASK_ID=row["task_id"]))
            print(res.text)
            if 'ok' in res.text:
                print('帐号任务解绑成功')
            # self.browser.quit()
            exit()

        # 网络连接出错 重试
        if self.browser.find_element_by_id('reload-button'):
            print('This site can’t provide a secure connection')
            # browser.find_element_by_id('reload-button').click()
            self.browser.refresh()
            time.sleep(random.randint(3, 10))

        # 过滤安装费 添加数码产品时候会提示需不需要上面安装
        if self.browser.find_element_by_id('btnVasModalSkip'):
            self.browser.find_element_by_id('btnVasModalSkip').click()

        print("加入购物车成功")
        # reply_log(row["task_id"], "加入购物车成功", getIpInfo_ip, row['account']['register_city'])
        print("添加其他商品到购物车")
        # reply_log(row["task_id"], "添加其他商品到购物车", getIpInfo_ip, row['account']['register_city'])

        # 搜索关键
        if row['asin']['asin'] != KEY:
            self.browser.find_element_by_id("twotabsearchtextbox").send_keys(KEY)
        else:
            self.browser.find_element_by_id("twotabsearchtextbox").send_keys('solar torch lantern')

        self.browser.find_element_by_xpath("//div[class='nav-search-submit nav-sprite']")

        self.reload_reconnect()   # 网络连接出错 重试

    def judge_follow_sale_page(self, goal_asin):
        """
        判断跟卖页面处理数据中
        :return:
        """
        if self.browser.find_element_by_xpath("//a[@class='a-button-text']"):
            for card_asin in self.browser.find_elements_by_xpath("//a[@class='a-button-text']"):
                # if row["asin"]["asin"] in card_asin._element.get_attribute("href"):
                if goal_asin in card_asin._element.get_attribute("href"):
                    try:
                        card_asin.click()
                    except:
                        print('遇到了跟新页面')
                        time.sleep(1000)
                    time.sleep(random.randint(3, 10))
                    break

    def check_agent_city_options(self):
        """
        做一检察代理ip和城市是否发生的操作
        :return:
        """
        # tools.proxy_check(proxies=proxies, proxy_city=row['account']['register_city'],proxy_ip=getIpInfo_ip, task_id=row["task_id"] )
        # print('环境正确')

        time.sleep(random.randint(3, 10))
        print('打开商品详情页:::')
        # reply_log(row["task_id"], "打开商品详情页", getIpInfo_ip, row['account']['register_city'])

        try:
            dont_know_what = self.browser.find_element_by_class_name("dismiss")
        except Exception as e:
            pass
        else:
            dont_know_what.click()
            print('不知道是什么的title::', self.browser.title)

        print('详情页:::')
        try:
            network_reconnect = self.browser.find_element_by_id('reload-button')
        except Exception as e:
            print('This site can’t provide a secure connection')
        else:
            network_reconnect.click()
            time.sleep(random.uniform(2, 5))

        time.sleep(random.uniform(3, 10))

    def run(self):
        if self.flag != "DONTNEXT":
            input('>>>')
            for _ in range(1, 11):
                try:
                    self.browser.get('http://httpbin.org/get')
                except Exception as e:
                    print(f'切换本地代理后还不可以使用,等待中 [{_}]...')
                    time.sleep(5)
                    continue
                else:
                    page_source = self.browser.page_source
                    if re.findall("(.*?):", self.proxies.replace("http://", ''))[0] not in page_source:
                        # print(f'\r代理还没有换过去...重试第[{_}]次中...', end='')
                        print(f'代理还没有换过去...重试第[{_}]次中...')
                        time.sleep(5)
                    else:
                        print('\n代理已经切换好了,可以准备下一步的操作了...')
                        flag = 'Done'
                        break
            else:
                flag = False

            if flag == 'Done':
                print('已经准备好了...')
                try:
                    self.found_page()
                    self.search_items()
                except Exception as e:
                    print('出现异常,重新启动...')
                    # reply_log(row["task_id"], "出现异常，重新启动刷单", getIpInfo_ip, row['account']['register_city'])
                    # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                    # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                    # print(res.text)
                    # if 'ok' in res.text:
                    #     print('账号任务解绑成功_ok_ok_ok')

                    traceback.print_exc()
                    print(f'错误信息: {e}')
                    self.browser.delete_all_cookies()   # 退出,已改
                    exit()
                finally:
                    self.browser.delete_all_cookies()    # 退出,已改
                    print('程序已经结束...')
                    os._exit(0)

            change_proxy.disable_proxy()


if __name__ == "__main__":
    app = AmazonBrush()
    app.run()
