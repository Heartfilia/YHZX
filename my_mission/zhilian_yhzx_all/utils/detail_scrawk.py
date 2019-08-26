import json
import time
import random
import requests
import datetime


class Detail(object):
    def __init__(self):
        self.session = requests.Session()
        self.detail_url = "https://rd5.zhaopin.com/api/rd/resume/detail?"

    @staticmethod
    def params_get(resume_no):
        t = int(time.time() * 1000)
        front = [
            '46ba3dcc4781446ab7b77f11468b6c36',
            '15f87159b7c440078fedea3be92d26e7',
            '97ea329932f04166b268e0cb0b2bfd61',
            'bf37a85ca31548808cc4f6222bf07783'
        ]
        max_len = len(front) - 1
        params = {
            '_': f'{t}',
            'resumeNo': f'{resume_no}_1_1',
            'x-zp-page-request-id': f'{front[random.randint(0, max_len)]}-{t- random.randint(50,1000)}-{random.randint(200000, 800000)}',
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
        }
        return params

    @staticmethod
    def headers_get(resume_no):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'text/plain',
            'Referer': f'https://rd5.zhaopin.com/resume/detail?resumeNo={resume_no}_1_1&openFrom=5',
            'Sec-Fetch-Mode': 'cors',
            "sec-fetch-site": "same-origin",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            "cookie": "x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5; sts_deviceid=16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d; urlfrom2=121126445; adfcid2=none; adfbid2=0; acw_tc=2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6; login_point=67827992; promoteGray=; diagnosis=0; LastCity=%E5%B9%BF%E5%B7%9E; LastCity%5Fid=763; dywez=95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html; __utmz=269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html; NTKF_T2D_CLIENTID=guest848ED7A8-2D6C-CB43-D002-4785D3149DAB; sou_experiment=psapi; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D; c=OYd5f54u-1565146352123-205a31b6147942073825198; _fmdata=RjVcPpTGcffpZk5l0yUErfjZkmBHOjkP6kSghdv6CtDZCGZsOU%2FpDWROFqcil8ZtN7Dj%2B8TdUuQHdk17CMivo0uhUPDkXO%2BWP45A2LG761M%3D; _xid=gfhUYYFKG3ST%2F1QH8tKqAHYh0%2FaBXgOv9PvNYIX3DV86QIuuKiO1uUlpUG%2BShxIUJBmMYroIFkBPaV7u7onPfw%3D%3D; x-zp-dfp=zlzhaopin-1564541208377-824fee2b5b7e3; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1564539142,1565159011; x-zp-device-id=767356337adeccab996d3c784380a003; JSloginnamecookie=onn20v%5Ft1lyuqqav%5Fgmhphzu6uby%40oauth%2Eweixin; JSShowname=""; JSpUserInfo=236a2d6b566a5c6459695b7550725d7340765a69596b526a5f6825693b654f651c71186a076b596a5a641e693675117254731d7613691e6b1b6a1568086903652d6514711b6a016b1b6a026412691c7553721073137613692b6b056a05681c6901651a655d71016a0c6b026a1264016907755e7220733c765769586b586a52685f69426542654a71406a5a6b2b6a1b641969477506720a731c765169386b3e6a596858694e65336527714b6a5e6b466a5f64486950755f725173487651692a6b266a596858694e65276532714b6a236b266a5b645a695c755d72547341765869536b5f6a5f683c6921654f6542714d6a3a6b226a5764586952752; uiioit=3d752c6452695d6a053555645d7550645e695b6a06355f6453752a642b69566a04355c641; zp-route-meta=uid=655193256,orgid=67827992; dywea=95841923.183147172171786560.1564539142.1565602976.1565657914.24; dywec=95841923; __utma=269921210.1113127844.1564539142.1565602976.1565657914.22; __utmc=269921210; __utmt=1; is-oversea-acount=0; at=bd190984fdba44e388fb723965dc71f5; rt=ebe692e9a70e4bd4bfe07597db596886; login-type=b; sts_sg=1; sts_evtseq=1; sts_sid=16c887beb33183-0a0a25481c30be-3c375f0d-2073600-16c887beb34625; sts_chnlsid=Unknown; zp_src_url=https%3A%2F%2Fpassport.zhaopin.com%2Forg%2Flogin%3Fbkurl%3Dhttps%253A%252F%252Frd5.zhaopin.com%252F; dyweb=95841923.2.10.1565657914; __utmb=269921210.2.10.1565657914"
        }
        return headers

    def response_get(self, resume_no):
        """
        响应
        :param resume_no: 简历的号码
        :return: 然后响应值
        """
        params = self.params_get(resume_no)
        headers = self.headers_get(resume_no)
        try:
            response = self.session.get(self.detail_url, params=params, headers=headers, verify=False)
        except:
            print('status_code: <404> NOT FOUND')
        else:
            print('status_code: <200> OK')
            return json.loads(response.text)

    def get_resume(self, no=None):
        """
        获取每个简历的id
        :return: 每个简历的id
        """
        if len(no) == 1:
            filename = f'0{no}'
        else:
            filename = no
        with open(f'info0812{filename}.json', 'r', encoding='utf-8') as f:
            resume = f.read()
        resume = json.loads(resume)
        lists = resume["data"]["dataList"]

        li = []
        for i in lists:
            d = i["id"]
            li.append(d)

        return li

    @staticmethod
    def deal_info(info):
        now_year = datetime.datetime.now().year
        resume = {
            'resume_from': 2,
        }
        data = info['data']
        detail = data['detail']          # dict
        jobResume = data['jobResume']    # dict
        candidate = data['candidate']    # dict
        job = data['job']                # dict
        account = job['orgName']

        name = detail['Name']
        mobile_phone = candidate['mobilePhone']
        company_dpt = job['jobTitle']
        resume_key = ''
        gender = detail['Gender']
        date_of_birth = candidate['birthYear'] + candidate['birthMonth'] + candidate['birthDay']
        current_residency = candidate['address']
        years_of_working = now_year - int(candidate['workYearsRangeId'][:4])
        hukou = detail['HuKouProvinceId'] + detail['HuKouCityId']   # 这里是ID信息 还没有转换为文字

        salary_num = detail['CurrentSalary']
        if salary_num:
            sn = str(salary_num)
            if len(sn) == 9:
                if sn[4] == 0:
                    current_salary = sn[:4] + '~' + sn[5:]
                else:
                    current_salary = sn[:4] + '~' + sn[4:]
            elif len(sn) == 10:
                current_salary = sn[:5] + '~' + sn[5:]
            else:
                current_salary = ''
        else:
            current_salary = ''

        politics_status = detail['PoliticsBackGround']           # 这里数数字代表
        marital_status = '1' if detail['MaritalStatus'] == '2' else '2'
        address = candidate['mobilePhone']
        zip_code = detail['PostalCode'] if detail['PostalCode'] else ''
        email = candidate['email'] if candidate['email'] else ''
        home_telephone = candidate['homePhone'] if candidate['homePhone'] else ''
        work_phone = candidate['workPhone'] if candidate['workPhone'] else ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = detail['CommentContent']
        i_can_start = ''
        employment_type = '1' if detail['DesiredEmploymentType'] == '2' else '2'
        industry_expected = detail['DesiredIndustry']                                 # 数字 未处理
        working_place_expected = '广州' if candidate['cityId'] == '763' else '其它'
        num_expected = detail['DesiredSalaryScope']
        time_now = int(jobResume['createdate'] / 1000)                 # 简历更新日期(时间戳 还未转换)
        dateModified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_now))
        # print('更新日期:', dateModified)
        if num_expected:
            sn = str(num_expected)
            if len(sn) == 9:
                if sn[4] == 0:
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
        info_experience = detail['WorkExperience']
        if info_experience:
            for ifo in info_experience:

                Sly = ifo['Salary']       # 0800110000
                if Sly[0] == '0':
                    if Sly[5] == '0':
                        Salary = Sly[1:5] + '~' + Sly[6:]
                    else:
                        Salary = Sly[1:5] + '~' + Sly[5:]
                else:
                    Salary = Sly[:5] + '~' + Sly[5:]

                dic = {
                    '公司名': ifo['CompanyName'],
                    '开始时间': ifo['DateStart'],
                    '结束时间': ifo['DateEnd'] if ifo['DateEnd'] else '',
                    '工作标题': ifo['JobTitle'],
                    '工作描述': ifo['WorkDescription'],
                    '薪资范围': Salary
                }
                word_experience.append(dic)

        project_experience = []
        pec = detail['ProjectExperience']
        if pec:
            for i in pec:
                dic = {
                    '开始时间': i['DateStart'],
                    '结束时间': i['DateEnd'],
                    '项目名字': i['ProjectName'],
                    '责任描述': i['ProjectResponsibility'],
                    '项目描述': i['ProjectDescription']
                }
                project_experience.append(dic)

        education = []
        edu = detail['EducationExperience']
        if edu:
            for i in edu:
                dic = {
                    '开始时间': i['DateStart'],
                    '结束时间': i['DateEnd'],
                    '学校': i['SchoolName'],
                    '专业': i['MajorName']
                }
                education.append(dic)

        honors_awards = ''
        practical_experience = ''
        training = detail['Training'] if detail['Training'] else ''
        language = str(detail['LanguageSkill']) if detail['LanguageSkill'] else ''
        it_skill = ''

        certifications = []
        cer = detail['AchieveCertificate']
        if cer:
            for i in cer:
                dic = {
                    '获得时间': i['AchieveDate'],
                    '证书名字': i['CertificateName']
                }
                certifications.append(dic)

        is_viewed = 1
        entry_date = dateModified
        get_type = 1
        external_resume_id = data['resumeNumber'][:-4]

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
        resume['industry_expected'] = industry_expected
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
        resume['entry_date'] = entry_date
        resume['get_type'] = get_type
        resume['external_resume_id'] = external_resume_id

        return resume, account

    def post_resume(self, jr, account):
        info = {
            'account': account,
            'data': [jr]
        }
        # with open('ttt.txt', 'w', encoding='utf-8') as f:
        #     f.write(str(info))

        url = 'http://testhr.gets.com:8989/api/autoOwnerResume.php?'
        rq = self.session.post(url, json=info)
        print('=' * 50)
        print(rq.text.encode('utf-8').decode('utf-8-sig'))

    def run(self):
        resume_lists = self.get_resume('1')
        print(resume_lists)
        # for i in resume_lists:
        #     time.sleep(random.randint(3, 5))
        #     info = self.response_get(i)
        #     json_resume, account = self.deal_info(info)
        #     self.post_resume(json_resume, account)


if __name__ == '__main__':
    app = Detail()
    app.run()
