#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 9:53
# @Author  : Lodge

# 配置文件都在这里了，大概需要修改的地方也就下面这几个
chrome_port = 55083               # 程序调用本地chrome浏览器的端口
# chrome.exe --remote-debugging-port=55083 --user-data-dir="C:\selenium_boss_ssm\AutomationProfile"
TOKEN = 'aPtSB5CuFcNWxd0'         # 不知道是什么,一个关键字,headers中的参数
receivers = '邓琦'               # 会收到信息的人
handler = '系统机器人'              # 交给谁处理这些信息
account_from = '广州外宝电子商务有限公司'      # 公司的名称
# account = '广州外宝电子商务有限公司'      # 公司的名称
account = 'nicole'                # 账号的所有人
phone_num = '①③②一⑥⑧②④一⑨③⑦⑨'         # 回馈信息里面发送的手机号和微信号
get_and_reply = f'好的，您的简历我已收到，若是简历通过筛选，我们将会在24小时内与您进一步沟通，如果您有不清晰的地方，也可以随时联系我：' \
                f'{account}:{phone_num}(微信同号:如被和谐了就是交换的手机号）'

POST_URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
TEST_POST_URL = 'http://testhr.gets.com:8989/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
MSG_URL = 'http://hr.gets.com:8989/api/autoAceBossChatLog.php?'  # 聊天记录存放的接口
TEST_MSG_URL = 'http://testhr.gets.com:8989/api/autoAceBossChatLog.php?'      # 聊天记录存放的接口

POSITION_URL = 'http://hr.gets.com:8989/api/autoAceBossJobType.php?type=publishJob'  # 获取职位信息的接口
POSITION_URL_CLEAR = 'http://hr.gets.com:8989/api/autoAceBossJobType.php?'  # 消除职位信息的接口

# cookies 的外面一定要用单引号，里面的内容有双引号
cookies = 'lastCity=101280100; _uab_collina=157018024966049470984417; _bl_uid=1qk0d1znbXwwL4xF8s0jqhX2Rvew; JSESSIONID=""; __c=1571656255; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1570180250,1571656256; __l=l=%2Fwww.zhipin.com%2Fuser%2Flogin.html&r=&friend_source=0&friend_source=0; __f=f7ef51e555b3fb81db54715cf655d0b7; t=8Ge6jaT55hIQrZgs; wt=8Ge6jaT55hIQrZgs; __a=44799888.1570180250.1570180250.1571656255.397.2.277.397; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1572656653'

# 下面的内容基本是不用动的,除了增加容错处理的地方
chat_msg = '亲亲，您好，方便提供一份简历吗？\n因为目前我们采用了技术自动抓取方式，我们会利用我司的邮件系统发送邀约等信息，但是我们不能精准定位到您的邮箱，所以烦请您再手动发一次您的邮箱给我哦，还有记得也要点击发送简历哦，以便我们可以第一时间导入到我司HR系统，更有效率开展接下来的邀约工作。'                  # 程序会主动发送的信息
send_time_tec = '技术人员为双休,上下班时间为9:00-18:30,周六加班双倍工资,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系您。'
send_time_oth = '行政文员销售为大小周,上下班时间为9:00-18:30,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系您。'
go_chat = '亲亲，你好，方便提供一份您的简历吗？有利于我们接下来的沟通。'

no_repeat = ['抱歉', '太远', '不好意思', '不考虑', '已经入职', '距离太远', '不来', '暂时',
             '不符', '不太适合', '对不起', '没有离职', '未离职', '达不到', '只考虑',
             '太低', '不用了', '不适合', '不合适', '不满足', '不足', '有机会']  # 程序判断对方不来的关键词
cookie = cookies    # 可以直接修改cookie不用重启程序的原因(会重导 reload)
SIMPLE_CHAT = [('上下班时间', '上班时间', '工作时间', '大小周', '时间情况', '几点'),
               ('好的', '可以', '没有问题', '没问题', '恩', '嗯'),
               ('什么状态', '什么情况', '简历投递了')]


test_chat_info = ''

# time
time_all = []
for h in range(10, 21):
    for m in range(0, 59, 20):    # 经过测试 还是需要半个小时处理一次为最佳 30
        if m == 0:
            sure_t = f'{h}:00'
        else:
            sure_t = f'{h}:{m}'
        time_all.append(sure_t)
time_tic = ['01:10', '09:00', '09:20', '09:40'] + time_all


# import requests
# requests.get(POSITION_URL_CLEAR + '16')