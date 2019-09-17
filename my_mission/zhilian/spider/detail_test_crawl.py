import datetime
import json
import time
import random
import requests
# http://hr.gets.com:8989/api/autoGetKeyword.php?type=download

session = requests.Session()

from spider.cookies import cookie
detail_url = "https://rd5.zhaopin.com/api/rd/resume/detail?"


def params_get(resume_no):
    t = int(time.time() * 1000)
    params = {
        '_': f'{t}',
        'resumeNo': f'{resume_no}_1_1',
        'x-zp-page-request-id': f'fed644deeddb46fbb0b4c75ed1c8a1f5-{t- random.randint(50,1000)}-69103',
        'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
    }
    return params


def headers_get(resume_no):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/resume/detail?resumeNo={resume_no}_1_1&openFrom=5',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": cookie
    }
    return headers


def response_get(resume_no):
    params = params_get(resume_no)
    headers = headers_get(resume_no)
    response = session.get(detail_url, params=params, headers=headers, verify=False)

    return response.text


def get_resume():
    """
    获取每个简历的id
    :return: 每个简历的id
    """
    with open('/utilsinfo081201.json', 'r', encoding='utf-8') as f:
        resume = f.read()

    resume = json.loads(resume)

    lists = resume["data"]["dataList"]

    for i in lists:
        time.sleep(1)
        d = i["id"]
        return d


def deal_info():
    now_year = datetime.datetime.now().year
    resume = {
        'resume_from': 2,
    }
    job = '数据处理工程'  # dict
    # account = resume_id  # job['orgName']

    name = "陈六宝"
    mobile_phone = '1234568911'
    company_dpt = 1
    resume_key = ''
    gender = '1'
    date_of_birth = '1995-03-09'
    current_residency = '广州'
    years_of_working = '1'

    hukou = '广州'

    salary_num = '0500107000'
    if salary_num:
        sn = str(salary_num)
        if len(sn) == 9:
            if sn[4] == '0':
                current_salary = sn[:4] + '~' + sn[5:]
            else:
                current_salary = sn[:4] + '~' + sn[4:]
        elif len(sn) == 10:
            current_salary = sn[:5] + '~' + sn[5:]
        else:
            current_salary = ''
    else:
        current_salary = ''

    politics_status = ''
    marital_status = '2'
    address = '中国广州'
    zip_code = ''
    email = ''
    home_telephone = ''
    work_phone = ''
    personal_home_page = ''
    excecutiveneed = ''
    self_assessment = '为了理想需要努力'
    i_can_start = ''
    employment_type = '2'
    industry_expected = []  # 数字 未处理

    working_place_expected = '广州'
    num_expected = '8000'
    time_now = time.time()
    dateModified = time.strftime('%Y-%m-%d', time.localtime(time_now))
    # print('更新日期:', dateModified)
    if num_expected:
        sn = str(num_expected)
        if len(sn) == 9:
            if sn[4] == '0':
                salary_expected = sn[:4] + '~' + sn[5:]
            else:
                salary_expected = sn[:4] + '~' + sn[4:]
        elif len(sn) == 10:
            salary_expected = sn[:5] + '~' + sn[5:]
        else:
            salary_expected = '面议'
    else:
        salary_expected = '面议'

    job_function_expected = ''
    current_situation = ''

    word_experience = []

    project_experience = []

    education = []

    honors_awards = ''
    practical_experience = ''
    training = ''
    language = ''
    it_skill = ''

    certifications = []

    is_viewed = 1
    resume_date = dateModified
    get_type = 1
    external_resume_id = "y3TAn8FICBBln4dJF8d2mA"

    resume['name'] = name
    resume['mobile_phone'] = mobile_phone
    resume['company_dpt'] = company_dpt
    resume['resume_key'] = resume_key
    resume['gender'] = gender
    resume['date_of_birth'] = date_of_birth
    resume['current_residency'] = current_residency
    resume['years_of_working'] = years_of_working
    resume['hukou'] = hukou
    resume['current_salary'] = current_salary
    resume['politics_status'] = politics_status
    resume['marital_status'] = marital_status
    resume['address'] = address
    resume['zip_code'] = zip_code
    resume['email'] = email
    resume['home_telephone'] = home_telephone
    resume['work_phone'] = work_phone
    resume['personal_home_page'] = personal_home_page
    resume['excecutiveneed'] = excecutiveneed
    resume['self_assessment'] = self_assessment
    resume['i_can_start'] = i_can_start
    resume['employment_type'] = employment_type
    resume['industry_expected'] = industry_expected[0] if industry_expected else ''
    resume['working_place_expected'] = working_place_expected
    resume['salary_expected'] = salary_expected
    resume['job_function_expected'] = job_function_expected
    resume['current_situation'] = current_situation
    resume['word_experience'] = word_experience
    resume['project_experience'] = project_experience
    resume['education'] = education
    resume['honors_awards'] = honors_awards
    resume['practical_experience'] = practical_experience
    resume['training'] = training
    resume['language'] = language
    resume['it_skill'] = it_skill
    resume['certifications'] = certifications
    resume['is_viewed'] = is_viewed
    resume['resume_date'] = resume_date
    resume['get_type'] = get_type
    resume['external_resume_id'] = external_resume_id
    # resume['labeltype'] = jobResume['labeltype']  # 1 待处理 2 有意向 3 已发面试 4 不合适

    return resume


def post_resume(jr=None, resume_id='3621', download_user='2244'):
        info = {
            'noneDlivery_resume_id': resume_id,
            'add_user': download_user,
            'data': [jr]
        }
        # with open('ttt.txt', 'w', encoding='utf-8') as f:
        #     f.write(str(info))
        print('info:', info)
        # url = 'http://testhr.gets.com:8989/api/autoOwnerResumeDownload.php?'  # here is the post api
        url = 'http://hr.gets.com:8989/api/autoOwnerResumeDownload.php?'

        rq = session.post(url, json=info)
        print(rq.text)


def run():
    # resume = get_resume()
    # print(resume)
    deal = deal_info()
    post_resume(deal)
    # response_get(resume)


if __name__ == '__main__':
    run()


