import json
import re
import random
import requests
from lxml import etree

from spider.helper import python_config
from spider.logger import *
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


class Job51HalfYear(object):
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
        self.driver.get(self.search_url)  # 打开最基本页面注入cookies
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
        #     WebDriverWait(
        #         self.driver,
        #         86400, poll_frequency=15).until(
        #         EC.presence_of_element_located((
        #             By.XPATH, '//div[@class="Common_ct clearfix"]/ul/li[1]/a')))
        #
        # self.driver.refresh()
        # time.sleep(2)
        #
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
            # send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//ul/li/a[@id="MainMenuNew1_HrUName"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》Program interrupt, need to fix《《《《《《')

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
        # self.do_info()
        self.do_search()        # search goal resume
        # self.do_quit()          # 避免下次登录还会出现ip问题
        # self.driver.quit()

    # ----------------------------- #

    def do_info(self):
        self.driver.get("http://report.ehire.51job.com/report/jobdecrease/index.php")

    # ----------------------------- #
    def do_search(self):
        self.driver.get(self.search_url)
        time.sleep(random.uniform(1, 2))
        # self.driver.find_element_by_xpath('//a[@id="search_submit"]').click()   # search at another page
        # time.sleep(random.uniform(2, 3))
        self.do_click_each()

    def do_click_each(self):
        # //span[@id="labAllResumes"]      get num
        # search_click = self.driver.find_element_by_xpath('//a[@id="ctrlSerach_search_submit"]')
        # self.driver.execute_script("arguments[0].click();", search_click)
        # time.sleep(random.uniform(1, 2))
        num_info = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
        num = re.findall(r'共(\d*)\+?条', num_info)[0]
        pg = int(num) // 20   # 共有多少页
        if num == '0':
            return False
        else:
            for x in range(1, pg+1):
                all_id = self.driver.find_elements_by_xpath('//*[@id="form1"]/div[2]/div/div[4]/div[3]/table/tbody/tr')
                LOG.info(f'当前在第{x}页，页面数据有{len(all_id)//2}条,全部数据有{num}条')
                for i in range(len(all_id) // 2):
                    n = i + 1      # 20
                    # window = self.driver.window_handles
                    # self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(2)
                    try:
                        self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{n}"]/td[3]/ul/li[1]/a').click()
                    except Exception as e:
                        print('当前页面状态错误，请手动处理页面信息后回车')
                        input('>')
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                    # self.driver.execute_script("arguments[0].click();", each_id)
                    time.sleep(random.uniform(2, 3))
                    window = self.driver.window_handles
                    self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                    try:
                        flag = self.judge_secret()
                    except Exception as e:
                        print('当前页面信息检索错误，请回到“当前状态”所在页面后回车')
                        input('>')
                        continue
                    else:
                        if not flag:
                            continue
                time.sleep(random.uniform(2, 3))
                # self.do_next_pg()   # 去下一页
                break  # 下一页我就不去了

    def do_next_pg(self, pn=None):
        # self.driver.find_element_by_xpath(f'//a[@id="pagerBottomNew_btnNum{pn}"]').click()
        self.driver.find_element_by_xpath(f'//*[@id="pagerBottomNew_nextButton"]').click()

    def do_search_page_go_next_page(self):
        try:
            next_button = self.driver.find_element_by_xpath('//a[@id="pagerBottomNew_nextButton"]')
            info = self.driver.find_element_by_xpath('//a[@id="pagerBottomNew_btnNum2"]').get_attribute('class')
        except Exception as e:
            # print(e)
            print('没有下一页了,要么退出,要么去搜其他的了')
        else:
            if info == 'active':
                pass
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
                receiver = '系统机器人'

            keywords.append(kw)
            k_v[kw] = (receiver, user)
        # keywords = ['测试']
        # k_v = {'测试': '系统机器人'}
        return keywords, k_v

    def temp_save_cart(self):
        # 下面是去暂存夹
        self.driver.get(self.cart_url)
        time.sleep(8)

        whole_temp_save = self.driver.find_element_by_xpath('//div[@class="fn-main list-main"]/div/ul[2]/li[1]').text
        # 以下是 共2条 的测试情况
        num = re.findall(r'(\d+)', whole_temp_save)
        if not num or num[0] == '0':
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：前程{company_name}暂存夹里面没有需要处理的数据
"""
            send_rtx_msg(msg)
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
                time.sleep(1)
                word_experience, education = self.get_brief(td)
                time.sleep(1)
                # base_td = main_node.find_element_by_xpath(f'./tr[{i * 2}]/td[2]/span/a')
                self.driver.execute_script("arguments[0].click();", td)
                time.sleep(1)
                if not self.judge_secret():
                    continue
                else:
                    time.sleep(1)
                    window = self.driver.window_handles
                    self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                    self.judge_secret()

    def judge_secret(self):
        # 判断 是否是保密简历
        time.sleep(0.5)
        try:
            self.driver.find_element_by_xpath('//*[@id="tdseekname"]').text
        except:
             return None

        # try:
        #     self.get_xml_info()
        # except Exception as e:
        #     print(e)
        self.get_xml_info()
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        # window = self.driver.window_handles
        # self.driver.switch_to.window(self.driver.window_handles[0])

    def get_xml_info(self):
        time.sleep(random.uniform(2, 3))
        html = self.driver.page_source
        xpt = etree.HTML(html)
        ne = self.driver.find_element_by_xpath('//td[@id="tdseekname"]').text.strip()
        name = re.findall(r'(\S+)和Ta', ne)[0]
        mobile_phone = xpt.xpath(
            '//*[@id="divResume"]/table[1]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[4]/text()')[
            0].strip()
        company_dpt = 1
        r_key = self.driver.find_element_by_xpath('//div[@id="headwrap"]/../span').text
        re_key = re.findall(r'class="keys">关键字：</td><td.*?"txt1"><span.*?tag">(.*?)</span>', html)
        resume_key = re_key[0] if re_key else ''
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
        c_salary = re.findall(r'目前年收入：.*?class="f16">(\d+ 万元).*?</span>', html, re.S)
        current_salary = c_salary[0] if c_salary else ''
        p_status = re.findall('class="keys">政治面貌：</td><td valign="top" class="txt2">(.*?)</td></tr>', html)
        politics_status = p_status[0] if p_status else ''
        m_status = re.findall('<tr><td.*?class="keys">婚姻状况：.*?class="txt2">(.*?)</td>', html)
        ma_status = m_status[0] if m_status else ''
        marital_status = '1' if ma_status == '已婚' else '2'
        address = current_residency
        zip_code = ''
        try:
            email = xpt.xpath(
                '//div[@class="rv_mail_limit"]/a/text()')[0].strip()
        except:
            email = ''
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
        t_str = re.findall('目前年收入', html)
        table_str = True if t_str else False
        # 个人信息 (当前年收入) 求职意向 工作经验 项目经验 教育经历 在校情况
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
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]/td/table/tbody/tr[1]/td[@class="time"]').text
                    comp_name = self.driver.find_element_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//span[@class="bold"]').text
                    do_what = self.driver.find_element_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="rtbox plate_right"]/span[@class="bold"]').text
                    work_description = ''
                    work_details = self.driver.find_elements_by_xpath(
                        f'//tr[@id="divInfo"]/td/table[{table_num + 1}]/tbody/tr[2]/td/table/tbody/tr[{i + 1}]//td[@class="tb1"]//tbody/tr/td[2]')
                    for ifo in work_details:
                        work_description += (ifo.text + '\n')
                    if do_what:
                        dic = {
                            '时间:': time_info,
                            '相关:': comp_name,
                            '内容:': do_what,
                            '描述:': work_description
                        }
                    else:
                        dic = {
                            '时间:': time_info,
                            '相关:': comp_name,
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
            if not table_str:
                table_num4 += 1
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
        time_now = time.time()
        dateModified = time.strftime('%Y-%m-%d', time.localtime(time_now))
        resume_date = dateModified
        get_type = 2
        external_resume_id = re.findall(r'(\d+)', r_key)[0]

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
            'external_resume_id': external_resume_id,
            'resume_logo': '',
        }

        load_json = {
            'account': f'{company_name}',
            "data": [dic]
        }

        # print('load_json:', load_json)
        self.post_resume(load_json)

    def get_brief(self, no):
        word_experience = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[1]//text()')  # ...
        education = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[2]//text()')  # ...
        return word_experience, education

    def post_resume(self, resume):
        url = POST_URL
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


def send_rtx_msg(msg):
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
    Job51HalfYear().session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    print('\033[1;45m 在此输入任意字符后程序再开始运行 \033[0m')
    input('>>>')
    while True:
        time_info = time.strftime('%a', time.localtime())
        if time_info in ['Sun']:
            sure_time = time.strftime('%H:%M', time.localtime())
            if sure_time in ['09:30']:
                app = Job51HalfYear()
                app.run()

        for _ in range(60):
            print(f"\r{random.choice('><|/I1X')}", end='')
            time.sleep(1)
