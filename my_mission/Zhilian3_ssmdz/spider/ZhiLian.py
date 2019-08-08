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
# from helper.Positions import POS        # 导入需要关注排行的位置的信息
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
        # self.driver.maximize_window()

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
            receivers = '聂清娜;陈淼灵'
            msg = '智联招聘自动追踪程序:广州时时美电子商务有限公司:24小时内重新登录来继续抓取信息'
            Message.send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》程序中断，需要维护信息了《《《《《《')

        time.sleep(5)

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
        receivers = '聂清娜;陈淼灵'                                        # <<<======
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
            company = self.driver.find_element_by_xpath('//td[@class="k-table__column"][5]').get_attribute('title')
            # company = '广州市银河在线饰品有限公司'
            page = self.driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
            # print('fresh_recruit:page:', page)
            main_nodes = self.driver.find_elements_by_xpath('//table/tbody/tr[@class="k-table__row"]/td[3]')

            api_all = self.get_info_api(company)   # 从规定的api里面获取到需要的信息  # dict
            pstn = [i['info'] for i in api_all['data'] if i]

            page_source = self.driver.page_source

            if company.strip() == "广州市银河在线饰品有限公司":
                com = '1'
            elif company.strip() == "广州外宝电子商务有限公司":
                com = '2'
            elif company.strip() == "广州时时美电子商务有限公司":
                com = '3'
            else:
                com = '1'

            reg = re.compile('>刷新时间：(.*?)</span>', re.S)
            time.sleep(5)
            li = reg.findall(page_source)

            time.sleep(1)

            qunty_xp = len(main_nodes)
            qunty_re = len(li)

            if qunty_xp > qunty_re:
                minu = qunty_xp - qunty_re
                for _ in range(minu):
                    li.insert(0, '')

            for node in main_nodes:
                time.sleep(2)
                try:
                    # i = node.find_element_by_xpath('./td[3]/div/p/span').text    # 简历时间信息
                    posi = node.find_element_by_xpath('./div').get_attribute('title')   # 判断 如果不在就插入 在就不管
                    # i = node.xpath('./td[3]/div/p/span')[0].strip()   # 简历时间信息
                except Exception as e:
                    LOG.warning('这个节点没有信息')
                    posi = ''

                try:
                    i = li[ind].strip()
                except:
                    i = ''

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
                    self.update_mysql_one(posi, i[:5])
                    if nums > int(lateRemind):
                        num += 1  # 统计有几个信息超过指定天没有刷新，有一个就加1
                else:
                    LOG.warning('没有查找到时间节点')
                    self.update_mysql_one(posi, 'Null')
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
        elif company == '广州时时美电子商务有限公司':
            cy = '3'
        else:
            cy = '1'

        ifo = requests.get(f'{ip_info}get/refresh/{cy}/z').text         # 这里地址也需要修改  《《《《《
        time.sleep(1)
        info = json.loads(ifo)
        # print('info:', type(info), info)   # dict
        return info

    def update_mysql_one(self, posi, dtm):
        sql = f'update info set lastFresh = "{dtm}" where info = "{posi.strip()}" and account=3'

        try:
            LOG.info('数据库准备修改数据>>>>>>>')
            self.cursor.execute(sql)
            self.db.commit()
            time.sleep(0.3)
        except Exception as e:
            LOG.warning('数据错误已经回滚>>>>>>>')
            self.db.rollback()

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
            time.sleep(0.3)
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
        # receivers = '朱建坤'                                              # <<<======
        receivers = '聂清娜;陈淼灵'
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
        self.driver.quit()

    def run(self):
        """
        程序主启动，包含》大 《异常检测
        :return:
        """
        self.get_post_page()
        self.driver.quit()


def main():
    app1 = ZhiLian()
    try:
        app1.run()
        LOG.info('招聘信息》》》抓取进程开启成功')
    except Exception as e:
        receivers = '朱建坤'
        msg = '2基本信息筛选1 出现问题，需要调试'
        Message.send_rtx_msg(receivers, msg)


if __name__ == '__main__':
    main()


