import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import time
import random
import traceback
# from mytools.utils import reply_log
# from mytools.browser_helper import BrowserHelper
from user_agent import generate_user_agent
import us.tools as tools
from us import config
import requests
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_experimental_option("debuggerAddress", "127.0.0.1:62486")
browser = webdriver.Chrome(options=options)


# 重连
# tools.reconnect()
process_id = len(sys.argv) > 1 and int(sys.argv[1]) or 1
asin = "amazon_add_card"
img_dir = os.path.abspath(os.path.dirname(__file__)) + "/screenshot/"
if not os.path.isdir(img_dir):
    os.mkdir(img_dir)


# desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
# desired_capabilities["pageLoadStrategy"] = "none"

def goods_index_handle(goal_asin=None):
    time.sleep(random.randint(3, 5))
    browser.execute_script('window.scrollTo(0, %s)' % random.randint(100, 400))
    # time.sleep(random.randint(3,10))
    # 增加selected_size码数字段
    try:
        size_chose = browser.find_element_by_id("dropdown_selected_size_name")
    except Exception as e:
        pass
    else:
        size_chose.click()

        n = len(browser.find_elements_by_class_name("a-dropdown-item"))
        time.sleep(random.randint(3, 10))
        if goal_asin:
            for i in range(0, n):
                size_name = browser.find_elements_by_class_name("a-dropdown-item")
                click_size = size_name[i].click()
                if goal_asin in browser.current_url:
                    break
                else:
                    size_name.click()
                    time.sleep(random.randint(3, 8))
        else:
            i = random.randint(1, n)
            size_name = browser.find_elements_by_class_name("a-dropdown-item")
            size_name[i].click()
    time.sleep(random.randint(3, 5))
    browser.execute_script('window.scrollTo(0, %s)' % random.randint(500, 1000))
    # 进入跟卖页面

    if browser.find_element_by_id("olp_feature_div"):
        browser.find_element_by_id("olp_feature_div").find_by_tag("a").click()
    elif browser.find_element_by_class_name("aok-float-right") and browser.find_element_by_class_name("aok-float-right").get_attribute("a"):
        browser.find_element_by_class_name("aok-float-right").get_attribute("a").click()
    else:
        browser.get("https://www.amazon.com/gp/offer-listing/" + goal_asin)


# 先获取代理IP, 根据代理IP的城市来分配合适的账号去下单
s = requests.Session()
# # GEO代理
# random_num = random.randint(100000, 999999)
# proxies = {'http': 'http://10502+US+10502-%s:MilkyWay2018@us-30m.geosurf.io:8000' % random_num,
#            'https': 'https://10502+US+10502-%s:MilkyWay2018@us-30m.geosurf.io:8000' % random_num,
#            }
# # OXY 代理
# # randomNum = random.random()
# # proxies = tools.get_oxylabs_proxy(config.marketplace_name,None, randomNum)

# getIpInfo = tools.get(s, 'https://ipinfo.io', proxies=proxies, timeout=15)
# # row 存放任务信息
# row = {}
# if getIpInfo:
#     ipInfo = json.loads(getIpInfo.text)
#     print(ipInfo)
#     # 代理IP必须为美国的，且城市不为空
#     if ipInfo.get("country") == "US" and ipInfo.get("city"):
#         ip = ipInfo['ip']
#         registerCity = ipInfo['city']
#         print(ip)
#         print(ipInfo.get("city"))

