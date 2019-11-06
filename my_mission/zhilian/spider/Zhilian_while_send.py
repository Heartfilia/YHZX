# -*- coding: utf-8 -*-
# auto crawl download resume
# __author__ = 'lodge'
# done_time = '22/08/2019' -- d/m/y
import importlib
import json
import random
import requests
from utils.logger import *    # includes logging infos
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
# =================================== #
import urllib3

ua = UserAgent()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# =================================== #

# Here are locally stored cookies. If it is in the selenium format, you don't need to use them
# In the case of the standard large dictionary pattern, you can hand it by self.get_api_cookie()
from helper import python_config

receivers = python_config.receivers
company_name = python_config.company_name
handler = python_config.handler


class ResumeDownloader(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
        self.base_url = 'https://www.zhaopin.com/'
        self.search_url = 'https://rd5.zhaopin.com/custom/searchv2/result'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
        self.driver = webdriver.Chrome()
        self.options = webdriver.ChromeOptions()
        # self.driver.maximize_window()

    @staticmethod
    def get_api_cookie(cook):
        """
        get cookie from api
        :return: selenium COULD USE this cookies format
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
        for cook in cooki:  # here are cookies' info
            if len(cook) < 6:
                new = dict(cook, **{
                    "domain": "zhaopin.com",
                    "path": "/",
                })
            else:
                new = cook
            self.driver.add_cookie(new)

    def get_post_page(self):
        # get base website and insert cookies information
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()

        if type(self.cookies) == dict:
            cooki = self.get_api_cookie(self.cookies)
            self.do_cookies(cooki)
        elif type(self.cookies) == list:
            self.do_cookies(self.cookies)

        time.sleep(3)
        self.driver.refresh()

        self.driver.get(self.search_url)   # access the goal website
        time.sleep(2)
        self.driver.refresh()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except Exception as e:
            print(e)
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            LOG.warning('*=*=*=*= i need help to fresh the cookie =*=*=*=*')
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：智联{company_name}简历邀请发送程序发现异常
处理标准：请到服务器手动处理登陆状态后等待即可
"""
            self.send_rtx_msg(msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》Program interrupt, need to fix《《《《《《')

        time.sleep(5)

        coo = self.driver.get_cookies()
        cook = list()
        for i in coo:
            if 'expiry' in i:
                del i['expiry']
            cook.append(i)
        self.save_cookies(cook)

        LOG.info('local cookies file has been refreshed')
        # =========================================================================================== #

        while True:
            self.search_page()
            time.sleep(20)

    def search_page(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="searchv2-intro__show-helper"]/img'))
            )
        except Exception as e:
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：智联{company_name}简历下载程序发现异常
处理标准：请人为到服务器手动处理登陆状态后重启程序
"""
            # self.send_rtx_msg(msg)
        else:
            time.sleep(1)
            photo = self.driver.find_element_by_xpath('//div[@class="searchv2-intro__show-helper"]/img')
            self.driver.execute_script("arguments[0].click();", photo)

        time.sleep(5)

        # input key_resume words here then get download resume
        # ==================================================== #
        # add key into input box and search to download
        resume_id_button = self.driver.find_element_by_xpath('//div[@class="k-tabs__nav"]/a[3]')
        self.driver.execute_script("arguments[0].click();", resume_id_button)
        self.do_input_key()

    def do_input_key(self):
        while True:
            api_get_url = 'http://hr.gets.com:8989/api/autoGetInterview.php?type=getInterview'
            list_dict_base = requests.get(api_get_url)
            list_dict = json.loads(list_dict_base.text)
            if list_dict:
                # extract content to search and download deliver then send to api_post
                for ld in list_dict:
                    if ld['resume_from'] != '2':
                        continue
                    if not ld['external_resume_id']:
                        print('空id,消除先')
                        self.session.post(
                            'http://hr.gets.com:8989/api/autoGetInterview.php?type=setInterview&external_resume_id=')
                    window = self.driver.window_handles
                    self.driver.switch_to.window(window[0])         # make sure that it was in search window
                    time.sleep(0.5)
                    input_box = self.driver.find_element_by_xpath('//div[@id="form-item-54"]/div/input')
                    input_box.clear()
                    input_box.send_keys(ld['external_resume_id'])
                    time.sleep(0.5)
                    search = self.driver.find_element_by_xpath(
                        '//*[@id="resume-filter-form"]/div/div/div[2]/div/button[2]')
                    self.driver.execute_script("arguments[0].click();", search)
                    time.sleep(3)
                    self.do_send_invite(ld['external_resume_id'])

            time.sleep(60)

    def do_send_invite(self, e_id):
        try:
            one = self.driver.find_element_by_xpath('//tbody[@class="k-table__body"]/tr[1]/td[2]/div/a')
            self.driver.execute_script("arguments[0].click();", one)
        except Exception as e:
            pass
        else:
            time.sleep(2)
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window)-1])
            page_source = self.driver.page_source
            if '面试时间'in page_source:
                print(f'{e_id}:已经邀约了......')
                self.session.post(
                    f'http://hr.gets.com:8989/api/autoGetInterview.php?type=setInterview&external_resume_id={e_id}')
                self.driver.close()
                return ''
            if ' 我要联系 TA' in page_source:
                self.driver.find_element_by_xpath(
                    '//*[@id="resume-detail-wrapper"]/div[1]/div[2]/div/div[1]/div[2]/a[1]').click()
                time.sleep(random.uniform(1, 2))

            self.driver.find_element_by_xpath('//div[@class="resume-content__status-box"]/a[2]').click()
            time.sleep(3)
            self.input_invite_detail(e_id)

    def input_invite_detail(self, e_id):
        time.sleep(10)
        tomorrow_week = time.strftime('%a', time.localtime(time.time() + 86400))
        if tomorrow_week == 'Sun':
            tomorrow_info = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 2))
            next_day = time.strftime('%d', time.localtime(time.time() + 86400 * 2)).lstrip('0')
            invite_week = time.strftime('%a', time.localtime(time.time() + 86400 * 2))
        else:
            tomorrow_info = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400))
            next_day = time.strftime('%d', time.localtime(time.time() + 86400)).lstrip('0')
            invite_week = time.strftime('%a', time.localtime(time.time() + 86400))

        t_info = self.driver.find_element_by_xpath(
            '//*[@id="send-interview"]/div/div[3]/form/div[2]/div/div[1]/div/input')
        self.driver.execute_script("arguments[0].click();", t_info)
        time.sleep(3)
        day_info = self.driver.find_element_by_xpath(
            f'//table[@class="k-date-table"]/tbody//span[text()="{next_day}"]'
        )
        # day_info.click()
        self.driver.execute_script("arguments[0].click();", day_info)
        time.sleep(1)
        notice_box = self.driver.find_element_by_xpath(
            '//div[@class="k-form-item__content interview-remark__content"]/div[1]/textarea')
        notice_box.clear()
        week_info = self.do_week_turn(invite_week)
        notice_box.send_keys(f'可以于{tomorrow_info}-{week_info},上午10:00-下午16:30前来面试,记得【携带简历】')
        self.send_message()
        # post_invite = self.driver.find_element_by_xpath('//*[@id="send-interview"]/div/div[4]/div[5]/button[1]')
        post_invite = self.driver.find_element_by_xpath('//*[@id="send-interview"]/div/div[4]/div[5]/button[2]')
        self.driver.execute_script("arguments[0].click();", post_invite)
        cancel_api = 'http://hr.gets.com:8989/api/autoGetInterview.php?type=setInterview&external_resume_id='
        self.session.post(cancel_api + e_id)
        LOG.info(f'{e_id}:的邀约信息发送成功')
        self.driver.close()

    @staticmethod
    def do_week_turn(invite_week):
        if invite_week == 'Sun':
            return '星期天'
        elif invite_week == 'Mon':
            return '星期一'
        elif invite_week == 'Tue':
            return '星期二'
        elif invite_week == 'Wed':
            return '星期三'
        elif invite_week == 'Thu':
            return '星期四'
        elif invite_week == 'Fri':
            return '星期五'
        elif invite_week == 'Sat':
            return '星期六'

    def send_message(self):
        time.sleep(2)
        coin = self.driver.find_element_by_xpath('//*[@id="send-interview"]/div/div[4]/div[4]/div/span').text
        if coin == '0':
            print(coin)
            pass
        else:
            self.driver.find_element_by_xpath(
                '//*[@id="send-interview"]/div/div[4]/div[4]/div/label/span[1]/span/i').click()

    @staticmethod
    def handle_0(n):
        if len(n) == 1:
            num = f'0{n}'
        else:
            num = n
        return num

    def do_get_requests_detail(self, resume_no):
        url = "https://rd5.zhaopin.com/api/rd/resume/detail?"
        # print('resume_no:', resume_no)
        time.sleep(random.uniform(1, 2))
        params = self.params_get(resume_no)
        headers = self.headers_get(resume_no)
        try:
            response = requests.get(url, params=params, headers=headers, verify=False)
            print('response::', response.text)
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            self.driver.close()
        except:
            LOG.error('status_code: <404> NOT FOUND')
        else:
            return json.loads(response.text)

    @staticmethod
    def params_get(ID_info):
        resume_no = ID_info.replace('%3B', ';')
        resume_no = resume_no.replace('%25', ')')
        resume_no = resume_no.replace('%28', '(')
        resume_no = resume_no.replace('%29', ')')
        print('resume_no::', resume_no)
        t = time.time()
        node = int(t * 1000)
        front = [
            '46ba3dcc4781446ab7b77f11468b6c36',
            '15f87159b7c440078fedea3be92d26e7',
            '97ea329932f04166b268e0cb0b2bfd61',
            'bf37a85ca31548808cc4f6222bf07783',
            'ab21f32d3b93418495b69a0b6b3f84dd',
            '914b5ee54b914c71a986c1ca8a163109',
            '6738b88351c04abb8784fc8393746192',
            '8d6f9ad358c34b84918ab5bf4887e677'
        ]
        max_len = len(front) - 1
        params = {
            "_": f"{node}",
            "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 999999)}",
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
            'resumeNo': f'{resume_no}'
        }
        return params

    @staticmethod
    def headers_get(resume_no):
        from spider import cookies
        cookie = importlib.reload(cookies).cookie
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Content-Type': 'text/plain',
            'Sec-Fetch-Mode': 'cors',
            "sec-fetch-site": "same-origin",
            'User-Agent': ua.random,
            'X-Requested-With': 'XMLHttpRequest',
            'zp-route-meta': 'uid=655193256,orgid=67827992',
            'referer': f'https://rd5.zhaopin.com/resume/detail?keyword=&resumeNo={resume_no}&openFrom=1',
            "cookie": cookie
        }
        return headers

    # 丄============================================ #
    def send_rtx_msg(self, msg):
        """
        rtx remind
        :param receivers:
        :param msg:
        :return:
        """
        post_data = {
            "sender": "系统机器人",
            "receivers": receivers,
            "msg": msg,
        }
        # self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)

    def save_cookies(self, cook):
        dic = {
            'fresh_time': time.ctime(time.time()),
            'cookies': cook
        }
        jsn = json.dumps(dic)
        with open(self.base_dir + r'\cookies.json', 'w') as f:
            f.write(jsn)
        time.sleep(1)

    def i_page(self):
        # the script does not need this module
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=50 * h, b=50 * (h + 1)))
            time.sleep(0.3)

        page = self.driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    def run(self):
        """
        程序主启动，包含》大 《异常检测
        :return:
        """
        self.get_post_page()
        self.driver.quit()

    def quit(self):
        self.driver.quit()


def main():
    # app1 = ResumeDownloader()
    # app1.run()
    while True:
        print('\033[1;45m 在此输入任意字符后程序再开始运行 \033[0m')
        input('>>>')
        try:
            app1 = ResumeDownloader()
            app1.run()
        except Exception as e:
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：智联{company_name}简历下载程序发现异常
处理标准：请人为到服务器手动处理登陆状态后重启程序
"""
            # app1.send_rtx_msg(msg)
            app1.quit()
            break
        else:
            for _ in range(20):
                time.sleep(1)


if __name__ == '__main__':
    main()
