# -*- coding: utf-8 -*-
# 智联招聘的信息爬取
import time
import datetime
# import re
import requests
from utils.logger import *    # includes logging infos
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        self.test_url = 'https://blog.csdn.net/'
        # self.proxies = ''
        self.session = requests.Session()

    def get_post_page(self):
        # 获取招聘信息页面 # 此处添加cookie出错
        driver.get(self.base_url)
        # 以下为测试信息
        # driver.get(self.test_url)
        # cook = self.fresh_cookie()
        # cook = driver.get_cookies()
        # print(cook)
        driver.delete_all_cookies()
        for cook in cookies:                     # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< error
            new = dict(cook, **{
                "domain": ".zhaopin.com",
                "expires": "2019-08-07T03:19:00.679Z",
                "path": "/",
                "httpOnly": False,
            })
            driver.add_cookie(cookie_dict=new)
        driver.refresh()
        # 以下为打开新窗口，加载页面
        driver.execute_script('window.open();')
        driver.switch_to_window(driver.window_handles[1])
        driver.get(self.goal_url)
        time.sleep(2)
        # 以下为关闭前一个窗口，不过没有必要
        driver.switch_to_window(driver.window_handles[0])
        time.sleep(5)
        # driver.close()
        coo = driver.get_cookies()
        cookies2 = coo
        # self.do_task()
        driver.quit()

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
        num = 0
        # 任务需求：检测到数据是2天没有刷新的就提醒
        # xpath: //tr[@class="k-table__row"]/td[3]/div/p/span
        # WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '')))
        page = driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        info = driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[3]/div/p/span').text
        # info的每个信息格式为： 刷新时间：07-27 09:15（4天前）
        for i in info:
            i = i.strip()
            month = int(i[5:7])  # 07
            day = int(i[8:10])   # 27
            # hour = int(i[11:13])  # 09
            nums = self.dayBetweenDates(month, day)
            if nums > 2:
                num += 1  # 统计有几个信息超过两天没有刷新，有一个就加1

        # 以下print转换为msg信息发送给关注人
        print(f'您在第{page}页有{num}条简历信息超过2天没有刷新了')
        return int(page)

    def do_task(self):
        while True:
            # page 为总共有多少页
            page = self.ipage()
            # 搜索该页面的刷新信息
            nowpage = self.fresh_recruit()    # 返回当前所在的页面
            # 搜索该页面的发布信息
            self.release_date()
            # 此页面处理完毕后，判断页面是否有下一页，然后处理是否翻页
            # self.Have_next()  # 暂时可以不管这个方式
            if nowpage < page:
                # 有下一页，点击下一页
                driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button[2]').click()

    def ipage(self):
        # 返回共有多少页
        page = driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    def Have_next(self):
        # 检测是否有下一页，进行翻页处理                     <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< problem
        try:
            # 不清楚这里的返回值是啥
            Is_Next = driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button/@disabled')
        except:
            # 以下的STATUS 都为 测试信息
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
        # 处理是否有下一页
        finally:
            Bool = STATUS

        return Bool

    def release_date(self):
        num = 0
        # 任务需求： 发布日期大于30天的提醒
        # xpath: //tr[@class="k-table__row"]/td[4]
        info = driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[4]').text
        page = driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        for i in info:
            # i = " 2019-07-27 "
            i = i.strip()
            month = int(i[5:7])
            day = int(i[-2:])
            nums = self.dayBetweenDates(month, day)
            if nums > 30:
                num += 1  # 统计有几个信息超过30天没有 重新发布/上线
        # 以下print转换为msg信息发送给关注人
        print(f'您在第{page}页有{num}个信息超过30天没有 重新发布/上线')

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

    def send_msg(self, msg=None):
        # 发送消息
        receivers = '朱建坤'
        # receivers = '聂清娜;张子珏;杨国玲;陈淼灵'
        # msg = 'testinfo2'
        post_data = {
            "sender": "系统机器人",
            "receivers": receivers,
            "msg": msg,
        }
        self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)

    def test(self):
        # self.dayBetweenDates(1, 25)  # 直接返回天数
        # test01: 测试携带cookie登录
        self.get_post_page()
        # self.send_msg()

    def run(self):
        pass


if __name__ == '__main__':
    app = ZhiLian()
    app.test()
    # app.run()

