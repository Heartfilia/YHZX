# -*- coding: utf-8 -*-
# 智联招聘的信息爬取
import json
import re
import random
from threading import Thread
import requests
import pymysql
from urllib.request import quote
from utils.logger import *    # includes logging infos
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Queue
from helper.Our_company import o_comp   # 导入我们公司的信息 list
from helper.Positions import POS        # 导入需要关注排行的位置的信息
from helper.company import competitor   # 导入竞争者的信息
from spider import Message
from helper.mysql_config import *
from lxml import etree

# 这里是本地存的cookies,如果是selenium格式的话就不用这里了，直接用
# 如果是标准的大字典模式，就可以交给self.get_api_cookie()来处理
ip_info = "http://192.168.6.112:8000/api/"


class ZhiLian(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
        self.base_url = 'https://www.zhaopin.com/'
        self.goal_url = 'https://rd5.zhaopin.com/job/manage'
        self.hr_url = 'https://rd5.zhaopin.com/resume/apply'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
        self.refresh_queue = Queue()   # 刷新消息的队列
        self.output_queue = Queue()    # 发布时间的队列

        self.db = pymysql.connect(host=host,
                                  port=port,
                                  user=user,
                                  password=password,
                                  database=database)
        self.cursor = self.db.cursor()

        # 开启基本的信息
        self.path = "chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=self.path)
        self.options = webdriver.ChromeOptions()
        self.driver.maximize_window()

    @staticmethod
    def get_api_cookie(cook):
        """
        从接口获取cookie
        :return: selenium 可用的 cookies 格式
        """
        cookie = []
        for key in cook:
            dic = dict()
            dic['domain'] = 'zhaopin.com'
            dic['path'] = '/'
            dic['name'] = key
            dic['value'] = cook[key]
            cookie.append(dic)

        return cookie

    def do_cookies(self, cooki):
        for cook in cooki:  # 这里是cookies的信息
            if len(cook) < 6:
                new = dict(cook, **{
                    "domain": "zhaopin.com",
                    # "expires": "2019-08-07T03:19:00.679Z",
                    "path": "/",
                    # "httpOnly": False,
                })
            else:
                new = cook
            self.driver.add_cookie(new)

    def get_post_page(self):
        # 获取招聘信息页面
        self.driver.get(self.base_url)    # 打开最基本页面注入cookies
        self.driver.delete_all_cookies()

        if type(self.cookies) == dict:
            cooki = self.get_api_cookie(self.cookies)
            self.do_cookies(cooki)
        elif type(self.cookies) == list:
            self.do_cookies(self.cookies)

        time.sleep(3)
        self.driver.refresh()
        # 以下为打开新窗口，加载页面
        self.driver.execute_script('window.open();')
        self.driver.switch_to_window(self.driver.window_handles[1])

        self.driver.get(self.goal_url)   # 访问目标网站
        time.sleep(2)
        try:
            # 判断是否登录成功还是在登录页面
            # 1.寻找元素在不在 >>> 2.1.不在的话异常，然后异常里面进行阻塞,处理了后接着运行 2.2.存在表明登录成功
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH,
                     '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except Exception as e:
            LOG.error('*=*=*=* 没有找到元素，可能是页面元素信息变更 *=*=*=*=*')
            LOG.error('*=*=*=* 现在需要管理员重新登录页面来刷新cookie *=*=*=*')
            # from spider import Message
            # receivers = '聂清娜;张子珏'
            receivers = '朱建坤'                                               # <<<======
            msg = '智联招聘自动追踪程序::24小时内重新登录来继续抓取信息'
            Message.send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》程序中断，需要维护信息了《《《《《《')

        # time.sleep(2)
        # 以下为关闭前一个窗口，不过没有必要
        # driver.switch_to_window(driver.window_handles[0])
        time.sleep(5)

        # 此处是存cookie操作 暂时不管 也没有完成

        coo = self.driver.get_cookies()
        cook = list()
        for i in coo:
            if 'expiry' in i:
                del i['expiry']
            cook.append(i)
        # LOG.info('》》》刷新本地的Cookies，保持高可用《《《')
        self.save_cookies(cook)

        # =========================================================================================== #
        LOG.info('本地的cookies文件已经刷新')
        for h in range(3):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=500 * h, b=500 * (h + 1)))
            time.sleep(1)

        time.sleep(3)
        self.do_task()
        self.send_msg()
        time.sleep(3)
        # =========================================================================================== #
        self.cursor.close()
        self.db.close()
        time.sleep(random.randint(5, 10))
        self.get_hr_book()           # ======================  需  要  打  开  ===================== #

    def get_hr_book(self):
        time.sleep(random.randint(3, 5))
        self.driver.get(self.hr_url)
        time.sleep(random.randint(3, 5))
        all_num = self.driver.find_element_by_xpath('//div[@class="k-tabs__nav-wrapper"]/div/div[1]/span[2]').text
        print('所有简历数量为：', all_num)
        all_page = self.driver.find_element_by_xpath('//span[@class="k-pagination__total"]').text
        reg = re.compile('(\d*)')
        page = int([i for i in reg.findall(all_page) if i != ''][0])    # 总共的页数
        print('所有页数为：', page)
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=500 * h, b=500 * (h + 1)))
            time.sleep(1)

        for _ in range(1, page+1):
            try:
                LOG.info(f'当前位置为第{_}页！')
                WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//button[@class="btn-next"]'))
                )
                for h in range(8):
                    self.driver.execute_script(
                        "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                            a=500 * h, b=500 * (h + 1)))
                    time.sleep(1)

            except Exception as e:
                LOG.debug('没有找到下一页')
                break
            else:
                self.parse_page()
                LOG.debug('准备前往下一页')
                if _ > 4:
                    LOG.info('只查询前5页简历信息，现在页码超过5页，退出查询')
                    break
                self.do_next_pg()

    def parse_page(self):
        time.sleep(random.randint(3, 5))
        # from spider import Message
        receivers = '朱建坤'                                        # <<<======
        button = self.driver.find_element_by_xpath('//div[@class="resume-header__actions"]//i[@class="fa fa-th-list"]')
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(random.randint(3, 8))
        # print(self.driver.page_source)
        # 人员 ： //div[@class="fixable-list__body"]/div[1]//div[@class="user-name__inner"]/a/span/text()
        # 职位 ： //div[@class="fixable-list__body"]//p[@class="job-title"]/text()
        # 公司 ： //div[@class="fixable-list__body"]/div[2]//div[@class="cell-extend-simple"]//dl[1]/dd//li[1]/span[2]
        main_nodes = self.driver.find_elements_by_xpath('//div[@class="fixable-list__body"]/div[1]//div[@class="user-name__inner"]/a/span')

        time.sleep(random.randint(3, 8))
        for i in range(len(main_nodes)):
            staff = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]/div[1]//div[@class="user-name__inner"]/a/span').get_attribute('title')
            position = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]//p[@class="job-title"]')
            company = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]/div[2]//div[@class="cell-extend-simple"]//dl[1]/dd//li[1]/span[2]')
            time.sleep(1)
            dic = {
                "staff": staff if staff else '',
                "position": position.text if position else '',
                "company": company.text if company else ''
            }
            # jsd = json.dumps(dic)
            with open(self.base_dir + r'\resume.txt', 'a') as f:
                f.write(str(dic) + ',\n')
            # print('*-*-*-*-*-*-*-*-' * 6 + '\n', dic)

            if dic["staff"] in competitor:
                msg = f'应聘{dic["position"]}的{dic["staff"]}曾经在{dic["company"]}工作过'
                Message.send_rtx_msg(receivers, msg)

        LOG.info('抢人程序跑完了》》等待接下来的操作')

    def do_next_pg(self):
        time.sleep(random.randint(3, 5))
        button = self.driver.find_element_by_xpath("//button[@class='btn-next'][1]")
        time.sleep(random.randint(3, 5))
        self.driver.execute_script("arguments[0].click();", button)

    def save_cookies(self, cook):
        dic = {
            'fresh_time': time.ctime(time.time()),
            'cookies': cook
        }
        jsn = json.dumps(dic)
        with open(self.base_dir + '\cookies.json', 'w') as f:
            f.write(jsn)
        time.sleep(1)

    def isLeapYear(self, year):
        """
        判断当前是否为平年，闰年
        :param year:
        :return:
        """
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        else:
            return False

    def dayBetweenDates(self, month1, day1):
        """
        1：为起始日期，2：为终止日期
        判断year1是否为闰年，选择year1当年每月的天数列表
        :param month1: 终止日期的月份
        :param day1: 终止日期的天数
        :return: int类型的天数信息(两个时间节点相减的信息)
        """
        # 先设置了默认为2019年
        year1 = 2019
        year2 = 2019
        # 获取今天的时间的信息
        nowtime = time.localtime(time.time())  # time.struct_time(tm_year=2016, tm_mon=4, tm_mday=7, tm_hour=10,
                                               # tm_min=3, tm_sec=27, tm_wday=3, tm_yday=98,
                                               # tm_isdst=0)
        month2 = nowtime.tm_mon  # 今天的月
        day2 = nowtime.tm_mday   # 今天的日
        # now_hour = nowtime.tm_hour  # 打开检查程序的小时数
        if self.isLeapYear(year1):
            # print(str(year1) + ':闰年')
            dayofmonth1 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 列表下标从0开始的 所以后面计算月份天数的时候，传入的月份应该-1
        else:
            # print(str(year1) + ':非闰年')
            dayofmonth1 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        year_temp = year2 - year1
        month_temp = month2 - month1

        if year_temp == 0:
            if month_temp == 0:
                days = day2 - day1
            else:
                # days = dayofmonth1[month1 - 1] - day1 + day2  # '掐头去尾'
                i = 1
                sum = 0
                # 假设计算3月5号到6月4号的天数，先计算3，4，5月的总天数,所以是 [month1 + i - 1-1]，然后减去5，加上4
                while i < month_temp + 1:
                    day = dayofmonth1[month1 + i - 1 - 1]
                    sum += day
                    i += 1
                days = sum - day1 + day2
        else:
            if self.isLeapYear(year2):
                dayofmonth2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                year_days = 366
            else:
                dayofmonth2 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                year_days = 365
            i = 1
            sum1 = 0
            sum2 = 0
            middle_year_sum_days = 0

            # 获取小年份剩余的天数
            while i < month1:
                day = dayofmonth1[month1 - i - 1]
                sum1 += day
                i += 1
            other_days1 = year_days - sum1 - day1

            # 获取大年份经过的天数
            i = 1
            while i < month2:
                day = dayofmonth2[month2 - i - 1]
                sum2 += day
                i += 1
            other_days2 = sum2 + day2

            # 获取中间年份的天数
            i = 1
            while i < year_temp:
                middle_year = year1 + i
                if self.isLeapYear(middle_year):
                    year_day = 366
                else:
                    year_day = 365
                middle_year_sum_days += year_day
                i += 1
            days = middle_year_sum_days + other_days1 + other_days2

        return days    # 返回天数 int 类型

    def fresh_recruit(self):
        """
        2天前的刷新信息
        :return:
        """
        try:
            WebDriverWait(self.driver, 1800).until(
                EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
            )
        except Exception as e:
            LOG.error('*=*=*=* 没有找到元素，可能是页面元素信息变更 *=*=*=*=*')
            LOG.error('*=*=*=* 现在需要管理员重新登录页面来刷新cookie *=*=*=*')
            receivers = '朱建坤'                                              # <<<======
            msg = '智联相关的程序需要重新检测！'
            Message.send_rtx_msg(receivers, msg)
        else:
            time.sleep(3)
            ind = 0
            num = 0
            # 任务需求：检测到数据是2天没有刷新的就提醒
            # xpath: //tr[@class="k-table__row"]/td[3]/div/p/span
            # WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '')))
            # company = self.driver.find_element_by_xpath('//div[@class="user__basic"]/span[@class="user__name"]/span').text
            company = self.driver.find_element_by_xpath('//td[@class="k-table__column"][5]').get_attribute('title')
            # company = '广州市银河在线饰品有限公司'
            page = self.driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
            # print('fresh_recruit:page:', page)
            main_nodes = self.driver.find_elements_by_xpath('//table/tbody/tr[@class="k-table__row"]/td[3]')

            # test_node = self.driver.find_elements_by_xpath('//table/tbody/tr[@class="k-table__row"]/td[3]/div/p/span')

            # print('fresh_recruit:info:', info)
            # //tr[@class="k-table__row"]/td[3]/div/p/span
            # //tr[@class="k-table__row"]/td[3]/div/@title
            # info的每个信息格式为： 刷新时间：07-27 09:15（20天前）
            # print("company:", company)
            api_all = self.get_info_api(company)   # 从规定的api里面获取到需要的信息  # dict
            pstn = [i['info'] for i in api_all['data'] if i]

            # print('*' * 20)
            # LOG.info('因为Selenium的问题，直接拿不到数据，所以采取本地数据拿取到!')
            # with open('local_selenium.html', 'w', encoding='utf-8') as f:
            #     f.write(self.driver.page_source)
            # print('*' * 20)

            page_source = self.driver.page_source

            if company.strip() == "广州市银河在线饰品有限公司":
                com = '1'
            elif company.strip() == "广州外宝电子商务有限公司":
                com = '2'
            else:
                com = '1'

            # for i in test_node:
            #     time.sleep(1)
            #     print('i2:::', i.text)
            reg = re.compile('>刷新时间：(.*?)</span>', re.S)
            time.sleep(5)
            li = reg.findall(page_source)
            # with open('local_selenium.html', 'r', encoding='utf-8') as f2:
            #     time.sleep(5)
            #     page_source = f2.read()

            # time.sleep(1)
            # xpt = etree.HTML(page_source)

            time.sleep(1)
            # WebDriverWait(self.driver, 120).until(
            #     EC.presence_of_all_elements_located(
            #         (By.XPATH, '//table/tbody/tr[@class="k-table__row"]/td[3]/div/p/span'))
            # )
            # main_tm = xpt.xpath('//table/tbody/tr[@class="k-table__row"]/td[3]/div/p/span')
            qunty_xp = len(main_nodes)
            qunty_re = len(li)
            # print('len:xp::', qunty_xp)
            # print('len:re::', qunty_re)
            if qunty_xp > qunty_re:
                minu = qunty_xp - qunty_re
                for _ in range(minu):
                    li.insert(0, '')

            # print('re::', li)
            for node in main_nodes:
                # print('fresh_i', i.text.strip())
                time.sleep(2)
                try:
                    # i = node.find_element_by_xpath('./td[3]/div/p/span').text    # 简历时间信息
                    posi = node.find_element_by_xpath('./div').get_attribute('title')   # 判断 如果不在就插入 在就不管
                    # i = node.xpath('./td[3]/div/p/span')[0].strip()   # 简历时间信息
                except Exception as e:
                    LOG.warning('这个节点没有信息')
                    posi = ''

                try:
                    # i = main_tm[ind].strip()
                    i = li[ind].strip()
                except:
                    i = ''

                # print("11ii::", i)

                # posi = node.find_element_by_xpath('./td[3]/div').get_attribute('title')   # 判断 如果不在就插入 在就不管
                # posi = node.xpath('./td[3]/div/@title')                                  # 判断 如果不在就插入 在就不管
                # print("posi:", posi)
                if posi not in pstn:
                    if posi:
                        self.insert_mysql_one(com, posi)
                    lateRemind = '2'
                else:
                    y = api_all['data'][pstn.index(posi)]
                    y = y['lateRemind']
                    lateRemind = str(y)   # 获取需要提醒的天数

                ind += 1

                # print('简历时间 i:', i)    07-09 19:59（28天前）
                if i:
                    month = int(i[:2])     # 07
                    day = int(i[3:5])      # 27
                    # hour = int(i[6:8])  # 09
                    nums = self.dayBetweenDates(month, day)
                    if nums > int(lateRemind):
                        num += 1  # 统计有几个信息超过指定天没有刷新，有一个就加1
                else:
                    LOG.warning('没有查找到时间节点')
                    # print('没有查找到时间节点')
                    continue

            msg = f'您在{company}账号的第{page}页有{num}条简历信息超过规定天数没有刷新了'
            LOG.info(msg)
            self.refresh_queue.put(msg)
            return int(page)

    @staticmethod
    def get_info_api(company):
        time.sleep(0.5)
        if company == '广州市银河在线饰品有限公司':
            cy = '1'
        elif company == '广州外宝电子商务有限公司':
            cy = '2'
        else:
            cy = '1'

        ifo = requests.get(f'{ip_info}get/refresh/{cy}/z').text         # 这里地址也需要修改  《《《《《
        time.sleep(1)
        info = json.loads(ifo)
        # print('info:', type(info), info)   # dict
        return info

    def insert_mysql_one(self, com, posi):
        # 方案一 ======== api插入  服务端会出错
        # time.sleep(0.5)
        # pos = quote(posi)        # 这里需要处理下url
        # post_url = f'http://127.0.0.1:8000/api/post/{com}/z/{pos}'
        # time.sleep(0.5)
        # self.session.post(post_url)
        # 方案二 ======== 直接插入
        sql = f'insert into info(info, isRemind, lateRemind, account, platform) values ("{posi.strip()}", "1" , "2", "{com}", "智联")'

        try:
            LOG.info('数据库准备输入>>>>>>>')
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            LOG.warning('数据错误已经回滚>>>>>>>')
            self.db.rollback()

    def ipage(self):
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=500 * h, b=500 * (h + 1)))
            time.sleep(1)

        page = self.driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    def Have_next(self):
        # 检测是否有下一页，进行翻页处理     <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< problem
        # 此处均为测试信息，可以不管的
        try:
            # 不清楚这里的返回值是啥
            Is_Next = self.driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button/@disabled')
            print('is_next', Is_Next)
        except:
            # 以下的STATUS 都为 测试信息
            # print(Is_Next)
            STATUS = True
            print('出错了但是问题不大')
        else:
            if Is_Next == 'true':
                # 已经没有下一页了
                STATUS = False
                pass
            else:
                STATUS = True
                print('测试信息：', Is_Next)

        return STATUS

    def release_date(self):
        """
        检测30天信息
        :return:
        """
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
        )
        time.sleep(5)
        num = 0
        # 任务需求： 发布日期大于30天的提醒
        # xpath: //tr[@class="k-table__row"]/td[4]
        company = self.driver.find_element_by_xpath('//div[@class="rd55-header__login-point"]/span').text
        info = self.driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[4]')
        page = self.driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        for i in info:
            # i = " 2019-07-27 "
            i = i.text.strip()
            # print('30 i :', i)
            if i:
                month = int(i[5:7])
                day = int(i[-2:])
                nums = self.dayBetweenDates(month, day)
                if nums > 30:
                    num += 1  # 统计有几个信息超过30天没有 重新发布/上线
            else:
                continue
        msg = f'您在{company}账号的第{page}页有{num}个信息超过30天没有 重新发布/上线'
        LOG.info(msg)
        self.output_queue.put(msg)

    def fresh_cookie(self):
        # 获取cookie 相当于刷新
        rep = requests.get(self.base_url, cookies=self.cookies)
        time.sleep(5)
        coo = rep.cookies
        print(coo)
        cook = requests.utils.dict_from_cookiejar(coo)  # cookies 信息： {'at': 'bc68fccbe0994b6d8f20f10c6bf11e76',...
        print(cook)
        # return cook

    def send_msg(self):
        """
        发送消息的函数
        receivers = 字符串,多个信息用 英文分号 分割
        :return:
        """
        receivers = '朱建坤'                                              # <<<======
        # receivers = '聂清娜;张子珏;杨国玲;陈淼灵'
        f_n = 0
        o_n = 0
        fresh_msg = ''
        output_msg = ''
        # 从消息队列中把应该获取的信息拼接，下面那个循环一样的
        for _ in range(self.refresh_queue.qsize()):
            if self.refresh_queue.empty():
                break
            else:
                m = self.refresh_queue.get()
                fresh_msg += m

        for _ in range(self.output_queue.qsize()):
            if self.output_queue.empty():
                break
            else:
                m = self.output_queue.get()
                output_msg += m

        fre_re = re.compile(r'(\d*)条简历信息')
        out_re = re.compile(r'(\d*)个信息')
        cmp_re = re.compile(r'您在(\w+)账号的第')
        nm = fre_re.findall(fresh_msg)
        om = out_re.findall(output_msg)
        comp = cmp_re.findall(fresh_msg)[0]
        com_re = re.compile(r'(\w+?)账号的第')
        company = com_re.findall(comp)[0]
        # print('company:::', company)
        for i in nm:
            f_n += int(i)
        if f_n > 0:
            msg = f'您在智联的<<{company}>>账号的招聘信息总共有{f_n}条超过规定天数没有刷新了请及时处理,修改提醒请点击\n' \
                  f'http://192.168.6.112:8000/admin \n然后在后台管理系统中处理'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送刷新信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
            print('msg:::', msg)
        else:
            LOG.info('>>>>>>>>>没有需要发送的<刷新>信息')

        for i in om:
            o_n += int(i)
        if o_n > 0:
            msg = f'您在智联的{company}账号的招聘信息总共有{o_n}条超过30天没有重新发布/上线'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送发布信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
        else:
            LOG.info('>>>>>>>>>没有需要发送的<发布>信息')

    def do_task(self):
        """
        任务翻页以及处理同样的信息事情
        :return:
        """
        while True:
            # page 为总共有多少页
            page = self.ipage()
            # print(f'总共有:{page}页')
            # 搜索该页面的刷新信息
            nowpage = self.fresh_recruit()    # 返回当前所在的页面
            # 搜索该页面的发布信息
            LOG.info('*' * 50)
            self.release_date()
            # 此页面处理完毕后，判断页面是否有下一页，然后处理是否翻页
            if nowpage < page:
                # 有下一页，点击下一页
                button = self.driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button[2]')
                self.driver.execute_script("arguments[0].click();", button)
                LOG.info(f'在第{nowpage}页运行成功')
                time.sleep(5)
            else:
                break

    def test(self):
        """
        开发时候使用的测试函数
        :return:
        """
        # self.dayBetweenDates(1, 25)  # 直接返回天数
        # test01: 测试携带cookie登录
        self.get_post_page()      # 《《《 需要开
        # self.send_msg()           # 《《《 需要开
        # self.fresh_cookie()
        self.driver.quit()

    def run(self):
        """
        程序主启动，包含》大 《异常检测
        :return:
        """
        # get_cookie: 从给的借口获得账户的cookie
        # 启动程序
        self.get_post_page()       # 《《《 需要开

        self.driver.quit()
        # try:
        #     self.get_post_page()       # 《《《 需要开
        #     self.send_msg()            # 《《《 需要开
        # except Exception as e:
        #     # 程序出错，可能需要重新登录
        #     LOG.warning('》》！！》》程序异常，出了问题需要跟进处理《《！！《《')
        # finally:
        #     self.driver.quit()


