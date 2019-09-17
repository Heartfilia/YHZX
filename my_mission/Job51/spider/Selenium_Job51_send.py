import datetime
import json
import re
import random
import requests

from spider.logger import *
from spider.helper import python_config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# test cookie
POST_URL = 'http://hr.gets.com:8989/api/autoOwnerResumeDownload.php?'
# 前程 关键字搜索 简历
receivers = python_config.receivers
handler = python_config.handler
company_name = python_config.company_name
chrome_port = python_config.chrome_port


class Job51Send(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
        self.search_url = 'https://ehire.51job.com/InboxResume/InboxRecentEngine.aspx'
        self.goal_url = 'https://ehire.51job.com/Navigate.aspx'
        self.cart_url = 'https://ehire.51job.com/Candidate/CompanyHrTmpNew.aspx'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))  # E:\Project\Job51_bak\spider

        # path = 'chromedriver.exe'
        # self.driver = webdriver.Chrome(executable_path=path)
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument(generate_user_agent(device_type="desktop"))
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # self.options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
        # self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=self.options)

    def get_first_page(self):
        self.driver.get(self.search_url)  # 打开最基本页面注入cookies
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
            )
        except Exception as e:
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            LOG.warning('*=*=*=** i need help to fresh the cookie **=*=*=*')
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            # send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('Program interrupt, needs to be fixed')

        self.do_search()        # search goal resume

    # ----------------------------- #
    def do_search(self):
        self.driver.get(self.search_url)
        time.sleep(random.uniform(1, 2))
        self.do_click_search()

    def do_click_search(self):
        ids = ['735617918']                                                                                    #
        key_click = self.driver.find_element_by_xpath('//a[@id="dic_keyword_2"]')
        self.driver.execute_script("arguments[0].click();", key_click)
        time.sleep(1)
        for Id in ids:
            time.sleep(0.5)
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            time.sleep(1)
            box_key = self.driver.find_element_by_xpath('//*[@id="ctlSearchInboxEngine1_txt_keyword"]')
            box_key.clear()
            box_key.send_keys(Id)
            time.sleep(1)
            sch = self.driver.find_element_by_xpath('//*[@id="div_searchlist"]/dl[4]/dd/div[1]/a')
            self.driver.execute_script("arguments[0].click();", sch)
            time.sleep(3)
            num_info = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
            num = re.findall(r'共(\d*)\+?条', num_info)[0]
            if num == '0':
                LOG.info('没有搜到此份简历，可能无效')
                data = ''
                kill_invalid_url = ''
                requests.post(kill_invalid_url, data=data)
            else:
                time.sleep(1)
                self.driver.find_element_by_xpath('//*[@id="trBaseInfo_1"]/td[3]/ul/li[1]/a').click()
                window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                try:
                    WebDriverWait(
                        self.driver,
                        30, poll_frequency=0.5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="tdseekname"]')))
                except Exception as e:
                    continue
                else:
                    time.sleep(2)
                    _name = self.driver.find_element_by_xpath('//*[@id="tdseekname"]').text
                    R_name = re.findall(r'(\w+)和Ta聊聊标签', _name)[0]
                    time.sleep(1)
                    self.driver.find_element_by_xpath(
                        '//*[@id="form1"]/div[7]/div[1]/div/div[3]/div[2]/div[1]/span').click()
                    time.sleep(1)
                    chose_time = self.driver.find_element_by_xpath('//*[@id="txt_interviewinvite_time"]')
                    self.driver.execute_script("arguments[0].click();", chose_time)

                    tomorrow_week = time.strftime('%a', time.localtime(time.time() + 86400))
                    if tomorrow_week == 'Sun':
                        next_day = time.strftime('%d', time.localtime(time.time() + 86400 * 2)).lstrip('0')
                    else:
                        next_day = time.strftime('%d', time.localtime(time.time() + 86400)).lstrip('0')

                    that_day = self.driver.find_element_by_xpath(
                        f'//*[@id="daterangepicker_txt_interviewinvite_time"]/div[4]/div[1]/table/tbody//td[text()="{next_day}"]')
                    self.driver.execute_script("arguments[0].click();", that_day)
                    time.sleep(0.8)
                    self.driver.find_element_by_xpath(
                        '//*[@id="daterangepicker_txt_interviewinvite_time"]/div[4]/div[2]/select[1]').click()
                    time.sleep(0.8)
                    self.driver.find_element_by_xpath(
                        '//*[@id="daterangepicker_txt_interviewinvite_time"]/div[4]/div[2]/select[1]/option[3]').click()
                    time.sleep(0.8)
                    make_sure = self.driver.find_element_by_xpath(
                        '//*[@id="daterangepicker_txt_interviewinvite_time"]/div[1]/div/button[1]')
                    self.driver.execute_script("arguments[0].click();", make_sure)
                    time.sleep(0.8)

                    bring_resume = self.driver.find_element_by_xpath(
                        '//*[@id="div_interviewinvite_remarks"]/label[1]/input')
                    self.driver.execute_script("arguments[0].click();", bring_resume)
                    time.sleep(0.5)

                    last_msg = self.driver.find_element_by_xpath('//*[@id="p_interviewinvite_msgcount"]/label').text
                    msg_num = re.findall(r'剩余(\d+)条', last_msg)[0]
                    if msg_num != '0':
                        send_k = self.driver.find_element_by_xpath('//*[@id="p_interviewinvite_msgcount"]/label/input')
                        self.driver.execute_script("arguments[0].click();", send_k)
                    time.sleep(0.5)

                    send_info = self.driver.find_element_by_xpath('//*[@id="div_interviewinvite_oper"]/a[2]')
                    # send_info = self.driver.find_element_by_xpath('//a[@id="interviewinviteconfirm"]')
                    self.driver.execute_script("arguments[0].click();", send_info)
                    time.sleep(5)
                    msg = f"""
********* Hr 自动化 ***********
状态情况：{R_name}:的邀约信息在前程发送成功!
发送时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}
"""
                    send_rtx_msg(msg, True)
                    self.driver.close()

    def post_resume(self, resume=None):
        url = POST_URL
        rq = self.session.post(url, json=resume)
        LOG.info(f'无效的简历为{resume},插入详情为:{rq.text}')

    # ---------------------------- #

    def run(self):
        self.get_first_page()


def send_rtx_msg(msg, flag=None):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    if flag:
        receivers = handler
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    Job51Send().session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    app = Job51Send()
    app.run()
    print('\033[1;45m 在此输入任意字符后程序再开始运行 \033[0m')
    input('>>>')
    while True:
        time_info = time.strftime('%a', time.localtime())
        if time_info not in ['Sun']:
            app = Job51Send()
            app.run()

        for _ in range(60):
            print(f"\r{random.choice('><|/I1X')}", end='')
            time.sleep(1)
