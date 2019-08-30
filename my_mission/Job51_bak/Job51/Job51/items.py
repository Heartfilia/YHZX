# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Job51Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()                              # 姓名
    mobile_phone = scrapy.Field()                      # 手机号码
    company_dpt = scrapy.Field()                       # 应聘的职位
    resume_key = scrapy.Field()   # ‘’                 # 不用管
    gender = scrapy.Field()       # 男1 女2             # 性别
    date_of_birth = scrapy.Field()                     # 生日
    current_residency = scrapy.Field()                 # 现居住地
    years_of_working = scrapy.Field()                  # 工作年限
    hukou = scrapy.Field()                             # 户籍
    current_salary = scrapy.Field()                    # 目前薪资
    politics_status = scrapy.Field()                   # 社会背景
    marital_status = scrapy.Field()  # 已婚1   未婚2     # 婚姻状况
    address = scrapy.Field()                           # 住址
    zip_code = scrapy.Field()                          # 邮编
    email = scrapy.Field()                             # 邮箱
    home_telephone = scrapy.Field()                    # 家庭电话
    work_phone = scrapy.Field()                        # 公司电话
    personal_home_page = scrapy.Field()                # 个人主页
    excecutiveneed = scrapy.Field()                    # 高级人才附加信息
    self_assessment = scrapy.Field()                   # 自我介绍
    i_can_start = scrapy.Field()                       # 不管
    employment_type = scrapy.Field()   # 全职1 兼职2    # 工作性质
    industry_expected = scrapy.Field()                 # 期望行业    【】
    working_place_expected = scrapy.Field()            # 期望工作地点
    salary_expected = scrapy.Field()                   # 期望薪资
    job_function_expected = scrapy.Field()             # 不用管
    current_situation = scrapy.Field()                 # 当前状况 可不管
    word_experience = scrapy.Field()                   # 工作经验  【】
    project_experience = scrapy.Field()                # 项目经验  【】
    education = scrapy.Field()                         # 教育信息  【】
    honors_awards = scrapy.Field()                     # 获得奖项  可不管
    practical_experience = scrapy.Field()              # 时间经验  可不管
    training = scrapy.Field()                          # 培训信息
    language = scrapy.Field()                          # 语言技能
    it_skill = scrapy.Field()                          # it技能
    certifications = scrapy.Field()                    # 证书     【】
    is_viewed = scrapy.Field()                         # 不管   1
    resume_date = scrapy.Field()                       # 简历日期
    get_type = scrapy.Field()                          # 不管   1
    external_resume_id = scrapy.Field()                # 唯一id(不知道前程有吗)
    # resume_from = 2/智联
