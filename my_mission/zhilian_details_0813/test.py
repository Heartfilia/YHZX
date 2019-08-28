# -*- coding: utf-8 -*-
import json

from requests import Session
session = Session()


jn = {'account': 'account', 'data': [{'resume_from': 2, 'name': '陈俊付', 'mobile_phone': '0', 'company_dpt': 1, 'resume_key': 'php', 'gender': '1', 'date_of_birth': '19951201', 'current_residency': '', 'years_of_working': 3, 'hukou': '广东 广州', 'current_salary': '6001~8000', 'politics_status': '6', 'marital_status': '2', 'address': '', 'zip_code': '', 'email': '', 'home_telephone': '', 'work_phone': '', 'personal_home_page': '', 'excecutiveneed': '', 'self_assessment': '1.有着2年的前端和后端的综合开发经验\r\n2.热爱思考，热爱分享，性格沉稳。\r\n3.本人积极乐观，有较强的团队合作意识，可应对工作压力，对工作有激情。\r\n4.有良好的php基础，熟悉mvc模式，能够熟练使用thinkphp框架', 'i_can_start': '', 'employment_type': '1', 'industry_expected': '计算机软件', 'working_place_expected': '广州', 'salary_expected': '8001~10000', 'job_function_expected': '', 'current_situation': '', 'word_experience': [{'公司名': '广州心流信息科技有限公司', '开始时间': '2018-03-01 00:00:00', '结束时间': '', '工作标题': 'php开发', '工作描述': '1.根据策划需求增加栏目显示所需活动数据。\n\n2.接入游戏平台的充值和登录', '薪资范围': '6001~8000'}], 'project_experience': [{'开始时间': '2018-03-01 00:00:00', '结束时间': '2019-02-01 00:00:00', '项目名字': '游戏管理后台', '责任描述': '1.sql优化，分表\n2.游戏平台的接入充值，登录', '项目描述': '1.游戏后台维护\n2.游戏平台接入'}, {'开始时间': '2017-09-01 00:00:00', '结束时间': '2018-03-01 00:00:00', '项目名字': '安全生产管理后台', '责任描述': '', '项目描述': '主要负责后台模块开发，有自检模块，数据统计模块，审核模块，用户上传图片模块\n'}, {'开始时间': '2017-07-01 00:00:00', '结束时间': '2017-10-01 00:00:00', '项目名字': '金融数据开放平台', '责任描述': '1.编写爬虫爬取目标网页上的数据\n2.按需求分析显示所需数据', '项目描述': '1.编写爬虫爬取目标网页上的数据\n2.按需求分析显示所需数据'}, {'开始时间': '2017-04-01 00:00:00', '结束时间': '2017-06-01 00:00:00', '项目名字': '广东省电子政务协会官网', '责任描述': '1.前端页面切图\n2.后台增删改查', '项目描述': '1.前端页面切图\n2.后台增删改查'}], 'education': [{'开始时间': '2014-09-01 08:00:00', '结束时间': '2017-06-01 08:00:00', '学校': '广州现代信息工程职业技术学院', '专业': '物联网应用技术'}], 'honors_awards': '', 'practical_experience': '', 'training': '', 'language': '', 'it_skill': '', 'certifications': [], 'is_viewed': 1, 'resume_date': '2019-08-05 12:09:37', 'get_type': 2, 'external_resume_id': 'b156gip87jjjjj4dJF8d2mA'}]}


def post_resume(resume):
    url = 'http://testhr.gets.com:8989/api/autoInsertResume.php?'
    rq = session.post(url, json=resume)
    print(f'数据的插入详情为:{rq.text}')


post_resume(jn)
