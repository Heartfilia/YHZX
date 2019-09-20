#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 9:53
# @Author  : Lodge

# 配置文件都在这里了，大概需要修改的地方也就下面这几个
chrome_port = 8055                # 程序调用本地chrome浏览器的端口
TOKEN = 'aPtSB5CuFcNWxd0'         # 不知道是什么,一个关键字
receivers = '朱建坤'               # 会收到信息的人
handler = '系统机器人'              # 交给谁处理这些信息
account = '广州外宝电子商务有限公司'   # 公司的名称
POST_URL = 'http://newhr.gets.com/api/autoOwnerResume.php?'  # 简历信息上传的位置,放这里是因为这里可能会改到测试机
cookies = 'toUrl=/; JSESSIONID=""; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1568689138; t=7GfwWgU6fhVNAOKs; wt=7GfwWgU6fhVNAOKs; __c=1568689608; __f=7737fd431c267b6cf1a5506b3372e5e5; _bl_uid=36k400h0nvt9vhaazg14iIgrCm0F; __l=r=https%3A%2F%2Fwww.zhipin.com%2Fuser%2Flogin.html&l=%2Fwww.zhipin.com%2Fchat%2Fim&friend_source=0&friend_source=0; __a=25258175.1568689137.1568689137.1568689608.21.2.20.21; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1568716744'

# 下面的内容基本是不用动的,除了增加容错处理的地方
chat_msg = '你好,请交换电话和简历信息,若条件符合,人事会工作日24小时内联系你[自动回复]'                  # 程序会主动发送的信息
send_time_tec = '技术人员为双休,上下班时间为9:00-18:30,周六加班双倍工资,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系你[自动回复]'
send_time_oth = '行政文员销售为大小周,如有意愿,上下班时间为9:00-18:30,如有意愿,可以交换电话简历信息,人事会工作日24小时内联系你[自动回复]'
go_chat = '你好,如果有意愿的话,可以交换电话和简历信息,若条件符合人事会在工作日24小时内联系你[自动回复]'
no_repeat = ['抱歉', '太远', '不好意思', '不考虑', '已经入职', '距离太远', '不来',
             '不符', '不太适合', '对不起', '但是', '没有离职', '未离职', '达不到',
             '太低', '不用了', '不适合', '不合适', '不满足', '不足']  # 程序判断对方不来的关键词
cookie = cookies    # 可以直接修改cookie不用重启程序的原因(会重导 reload)
SIMPLE_CHAT = [('上下班时间', '上班时间', '工作时间', '大小周', '时间情况', '几点'),
               ('好的', '可以', '没有问题', '没问题', '恩', '嗯'),
               ('什么状态', '什么情况', '简历投递了')]