# 获取需要下达你的任务（不传城市 获取固定ip账号）
url = "http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=getTaskOrdersList2&marketplace_id=1&get_type=1&inner_debug=True"
res = tools.get(s, url, 5)
print(res.text)
if res:
    resDict = json.loads(res.text)
    if resDict.get("status") == 2001:
        print('没有匹配基本条件的任务')
        time.sleep(120)
        exit()
    elif resDict.get("status") == 2002:
        print('没有匹配下单时间的任务')
        time.sleep(120)
        exit()
    elif resDict.get("status") == 3001:
        print('没有匹配的账户,需要更换IP城市')
        time.sleep(1)
        exit()
    else:
        for i in resDict:
            print(i)
            if int(resDict[i]['progress_status']) < 2 and int(i) > 191:
                row = resDict[i]
                print(f'任务详情为：{row}')
                # print('=' * 20)
                # print('IP所属的城市---', registerCity)
                # print('任务所属的城市--', row['account']['register_city'])
                # print('=' * 20)
                # if row['account']['register_city'] == registerCity:
                break
                # else:
                #     print('任务城市与注册IP城市不一致,解绑任务账号')
                #     '''
                #     加入一个解绑任务账号(不把账号设为无效)的api接口
                #     '''
                #     url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                #     res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                #     print(res.text)
                #     if 'ok' in res.text:
                #         print('任务账号解绑成功')
                #     time.sleep(3)
                #     exit()
    # else:
    #     print('ip地址有误，退出')
    #     time.sleep(5)
    #     exit()
# else:
#     print('获取不到代理IP信息， 退出')
#     time.sleep(5)
#     exit()

data = tools.get_file("%s.txt" % row["task_id"], 'order')
if data:
    url = "http://third.gets.com/api/index.php"
    params = {"act": "modifyTaskOrderStatus",
              "sec": "20171212getscn"}
    response = tools.post(requests.session(), url, params=params, post_data=data)
    exit()

# # GEO 代理
# proxies = {'http': 'http://10502+US+10502-%s:MilkyWay2018@us-30m.geosurf.io:8000' % random_num,
#            'https': 'https://10502+US+10502-%s:MilkyWay2018@us-30m.geosurf.io:8000' % random_num,
#            }
# OXy 代理
# proxies = tools.get_oxylabs_proxy(config.marketplace_name, row['account']['register_city'], randomNum)
# 　固定ｉｐ
print(row['account'])
ip_type = row['account']['ip_type']
if int(ip_type) == 1:
    print(f'该注册账号的ip类型为:{ip_type},属于固定ip')
else:
    print(f'该注册账号的ip类型为:{ip_type},属于动态ip，不可用，请切换为固定ip下单')
    os._exit(0)

proxies = {
    'http': 'http://%s:8800' % (row['account']['register_ip']),
    'https': 'http://%s:8800' % (row['account']['register_ip'])
}
print(f'固定ip为：{proxies}')
getIpInfo = tools.get(s, 'https://ipinfo.io', proxies=proxies)

if getIpInfo:
    ipInfo = json.loads(getIpInfo.text)
    ip = ipInfo['ip']
    registerCity = ipInfo['city']
    print(f'ip为{ip}\r\n 城市{registerCity}')
else:
    print('代理不可用 ，请求失败')
    os._exit(0)
# if not getIpInfo:
#     # 没有获取得到目标城市的代理
#     print('get ip failed!')
#     dic = {}
#     dic[row["task_id"]] = {}
#     dic[row["task_id"]]["task_id"] = row["task_id"]
#     dic[row["task_id"]]["status"] = 102
#     url = "http://third.gets.com/api/index.php"
#     params = {"act": "modifyTaskOrderStatus",
#               "sec": "20171212getscn"}
#     response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
# 加入一个解绑任务账号(不把账号设为无效)的api接口
# url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
# res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
# print(res.text)
# if 'ok' in res.text:
#     print('帐号任务解绑成功')
# exit()


# 　检查的ｉｐ 参数 可以不要
getIpInfo_ip = json.loads(getIpInfo.text)['ip']
# print(getIpInfo_ip)
# print(row['account']['register_city'])
# print(row['account']['ip'])


try:
    # 增加代理ip
    proxy = proxies['http']

    header = json.loads(row['account']["header"])

    header['user-agent'] = generate_user_agent(device_type="desktop")
    print(header['user-agent'])
    no = row['account']["login_amazon_email"].split("@")[0]
    print(proxy)
    print(row['account']["login_amazon_email"])
    sip = row['account']["ip"]
    # headless = True
    headless = False

    # helper = BrowserHelper(headless=headless, proxy=proxy, headers=header)
    # 如果请求大于20次，则暂时不运行
