# import datetime
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

from Job51.download_today import Job51Down

API_GET_URL = python_config.API_GET_URL
POST_URL = python_config.POST_URL
POST_URL_COST = python_config.POST_URL_COST
POST_Search_URL = python_config.POST_Search_URL
# 51job简历下载
receivers = python_config.receivers
handler = python_config.handler
company_name = python_config.company_name
chrome_port = python_config.chrome_port
account_main = python_config.account_main


class NotDownloadError(Exception):
    def __init__(self, _Error_Info_):
        super().__init__(self)  # 初始化父类
        self.errorinfo = _Error_Info_

    def __str__(self):
        return self.errorinfo


class Job51HalfYear(object):
    """
    主动投递信息
    """

    def __init__(self):
        self.search_url = 'https://ehire.51job.com/InboxResume/InboxRecentEngine.aspx'
        self.goal_url = 'https://ehire.51job.com/Navigate.aspx'
        self.cart_url = 'https://ehire.51job.com/Candidate/CompanyHrTmpNew.aspx'
        self.position_get = 'https://ehire.51job.com/Jobs/JobSearchPost.aspx'
        self.download_url = 'https://ehire.51job.com/InboxResume/TalentCandidateList.aspx?Page=2&Folder=BAK'
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

    def do_get_some_goal(self):
        # 名字   到期时间   职位数   置顶数   短信数   简历下载数   今日安排  明日安排  本月已经邀请
        hr_account = self.driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[1]/a/span[1]').text
        hr_expire = self.driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[1]/p').text[6:]
        hr_position_num = self.driver.find_element_by_xpath('//*[@id="jobSp"]').text
        hr_position_top = self.driver.find_element_by_xpath('//*[@id="topSp"]').text
        hr_message_num = self.driver.find_element_by_xpath('//*[@id="smsSp"]').text
        hr_download_num = self.driver.find_element_by_xpath('//*[@id="resumeSp"]').text
        hr_today = self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/div[1]/div/div[1]/a/span').text
        hr_tomorrow = self.driver.find_element_by_xpath(
            '//*[@id="content"]/div[2]/div[1]/div[1]/div/div[2]/a/span').text
        hr_this_month = self.driver.find_element_by_xpath(
            '//*[@id="content"]/div[2]/div[1]/div[1]/div/div[4]/a/span').text
        info = {
            'account': account_main,
            'data': {
                # 'hr_account': hr_account,
                # 'hr_expire': hr_expire,
                'applied_for_resume': hr_position_num,  #
                'remain_refresh_no': hr_position_top,  #
                # 'hr_message_num': hr_message_num,
                'remain_downloads': hr_download_num,  #
                # 'hr_today': hr_today,
                # 'hr_tomorrow': hr_tomorrow,
                # 'hr_this_month': hr_this_month,
                'recent_received_num': '',  ###
                'hr_put_position': '',  #
                'use_coin': 0,  #
                'expire_coin': 0,  #
                'hittotal': 0,
                'month_browse_no': 0,
                'posts_available_today': 0,
            }
        }
        return info

    def post_to_login(self, info):
        URL = POST_URL_COST
        rq = requests.post(URL, json=info)
        print('info:::::', info)
        print('每日数据插入:', rq.text)

    def get_out_put_position(self, info):
        self.driver.get(self.position_get)
        num_char = self.driver.find_element_by_xpath('//*[@id="labAllResumes"]').text
        num_pos = re.findall(r'共(\d+)条', num_char)[0]
        info['data']['publish_posts_no'] = num_pos

        self.post_to_login(info)

    def get_first_page(self):
        self.driver.get(self.goal_url)
        # page_source = self.driver.page_source
        info = self.do_get_some_goal()
        time.sleep(5)  # 等待处理基本页面的信息的上传  <<<
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
            LOG.warning('》》》》》》Program interrupt, need to fix《《《《《《')

        self.do_search(info)  # search goal resume

    def do_info(self):
        self.driver.get("http://report.ehire.51job.com/report/jobdecrease/index.php")

    def do_other_info(self, info):
        # 近一周投递数量
        recent_received = self.driver.find_element_by_xpath('//*[@id="labAllResumes"]').text
        recent_received_num = re.findall(r'共(\d+)条', recent_received)[0]
        info['data']['recent_received_num'] = recent_received_num
        time.sleep(5)  # 等待处理基本页面的信息的上传  <<<
        self.get_out_put_position(info)

    def do_search(self, info):

        self.driver.get(self.search_url)
        time.sleep(random.uniform(1, 2))
        self.do_other_info(info)
        time.sleep(5)

        # self.driver.find_element_by_xpath('//a[@id="search_submit"]').click()   # search at another page
        self.driver.get(self.search_url)
        time.sleep(random.uniform(2, 3))
        self.do_click_each()
        # print('干脆再加一页')
        # self.do_click_each()
        # print('干脆再加一页')
        # self.do_click_each()
        # print('干脆再加一页')
        # self.do_click_each()
        # print('干脆再加一页')
        # self.do_click_each()

    def do_click_each(self):
        self.driver.switch_to.window(self.driver.window_handles[0])
        num_info = self.driver.find_element_by_xpath('//span[@id="labAllResumes"]').text
        num = re.findall(r'共(\d*)\+?条', num_info)[0]
        pg = int(num) // 50  # 共有多少页
        time.sleep(2)
        # input('这里回车决定了你要爬第几页的内容,手动大法好>')
        if num == '0':
            return False
        else:
            for x in range(1, pg + 1):
                all_id = self.driver.find_elements_by_xpath('//*[@id="form1"]/div[2]/div/div[4]/div[3]/table/tbody/tr')
                LOG.info(f'当前在第{x}页，页面数据有{len(all_id) // 2}条,全部数据有{num}条')
                for i in range(50):
                    n = i + 1  # 20
                    # window = self.driver.window_handles
                    # self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(1)
                    try:
                        self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{n}"]/td[3]/ul/li[1]/a').click()
                    except Exception as e:
                        print('恶意投递，跳过继续处理...')
                        # self.driver.switch_to.window(self.driver.window_handles[1])
                        # self.driver.close()
                        # self.driver.switch_to.window(self.driver.window_handles[0])
                        continue
                    # self.driver.execute_script("arguments[0].click();", each_id)
                    time.sleep(random.uniform(3, 5))
                    window = self.driver.window_handles
                    self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                    try:
                        flag = self.judge_secret()
                    except Exception as e:
                        print('页面信息错误，直接跳过了错误信息')
                        continue
                    else:
                        if not flag:
                            continue
                time.sleep(random.uniform(3, 5))
                # self.do_next_pg()   # 去下一页
                break  # 下一页我就不去了

    def do_next_pg(self, pn=None):
        # self.driver.find_element_by_xpath(f'//a[@id="pagerBottomNew_btnNum{pn}"]').click()
        np = self.driver.find_element_by_xpath(f'//*[@id="pagerBottomNew_nextButton"]')
        # np.click()
        self.driver.execute_script("arguments[0].click();", np)

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
            num = num[0]  # 2    4丅
            main_node = self.driver.find_element_by_xpath('//div[@class="list-table"]//tbody')
            for i in range(1, int(num) + 1):
                td = main_node.find_element_by_xpath(f'./tr[{i * 2 - 1}]/td[2]/span/a').text  # id
                base_td_show = main_node.find_element_by_xpath(
                    f'//div[@class="list-table"]//tbody/tr[{i * 2 - 1}]/td[3]/span')  # click to detail
                self.driver.execute_script("arguments[0].click();", base_td_show)
                # resume_key
                resume_key = td
                # gender
                gender = '1' if self.driver.find_element_by_xpath(
                    f'//tr[@id="trBaseInfo_{i}"]/td[6]').text == '男' else '2'
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

    def judge_secret(self, flag=None):
        # 判断 是否是保密简历
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//*[@id="tdseekname"]').text
        except:
            return None
        else:
            try:
                self.get_xml_info(flag)
            except Exception as e:
                print('页面信息格式错误,已经跳过...')
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True
        # window = self.driver.window_handles
        # self.driver.switch_to.window(self.driver.window_handles[0])

    def get_xml_info(self, flag=None):
        # time.sleep(random.uniform(0, 1))
        for h in range(3):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=800 * h, b=800 * (h + 1)))
            time.sleep(1)
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
        self_assessment = self_assessment[0] if self_assessment else ''
        i_can_start = ''
        e_type = re.findall('<tr><td.*?class="keys">工作类型：.*?class="txt2">(.*?)</td>', html)[0]
        employment_type = '1' if '全' in e_type else '2'
        industry_expected = re.findall('<tr><td.*?class="keys">行业：.*?class="txt2"><span class="tag">(.*?)</span>', html)
        industry_expected = industry_expected[0] if industry_expected else ''  # 可能为空
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
        # print('程序已经到达了这里了...')
        try:
            aply_positon = self.driver.find_element_by_xpath('//*[@id="applyJob"]')
        except Exception as e:
            apply_positon = ''
        else:
            apply_positon = aply_positon.text

        try:
            table_num = table_info.index('工作经验')
            if not table_str:
                table_num += 1
        except Exception as e:
            word_experience = []
        else:
            try:
                tr_info = self.driver.find_elements_by_xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr')
                word_experience = []
                tr_num = len(tr_info)
                for i in range(tr_num):
                    time_info = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]/td/table/tbody/tr[1]/td[@class="time"]').text
                    comp_name = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//span[@class="bold"]').text
                    do_what = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox plate_right"]/span[@class="bold"]').text
                    work_description = ''
                    work_details = self.driver.find_elements_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="tb1"]//tbody/tr/td[2]')
                    for ifo in work_details:
                        work_description += (ifo.text + '\n')
                    if do_what:
                        dic = {
                            '起止时间': time_info,
                            '公司信息': comp_name,
                            '工作内容': do_what,
                            '描述': work_description
                        }
                    else:
                        dic = {
                            '起止时间': time_info,
                            '公司信息': comp_name,
                            '描述': work_description
                        }

                    word_experience.append(dic)
            except Exception as e:
                word_experience = []

        word_experience.insert(0, {'应聘职位': apply_positon})

        try:
            table_num2 = table_info.index('项目经验')
            if not table_str:
                table_num2 += 1
        except Exception as e:
            # print(e)
            project_experience = []
        else:
            tr2_info = xpt.xpath(f'//*[@id="divInfo"]//tbody/tr/td[text()="项目经验"]/../../tr/td/table/tbody/tr')
            project_experience = []
            tr2_num = len(tr2_info)
            for i in range(tr2_num):
                time_info = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="项目经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')
                pro_name = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="项目经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')
                project_details = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="项目经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="txt1"]/text()')

                dic = {
                    '项目时间': time_info[0],
                    '项目名称': ''.join(pro_name),
                    '描述': ''.join(project_details)
                }

                project_experience.append(dic)

        education = []
        try:
            tr3_info = self.driver.find_elements_by_xpath(f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr')
            tr3_num = len(tr3_info)
            for i in range(tr3_num):
                time_info = self.driver.find_element_by_xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="time"]').text
                school_name = self.driver.find_element_by_xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]').text
                class_rate = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]//text()')[0]
                main_major = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]//text()')[2]
                dic = {
                    '教育时间': time_info,
                    '学校名称': school_name,
                    '专业等级': class_rate,
                    '主研专业': main_major
                }
                education.append(dic)

        except Exception as e:
            # print(e)
            pass

        honors_awards = ''
        practical_experience = ''
        training = ''
        language = ''
        it_skill = ''
        certifications = []
        try:
            tr4_info = xpt.xpath(f'//*[@id="divInfo"]//tbody/tr/td[text()="技能特长"]/../../tr/td/table/tbody/tr')
            tr4_num = len(tr4_info)
            for i in range(tr4_num):
                time_info = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="技能特长"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')[
                    0]
                certifications_name = xpt.xpath(
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="技能特长"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')[
                    0]
                dic = {
                    '获得时间': time_info,
                    '名称': certifications_name,
                }

                certifications.append(dic)
        except Exception as e:
            # print(e)
            pass

            # print("certifications:", education)
        # //tr[@id="divInfo"]/td/table[6]/tbody/tr[2]/td/table/tbody/tr[2]//tbody/tr[4]//td[@class="time"]/text()
        otherinfo = ''  #
        source_file = ''  #
        is_viewed = 1  #
        # time_tic = time.time()
        # dateModified = time.strftime('%Y-%m-%d', time.localtime(time_tic))
        dateModified = self.driver.find_element_by_xpath('//*[@id="applyUpdateTime"]').text.strip()
        resume_date = time.strftime('%Y-%m-%d', time.localtime())
        update_date = dateModified

        get_type = 1
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
            'update_date': update_date
        }

        load_json = {
            'job_name': apply_positon,
            'account': f'{python_config.account_from}',
            'add_user': f'{python_config.account_from}',
            "data": [dic]
        }

        # print('load_json:', load_json)
        self.post_resume(load_json)

    def get_brief(self, no):
        word_experience = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[1]//text()')  # ...
        education = self.driver.find_element_by_xpath(f'//div[@id="divResult_{no}"]/dl[2]//text()')  # ...
        return word_experience, education

    def post_resume(self, resume):
        url = python_config.POST_URL_AUTO
        rq = self.session.post(url, json=resume)
        print(resume)
        LOG.info(f'数据的插入详情为:{rq.text}')

    @staticmethod
    def handle_0(n):
        if len(n) == 1:
            num = f'0{n}'
        else:
            num = n
        return num

    def do_quit(self):
        # self.driver.get(self.cart_url)
        # time.sleep(random.uniform(1, 2))
        LOG.info('每日例行推出界面启动...')
        quit_button = self.driver.find_element_by_xpath('//*[@id="MainMenuNew1_hl_LogOut"]')
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

    def all_download_get(self):
        time.sleep(random.uniform(2, 3))
        today_info = time.strftime('%Y-%m-%d', time.localtime())
        try:
            today_download = self.driver.find_elements_by_xpath(f'//tr/td[text()="{today_info}"]')
        except Exception as e:
            today_nums = 0
        else:
            today_nums = len(today_download)

        if today_nums == 0:
            return False
        else:
            for n in range(1, today_nums + 1):
                time.sleep(4)
                try:
                    self.driver.find_element_by_xpath(f'//tr[@id="trBaseInfo_{n}"]/td[3]/ul/li[1]/a').click()
                except Exception as e:
                    print('当前页面状态错误，请手动处理页面信息后回车')
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    continue
                time.sleep(random.uniform(3, 5))
                window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])
                try:
                    flag = self.judge_secret(True)
                except Exception as e:
                    print('自动跳过该页面的错误状态...')
                    continue
                else:
                    if not flag:
                        continue
            time.sleep(random.uniform(3, 5))
            if today_nums == 50:
                print('因为当前页的数据为20条，那么下一页可能也存在数据，尝试跳下一页检索')
                self.do_next_pg()
                self.all_download_get()

    def be_ready_login_next_time(self):
        password_box = self.driver.find_element_by_xpath('//*[@id="txtPasswordCN"]')
        password_box.clear()
        password_box.send_keys(python_config.PASSWORD)
        time.sleep(1)
        log_btn = self.driver.find_element_by_xpath('//*[@id="Login_btnLoginCN"]')
        self.driver.execute_script("arguments[0].click();", log_btn)
        time.sleep(10)

    def run(self):
        time.sleep(5)
        self.driver.get(self.download_url)
        self.all_download_get()
        # =================== #
        time.sleep(10)
        self.get_first_page()
        time.sleep(5)
        self.do_quit()
        time.sleep(2)
        self.be_ready_login_next_time()


def send_rtx_msg(msg, flag=None):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    if flag:
        receivers = handler
    else:
        receivers = python_config.receivers

    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    app = Job51Down()
    app.run()
    print('下载数据已经下载完毕...')
    app = Job51HalfYear()
    # app.do_click_each()
    # input('>>>>>')
    app.run()
    # app.do_search(None)
