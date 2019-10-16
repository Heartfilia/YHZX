# import datetime
import json
import re
import random
# from threading import Thread
# from functools import wraps

import requests
from lxml import etree

from spider.helper import python_config
from spider.logger import *
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

API_GET_URL = python_config.API_GET_URL
POST_URL = python_config.POST_URL
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


class Job51Down(object):
    def __init__(self):
        self.down_url = 'https://ehire.51job.com/InboxResume/CompanyHRDefault2.aspx?Page=2'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))  # E:\Project\Job51_bak\spider
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument('--disable-gpu')
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
        self.driver = webdriver.Chrome(options=self.options)

    def get_first_page(self):
        self.driver.get(self.down_url)
        time.sleep(random.uniform(1, 2))
        self.do_click_search()

    def do_click_search(self):
        today_tic = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
        time.sleep(random.uniform(0, 1))
        chose_btn = self.driver.find_element_by_xpath('//*[@id="form1"]/div[4]/div/div[4]/div[2]/ul[2]/li[4]/select')
        chose_btn.click()
        # self.driver.execute_script("arguments[0].click();", chose_btn)
        time.sleep(1)
        chose_50 = self.driver.find_element_by_xpath(
            '//*[@id="form1"]/div[4]/div/div[4]/div[2]/ul[2]/li[4]/select/option[3]')
        chose_50.click()
        # today_tic = '2019-09-30'
        # self.driver.execute_script("arguments[0].click();", chose_50)
        time.sleep(3)
        # input('手动大法好>>')
        try:
            tic_all = self.driver.find_elements_by_xpath(f'//tr/td[text()="{today_tic}"]')
        except Exception as e:
            tic_num = 0
        else:
            tic_num = len(tic_all)

        if tic_num == 0:
            return False
        else:
            for i in range(1, tic_num + 1):
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(1)
                try:
                    a_id = self.driver.find_element_by_xpath(f'//*[@id="trBaseInfo_{i}"]/td[3]/ul/li[1]/a')
                except Exception as e:
                    continue
                else:
                    a_id.click()
                time.sleep(random.uniform(2, 3))
                window = self.driver.window_handles
                self.driver.switch_to.window(self.driver.window_handles[len(window) - 1])

                current_url = self.driver.current_url
                e_id = re.findall(r'hidSeqID=(\d+)&?', current_url)
                if e_id:
                    e_id = e_id[0]
                else:
                    continue

                self.get_xml_info(e_id)
                self.driver.close()

    def get_xml_info(self, ex_id):
        time.sleep(random.uniform(2, 3))
        html = self.driver.page_source
        xpt = etree.HTML(html)
        ne = self.driver.find_element_by_xpath('//td[@id="tdseekname"]').text.strip()
        name = re.findall(r'(\S*)', ne)[0]
        mobile_phone = self.driver.find_element_by_xpath(
            '//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]'
        ).text.strip()
        company_dpt = 1
        resume_key = ''
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
        try:
            email = self.driver.find_element_by_xpath('//*[@id="divResume"]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[2]/tbody/tr/td/table[1]/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr/td[2]/a')
        except Exception as e:
            email = ''
        else:
            email = email.text
        home_telephone = ''
        work_phone = ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = re.findall('<tr><td.*?class="keys">自我评价：.*?class="txt1">(.*?)</td>', html)
        self_assessment = self_assessment[0] if self_assessment else ''
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
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr')
                word_experience = []
                tr_num = len(tr_info)
                for i in range(tr_num):
                    time_info = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="time"]').text
                    comp_name = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//span[@class="bold"]').text
                    do_what = self.driver.find_element_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox plate_right"]/span[@class="bold"]').text
                    work_description = ''
                    work_details = self.driver.find_elements_by_xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="工作经验"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="tb1"]//tbody/tr/td[2]')
                    for ifo in work_details:
                        work_description += (ifo.text + '\n')
                    dic = {
                        '起止时间': time_info,
                        '公司信息': comp_name,
                        '工作内容': do_what,
                        '描述': work_description
                    }

                    word_experience.append(dic)
            except Exception as e:
                word_experience = []

        try:
            table_num2 = table_info.index('项目经验')
            if not table_str:
                table_num2 += 1
        except Exception as e:
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
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr')
                education = []
                tr3_num = len(tr3_info)
                for i in range(tr3_num):
                    time_info = xpt.xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="time"]/text()')[0]
                    school_name = xpt.xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="rtbox"]//text()')[
                        0]
                    class_rate = xpt.xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]//text()')[
                        0]
                    main_major = xpt.xpath(
                        f'//*[@id="divInfo"]//tbody/tr/td[text()="教育经历"]/../../tr/td/table/tbody/tr[{i + 1}]//td[@class="phd tb1"]/span/text()')[
                        1]
                    dic = {
                        '教育时间': time_info,
                        '学校名称': school_name,
                        '专业等级': class_rate,
                        '主研专业': main_major
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
                    f'//*[@id="divInfo"]//tbody/tr/td[text()="技能特长"]/../../tr/td/table/tbody/tr')
                education = []
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
                        '证书名称': certifications_name,
                    }

                    certifications.append(dic)
            except Exception as e:
                # print(e)
                education = []

        otherinfo = ''  #
        source_file = ''  #
        is_viewed = 1  #
        r_date = xpt.xpath('//span[@id="lblResumeUpdateTime"]/b/text()')
        resume_date = time.strftime("%Y-%m-%d", time.localtime())
        update_date = r_date[0] if r_date else ''
        get_type = 2
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
            'external_resume_id': external_resume_id,
            # 'account_from': python_config.
            'update_date': update_date
        }

        load_json = {
            'add_user': python_config.account_main,
            'account': python_config.download_user,
            "data": [dic]
        }

        self.post_resume(load_json)

    def post_resume(self, resume):
        resume2 = json.dumps(resume)
        print('resume:', resume2)
        url = POST_URL
        rq = self.session.post(url, json=resume)
        LOG.info(f'数据的插入详情为:{rq.text}')

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
    else:
        receivers = python_config.receivers

    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    # requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    app = Job51Down()
    app.run()
    print('\033[1;45m 程序结束 \033[0m')
