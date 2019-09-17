import datetime
import json
import re
import random
import requests
from lxml import etree
from spider.logger import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# test cookie
cookie = "guid=e81bba60a47ccb706a6a99ab93918824; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; search=jobarea%7E%60030200%7C%21ord_field%7E%600%7C%21recentSearch0%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAamazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565682815%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch1%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%D1%C7%C2%ED%D1%B7%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565312878%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch2%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA030202%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAAmazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565251247%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch3%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAAmazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565251214%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21collapse_expansion%7E%601%7C%21; EhireGuid=e82df8d95f004368aca6757974f4ed5c; LangType=Lang=&Flag=1; _ujz=MTU3NTgxNzc3MA%3D%3D; 51job=cenglish%3D0%26%7C%26; ASP.NET_SessionId=fzxcyvrpghaive204cztqqeq; AccessKey=cc9b06f40cee4a0; RememberLoginInfo=member_name=7A4B1B5BF1669EE7E4DDD8913FED4ECD&user_name=86404CFDD31E2394; HRUSERINFO=CtmID=2725554&DBID=4&MType=02&HRUID=5975204&UserAUTHORITY=1100111010&IsCtmLevle=1&UserName=yhzx153&IsStandard=0&LoginTime=08%2f20%2f2019+16%3a52%3a41&ExpireTime=08%2f20%2f2019+17%3a20%3a45&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=0&CtmLiscense=6&mb=&AccessKey=200b1b61370330ce&source=0"


