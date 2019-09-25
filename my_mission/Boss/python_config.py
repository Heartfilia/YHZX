#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 9:53
# @Author  : Lodge

# 配置文件都在这里了，大概需要修改的地方也就下面这几个
chrome_port = 8055                # 程序调用本地chrome浏览器的端口
TOKEN = 'aPtSB5CuFcNWxd0'         # 不知道是什么,一个关键字,headers中的参数
receivers = '朱建坤'               # 会收到信息的人
handler = '系统机器人'              # 交给谁处理这些信息
account = '广州洛洛服饰有限公司'      # 公司的名称
account_from = 'Ling'             # 账号的所有人
phone_num = 'l8578608256'         # 回馈信息里面发送的手机号和微信号
get_and_reply = f'好的，您的简历我已收到，若是简历通过筛选，我们将会在24小时内与您进一步沟通，如果您有不清晰的地方，也可以随时联系我：' \
                f'{account_from}:{phone_num}(微信同号）'

POST_URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
MSG_URL = ''
# cookies 的外面一定要用单引号，里面的内容有双引号
cookies = 'JSESSIONID=""; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1568854097; __c=1568856405; _bl_uid=d7k5k0dIqmF0gCljhiFbkhOdIan0; __l=r=https%3A%2F%2Fwww.zhipin.com%2Fuser%2Flogin.html&l=%2Fwww.zhipin.com%2Fchat%2Fim&friend_source=0&friend_source=0; lastCity=101280100; t=7GfwWgU6fhVNAOKs; wt=7GfwWgU6fhVNAOKs; __f=7737fd431c267b6cf1a5506b3372e5e5; __a=6073313.1568854100.1568854100.1568856405.78.2.77.78; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1569319398'

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


test_chat_info = """{'name': '吴楚鹏', 'phone': '1234567899', 'external_resume_id': '2eeeb975fe8b19ef33J_2dg~', 'data': [{'add_time': '2019-09-23 15:11:32', 'from_uid': 49660662, 'from_name': '陈女士', 'to_uid': 76652899, 'to_name': '刘展全', 'msg': '陈女士:我公司正在招贤纳士，可否邀您聊聊呢？'}, {'add_time': '2019-09-23 15:11:32', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': '点击修改去设置中修改打招呼语'}, {'add_time': '2019-09-23 15:16:00', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': '刘展全:[微笑]'}, {'add_time': '2019-09-23 15:16:24', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': '刘展全:对方想发送附件简历到您邮箱，您是否同意'}, {'add_time': '2019-09-24 15:09:39', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': 'jl.pdf'}, {'add_time': '2019-09-24 15:09:39', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': '对方已投递简历，您可至邮箱中查看和下载。未收到邮件？'}, {'add_time': '2019-09-24 16:30:57', 'from_uid': 49660662, 'from_name': '陈女士', 'to_uid': 76652899, 'to_name': '刘展全', 'msg': '陈女士:我们是广州市荔湾区逢源路128号，金升大厦803'}, {'add_time': '2019-09-24 16:30:59', 'from_uid': 49660662, 'from_name': '陈女士', 'to_uid': 76652899, 'to_name': '刘展全', 'msg': '陈女士:{"locationDesc":"广州市荔湾区政务服务中心(广州荔湾区广州市荔湾区政务服务中心8楼802房)","longitude":113.238928,"latitude":23.121233}'}, {'add_time': '2019-09-24 16:31:52', 'from_uid': 49660662, 'from_name': '陈女士', 'to_uid': 76652899, 'to_name': '刘展全', 'msg': '陈女士给你发送了面试邀请'}, {'add_time': '2019-09-24 16:48:47', 'from_uid': 76652899, 'from_name': '刘展全', 'to_uid': 49660662, 'to_name': '陈女士', 'msg': '刘展全:有点太远了！我想找天河区的，谢谢哈'}, {'add_time': '2019-09-24 17:32:59', 'from_uid': 49660662, 'from_name': '陈女士', 'to_uid': 76652899, 'to_name': '刘展全', 'msg': '陈女士:好的'}]}"""