except Exception as e:
    # 出现异常，重新启动
    print('yichang')
    # reply_log(row["task_id"], "出现异常，重新启动刷单", getIpInfo_ip, row['account']['register_city'])
    # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
    # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
    # print(res.text)
    # if 'ok' in res.text:
    #     print('账号任务解绑成功_ok_ok_ok')
    # traceback.print_exc()
    # browser.quit()
    exit()

print('diyige  try try')
try:
    # 打开浏览器，访问登陆页
    browser.set_window_size(1200, 820)
    delta = process_id % 5
    browser.set_window_position(400 * (delta - 1), 8)

    try:
        browser.get("https://www.amazon.com/")
    except:
        print('超时')
        # 出现异常，重新启动
        # reply_log(row["task_id"], "出现异常，重新启动刷单", getIpInfo_ip, row['account']['register_city'])
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
        res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
        print(res.text)
        if 'ok' in res.text:
            print('账号任务解绑成功_ok_ok_ok')
        traceback.print_exc()
        browser.quit()
        exit()

    print('dierge tianjia cookie zhong')
    browser.delete_all_cookies()

    if row['account']['cookies']:
        browser.delete_all_cookies()
        listCookies = json.loads(row['account']['cookies'])

        cookie_jar = [{"name": key, "value": listCookies[key]} for key in listCookies]
        for cookie_j in cookie_jar:
            browser.add_cookie(cookie_j)
        # for cookie in listCookies:
        #     for k in {'name', 'value', 'domain', 'path', 'expiry', 'httpOnly', 'secure'}:
        #         if k not in list(cookie.keys()):
        #             if k == 'expiry':
        #                 t = time.time()
        #                 cookie[k] = int(t)
        #     browser.add_cookie(
        #         {k: cookie[k] for k in {'name', 'value', 'domain', 'path', 'expiry', 'httpOnly', 'secure'}})
        # time.sleep(10)
        browser.get("https://www.amazon.com/")
        time.sleep(random.randint(3, 10))
    else:
        # helper.logger.info('cookies失效')
        os._exit(0)

    # 　清除广告弹窗
    # try:
    #     browser.find_element_by_id('b2bCamModalOverlay')
    # except Exception as e:
    #     print('出现广告弹窗')
    #     browser.execute_script('document.querySelector("#btnNoThanks > span > input").click()')

    print("搜索关键字 ===>>> tianjia zhong")
    # reply_log(row["task_id"], "搜索关键字", getIpInfo_ip, row['account']['register_city'])

    for KEY in row['asin']["keywords"].split(","):
        time.sleep(3)
        input_box = browser.find_element_by_id("twotabsearchtextbox")
        input_box.send_keys(row['asin']["keywords"])
        input_box.send_keys(Keys.ENTER)
        numb = 0
        while True:
            # browser.find_element_by_xpath("//div[class='nav-search-submit nav-sprite']").click()


            time.sleep(random.randint(3, 10))
            # 　如果出现网络连接失败　点击重新连接
            # if browser.find_element_by_id('reload-button'):
            #     print('This site can’t provide a secure connection')
            #     browser.find_element_by_id('reload-button').click()
            #     time.sleep(random.randint(3, 10))

            if browser.find_element_by_class_name('sg-col-inner'):
                break
            elif numb > 5:
                '''
                加入一个解绑任务账号(不把账号设为无效)的api接口
                '''
                # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                # print(res.text)
                # if 'ok' in res.text:
                #     print('任务账号解绑成功')
                time.sleep(random.randint(3, 10))
                exit()
            numb += 1
        print(f'商品列表页标题为: {browser.title}')
        time.sleep(random.randint(3, 10))

        print("打开商品列表页")
        # reply_log(row["task_id"], "打开商品列表页", getIpInfo_ip, row['account']['register_city'])
        page_num = 1
        max_page_num = 3
        while page_num < max_page_num:

            # 滚动一下 商品列表页
            # helper.logger.info("打开商品列表页, 滚动详情页")
            browser.execute_script('window.scrollTo(0, 0);')
            for h in range(8):
                browser.execute_script(
                    f'window.scrollTo({500 * h}, {500 * (h + 1)});')
                time.sleep(random.randint(1, 3))

            # 　如果出现网络连接失败　点击重新连接
            # if browser.find_element_by_id('reload-button'):
            #     print('This site can’t provide a secure connection')
            #     browser.find_element_by_id('reload-button').click()
            #     time.sleep(random.randint(3, 10))

            asins = browser.find_elements_by_xpath('//a[@class="a-link-normal a-text-normal"]')
            print('asins::', len(asins))
            for asin in asins:
                goods_url = asin.get_attribute("href")
                # print(goods_url)
                for goal_asin in row["asin"]["asin"].split(','):
                    if browser.find_element_by_id('nav-cart-count') and int(
                            browser.find_element_by_id('nav-cart-count').text.replace("+", "")) == 0:
                        if page_num < max_page_num - 1 and goal_asin in goods_url:
                            browser.get(goods_url)
                        elif page_num >= max_page_num - 1:
                            browser.get('https://www.amazon.com/dp/%s?psc=1' % goal_asin)
                            print(browser.title)
                            if browser.title == '找不到页面' or browser.title == 'Page Not Found':
                                print("找不到指定产品，刷单终止")
                                # reply_log(row["task_id"], "找不到指定产品，刷单终止", getIpInfo_ip, row['account']['register_city'])
                                dic = {}
                                dic[row["task_id"]] = {}
                                dic[row["task_id"]]["task_id"] = row["task_id"]
                                dic[row["task_id"]]["status"] = 21
                                dic[row["task_id"]]["order_no"] = '',
                                url = "http://third.gets.com/api/index.php"
                                params = {"act": "modifyTaskOrderStatus",
                                          "sec": "20171212getscn"}
                                response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
                                browser.quit()
                                exit()
                        else:
                            break
                        '''
                        做一检察代理ip和城市是否发生的操作
                        '''
                        # tools.proxy_check(proxies=proxies, proxy_city=row['account']['register_city'],proxy_ip=getIpInfo_ip, task_id=row["task_id"] )
                        # print('环境正确')

                        time.sleep(random.randint(3, 10))
                        print("打开商品详情页")
                        # reply_log(row["task_id"], "打开商品详情页", getIpInfo_ip, row['account']['register_city'])
                        try:
                            不知道是什么 = browser.find_element_by_class_name("dismiss")
                        except Exception as e:
                            pass
                        else:
                            不知道是什么.click()
                            print('title::', browser.title)

                        print('详情页')
                        # 网络连接出错 重试
                        try:
                            网络重连 = browser.find_element_by_id('reload-button')
                        except Exception as e:
                            print('This site can’t provide a secure connection')
                        else:
                            网络重连.click()
                            time.sleep(random.randint(3, 10))

                        time.sleep(random.randint(3, 10))
                        # 商品详情页操作
                        goods_index_handle(goal_asin)


                        if browser.find_element_by_xpath("//a[@class='a-button-text']"):
                            for card_asin in browser.find_elements_by_xpath("//a[@class='a-button-text']"):
                                # if row["asin"]["asin"] in card_asin._element.get_attribute("href"):
                                if goal_asin in card_asin._element.get_attribute("href"):
                                    try:
                                        card_asin.click()
                                    except:
                                        print('遇到了跟新页面')
                                        time.sleep(1000)
                                    time.sleep(random.randint(3, 10))
                                    break

                        for shop in browser.find_element_by_class_name("olpOffer"):
                            # 增加订单类型order_type
                            if row["asin"]["order_type"].upper() == "FBA":
                                # browser.find_element_by_**(".olpOffer")[1].find_by_css(".a-icon-popover")
                                if shop.find_by_css(".a-icon-popover"):  # 订单为FBA订单
                                    # 判断店家
                                    if shop.find_by_css(".olpSellerName").text.lower() == row["asin"][
                                        "shop_name"].lower():
                                        shop.find_by_css(".a-button-input").click()
                                        time.sleep(random.randint(3, 10))
                                        break

                            elif row["asin"]["order_type"].upper() == "FBM":
                                if not shop.find_by_css(".a-icon-popover"):
                                    if shop.find_by_css(".olpSellerName").text.lower() == row["asin"][
                                        "shop_name"].lower():
                                        shop.find_by_css(".a-button-input").click()
                                        time.sleep(random.randint(3, 10))
                                        break

                            elif row["asin"]["order_type"].upper() == "FBA 或 FBM":
                                if shop.find_by_css(".olpSellerName").text.lower() == row["asin"]["shop_name"].lower():
                                    shop.find_by_css(".a-button-input").click()
                                    time.sleep(random.randint(3, 10))
                                    break

                        else:
                            if browser.find_element_by_id('olpProduct'):
                                dic = {}
                                dic[row["task_id"]] = {}
                                dic[row["task_id"]]["task_id"] = row["task_id"]
                                dic[row["task_id"]]["status"] = 23
                                dic[row["task_id"]]["order_no"] = row['account']["first_order_no"]
                                url = "http://third.gets.com/api/index.php"
                                params = {"act": "modifyTaskOrderStatus",
                                          "sec": "20171212getscn"}
                                response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
                                print("没有找到店铺")
                                # reply_log(row["task_id"], "没有找到店铺", getIpInfo_ip, row['account']['register_city'])
                            '''
                            加入一个解绑任务账号(不把账号设为无效)的api接口
                            '''
                            url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                            res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                            print(res.text)
                            if 'ok' in res.text:
                                print('帐号任务解绑成功')
                            browser.quit()
                            exit()

                        # 网络连接出错 重试
                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            # browser.find_element_by_id('reload-button').click()
                            browser.refresh()
                            time.sleep(random.randint(3, 10))

                        # 过滤安装费 添加数码产品时候会提示需不需要上面安装
                        if browser.find_element_by_id('btnVasModalSkip'):
                            browser.find_element_by_id('btnVasModalSkip').click()

                        print("加入购物车成功")
                        # reply_log(row["task_id"], "加入购物车成功", getIpInfo_ip, row['account']['register_city'])
                        print("添加其他商品到购物车")
                        # reply_log(row["task_id"], "添加其他商品到购物车", getIpInfo_ip, row['account']['register_city'])
                        # 搜索关键
                        if row['asin']['asin'] != KEY:
                            browser.find_element_by_id("twotabsearchtextbox").fill(KEY)
                        else:
                            browser.find_element_by_id("twotabsearchtextbox").fill('solar torch lantern')

                        browser.find_element_by_xpath("//div[class='nav-search-submit nav-sprite']")

                        # 网络连接出错 重试
                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            browser.find_element_by_id('reload-button').click()
                            time.sleep(random.randint(3, 10))

                        # 随机挑选商品
                        n = len(browser.find_elements_by_class_name("s-result-item"))
                        i = random.randint(0, n)
                        random_asin = browser.find_elements_by_class_name("s-result-item")[i].get_attribute("data-asin")
                        if browser.find_element_by_class_name("s-color-twister-title-link"):
                            asins = browser.find_element_by_class_name("s-color-twister-title-link")
                        else:
                            asins = browser.find_element_by_xpath("//a[@class='a-link-normal a-text-normal']")

                        if random_asin not in row["asin"]["asin"]:
                            if browser.find_element_by_class_name("s-color-twister-title-link"):
                                other_url = browser.find_element_by_class_name("s-color-twister-title-link")[i].get_attribute("href")
                            else:
                                other_url = browser.find_element_by_xpath("//a[@class='a-link-normal a-text-normal']")[i].get_attribute("href")
                        else:
                            if browser.find_element_by_class_name("s-color-twister-title-link"):
                                other_url = browser.find_elements_by_class_name("s-color-twister-title-link")[i].get_attribute("href")
                            else:
                                other_url = browser.find_elements_by_xpath("//a[@class='a-link-normal a-text-normal']")[i].get_attribute("href")
                        browser.get(other_url)

                        # 网络连接出错 重试
                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            browser.find_element_by_id('reload-button').click()
                            time.sleep(random.randint(3, 10))

                        # 商品详情页操作
                        goods_index_handle(random_asin)

                        # 网络连接出错 重试
                        # if browser.find_element_by_id('reload-button'):
                        #     print('This site can’t provide a secure connection')
                        #     # browser.find_element_by_id('reload-button').click()
                        #     browser.reload()
                        #     time.sleep(random.randint(3, 10))

                        time.sleep(random.randint(3, 6))
                        browser.find_element_by_class_name("olpOffer").get_attribute("a-button-input").click()

                        # 网络连接出错 重试
                        # if browser.find_element_by_id('reload-button'):
                        #     print('This site can’t provide a secure connection')
                        #     browser.find_element_by_id('reload-button').click()
                        #     time.sleep(random.randint(3, 10))

                        # 过滤安装费 添加数码产品时候会提示需不需要上面安装
                        if browser.find_element_by_id('btnVasModalSkip'):
                            browser.find_element_by_id('btnVasModalSkip').click()

                        print("其他商品添加到购物车成功")

                    # 下单流程
                    helper.click_by_id("nav-cart")
                    time.sleep(random.randint(3, 10))

                    # 网络连接出错 重试
                    # if browser.find_element_by_id('reload-button'):
                    #     print('This site can’t provide a secure connection')
                    #     browser.reload()
                    #     time.sleep(random.randint(3, 10))

                    '''
                    做一检察代理ip和城市是否发生的操作
                    '''
                    # tools.proxy_check(proxies=proxies, proxy_city=row['account']['register_city'],
                    #                   proxy_ip=getIpInfo_ip, task_id=row["task_id"])

                    print("删除购物车多余的商品")
                    # reply_log(row["task_id"], "删除购物车多余的商品", getIpInfo_ip, row['account']['register_city'])
                    # 更新
                    num = int(
                        browser.find_element_by_id('sc-subtotal-label-activecart').text.split('(')[1].split(' ')[0])
                    print(f'商品数量一共有{num} 个')
                    sameAsin = 1
                    for i in range(num):
                        data_asin = browser.find_element_by_**(".sc-list-item-border")[i]._element.get_attribute(
                            "data-asin")
                        if data_asin not in row["asin"]["asin"]:
                            time.sleep(random.randint(3, 10))
                            print(i)
                            print('delete this shopping')
                            time.sleep(random.randint(3, 10))
                            print('刷新网页')
                            browser.reload()
                            time.sleep(random.randint(3, 10))
                            try:
                                browser.find_by_xpath(
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
                                browser.find_element_by_**(".sc-list-item-border")[i].find_by_css(
                                    ".sc-action-delete").click()
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
                    if int(browser.find_element_by_id('sc-subtotal-label-activecart').text.split('(')[1].split(' ')[
                               0]) == 1:
                        try:
                            browser.find_element_by_**(".a-dropdown-container").last.click()
                            # 做一个判断（下拉菜单 第一个可能是 0）
                            page_num = browser.find_element_by_**(".a-popover-wrapper").last.find_by_tag(
                                "li").first.text
                            if page_num in '1':
                                browser.find_element_by_**(".a-popover-wrapper").last.find_by_tag("li").first.click()
                            else:
                                browser.find_element_by_**(".a-popover-wrapper").last.find_by_tag("li")[1].click()
                        except:
                            pass
                        try:
                            browser.find_element_by_name('quantityBox').click()
                            browser.find_element_by_name('quantityBox').clear()
                            browser.fill('quantityBox', 1)
                            browser.find_element_by_**(".sc-update-link").click()
                        except:
                            pass
                        time.sleep(random.randint(1, 3))
                        helper.click_by_id("sc-buy-box-ptc-button")
                        time.sleep(random.randint(3, 10))
                        helper = tools.sign_in_password(row['account']['login_amazon_email'],
                                                        row['account']["login_amazon_password"],
                                                        "https://www.amazon.com/gp/message", helper, row["task_id"], 1)

                        if row['account']['amazon_account_type'] == 3 or row['account']['amazon_account_type'] == 2:
                            if browser.find_element_by_**(".a-button-primary"):
                                helper.click_by_css(".a-button-primary")

                        # 网络连接出错 重试
                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            browser.reload()
                            time.sleep(random.randint(3, 5))

                        # 去掉会员广告弹窗
                        try:
                            vip_ad_box = browser.find_element_by_class_name("prime-nothanks-button")
                        except Exception as e:
                            pass
                        else:
                            print('出现广告弹窗')
                            vip_ad_box.click()
                        # 网络连接出错 重试

                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            browser.refresh()
                            time.sleep(random.randint(3, 10))
                        # 出现手机号码验证
                        if browser.find_element_by_id("authportal-center-section"):
                            time.sleep(5)
                            print('出现手机号码验证')
                            helper.click_by_id("ap-account-fixup-phone-skip-link")

                        # 网络连接出错 重试
                        if browser.find_element_by_id('reload-button'):
                            print('This site can’t provide a secure connection')
                            browser.refresh()
                            time.sleep(random.randint(3, 10))

                        isClickPrime = 0
                        # 选择免费物流 如果任务为会员 则点击会员申请
                        if 'request_amazon_account_type' in row:
                            if int(row['request_amazon_account_type']) == 2:
                                if browser.find_element_by_**('.prime-fake-radio'):
                                    browser.find_element_by_**('.prime-fake-radio').click()
                                    # 选择免费物流且注册会员后的弹窗处理 点击申请会员
                                    if browser.find_element_by_id('primeSignupButton'):
                                        browser.find_element_by_id('primeSignupButton').click()
                                        isClickPrime = 1
                                    elif browser.find_element_by_id('prime-acquisition-spc-popover-submit-button'):
                                        browser.find_element_by_id('prime-acquisition-spc-popover-submit-button').click()
                                        isClickPrime = 1
                        time.sleep(random.randint(2, 5))

                        '''
                        # 做一检察代理ip和城市是否发生的操作
                        # '''
                        # tools.proxy_check(proxies=proxies, proxy_city=row['account']['register_city'],
                        #                   proxy_ip=getIpInfo_ip, task_id=row["task_id"])

                        # 点击会员后，币种发生改变，需要再次点击marketplaceRadio
                        if browser.find_element_by_id("marketplaceRadio"):
                            helper.click_by_id("marketplaceRadio")

                        time.sleep(random.randint(3, 10))
                        # 获取金额
                        # 获取金额
                        try:
                            # text_price = browser.find_element_by_id("subtotals-marketplace-table").find_by_css(".grand-total-price").text
                            text_price = browser.find_element_by_id("subtotals-marketplace-table").find_by_css(
                                ".grand-total-price").text
                            print(f'金额为：{text_price}')
                            print(text_price.split())
                        except Exception as e:
                            # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
                            # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
                            # print(res.text)
                            # if 'ok' in res.text:
                            #     print('帐号任务解绑成功')
                            browser.quit()
                            time.sleep(random.randint(3, 10))
                            exit()
                        order_price = text_price.split()
                        if len(order_price) == 1:
                            order_price = text_price.split("$")[1]
                        else:
                            order_price = text_price.split()[1]
                        if float(order_price) > float(row['payment']['single_max_trade']):
                            print("订单金额大于50美金")
                            # reply_log(row["task_id"], "订单金额大于50美金", getIpInfo_ip, row['account']['register_city'])
                            dic = {}
                            dic[row["task_id"]] = {}
                            dic[row["task_id"]]["task_id"] = row["task_id"]
                            dic[row["task_id"]]["status"] = 25
                            dic[row["task_id"]]["order_no"] = '',
                            url = "http://third.gets.com/api/index.php"
                            params = {"act": "modifyTaskOrderStatus",
                                      "sec": "20171212getscn"}
                            response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
                            browser.quit()
                            exit()

                        img_file_name = browser.save_screenshot(img_dir + no)
                        print("保存浏览器截图:%s" % os.path.basename(img_file_name))
                        helper.click_by_css(".place-order-button-link")

                        time.sleep(random.randint(3, 10))
                        print("付款成功")
                        # reply_log(row["task_id"], "付款成功", getIpInfo_ip, row['account']['register_city'])
                        order_number_count = len(browser.find_element_by_**(".a-span7").find_by_tag("h5"))
                        if order_number_count == 1:
                            order_number = browser.find_element_by_**(".a-span7").find_by_tag("h5").find_by_css(
                                ".a-text-bold").text
                        else:
                            order_index = 0
                            for order_dom in browser.find_element_by_**(".a-span7").find_by_tag("h5"):
                                if browser.find_element_by_**(".a-span7").find_by_css(
                                        "ul[class='a-unordered-list a-vertical']")[order_index].find_by_css(
                                    "span[class='wrap-item-title']"):
                                    order_number = order_dom.find_by_css(".a-text-bold").text
                                    break
                                else:
                                    order_index += 1

                        helper.logger.info("Order Number: %s" % order_number)
                        cookies = browser.get_cookies()
                        cookies1 = {}
                        for cookie in cookies:
                            cookies1[cookie['name']] = cookie['value']
                        jsonCookies = json.dumps(cookies1)
                        payment_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                        payment_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
                        status = 2
                        if int(row['feedback']['request_feedback']) == 0 and int(row['review']['request_review']) == 0:
                            status = 6
                        elif int(row['feedback']['request_feedback']) == 0 and int(
                                row['review']['request_review']) != 0:
                            status = 4
                        dic = {}
                        dic[row["task_id"]] = {}
                        dic[row["task_id"]]["task_id"] = row["task_id"]
                        dic[row["task_id"]]["status"] = status
                        dic[row["task_id"]]["order_no"] = order_number
                        dic[row["task_id"]]["payment_date"] = payment_date + ' ' + payment_time
                        dic[row["task_id"]]["actual_order_amount"] = order_price
                        # 如果有两个订单号 则开通会员
                        if order_number_count == 2 or isClickPrime == 1:
                            dic[row["task_id"]]["is_open_prime"] = 1
                        # 保存一下订单信息 防止post失败
                        tools.save_file("%s.txt" % row["task_id"], json.dumps(dic), 'order')

                        url = "http://third.gets.com/api/index.php"
                        params = {"act": "modifyTaskOrderStatus",
                                  "sec": "20171212getscn"}
                        response = tools.post(requests.session(), url, params=params, post_data=json.dumps(dic))
                        # 下单时间
                        # order_num = int(row["order_num"]) + 1
                        # 提交账号信息
                        cookies = browser.get_cookies()
                        cookies1 = {}
                        for cookie in cookies:
                            cookies1[cookie['name']] = cookie['value']
                        jsonCookies = json.dumps(cookies1)
                        postDateUser = {
                            'data': {
                                'account_id': row['account']['account_id'],
                                'header': header,
                                'cookie': cookie
                            }
                        }
                        url = "http://third.gets.com/api/index.php"
                        params = {"act": "updateAccountLoginSuccessInfo",
                                  "sec": "20171212getscn"}
                        response = tools.post(requests.session(), url, params=params, post_data=jsonCookies)
                        img_file_name = browser.save_screenshot(img_dir + order_number)
                        helper.logger.info("保存浏览器截图:%s" % os.path.basename(img_file_name))
                        browser.quit()
                        os._exit(0)
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
                    browser.quit()
                    time.sleep(random.randint(3, 10))
                    exit()
            page_num += 1
            print("翻页查找%s" % page_num)
            # reply_log(row["task_id"], "翻页查找", getIpInfo_ip, row['account']['register_city'])
            try:
                next_btn = browser.find_element_by_xpath('//*[@id="search"]/div[1]/div[2]/div/span[8]/div/span/div/div/ul/li[7]/a')
            except Exception as e:
                print('没有下一页了...')
            else:
                next_btn.click()

            time.sleep(random.randint(3, 10))
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
        # browser.quit()
        exit()

except Exception as e:
    print('出现异常，重新启动')
    # reply_log(row["task_id"], "出现异常，重新启动刷单", getIpInfo_ip, row['account']['register_city'])
    # url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
    # res = tools.get(s, url=url.format(TASK_ID=row["task_id"]))
    # print(res.text)
    # if 'ok' in res.text:
    #     print('账号任务解绑成功_ok_ok_ok')

    traceback.print_exc()
    print(f'错误信息: {e}')
    browser.quit()
    exit()
finally:
    print('tuichu')
    # browser.quit()
    # os._exit(0)
