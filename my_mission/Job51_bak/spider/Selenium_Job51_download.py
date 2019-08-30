import datetime
import json
import re
import random
import requests
from lxml import etree
from pygments.console import esc
from user_agent import generate_user_agent

from spider.logger import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# test cookie
# cookie = "guid=e81bba60a47ccb706a6a99ab93918824; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; EhireGuid=e82df8d95f004368aca6757974f4ed5c; LangType=Lang=&Flag=1; _ujz=MTU3NTgxNzc3MA%3D%3D; RememberLoginInfo=member_name=7A4B1B5BF1669EE7E4DDD8913FED4ECD&user_name=86404CFDD31E2394; search=jobarea%7E%60030200%7C%21ord_field%7E%600%7C%21recentSearch0%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAPython+%B8%DF%BC%B6%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch1%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FApython%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch2%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch3%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAphp%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch4%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAamazon%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21collapse_expansion%7E%601%7C%21; 51job=cenglish%3D0%26%7C%26; ASP.NET_SessionId=xczei1muubtzxmtiew5wgivb; AccessKey=41d21038f461460; HRUSERINFO=CtmID=2725554&DBID=4&MType=02&HRUID=5975204&UserAUTHORITY=1100111010&IsCtmLevle=1&UserName=yhzx153&IsStandard=0&LoginTime=08%2f24%2f2019+09%3a18%3a21&ExpireTime=08%2f24%2f2019+09%3a28%3a21&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=0&CtmLiscense=6&mb=&AccessKey=7e38cbf133a066c0&source=0"
API_GET_URL = 'http://hr.gets.com:8989/api/autoGetKeyword.php?type=download'
# 51job简历下载


class NotDownloadError(Exception):
    def __init__(self, _error_info_):
        super().__init__(self)  # 初始化父类
        self.error_info = _error_info_

    def __str__(self):
        return self.error_info