class Job51(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
        self.base_url = 'https://ehire.51job.com/MainLogin.aspx'
        self.goal_url = 'https://ehire.51job.com/Navigate.aspx'
        self.cart_url = 'https://ehire.51job.com/Candidate/CompanyHrTmpNew.aspx'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))  # E:\Project\Job51_bak\spider

        # path = 'chromedriver.exe'
        # self.driver = webdriver.Chrome(executable_path=path)
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        # self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9221")
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
        self.driver.get(self.goal_url)  # 打开最基本页面注入cookies
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

        try:
            # 判断是否登录成功还是在登录页面
            # 1.寻找元素在不在 >>> 2.1.不在的话异常，然后异常里面进行阻塞,处理了后接着运行 2.2.存在表明登录成功
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
            )
        except Exception as e:
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            LOG.warning('*=*=*=** i need help to fresh the cookie **=*=*=*')
            LOG.warning('*=*=*=*==*=*=*=*=*=*=*=*=*=*==*=*=*=*=*=*=*=*=*=*')
            # receivers = '朱建坤'
            # msg = '前程无忧自动追踪程序:广州时时美电子商务有限公司:24小时内重新登录来继续抓取信息'
            # send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》Program interrupt, need to fix《《《《《《')

        time.sleep(3)
        #
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
        self.msg_bubble()       # 处理小气泡的消息
        self.do_downloaded_resume()
        # self.do_quit()          # 避免下次登录还会出现ip问题
        # self.driver.quit()

    def do_downloaded_resume(self):
        self.driver.get("https://ehire.51job.com/InboxResume/CompanyHRDefault2.aspx?Page=2&belong=3&Folder=BAK")
        time.sleep(random.uniform(1, 2))
        all_nums = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
        sure_num = re.findall(r"(\d+)", all_nums)[0]
        page = int(sure_num) // 20
        for i in range(page):
            od = i + 1
            try:
                name = self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{od}"]/td[3]/ul/li[1]/a')
            except:
                break
            if name:
                name.click()
                window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                self.get_xml_info()
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(random.uniform(1, 2))

    def msg_bubble(self):
        try:
            WebDriverWait(self.driver, 20, poll_frequency=2).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//a[@id="MainMenuNew1_HrChat"]/span'))
            )
        except Exception as e:
            print(e)
        else:
            num = self.driver.find_element_by_xpath('//*[@id="chatUnReadNum"]').text
            if not num:
                return None
            button = self.driver.find_element_by_xpath('//a[@id="MainMenuNew1_HrChat"]/span')
            # self.driver.execute_script("arguments[0].click();", button)
            button.click()
            time.sleep(1)
            window = self.driver.window_handles
            self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
            # //div[@class="wc-scroll-box"]/ul/li
            # //div[@class="wc-body wc-scroll-view wc-no-scroll"]/div[1]/ul/li
            flag = self.do_judge_have_msg()
            if flag:
                msg = self.view_brief_detail()
                msg_handled = '\n----------------\n'.join(msg)
                receivers = '聂清娜'
                send_rtx_msg(receivers, msg_handled)
                self.driver.close()
                # window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[0])
            else:
                print('nothing here')

    def view_brief_detail(self):
        """
        如果存在消息的话就处理了这里的消息，只回复最表面的消息
        :return:
        """
        main_nodes = self.driver.find_elements_by_xpath('//div[@class="wc-scroll-box"]/ul/li')
        msg = []
        for node in main_nodes:
            wc_name = node.find_element_by_xpath('.//p[1]/span[1]').text
            wc_time = node.find_element_by_xpath('.//p[1]/span[2]').text
            wc_text = node.find_element_by_xpath('.//p[2]/span[1]').text
            unread = node.find_element_by_xpath('.//p[2]/span[2]').text
            wc_read = unread if unread else '0'

            data = f"消息时间: {wc_time}\n姓名: {wc_name}\n内容: {wc_text}\n几条未读: {wc_read}\n"
            msg.append(data)
        return msg

    def do_judge_have_msg(self):
        """
        判断是否有消息
        :return:
        """
        try:
            WebDriverWait(self.driver, 5, poll_frequency=1).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@class="wc-body wc-scroll-view wc-no-scroll"]/div[1]/ul/li'))
            )
        except Exception as e:
            return None
        else:
            return True

    def do_quit(self):
        self.driver.get(self.cart_url)
        time.sleep(random.uniform(1, 2))
        quit_button = self.driver.find_element_by_xpath('//a[@id="MainMenuNew1_hl_LogOut"]')
        self.driver.execute_script("arguments[0].click();", quit_button)

    # ----------------------------- #

    def temp_save_cart(self):
        # 下面是去暂存夹
        self.driver.get(self.cart_url)
        time.sleep(8)

        whole_temp_save = self.driver.find_element_by_xpath('//div[@class="fn-main list-main"]/div/ul[2]/li[1]').text
        # 以下是 共2条 的测试情况
        num = re.findall('(\d+)', whole_temp_save)
        if not num or num[0] == '0':
            receivers = '朱建坤'
            msg = '前程无忧暂存夹里面没有需要处理的数据'
            send_rtx_msg(receivers, msg)
        else:
            num = num[0]     # 2    4丅
            main_node = self.driver.find_element_by_xpath('//div[@class="list-table"]//tbody')
            for i in range(1, int(num) + 1):
                td = main_node.find_element_by_xpath(f'./tr[{i * 2 - 1 }]/td[2]/span/a').text  # id
                base_td_show = main_node.find_element_by_xpath(f'//div[@class="list-table"]//tbody/tr[{i * 2 - 1 }]/td[3]/span')  # click to detail
                self.driver.execute_script("arguments[0].click();", base_td_show)
                # resume_key
                resume_key = td
                # gender
                gender = '1' if self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{i}"]/td[6]').text == '男' else '2'
                # address
                address = self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{i}"]/td[7]').text
                # years_of_working
                years_of_working = self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{i}"]/td[5]').text
                # current_residency
                current_residency = address
                time.sleep(4)
                word_experience, education = self.get_brief(td)
                time.sleep(4)
                # base_td = main_node.find_element_by_xpath(f'./tr[{i * 2}]/td[2]/span/a')
                self.driver.execute_script("arguments[0].click();", td)
                time.sleep(5)
                if not self.judge_secret():
                    receivers = '朱建坤'
                    msg = f'简历收藏夹里面的 ID为:{td}的简历详信息被隐藏,只能查看简略信息'
                    send_rtx_msg(receivers, msg)
                    continue
                else:
                    time.sleep(1)
                    window = self.driver.window_handles
                    self.driver.switch_to_window(self.driver.window_handles[len(window) - 1])
                    self.judge_secret()

    def judge_secret(self):
        # 判断 是否是保密简历
        title = self.driver.title
        if "ID" not in title:
            return None
        self.get_xml_info()

    def get_xml_info(self):
        time.sleep(random.uniform(2, 3))
        title = self.driver.title
        html = self.driver.page_source
        xpt = etree.HTML(html)
        ne = self.driver.find_element_by_xpath('//td[@id="tdseekname"]').text.strip()
        name = re.findall(r'(\S*)', ne)[0]
        mobile_phone = xpt.xpath(
            '//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/text()')[0].strip()
        company_dpt = 1
        resume_key = ''
        # brief_detail = xpt.xpath('//table[@class="infr"]/tbody/tr[3]/td[1]/text()')[1:]   # middle
        all_detail = self.driver.find_elements_by_xpath('//table[@class="infr"]/tbody/tr[3]/td[1]')
        brief_detail = ''.join([ifo.text for ifo in all_detail if ifo])
        gender = '1' if '男' in brief_detail else '2'
        date_of_birth = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日)', brief_detail)[0]
        c_residency = re.findall(r'现居住.*?(\D+)?\d', brief_detail, re.S)
        current_residency = c_residency[0].strip() if c_residency else re.findall(r'现居住.*?(\D{2})', brief_detail, re.S)[
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
        email = xpt.xpath('//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a/text()')[0].strip()
        home_telephone = ''
        work_phone = ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = re.findall('<tr><td.*?class="keys">自我评价：.*?class="txt1">(.*?)</td>', html)
        i_can_start = ''
        e_type = re.findall('<tr><td.*?class="keys">工作类型：.*?class="txt2">(.*?)</td>', html)[0]
        employment_type = '1' if '全' in e_type else '2'
        industry_expected = re.findall('<tr><td.*?class="keys">行业：.*?class="txt2"><span class="tag">(.*?)</span>', html)
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
        # 个人信息 求职意向 工作经验 项目经验 教育经历 在校情况
        try:
            table_num = table_info.index('工作经验')
            if "目前年收入" not in table_info:
                table_num += 1
        except Exception as e:
            # print(e)
            word_experience = []
        else:
            try:
                tr_info = self.driver.find_elements_by_xpath(f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr')
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
        except Exception as e:
            # print(e)
            education = []
        else:
            try:
                tr3_info = xpt.xpath(f'//tr[@id="divInfo"]/td/table[{table_num3 + 1}]/tbody/tr[2]/td/table/tbody/tr')
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
        except Exception as e:
            # print(e)
            certifications = []
        else:
            try:
                tr4_info = xpt.xpath(f'//tr[@id="divInfo"]/td/table[{table_num4 + 1}]/tbody/tr[2]/td/table/tbody/tr')
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
        e_id = self.driver.find_element_by_xpath('//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[1]/span').text
        external_resume_id = re.findall(r'(\d+)', e_id)[0]

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
            'noneDlivery_resume_id': "0",
            'add_user': "000",
            "data": [dic]
        }

        print("load_json:", load_json)
        self.post_resume(load_json)

    def do_all(self, all_parameters):
        pass

    def get_brief(self, no):
        word_experience = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[1]//text()')  # ...
        education = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[2]//text()')  # ...
        return word_experience, education

    def post_resume(self, resume):
        url = 'http://hr.gets.com:8989/api/autoOwnerResumeDownload.php?'
        rq = self.session.post(url, json=resume)
        LOG.info(f'数据的插入详情为:{rq.text}')

    @staticmethod
    def handle_0(n):
        if len(n) == 1:
            num = f'0{n}'
        else:
            num = n
        return num

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
    app = Job51()
    app.run()
