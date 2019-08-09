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
            desire_city = desire['cityName']           # ������������
            dst.append(desire_city)

        each_lj = {
            "beginData": lj["beginDate"],
            "companyName": lj["companyName"],
            "jobName": lj["jobName"],
            "description": lj["description"]
        }
        lsj.append(each_lj)

        each_info = {
            "number": data['number'],                   # �����Ǹ�Ψһ�� ID
            "name": data['userName'],                   # ����
            "createTime": data['createTime'],           # ˢ��ʱ��
            "gender": data['gender'],                   # �Ա�
            "age": data['age'],                         # ����
            "workYears": data['workYears'],             # ��������
            "eduLevel": data['eduLevel'],               # ѧ����Ϣ
            "city": data['city'],                       # �־�ס��
            "school": data['school'],                   # ѧУ��������ַ�����
            "phone": data['phone'],                     # �ֻ�����Ϣ
            "email": data['email'],                     # ������Ϣ
            "self_assessment": data['selfEvaluation'],  # �������ۣ�����Ҫ��ģ��������ţ�
            "desirecity": dst,                          # �����ĳ���
            "lastJobDetail": lsj                        # �ϸ�������Ϣ
        }

        goal['data'].append(each_info)

    # ll = json.dumps(goal)
    goal = str(goal)
    with open('resume_first.txt', 'w', encoding='utf-8') as file:
        file.write(goal)


if __name__ == '__main__':
    analysis_data()