class Job51(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
        self.search_url = 'https://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx'
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
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9221")
        # self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=self.options)

    @staticmethod
    def get_api_cookie(cook):
        cookie = []
        for key in cook:
            dic = dict()
            dic['domain'] = 'N/A'
            dic['path'] = 'N/A'
            dic['name'] = key
            dic['value'] = cook[key]
            cookie.append(dic)

        return cookie

    def do_cookies(self, cooki):
        for cook in cooki:  # 这里是cookies的信息
            if len(cook) < 6:
                new = dict(cook, **{
                    "domain": "N/A",
                    "path": "N/A",
                })
            else:
                new = cook
            self.driver.add_cookie(new)

    def get_first_page(self):
        # self.driver.get(self.goal_url)  # 打开最基本页面注入cookies
        # self.driver.delete_all_cookies()
        #
        # try:
        #     if type(self.cookies) == dict:
        #         cooki = self.get_api_cookie(self.cookies)
        #         self.do_cookies(cooki)
        #     elif type(self.cookies) == list:
        #         self.do_cookies(self.cookies)
        #     time.sleep(5)
        #     self.driver.get(self.goal_url)  # 访问目标网站
        # except Exception as e:
        #     print('error:', e)
        #     receivers = '朱建坤'
        #     msg = '需要登录刷新cookies'
        #     send_rtx_msg(receivers, msg)
        #     WebDriverWait(
        #         self.driver,
        #         86400, poll_frequency=15).until(
        #         EC.presence_of_element_located((
        #             By.XPATH, '//div[@class="Common_ct clearfix"]/ul/li[1]/a')))
        #
        # self.driver.refresh()
        # time.sleep(2)
        #
        # try:
        #     # 判断是否登录成功还是在登录页面
        #     # 1.寻找元素在不在 >>> 2.1.不在的话异常，然后异常里面进行阻塞,处理了后接着运行 2.2.存在表明登录成功
        #     WebDriverWait(self.driver, 5).until(
        #         EC.presence_of_element_located((By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
        #     )
        # except Exception as e:
        #     LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
        #     LOG.warning('*=*=*=** i need help to fresh the cookie **=*=*=*')
        #     LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
        #     # receivers = '朱建坤'
        #     # msg = '前程无忧自动追踪程序:广州时时美电子商务有限公司:24小时内重新登录来继续抓取信息'
        #     # send_rtx_msg(receivers, msg)
        #     WebDriverWait(self.driver, 86400, poll_frequency=30).until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
        #     )
        # except KeyboardInterrupt:
        #     LOG.warning('》》》》》》Program interrupt, need to fix《《《《《《')
        #
        # time.sleep(3)

        # coo = self.driver.get_cookies()
        # cook = list()
        # for i in coo:
        #     if 'expiry' in i:
        #         del i['expiry']
        #     cook.append(i)
        # self.save_cookies(cook)
        #
        # LOG.info('local cookies file has been refreshed')
        # =========================================================================================== #

        # self.temp_save_cart()   # 处理暂存夹消息
        self.do_search()          # search goal resume
        # self.do_quit()          # 避免下次登录还会出现ip问题
        # self.driver.quit()

    # ----------------------------- #
    def do_search(self):
        self.driver.get(self.search_url)
        time.sleep(random.uniform(1, 2))

        try:
            self.driver.find_element_by_xpath('//a[@id="search_submit"]').click()   # search at another page
        except Exception as e:
            print('\033[1;45m 处理好错误状态后>点进搜索页面>再开始运行 \033[0m')
            input('>')
            self.do_search()   # 若长期如此状态，需要重启程序一次
        else:
            time.sleep(random.uniform(2, 3))
            self.do_input_key()

    # def input_keyword_and_search(self):
    #     keywords, k_v = self.get_api_pos()
    #     time.sleep(random.uniform(1, 2))
    #
    #     # circle to input keywords to search
    #     self.chose_place()
    #
    #     self.chose_date()
    #     for keyword in keywords:
    #         flag = self.input_content(keyword)
    #         if not flag:
    #             continue

    def do_input_key(self):
        while True:
            # cycle to detect api info
            # the id might not be
            api_get_url = API_GET_URL
            list_dict = requests.get(api_get_url)
            list_dict = json.loads(list_dict.text)
            if list_dict:
                # extract content to search and download deliver then send to api_post
                for ld in list_dict:
                    window = self.driver.window_handles
                    self.driver.switch_to.window(window[0])         # make sure that it was in search window
                    external_resume_id = ld['external_resume_id']   # this is keyword, i need to search deliver by this
                    if not external_resume_id.isdigit():
                        continue
                    resume_id = ld['resume_id']                   # i need to change this name to noneDlivery_resume_id
                    download_user = ld['download_user']           # who download
                    try:
                        input_box = self.driver.find_element_by_xpath('//input[@id="ctrlSerach_search_keyword_txt"]')
                    except Exception as e:
                        print('\033[1;45m 处理好错误状态后>二级搜索页面>再开始运行 \033[0m')
                        input('>')
                        continue

                    input_box.clear()
                    input_box.send_keys(external_resume_id)
                    time.sleep(1)
                    search = self.driver.find_element_by_xpath(
                        '//a[@id="ctrlSerach_search_submit"]')
                    self.driver.execute_script("arguments[0].click();", search)

                    try:
                        WebDriverWait(
                            self.driver,
                            3, poll_frequency=0.5).until(
                            EC.presence_of_element_located((
                                By.XPATH, '//div[@class="Common_panel_body"]//p')))
                        txt = self.driver.find_element_by_xpath('//*[@id="tip_msgbox"]/div/div/p')
                        if "不开放公开搜索" not in txt.text:
                            raise Exception
                    except Exception:
                        flag = self.do_get_only_one(external_resume_id, resume_id, download_user)
                        if flag == 'continue':
                            continue
                        elif flag == 'pass':
                            pass
                    else:
                        self.driver.find_element_by_xpath('//*[@id="tip_msgbox"]/div/div/span').click()
                        time.sleep(2)
                        # self.driver.close()
                        continue

                for _ in range(40):
                    if _ % 2 == 0:
                        x = '>'
                    else:
                        x = '='
                    print(f'\rThe Program is sleeping :{x}', end='', flush=True)
                    time.sleep(1)
                # this account has been done all the demand then wait the the invalid key searched by another account
            else:
                # sleep random time and then requests again
                quarter_hour = time.localtime(time.time()).tm_min
                if quarter_hour in [0, 15, 30, 45]:
                    # each quarter_hour to refresh this site to keep session alive
                    print('every half an hour, make fresh')
                    self.driver.refresh()
                    for _ in range(60):
                        if _ % 2 == 0:
                            x = '>'
                        else:
                            x = '='
                        print(f'\rafter fresh page then wait 60s: status:{x}', end='', flush=True)
                        time.sleep(1)
                else:
                    for _ in range(15):
                        if _ % 2 == 0:
                            x = '>'
                        else:
                            x = '='
                        print(f'\rThe Program is waiting :{x}', end='', flush=True)
                        time.sleep(1)

    def do_get_only_one(self, ex_id, resume_id, download_user):
        """
        try to search this unique resume and download it
        :return:
        """
        # at first, you need to judge is_loaded
        time.sleep(1)
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//td[@class="Common_list_table-id-text"][1]/span/a'))
            )
        except Exception as e:
            # print(e)
            return 'continue'
        else:
            try:
                num_t = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
                num = re.findall(r'共(\d*)条', num_t)[0]
                # if not none, it prove that get sure info
                if num.isdigit():
                    if int(num) == 0:
                        raise ValueError(
                            "\nValueError: this account can't find the key resume, switch another account")
                    pass
                else:
                    raise Exception
            except ValueError:
                return 'continue'
            except Exception as e:
                # print('the exception is:', e)
                print('the progress not found the only one you want')   # although it might not be appeared
                return 'continue'
            else:
                self.driver.find_element_by_xpath('//td[@class="Common_list_table-id-text"][1]/span/a').click()
                time.sleep(2)
                # switch window
                window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                # switch to the last window to get i wanna get
                # get_now_url = self.driver.current_url
                # before click download, judge it whether downloaded
                flag = self.driver.title
                # if '私密' or '关闭' in flag:
                #     self.driver.close()
                #     return 'continue'

                if flag:
                    try:
                        try:
                            num = self.driver.find_element_by_xpath('//*[@id="divResume"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]').text
                        except Exception as e:
                            num = self.driver.find_element_by_xpath('//*[@id="divResume"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td[2]').text

                        if num.isdigit():
                            print('download resume needs to post')
                            self.get_xml_info(ex_id, resume_id, download_user)
                            time.sleep(2)
                        else:
                            raise NotDownloadError('if not down')
                    except NotDownloadError:
                        down_key = self.driver.find_element_by_xpath('//a[@id="UndownloadLink"]')
                        self.driver.execute_script("arguments[0].click();", down_key)
                        time.sleep(1)
                        self.driver.find_element_by_xpath('//*[@id="tip_msgbox"]/div/div/span').click()
                        # self.driver.find_element_by_xpath('//*[@id="tip_msgbox"]/div/div/a').click()   # unsure
                        time.sleep(2)
                        self.driver.refresh()
                        self.get_xml_info(ex_id, resume_id, download_user)

                    self.driver.close()

                time.sleep(2)
                return 'pass'

    # def chose_date(self):
    #     time.sleep(0.5)
    #     # chose_one = self.driver.find_element_by_xpath('//ul[@id="other_search_term_ch"]/li[8]/div/a')
    #     chose_one = self.driver.find_element_by_xpath('//a[@id="search_rsmupdate_a_2"]')
    #     self.driver.execute_script("arguments[0].click();", chose_one)
    #
    # def chose_place(self):
    #     time.sleep(0.5)
    #     chose_place = self.driver.find_element_by_xpath('//input[@id="ctrlSerach_search_expjobarea_input"]')
    #     self.driver.execute_script("arguments[0].click();", chose_place)
    #
    #     time.sleep(random.uniform(0, 1))
    #     _chose_GZ = self.driver.find_element_by_xpath('//*[@id="rsm_parentarea_div"]/div[2]/ul/li[3]/p/a')
    #     # //*[@id="rsm_parentarea_div"]/div[2]/ul/li[3]/p/a
    #     self.driver.execute_script("arguments[0].click();", _chose_GZ)
    #
    #     time.sleep(random.uniform(0, 1))
    #     # sure_ = self.driver.find_element_by_xpath('//a[@id="aconfirm"]')
    #     # self.driver.execute_script("arguments[0].click();", sure_)

    def input_content(self, keyword):
        box = self.driver.find_element_by_xpath('//input[@id="ctrlSerach_search_keyword_txt"]')
        box.clear()
        box.send_keys(keyword)
        time.sleep(random.uniform(1, 2))
        flag = self.do_click_search()
        if not flag:
            return False

    def do_click_search(self):
        search_click = self.driver.find_element_by_xpath('//a[@id="ctrlSerach_search_submit"]')
        self.driver.execute_script("arguments[0].click();", search_click)
        time.sleep(random.uniform(1, 2))
        num_info = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
        num = re.findall(r'共(\d*)\+?条', num_info)[0]
        if num == '0':
            return False
        else:
            # all_id = self.driver.find_elements_by_xpath('//div[@class="Common_list-table"]/table/tbody/tr')  # 40
            a_id = self.driver.find_element_by_xpath('//div[@class="Common_list-table"]/table/tbody/tr')  # 40

            a_id.click()
            time.sleep(random.uniform(0, 1))
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            flag = self.judge_secret()
            if flag:
                return True
            # n = 1
            # for i in range(len(all_id)):
            #     # print('i:', i + 1)           # 0 >>>
            #     n = i + 1
            #     if n % 2 == 0:
            #         n += 1
            #         continue
            #     else:
            #         # window = self.driver.window_handles
            #         # self.driver.switch_to.window(self.driver.window_handles[0])
            #         time.sleep(1)
            #         self.driver.find_element_by_xpath(
            #             f'//div[@class="Common_list-table"]/table/tbody/tr[{n}]/td[2]/span/a').click()
            #         # self.driver.execute_script("arguments[0].click();", each_id)
            #         # n += 1
            #         time.sleep(random.uniform(0, 1))
            #         window = self.driver.window_handles
            #         self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            #
            #         flag = self.judge_secret()
            #         if not flag:
            #             continue

    def do_search_page_go_next_page(self):
        try:
            next_button = self.driver.find_element_by_xpath('//a[@id="pagerBottomNew_nextButton"]')
        except Exception as e:
            # print(e)
            print('没有下一页了,要么退出,要么去搜其他的了')
        else:
            self.driver.execute_script("arguments[0].click();", next_button)

    @staticmethod
    def get_api_pos():
        p = requests.get('http://hr.gets.com:8989/api/autoGetKeyword.php').text
        time.sleep(0.5)
        data = json.loads(p)
        keywords = []
        k_v = {}
        for key in data:
            kw = key.get('keywords')
            user = key.get('add_user')
            receiver = key.get('receiver')
            if receiver is None:
                receiver = '0000'

            keywords.append(kw)
            k_v[kw] = (receiver, user)
        return keywords, k_v

    def judge_secret(self):
        # 判断 是否是保密简历
        time.sleep(0.5)
        title = self.driver.title
        if "ID" not in title:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return None
        else:
            return True
        # window = self.driver.window_handles
        # self.driver.switch_to.window(self.driver.window_handles[0])

    def get_xml_info(self, ex_id, resume_id=None, download_user=None):
        time.sleep(random.uniform(2, 3))
        html = self.driver.page_source
        xpt = etree.HTML(html)
        ne = self.driver.find_element_by_xpath('//td[@id="tdseekname"]').text.strip()
        name = re.findall(r'(\S*)', ne)[0]
        # mobile_phone = xpt.xpath(
        #     '//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/text()')[
        #     0].strip()
        mobile_phone = self.driver.find_element_by_xpath('//*[@id="divResume"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]').text
        company_dpt = 1
        resume_key = ''
        # brief_detail = xpt.xpath('//table[@class="infr"]/tbody/tr[3]/td[1]/text()')[1:]   # middle
        all_detail = self.driver.find_elements_by_xpath('//table[@class="infr"]/tbody/tr[3]/td[1]')
        brief_detail = ''.join([ifo.text for ifo in all_detail if ifo])
        gender = '1' if '男' in brief_detail else '2'
        date_of_birth = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日)', brief_detail)[0]
        c_residency = re.findall(r'现居住.*?(\D+)?\d', brief_detail, re.S)
        current_residency = c_residency[0].strip() if c_residency else \
        re.findall(r'现居住.*?(\D{2})', brief_detail, re.S)[
            0].strip()
        y_working = re.findall(r'(\d*?年)工作经验', brief_detail)
        years_of_working = y_working[0] if y_working else '无工作经验'
        hu_kou = re.findall(r'<tr><td.*?class="keys">户口/国籍：.*?class="txt2">(.*?)</td>', html)
        hukou = hu_kou[0] if hu_kou else ""
        current_salary = ''
        politics_status = ''
        m_status = re.findall('<tr><td.*?class="keys">婚姻状况：.*?class="txt2">(.*?)</td>', html)
        ma_status = m_status[0] if m_status else ''
        marital_status = '1' if ma_status == '已婚' else '2'
        address = current_residency
        zip_code = ''
        # email = xpt.xpath(
        #     '//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a/text()')[
        #     0].strip()
        email = self.driver.find_element_by_xpath('//*[@id="divResume"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a')
        email = email.text if email else ''
        home_telephone = ''
        work_phone = ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = re.findall('<tr><td.*?class="keys">自我评价：.*?class="txt1">(.*?)</td>', html)
        i_can_start = ''
        e_type = re.findall('<tr><td.*?class="keys">工作类型：.*?class="txt2">(.*?)</td>', html)[0]
        employment_type = '1' if '全' in e_type else '2'
        industry_expected = re.findall('<tr><td.*?class="keys">行业：.*?class="txt2"><span class="tag">(.*?)</span>',
                                       html)
        industry_expected = industry_expected if industry_expected else ''  # 可能为空
        w_expected = re.findall('<tr><td.*?class="keys">地点：.*?class="txt2"><span class="tag">(.*?)</span>', html)
        working_place_expected = w_expected[0] if w_expected else ''
        s_expected = re.findall('<tr><td.*?class="keys">期望薪资：.*?class="txt2">(.*?)</td>', html)
        salary_expected = s_expected[0] if s_expected else ''
        job_d = re.findall(
            '<tbody><tr><td valign="top" class="keys">职能/职位：</td><td valign="top" class="txt2"><span class="tag">(.*?)</span>',
            html)
        job_f_d = ''.join(job_d) if job_d else ''
        jo_ed = re.findall(r'(\w*?)', job_f_d) if job_f_d else ''
        job_function_expected = ''.join(jo_ed) if jo_ed else ''
        c_situation = xpt.xpath('//table[@class="infr"]/tbody/tr[2]/td[1]//text()')
        current_situation = c_situation[0].strip() if c_situation else ''
        t_info = self.driver.find_elements_by_xpath('//tr[@id="divInfo"]/td/table/tbody/tr[1]/td')
        table_info = [t_i.text.strip() for t_i in t_info if t_i]
        t_str = re.findall('目前年收入', html)
        table_str = True if t_str else False
        # 个人信息 求职意向 工作经验 项目经验 教育经历 在校情况
        try:
            table_num = table_info.index('工作经验')
            if not table_str:
                table_num += 1
        except Exception as e:
            # print(e)
            word_experience = []
        else:
            try:
                tr_info = self.driver.find_elements_by_xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr')
                word_experience = []
                tr_num = len(tr_info)
                for i in range(tr_num):
                    time_info = self.driver.find_element_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="time"]').text
                    comp_name = self.driver.find_element_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//span[@class="bold"]').text
                    do_what = self.driver.find_element_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="rtbox plate_right"]/span[@class="bold"]').text
                    work_description = ''
                    work_details = self.driver.find_elements_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="tb1"]//tbody/tr/td[2]')
                    for ifo in work_details:
                        work_description += (ifo.text + '\n')
                    dic = {
                        '时间:': time_info,
                        '相关:': comp_name,
                        '内容:': do_what,
                        '描述:': work_description
                    }

                    word_experience.append(dic)
            except Exception as e:
                # print(e)
                word_experience = []

        try:
            table_num2 = table_info.index('项目经验')
            if not table_str:
                table_num2 += 1
        except Exception as e:
            # print(e)
            project_experience = []
        else:
            tr2_info = xpt.xpath(f'//tr[@id="divInfo"]/td/table[{table_num2 + 1}]/tbody/tr[2]/td/table/tbody/tr')
            project_experience = []
            tr2_num = len(tr2_info)
            for i in range(tr2_num):
                time_info = xpt.xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num2 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')
                pro_name = xpt.xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num2 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')
                project_details = xpt.xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num2 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="txt1"]/text()')

                dic = {
                    '时间:': time_info,
                    '名称:': pro_name,
                    '描述:': project_details
                }

                project_experience.append(dic)

        try:
            table_num3 = table_info.index('教育经历')
            if not table_str:
                table_num3 += 1
        except Exception as e:
            # print(e)
            education = []
        else:
            try:
                tr3_info = xpt.xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr')
                education = []
                tr3_num = len(tr3_info)
                for i in range(tr3_num):
                    time_info = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')[
                        0]
                    school_name = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')[
                        0]
                    class_rate = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]//text()')[
                        0]
                    main_major = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]/span/text()')[
                        1]
                    dic = {
                        '时间:': time_info,
                        '名称:': school_name,
                        '等级:': class_rate,
                        '专业:': main_major
                    }
                    education.append(dic)

            except Exception as e:
                # print(e)
                education = []

        honors_awards = ''
        practical_experience = ''
        training = ''
        language = ''
        it_skill = ''
        certifications = []
        try:
            table_num4 = table_info.index('技能特长')
            if not table_str:
                table_num4 += 1
        except Exception as e:
            # print(e)
            certifications = []
        else:
            try:
                tr4_info = xpt.xpath(
                    f'//tr[@id="divInfo"]/td/table[{table_num4 + 1}]/tbody/tr[2]/td/table/tbody/tr')
                education = []
                tr4_num = len(tr4_info)
                for i in range(tr4_num):
                    time_info = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num4 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')[
                        0]
                    certifications_name = xpt.xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num4 + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')[
                        0]
                    dic = {
                        '时间:': time_info,
                        '名称:': certifications_name,
                    }

                    certifications.append(dic)
            except Exception as e:
                # print(e)
                education = []

            # print("certifications:", education)
        # //tr[@id="divInfo"]/td/table[6]/tbody/tr[2]/td/table/tbody/tr[2]//tbody/tr[4]//td[@class="time"]/text()
        otherinfo = ''  #
        source_file = ''  #
        is_viewed = 1  #
        r_date = xpt.xpath('//span[@id="lblResumeUpdateTime"]/b/text()')
        resume_date = r_date[0] if r_date else ''
        get_type = 2
        # e_id = self.driver.find_element_by_xpath(
        #     '//*[@id="divResume"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td[1]/span').text
        external_resume_id = ex_id

        dic = {
            'resume_from': 1,
            'name': name,
            'mobile_phone': mobile_phone,
            'company_dpt': company_dpt,
            'resume_key': resume_key,
            'gender': gender,
            'date_of_birth': date_of_birth,
            'current_residency': current_residency,
            'years_of_working': years_of_working,
            'hukou': hukou,
            'current_salary': current_salary,
            'politics_status': politics_status,
            'marital_status': marital_status,
            'address': address,
            'zip_code': zip_code,
            'email': email,
            'home_telephone': home_telephone,
            'work_phone': work_phone,
            'personal_home_page': personal_home_page,
            'excecutiveneed': excecutiveneed,
            'self_assessment': self_assessment,
            'i_can_start': i_can_start,
            'employment_type': employment_type,
            'industry_expected': industry_expected,
            'working_place_expected': working_place_expected,
            'salary_expected': salary_expected,
            'job_function_expected': job_function_expected,
            'current_situation': current_situation,
            'word_experience': word_experience,
            'project_experience': project_experience,
            'education': education,
            'honors_awards': honors_awards,
            'practical_experience': practical_experience,
            'training': training,
            'language': language,
            'otherinfo': otherinfo,
            'source_file': source_file,
            'it_skill': it_skill,
            'certifications': certifications,
            'is_viewed': is_viewed,
            'resume_date': resume_date,
            'get_type': get_type,
            'external_resume_id': external_resume_id
        }

        load_json = {
            'noneDlivery_resume_id': resume_id,
            'add_user': download_user,
            "data": [dic]
        }

        # print('load_json:', load_json)
        self.post_resume(load_json)

    def get_brief(self, no):
        word_experience = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[1]//text()')  # ...
        education = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[2]//text()')  # ...
        return word_experience, education

    def post_resume(self, resume):
        resume2 = json.dumps(resume)
        print('resume:', resume2)
        url = 'http://hr.gets.com:8989/api/autoOwnerResumeDownload.php??'
        rq = self.session.post(url, json=resume)
        LOG.info(f'数据的插入详情为:{rq.text}')

    @staticmethod
    def handle_0(n):
        if len(n) == 1:
            num = f'0{n}'
        else:
            num = n
        return num

    def do_quit(self):
        self.driver.get(self.cart_url)
        time.sleep(random.uniform(1, 2))
        quit_button = self.driver.find_element_by_xpath('//a[@id="MainMenuNew1_hl_LogOut"]')
        self.driver.execute_script("arguments[0].click();", quit_button)

    # ---------------------------- #

    def save_cookies(self, cook):
        dic = {
            'fresh_time': time.ctime(time.time()),
            'cookies': cook
        }
        jsn = json.dumps(dic)
        with open(self.base_dir + r'\cookies.json', 'w') as f:
            f.write(jsn)
        time.sleep(1)

    def run(self):
        self.get_first_page()


def send_rtx_msg(receivers, msg):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    Job51().session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    # app = Job51()
    # app.run()
    while True:
        try:
            print('\033[1;45m 在此输入任意字符后程序再开始运行 \033[0m')
            input('>>>')
            app = Job51()
            app.run()
        except Exception as e:
            print('continue')
            receiver = '聂清娜'
            msg = '前程需要重新登陆,登陆好了之后记得在终端等待页面输入任意字符'
            send_rtx_msg(receiver, msg)
            continue
