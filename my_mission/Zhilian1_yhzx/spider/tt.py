# -*- coding: gb18030 -*-
import json


def analysis_data(dic=None):
    # with open('resume.json', 'r', encoding='gb18030') as f:
    #     dic = f.read()
    #     dic = json.loads(jnf)

    dataList = dic['data']['dataList']
    goal = {
        'data': []
    }
    for data in dataList:
        dst = []
        lsj = []
        desiredCitys = data['desiredCitys']
        lj = data['lastJobDetail']
        for desire in desiredCitys:
            desire_city = desire['cityName']           # 期望工作城市
            dst.append(desire_city)

        each_lj = {
            "beginData": lj["beginDate"],
            "companyName": lj["companyName"],
            "jobName": lj["jobName"],
            "description": lj["description"]
        }
        lsj.append(each_lj)

        each_info = {
            "number": data['number'],                   # 就是那个唯一的 ID
            "name": data['userName'],                   # 姓名
            "createTime": data['createTime'],           # 刷新时间
            "gender": data['gender'],                   # 性别
            "age": data['age'],                         # 年龄
            "workYears": data['workYears'],             # 工作年限
            "eduLevel": data['eduLevel'],               # 学历信息
            "city": data['city'],                       # 现居住地
            "school": data['school'],                   # 学校（多个的字符串）
            "phone": data['phone'],                     # 手机号信息
            "email": data['email'],                     # 邮箱信息
            "self_assessment": data['selfEvaluation'],  # 自我评价（不是要求的，但是留着）
            "desirecity": dst,                          # 期望的城市
            "lastJobDetail": lsj                        # 上个工作信息
        }

        goal['data'].append(each_info)

    # ll = json.dumps(goal)
    goal = str(goal)
    with open('resume_first.txt', 'w', encoding='utf-8') as file:
        file.write(goal)


if __name__ == '__main__':
    analysis_data()