class Rate(object):
    """
    智能检测排名靠后问题程序
    """
    def __init__(self):
        # self.option = webdriver.ChromeOptions()
        # self.option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # self.path = "chromedriver.exe"
        # self.browser = webdriver.Chrome(options=self.option, executable_path=self.path)
        self.base_url = 'https://sou.zhaopin.com/'
        self.js_url = 'https://fe-api.zhaopin.com/c/i/sou?'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
            'referer': 'https://www.zhaopin.com/',
        }
        # 信息已经过期
        self.req_cookies = {
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
            'sts_deviceid': '16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d',
            'acw_tc': '2760827115645391462656402e91acd157b0d446a910bb2afc512e1ed3ef06',
            'urlfrom2': '121126445',
            'adfcid2': 'none',
            'adfbid2': '0',
            'x-zp-device-id': 'd249967fbc2a8769053b7d5bfee9690b',
            'x-zp-dfp': 'zlzhaopin-1564541208377-824fee2b5b7e3',
            'JSloginnamecookie': '15521262081',
            'JSShowname': '""',
            'JSpUserInfo': '3d692e695671417154775b755c6a5c7541775869586953714c7129772775546a557545775d6958695a71457153775b75596a5c75417753692f6926714a7156775b755f6a52754777586953695d71447125771875186a4a751377076907695071247131775475586a5f7531773c6957695d715a7156774975586a55754a77596953695071367129775475586a5f7525772969576921713a7154775b755c6a5c75417758695869537142715e773c753d6a597541775369396922714a71557752753c6a34753e775569056905711971577759751f6a3b750477596906691271027114771875086a12752f770f690769037107710d7713751c6a527505770a69136950716',
            'uiioit': '3d753d684968426454380b6446684d7959745874566500395f732a753d68496844645e384',
            'zp-route-meta': 'uid=655193256,orgid=67827992',
            'login_point': '67827992',
            'promoteGray': '',
            'diagnosis': '0',
            'LastCity': '%E5%B9%BF%E5%B7%9E',
            'LastCity%5Fid': '763',
            'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D',
            'dywez': '95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html',
            '__utmz': '269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html',
            'NTKF_T2D_CLIENTID': 'guest848ED7A8-2D6C-CB43-D002-4785D3149DAB',
            'sou_experiment': 'psapi',
            'ZP_OLD_FLAG': 'false',
            'urlfrom': '121126445',
            'adfcid': 'none',
            'adfbid': '0',
            'dywea': '95841923.183147172171786560.1564539142.1564648972.1564714276.14',
            'dywec': '95841923',
            'dyweb': '95841923.1.10.1564714276',
            'Hm_lvt_38ba284938d5eddca645bb5e02a02006': '1564620760,1564709828,1564712348,1564714276',
            'Hm_lpvt_38ba284938d5eddca645bb5e02a02006': '1564714276',
            '__utma': '269921210.1113127844.1564539142.1564648972.1564714276.14',
            '__utmc': '269921210',
            '__utmt': '1',
            '__utmb': '269921210.1.10.1564714276',
            'sts_sg': '1',
            'sts_sid': '16c503d169151c-05fa9b217424fd-5a13331d-2073600-16c503d1692721',
            'sts_chnlsid': 'Unknown',
            'jobRiskWarning': 'true',
            'sts_evtseq': '2',
        }
        self.pos_que = Queue()      # 职位准备存入队列

    def next_page(self):
        """
        处理下一页 以及 判断总共页数
        :return:
        """
        try:
            # self.browser.find_element_by_class_name('btn soupager__btn soupager__btn--disable')  # 没有下一页的标志
            self.browser.find_element_by_class_name('btn soupager__btn')                           # 能翻页
        except Exception as e:
            # 最后一页
            status = False
        else:
            # 有下一页
            status = True
        finally:
            print(status)
            return status

    def case_rate(self):   # selenium
        # https://sou.zhaopin.com/?jl=763&sf=0&st=0&kw=python&kt=3&p=3
        # 重新开一个窗口，与公司账户端独立
        self.browser.get(self.base_url)
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="a-modal__content"]/div/button'))
        )
        self.browser.find_element_by_xpath('//div[@class="a-modal__content"]/div/button').click()
        time.sleep(2)
        LOG.info('二 》》》排名靠后检测问题程序打开')
        for position in POS:
            input_box = self.browser.find_element_by_class_name('search-box__common__input')
            time.sleep(1)
            input_box.clear()
            time.sleep(1)
            input_box.send_keys(position)
            print('能走到这里')
            time.sleep(1)
            for _ in range(1, 6):
                # self.browser.execute_script(jd)
                for h in range(20):
                    self.browser.execute_script(
                        "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                            a=500 * h, b=500 * (h + 1)))
                    time.sleep(1)

                time.sleep(10)
                if self.next_page():   # 判断是否有下一页，有的话就翻页，没有就break
                    # 翻页
                    print('有下一页')
                    pass
                else:
                    LOG.info(f'《{position}》这个职位没有下一页了当前为第{_}页')
                    break
                time.sleep(10)
        pass

    def re_get(self):
        # resp = requests.get(self.base_url, headers=self.headers, cookies=self.req_cookies, verify=False)

        # LOG.info('请求get信息的状态是:', resp.status_code)
        # cookie = resp.cookies
        # cookie = requests.utils.dict_from_cookiejar(cookie)
        # print(cookie)
        # with open('req_cookies.txt', 'w') as f:
        #     f.write(cookie)
        # return cookie
        pass

    def session_get(self):
        while True:
            if self.pos_que.empty():
                break
            else:
                position = self.pos_que.get()
                time.sleep(5)
                for page in range(6):
                    start = page * 90
                    now_page = page + 1       # 现在页数
                    params = {
                        "start": str(start),
                        "pageSize": "90",  # 每页数据
                        "cityId": "763",  # 广州
                        "workExperience": "-1",
                        "education": "-1",
                        "companyType": "-1",
                        "employmentType": "-1",
                        "jobWelfareTag": "-1",
                        "kw": position,
                        "kt": "3",      # 这个参数很重要，没有就服务器错误
                        # "_v": "0.33455201",  # <<<<<<<<<<<
                        # "x-zp-page-request-id": f"475845d52fa846b9b68d41ef6fce3fca-{int(time.time() * 1000)}-972139",  # <<<<<<
                        # "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5",
                        # 上面三个数据都不重要，可以不传输的
                    }
                    time.sleep(10)
                    try:
                        requests.packages.urllib3.disable_warnings()
                        resp = requests.get(self.js_url, params=params, headers=self.headers, cookies=self.req_cookies, verify=False)
                    except Exception as e:
                        LOG.error(f'{position}职位的第{now_page}页内容已经写入失败》[可能：请求信息过期或者没有后续页面了]》')
                        break
                    else:
                        dic = json.loads(resp.text, encoding='utf-8')
                        count = dic['data']['count']
                        LOG.info(f'{position}这个岗位总共有{count}个发布信息')
                        if int(count) > 90:
                            last_page = int(count) // 90      # 获取最后一页页码
                        else:
                            last_page = 1
                        data = dic['data']['results']    # list
                        now_info = [f'{position}:{now_page}:::']
                        for com in data:
                            co = com['company']['name']    # goal
                            now_info.append(co)
                        time.sleep(1)
                        with open('information.txt', 'a', encoding='gb18030') as f:
                            f.write(str(now_info) + '\r\n')
                        LOG.info(f'{position}职位的第{now_page}页内容已经写入成功》》》》》》')
                        now_page_info = set(now_info)
                        if now_page_info & o_comp:
                            LOG.info(f'##### 在第{now_page}页的<<{position}>>职位查到公司信息')
                            break    # 只要在规定页码内查到公司信息就可以退出了
                        if now_page == last_page:
                            if not now_page_info & o_comp:
                                LOG.warning(f'智联)))){position}>>职位没有在规定页码内，需要处理')
                                # from spider import Message
                                receivers = '朱建坤'                                              # <<<======
                                msg = f'2)))){position}>>职位没有在规定页码内，需要处理'
                                Message.send_rtx_msg(receivers, msg)
                                break
                        if count <= start:
                            LOG.info(f"<<<{position}>>>职位只有{now_page}页数据，已经停止搜索")
                            break

    def save_pos(self):
        for p in POS:
            LOG.info(f'！！！>>> {p} 职位已经放入队列 >>>>>')
            self.pos_que.put(p)

    def requests_json(self):
        with open('information.txt', 'a') as f:
            f.write(time.ctime(time.time()) + '::开始记录公司信息\n')
            f.write('=' * 50 + '\n')    #
        # self.re_get()
        q1 = []
        for i in range(1):
            t1 = Thread(target=self.save_pos)
            t1.start()
            LOG.info(f'#####存职位》》的线程{i}已经启动#####')
            q1.append(t1)

        time.sleep(random.randint(3, 7))

        q2 = []
        for i in range(2):
            t2 = Thread(target=self.session_get)
            LOG.info(f'#####搜信息》》的线程{i}已经启动#####')
            t2.start()
            q2.append(t2)

        time.sleep(random.randint(2, 5))
        for i in q1:
            i.join()
        LOG.info(f'#####存职位》》的线程已经回收#####')
        for i in q2:
            i.join()
        LOG.info(f'#####搜信息》》的线程已经回收#####')

    def run(self):
        try:
            # self.case_rate()  # 《《《 需要开
            self.requests_json()   # https://fe-api.zhaopin.com/c/i/sou?
        except Exception as e:
            # 程序出错，可能需要处理
            LOG.warning('》》》》》》程序异常，出了问题需要跟进处理《《《《《')
            receivers = '朱建坤'
            # receivers = '聂清娜;张子珏;杨国玲;陈淼灵'                        # <<<======
            msg = '自动排查排名靠后程序出错'
            Message.send_rtx_msg(receivers, msg)


class QiangRen(object):
    def __init__(self):
        self.t = int(time.time() * 1000)
        # self.goal_url = f'https://rd5.zhaopin.com/api/rd/resume/list?_={self.t}&x-zp-page-request-id=85e5a225faf442fbac34fb2286194763-{self.t}-42410&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5'
        self.goal_url = f'https://rd5.zhaopin.com/api/rd/resume/list?_=1564991558352&x-zp-page-request-id=b116247a3361418cbd6a9dbe2c5e7b0f-1564991390220-588985&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5'
        self.base_url = f'https://rd5.zhaopin.com/api/rd/resume/list?'
        self.headers = {
            # ':authority': 'rd5.zhaopin.com',
            # ':method': 'POST',
            # ':path': '/api/rd/resume/list?_=1564983961418&x-zp-page-request-id=dc2a6b8319ff46e8a59d18c6a0f88fb6-1564983960816-698407&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
            # ':scheme': 'https',
            'accept': 'application/json, text/javascript, */*; q=0.01',      # 这句很关键
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9',
            # 'content-length': '139',
            # 'content-type': 'text/plain',
            'origin': 'https://rd5.zhaopin.com',
            'referer': 'https://rd5.zhaopin.com/resume/apply',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
            # 'x-requested-with': 'XMLHttpRequest',
        }
        self.cookies = {
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',   #
            'sts_deviceid': '16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d',    #
            'urlfrom2': '121126445',    #
            'adfcid2': 'none',    #
            'adfbid2': '0',    #
            'x-zp-device-id': 'd249967fbc2a8769053b7d5bfee9690b',    #
            'acw_tc': '2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6',    #
            'x-zp-dfp': 'zlzhaopin-1564541208377-824fee2b5b7e3',    #
            'JSloginnamecookie': '15521262081',    #
            'JSShowname': '""',    #
            'JSpUserInfo': '3d692e695671417154775b755c6a5c7541775869586953714c7129772775546a557545775d6958695a71457153775b75596a5c75417753692f6926714a7156775b755f6a52754777586953695d71447125771875186a4a751377076907695071247131775475586a5f7531773c6957695d715a7156774975586a55754a77596953695071367129775475586a5f7525772969576921713a7154775b755c6a5c75417758695869537142715e773c753d6a597541775369396922714a71557752753c6a34753e775569056905711971577759751f6a3b750477596906691271027114771875086a12752f770f690769037107710d7713751c6a527505770a69136950716',   #
            'uiioit': '3d753d684968426454380b6446684d7959745874566500395f732a753d68496844645e384',    #
            'login_point': '67827992',    #
            'promoteGray': '',    #
            'diagnosis': '0',     #
            'LastCity': '%E5%B9%BF%E5%B7%9E',     #
            'LastCity%5Fid': '763',     #
            'dywez': '95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html',   #
            '__utmz': '269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html',   #
            'NTKF_T2D_CLIENTID': 'guest848ED7A8-2D6C-CB43-D002-4785D3149DAB',     #
            'sou_experiment': 'psapi',     #
            'ZP_OLD_FLAG': 'false',      #
            'zp-route-meta': 'uid=655193256,orgid=67827992',     #
            'urlfrom': '121126445',     #
            'adfcid': 'none',     #
            'adfbid': '0',     #
            'sts_sg': '1',    #
            'sts_chnlsid': 'Unknown',      #
            'jobRiskWarning': 'true',    #
            'dywec': '95841923',     #
            '__utmc': '269921210',     #
            'Hm_lvt_38ba284938d5eddca645bb5e02a02006': '1564714276,1564715492,1564724007,1564975164',    #
            'is-oversea-acount': '0',     #
            'at': 'bc68fccbe0994b6d8f20f10c6bf11e76',       #
            'rt': 'ed94a17d09454492a834a67a209f473a',       #
            'login-type': 'b',       #
            'zp_src_url': 'https%3A%2F%2Fpassport.zhaopin.com%2Forg%2Flogin%3Fbkurl%3Dhttps%253A%252F%252Frd5.zhaopin.com%252Fjob%252Fmanage',    #
            'JsNewlogin': '1837743086',     #
            'loginreleased': '1',        #
            'privacyUpdateVersion': '1',       #
            'CANCELALL': '1',         #
            'Hm_lpvt_38ba284938d5eddca645bb5e02a02006': '1564975254',          #
            'ZL_REPORT_GLOBAL': '{%22sou%22:{%22actionid%22:%22db6edcde-6d31-4be7-a83e-08f44595ff76-sou%22%2C%22funczone%22:%22smart_matching%22}}',   #
            'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D',  #
            # 'sts_sid': '16c6043c099ae4-09391b3f662b1c-5a13331d-2073600-16c6043c09aa50',
            'dywea': '95841923.183147172171786560.1564539142.1564983149.1564985773.19',     # <<<<<<
            '__utma': '269921210.1113127844.1564539142.1564983149.1564985773.18',           # <<<<<<
            # 'sts_evtseq': '4',
            # 'dyweb': '95841923.5.10.1564983149',
            # '__utmb': '269921210.5.10.1564983149',
        }

    def getpage(self,):
        # page = 1
        data = {
            '_': str(self.t),
            'x-zp-page-request-id': f'635a78aae7de43d6896046b171250cfa-{self.t - random.randint(100, 150)}-159627',
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
        }
        jsond = "isNewList=true&sort=time&S_ResumeState=1&S_CreateDate=190729,190805&S_feedback=&searchSource=1&page=1&pageSize=20"
        session = requests.Session()
        try:
            resp = session.post(self.goal_url, cookies=self.cookies, json=jsond, headers=self.headers, verify=False)
        except Exception as e:
            print('错误')
        else:
            jstr = resp.content.decode('utf-8')
            info = json.loads(jstr)
            print(info)
            # print(info['data']['dataList'])
            # for i in info['data']['dataList']:
            #     userName = i['userName']
            #     jobTitle = i['jobTitle']
            #     lastCompany = i['lastCompany']
            #     dic = {
            #         "userName": userName,
            #         "jobTitle": jobTitle,
            #         "lastCompany": lastCompany
            #     }
            #     print('*' * 50)
            #     print(dic)

    def run(self):
        self.getpage()    # 第一步，获取页面信息(api) 刷新本地cookies


def main():
    app1 = ZhiLian()
    app1.run()

    LOG.info('招聘信息》》》抓取进程开启成功')

    time.sleep(random.randint(30, 60))   # 因为没有用代理，所以这两个页面其实是同源的，防止ip被封，休息一段时间，反正也不急嘛

    app2 = Rate()
    app2.run()

    LOG.info('页面信息》》》抓取进程开启成功')
    #

    # time.sleep(10)
    # try:
    #     app3 = QiangRen()
    #     app3.run()
    # except Exception as e:
    #     LOG.error('### 抢人信息》》》抓取进程错误 ###')
    # else:
    #     # LOG.info('### 抢人信息》》》抓取进程开启成功 ###')
    #     print('### 抢人信息》》》抓取进程开启成功 ###')
    # app3 = QiangRen()
    # app3.run()


if __name__ == '__main__':
    main()


