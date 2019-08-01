# -*- coding: utf-8 -*-
# 智联招聘的信息爬取
# import time
from datetime import datetime
import re
import requests
from utils.logger import *    # includes logging infos
from helper.js_downpage import jd    # js to page bottom
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Queue

from helper.cookie2 import cookies

# 开启基本的信息
path = "chromedriver.exe"
driver = webdriver.Chrome(executable_path=path)
options = webdriver.ChromeOptions()
cookies2 = None


class ZhiLian(object):
    def __init__(self):
        self.base_url = 'https://www.zhaopin.com/'
        self.goal_url = 'https://rd5.zhaopin.com/job/manage'
        # self.test_url = 'https://blog.csdn.net/'
        # self.proxies = ''
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__))) + r'\utils'
        self.refresh_queue = Queue()   # 刷新消息的队列
        self.output_queue = Queue()    # 发布时间的队列

    def get_post_page(self):
        # 获取招聘信息页面  ####  先从接口获取cookie
        cke = self.get_
        driver.get(self.base_url)
        # 以下为测试信息
        # driver.get(self.test_url)
        driver.delete_all_cookies()
        for cook in cookies:                     #
            if len(cook) < 6:
                new = dict(cook, **{
                    "domain": ".zhaopin.com",
                    "expires": "2019-08-07T03:19:00.679Z",
                    "path": "/",
                    "httpOnly": False,
                })
            else:
                new = cook
            driver.add_cookie(cookie_dict=new)
        driver.refresh()
        # 以下为打开新窗口，加载页面
        driver.execute_script('window.open();')
        driver.switch_to_window(driver.window_handles[1])
        driver.get(self.goal_url)
        time.sleep(2)
        # 以下为关闭前一个窗口，不过没有必要
        # driver.switch_to_window(driver.window_handles[0])
        # time.sleep(5)

        # 此处是存cookie操作 暂时不管 也没有完成    《《《《《《《《《《《《《《《《《
        coo = driver.get_cookies()
        self.save_cookies(coo)

        driver.execute_script(jd)
        time.sleep(10)
        self.do_task()

    def save_cookies(self, coo):
        fna = self.base_dir + r'\cookies.py'
        print(type(coo))   # list
        print(coo)
        # with open(fna, 'w') as f:
        #     f.write()

    # 判断当前是否为平年，闰年
    def isLeapYear(self, year):
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        else:
            return False

    # 1：为起始日期，2：为终止日期 、判断year1是否为闰年，选择year1当年每月的天数列表
    def dayBetweenDates(self, month1, day1):
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
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
        )
        time.sleep(5)
        num = 0
        # 任务需求：检测到数据是2天没有刷新的就提醒
        # xpath: //tr[@class="k-table__row"]/td[3]/div/p/span
        # WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '')))
        page = driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        # print('fresh_recruit:page:', page)
        info = driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[3]/div/p/span')
        # print('fresh_recruit:info:', info)
        # info的每个信息格式为： 刷新时间：07-27 09:15（4天前）
        for i in info:
            # print('fresh_i', i.text.strip())
            i = i.text.strip()
            if i:
                # print("简历刷新信息:", i)
                month = int(i[5:7])  # 07
                day = int(i[8:10])   # 27
                # hour = int(i[11:13])  # 09
                nums = self.dayBetweenDates(month, day)
                if nums > 2:
                    num += 1  # 统计有几个信息超过两天没有刷新，有一个就加1
            else:
                continue

        # 以下print转换为msg信息发送给关注人
        msg = f'您在第{page}页有{num}条简历信息超过2天没有刷新了'
        LOG.info(msg)
        self.refresh_queue.put(msg)
        return int(page)

    def do_task(self):
        while True:
            # page 为总共有多少页
            page = self.ipage()
            # print(f'总共有:{page}页')
            # 搜索该页面的刷新信息
            nowpage = self.fresh_recruit()    # 返回当前所在的页面
            # 搜索该页面的发布信息
            LOG.info(f'****************')
            self.release_date()
            # 此页面处理完毕后，判断页面是否有下一页，然后处理是否翻页
            # self.Have_next()  # 暂时可以不管这个方式
            if nowpage < page:
                # 有下一页，点击下一页
                button = driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button[2]')
                driver.execute_script("arguments[0].click();", button)
                LOG.info(f'在第{nowpage}页运行成功')
                time.sleep(5)
            else:
                break

    @staticmethod
    def ipage():
        # 返回共有多少页
        driver.execute_script(jd)
        page = driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    @staticmethod
    def Have_next():
        # 检测是否有下一页，进行翻页处理                     <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< problem
        try:
            # 不清楚这里的返回值是啥
            Is_Next = driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button/@disabled')
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
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
        )
        time.sleep(5)
        num = 0
        # 任务需求： 发布日期大于30天的提醒
        # xpath: //tr[@class="k-table__row"]/td[4]
        info = driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[4]')
        page = driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        for i in info:
            # i = " 2019-07-27 "
            i = i.text.strip()
            if i:
                month = int(i[5:7])
                day = int(i[-2:])
                nums = self.dayBetweenDates(month, day)
                if nums > 30:
                    num += 1  # 统计有几个信息超过30天没有 重新发布/上线
            else:
                continue
        # 以下print转换为msg信息发送给关注人
        msg = f'您在第{page}页有{num}个信息超过30天没有 重新发布/上线'
        LOG.info(msg)
        self.output_queue.put(msg)

    def case_rate(self):
        # https://sou.zhaopin.com/?p=3&jl=763&sf=0&st=0&kw=python&kt=3
        # 解决关键职位页面太后问题
        pass

    def fresh_cookie(self):
        # 获取cookie 相当于刷新
        rep = requests.get(self.base_url, cookies=cookies)
        coo = rep.cookies
        cook = requests.utils.dict_from_cookiejar(coo)  # cookies 信息： {'at': 'bc68fccbe0994b6d8f20f10c6bf11e76',...
        return cook

    def send_msg(self):
        # 发送消息
        receivers = '朱建坤'
        # receivers = '聂清娜;张子珏;杨国玲;陈淼灵'
        f_n = 0
        o_n = 0
        fresh_msg = ''
        output_msg = ''
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
        nm = fre_re.findall(fresh_msg)
        om = out_re.findall(output_msg)
        for i in nm:
            f_n += int(i)
        if f_n > 0:
            msg = f'您在智联的招聘信息总共有{f_n}条超过2天没有刷新了'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送刷新信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
        else:
            LOG.info('>>>>>>>>>没有需要发送的刷新信息')

        for i in om:
            o_n += int(i)
        if o_n > 0:
            msg = f'您在智联的招聘信息总共有{o_n}条超过30天没有重新发布/上线'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送发布信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
        else:
            LOG.info('>>>>>>>>>没有需要发送的发布信息')

    def test(self):
        # self.dayBetweenDates(1, 25)  # 直接返回天数
        # test01: 测试携带cookie登录
        self.get_post_page()
        self.send_msg()
        driver.quit()
        pass

    def run(self):
        # get_cookie: 从给的借口获得账户的cookie
        # 启动程序
        driver.quit()
        pass


if __name__ == '__main__':
    app = ZhiLian()
    app.test()
    # app.run()

