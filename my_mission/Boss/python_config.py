#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 9:53
# @Author  : Lodge

# 配置文件都在这里了，大概需要修改的地方也就下面这几个
chrome_port = 55082               # 程序调用本地chrome浏览器的端口
TOKEN = 'oPZMpgYLwfy25nH'         # 不知道是什么,一个关键字,headers中的参数
receivers = '杨国玲'               # 会收到信息的人
handler = '系统机器人'              # 交给谁处理这些信息
account = '广州外宝电子商务有限公司'      # 公司的名称
account_from = 'Ling'             # 账号的所有人
phone_num = '185-78608256'         # 回馈信息里面发送的手机号和微信号
get_and_reply = f'好的，您的简历我已收到，若是简历通过筛选，我们将会在24小时内与您进一步沟通，如果您有不清晰的地方，也可以随时联系我：' \
                f'{account_from}:{phone_num}(微信同号）'

POST_URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
TEST_POST_URL = 'http://testhr.gets.com:8989/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
MSG_URL = 'http://hr.gets.com:8989/api/autoAceBossChatLog.php?'  # 聊天记录存放的接口
TEST_MSG_URL = 'http://newhr.gets.com/api/autoAceBossChatLog.php?'      # 聊天记录存放的接口
# cookies 的外面一定要用单引号，里面的内容有双引号
cookies = 'lastCity=101280100; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1570180253; _uab_collina=157018025340062181286503; __c=1570180254; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=&friend_source=0&friend_source=0; t=MP7lAPYD5hosMlah; wt=MP7lAPYD5hosMlah; __f=3f66fc09bb1c5f151bd878cb4c8e4247; _bl_uid=jakLv17Lb3qw46wU8z7gf932aXdz; __a=39722586.1570180254..1570180254.9.1.9.9; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1570182546'

# 下面的内容基本是不用动的,除了增加容错处理的地方
chat_msg = '亲亲，方便提供一份您的简历吗？有利于我们接下来的沟通。'                  # 程序会主动发送的信息
send_time_tec = '技术人员为双休,上下班时间为9:00-18:30,周六加班双倍工资,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系您。'
send_time_oth = '行政文员销售为大小周,上下班时间为9:00-18:30,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系您。'
go_chat = '亲亲，你好，方便提供一份您的简历吗？有利于我们接下来的沟通。'

no_repeat = ['抱歉', '太远', '不好意思', '不考虑', '已经入职', '距离太远', '不来', '暂时',
             '不符', '不太适合', '对不起', '但是', '没有离职', '未离职', '达不到', '只考虑',
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
