# -*- coding: utf-8

import json
import random
import time
from utils.logger import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
path = "chromedriver.exe"
driver = webdriver.Chrome(executable_path=path)
options = webdriver.ChromeOptions()

with open('cookies_hr.json', 'r') as f:
    cookies = json.loads(f.read())['cookies']    # 打开保存在本地的cookie

goal_url = 'https://rd5.zhaopin.com/resume/apply'


def judge_format():
    # 以上格式为处理不同格式的cookie
    if type(cookies) == dict:
        cook = get_api_cookie(cookies)
        do_cookies(cook)
    elif type(cookies) == list:
        do_cookies(cookies)


def deal_page():
    driver.get('https://rd5.zhaopin.com')
    driver.delete_all_cookies()        # 删除原始cookie
    judge_format()                     # 判断格式
    driver.refresh()                   # 刷新页面
    time.sleep(3)
    driver.get(goal_url)               # 访问目标页面
    time.sleep(5)


def get_api_cookie(cook):
    co = list()
    for key in cook:
        dic = dict()
        dic['domain'] = 'zhaopin.com'
        dic['path'] = '/'
        dic['name'] = key
        dic['value'] = cook[key]
        co.append(dic)

    time.sleep(3)
    return co


def do_cookies(cookie):
    for cook in cookie:  # 这里是cookies的信息
        if len(cook) < 6:
            new = dict(cook, **{
                "domain": "zhaopin.com",
                # "expires": "2019-08-07T03:19:00.679Z",
                "path": "/",
                # "httpOnly": False,
            })
        else:
            new = cook
        driver.add_cookie(new)


def solve_main_page():
    # 处理首页的各个简历的信息
    try:
        a = driver.find_element_by_xpath("//div[@class='user-name__inner']/a")   # 获取每个名字的节点可以 点击的 a 节点
    except:
        print('木有')
        time.sleep(10)
        solve_main_page()
        a = ''

    driver.execute_script("arguments[0].click();", a)
    time.sleep(5)
    scroll_page()
    html = driver.page_source
    parse_page(html)
    # time.sleep(10)

    # num = len(a)           # 获取节点的数量，然后点击的次数由这里决定
    # if num == 0:
    #     return False       # 如果到了这个页面也还没有数据的话，可能是数据没有加载出来或者页面错误

    # for i in range(num):
    #     driver.execute_script('window.open();')
    #     driver.switch_to_window(driver.window_handles[1])
    #     time.sleep(random.randint(3, 5))
    #     driver.execute_script("arguments[0].click();", i)     # 点击了名字 到了页面详情信息
    #     time.sleep(random.randint(5, 10))                     # 进来了， 然后就等它一会万一信号不好呢
    #     html = driver.page_source                             # 获取页面的源码信息，后面来处理
    #     parse_page(html)                                      # 看吧 就去处理信息了
    #     close_window()                                        # 本页信息处理完毕然后关掉当前页
    #     break                                                 # 暂时只处理第一页来试试


def parse_page(html):
    # 这里就是处理页面信息的地方,在这里我要把数据分开给不同的程序去处理 然后这里汇总
    time.sleep(3)   # 我就是喜欢慢慢来 稳一点
    with open('local.html', 'w', encoding='utf-8') as file:
        file.write(html)


def scroll_page():
    # 稍微滑动滑动页面嘛 假装我就是人
    time.sleep(2)
    for h in range(8):
        driver.execute_script(
            "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                a=500 * h, b=500 * (h + 1)))
        time.sleep(1)


def analysis_data(dic=None):
    with open('resume.json', 'r', encoding='utf-8') as f:
        jnf = json.loads(f.read())

    dataList = jnf['data']['dataList']
    # dataList = dic['data']['dataList']
    goal = {
        'data': []
    }
    for data in dataList:
        dst = []
        lsj = []
        desiredCitys = data['desiredCitys']
        lj = data['lastDetail']
        for desire in desiredCitys:
            desire_city = desire['cityName']           # 期望工作城市
            dst.append(desire_city)

        each_lj = {
            "beginData": lj["beginData"],
            "companyName": lj["companyName"],
            "jobName": lj["jobName"],
            "description": lj["description"]
        }
        lsj.append(each_lj)

        each_info = {
            "number": data['number'],                   # 就是那个唯一的 ID
            "name": data['userName'],                   # 姓名
            "createTime": data['createTime'],           # 刷新时间
            "gender": data['gender'],                   # 性别
            "workYears": data['workYears'],             # 工作年限
            "eduLevel": data['eduLevel'],               # 学历信息
            "city": data['city'],                       # 现居住地
            "school": data['school'],                   # 学校（多个的字符串）
            "phone": data['phone'],                     # 手机号信息
            "email": data['email'],                     # 邮箱信息
            "self_assessment": data['selfEvaluation'],  # 自我评价（不是要求的，但是留着）
            "desirecity": dst,                          # 期望的城市
            "lastJobDetail": lsj                        # 上个工作信息
        }

        goal['data'].append(each_info)

    ll = json.dumps(goal)
    with open('resume_first.json', 'w', encoding='utf-8') as file:
        file.write(ll)

def close_window():
    time.sleep(2)
    driver.close()
    time.sleep(5)


def close_browser():
    driver.quit()


def run():
    deal_page()        # 打开页面
    solve_main_page()  # 处理主页的内容
    close_browser()


if __name__ == '__main__':
    run()

# if type(cookies) == dict:
#     cooki = get_api_cookie(cookies)
#     do_cookies(cooki)
# elif type(cookies) == list:
#     do_cookies(cookies)
# 以上格式为处理不同格式的cookie
