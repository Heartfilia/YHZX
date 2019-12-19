import datetime
import json
import random
import sys

import requests
from mytools.tools import post

# url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressGetOneValidAddress'
# url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet'
# url = url='http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountPost'
# data = json.dumps({'data':None})
# resp = requests.post(url,data)
# print(resp.status_code)
# print(resp.text)
# if resp.status_code == 200:
#     print(resp.text)
#     print(type(resp.text))

# 线上获取需要注册的用户信息
# url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet&country_code=US&validate_email=3985652123@qq.com&dynamic_ip=99.33.36.25'
# url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet&validate_email=3985652123@qq.com&dynamic_ip=99.33.36.25'
# resp = requests.get(url)
# print(resp.text)
# print(resp.status_code)
# print(resp.json())


#=========================================================
#线上获取有效地址信息
# url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetOneValidAddress'
# resp = requests.get(url)
# print(resp.status_code)
# print(resp.text)

#===============================================================
# # # 八、获取刷单列表
# # #线上地址
# url = 'index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type={getType}&limit={limit}&debug_list={debugList}&debug_allot={debugAllot}'
url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=1&limit=1'
#获取评论数据
url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=3&limit=20'
# # #测试地址
# url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&country_code=US&get_type=1&limit=10'
resp = requests.get(url)
print(resp.text)
# task_infos = requests.get(url).json()
# print(requests.get(url).text)
# print(task_infos)
# for key in task_infos.keys():
#     task_id = int(key)
#     print(key)
# a = json.loads(task_infos[str(task_id)]['account']['header'])['user-agent']
# b = task_infos[str(task_id)]["account"]["login_aliexpress_email"]
# c = task_infos[str(task_id)]["account"]["login_aliexpress_password"]
# d = task_infos[str(task_id)]["address"]["FullName"]
# e =task_infos[str(task_id)]["address"]["AddressLine1"]
# f = task_infos[str(task_id)]["address"]["AddressLine2"]
# g = task_infos[str(task_id)]["address"]["StateOrRegion"]
# h = task_infos[str(task_id)]["address"]["City"]
# i = task_infos[str(task_id)]["address"]["PostalCode"]
# j = task_infos[str(task_id)]["address"]["PhoneNumber"]
# print(a)
# print(b)
# print(c)
# print(d)
# print(e)
# print(f)
# print(g)
# print(h)
# print(i)
# print(j)
# print(task_infos[str(task_id)]["payment"]["CreditCardNumber"])
#==========================================
#测试机
#获取待注册的用户信息
# resp = requests.get('http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet&validate_email=3985652147@qq.com&dynamic_ip=183.234.61.117')
# print(resp.json())
# try:
#     sys.exit(0)
# except:
#
#     print('程序退出')

#=====================================================================================================================================
# def main():
#     # while True:
#     #测试机地址，获取刷单任务，返回字典格式的json串
#     # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=1&limit=1&debug_list=0&debug_allot=0'
#     #线上地址，获取刷单任务，返回字典格式的json串
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetTaskOrdersList2&get_type=1&limit=1&debug_list=0&debug_allot=0'
#     resp = requests.get(url)
#     print(resp.text)
#     if resp.json() == []:
#         # logger.info('未获取到待刷单列表的数据，程序结束！')
#         print('未获取到待刷单列表的数据，程序结束！')
#         sys.exit(0)
#     else:
#         # logger.info('成功获取到一条待刷单的数据！')
#         print('成功获取到一条待刷单的数据！')
#         task_infos = resp.json()
#         # print(task_infos)
#         for key in task_infos.keys():
#             task_id = int(key)
#         print(task_id,task_infos)
#             # spider = AliexpressOrderSpider(task_infos,task_id)
#             # spider.run()
#
#
# if __name__ == '__main__':
#     main()

#=====================================================================================================================
"""
更换订单号
"""
import time
import  requests
def get_oxylabs_proxy(_country,_city ,_session):
# def get_oxylabs_proxy(_country,_session):
    #端口10000随机
    #端口10001 - 19999 美国端口
    username = 'rdby111'
    password = '4G5wTzP5rj'
    country = _country
    city = _city
    session = _session
    port = 10000
    if _country == 'gb':
        port = 20000
    if _country == 'ca' or _country == 'cn' or _country == 'de':
        port = 30000

    if city :
        entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
                 (username, country,city,session, password,country,port))
    else:
        entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
             (username, country,session, password,country,port))
    proxies = {
        'http': entry,
        'https': entry,
    }
    return proxies

def get(session, url, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    while re_time < retry:
        re_time += 1
        try:
            res = session.get(url, *args, **kwargs)
            res.raise_for_status()
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            time.sleep(1.5)
    return res
def update_brushing_status( data):
    # 测试机
    # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
    # 线上
    url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
    resp = requests.post(url=url, data=data)
    # print(resp.text)
    if resp.json()['msg'] == 'ok':
        # logger.info('刷单状态更新成功！')
        print('刷单状态更新成功！')
    else:
        # logger.info('刷单状态更新失败！')
        print('刷单状态更新失败！')
# #
#
# 新增刷单操作日志
def create_task_order_log(data):
    url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
    resp = requests.post(url, data)
    if resp.json()['status'] == 0:
        # logger.info('新增刷单操作日志成功!')
        print('新增刷单操作日志成功!')
    else:
        # logger.info('新增刷单操作日志失败!')
        print('新增刷单操作日志成功!')
#
def get_ip_info( proxies):
    getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
    if getIpInfo:
        ipInfo = json.loads(getIpInfo.text)
        ip = ipInfo['ip']
    else:
        ip = '未获取到ip'
    return ip
#
proxy = get_oxylabs_proxy('us',_city=None, _session=random.random())

brushing_data = {
                    str(3314):{
                        "task_id":3314,
                        "status":2,
                        "order_no":'8002320382127368',
                        "payment_date":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "actual_order_amount":float('21.76')
                    }
                }
update_brushing_status(json.dumps(brushing_data))
# 新增刷单操作日志
log_data = {
    "task_id": 3314,
    "info": "刷单成功！",
    'ip': get_ip_info(proxies={'https': proxy})
}
create_task_order_log(json.dumps(log_data))

#=========================================================================================================================
#加不了购物车
# import time
# import  requests
# def get_oxylabs_proxy(_country,_city ,_session):
# # def get_oxylabs_proxy(_country,_session):
#     #端口10000随机
#     #端口10001 - 19999 美国端口
#     username = 'rdby111'
#     password = '4G5wTzP5rj'
#     country = _country
#     city = _city
#     session = _session
#     port = 10000
#     if _country == 'gb':
#         port = 20000
#     if _country == 'ca' or _country == 'cn' or _country == 'de':
#         port = 30000
#
#     if city :
#         entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
#                  (username, country,city,session, password,country,port))
#     else:
#         entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
#              (username, country,session, password,country,port))
#     proxies = {
#         'http': entry,
#         'https': entry,
#     }
#     return proxies
#
# def get(session, url, retry=5, *args, **kwargs):
#     re_time = 0
#     res = None
#     if "timeout" not in kwargs:
#         kwargs["timeout"] = 15
#
#     while re_time < retry:
#         re_time += 1
#         try:
#             res = session.get(url, *args, **kwargs)
#             res.raise_for_status()
#             break
#         except:
#             print("网络错误,正在重试 [%s] 次." % re_time)
#             time.sleep(1.5)
#     return res
# def update_brushing_status( data):
#     # 测试机
#     # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     # 线上
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     resp = requests.post(url=url, data=data)
#     # print(resp.text)
#     if resp.json()['msg'] == 'ok':
#         # logger.info('刷单状态更新成功！')
#         print('刷单状态更新成功！')
#     else:
#         # logger.info('刷单状态更新失败！')
#         print('刷单状态更新失败！')
# # #
# #
# # 新增刷单操作日志
# def create_task_order_log(data):
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
#     resp = requests.post(url, data)
#     if resp.json()['status'] == 0:
#         # logger.info('新增刷单操作日志成功!')
#         print('新增刷单操作日志成功!')
#     else:
#         # logger.info('新增刷单操作日志失败!')
#         print('新增刷单操作日志成功!')
# #
# def get_ip_info( proxies):
#     getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
#     if getIpInfo:
#         ipInfo = json.loads(getIpInfo.text)
#         ip = ipInfo['ip']
#     else:
#         ip = '未获取到ip'
#     return ip
# #
# proxy = get_oxylabs_proxy('us',_city=None, _session=random.random())
#
# brushing_data = {
#                     str(59):{
#                         "task_id":59,
#                         "status":23,
#                         # "order_no":'100167474425293',
#                         # "payment_date":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                         # "actual_order_amount":float('21.24')
#                     }
#                 }
# update_brushing_status(json.dumps(brushing_data))
# # 新增刷单操作日志
# log_data = {
#     "task_id": 59,
#     "info": "商品下架，无法添加到购物车，刷单失败！",
#     'ip': get_ip_info(proxies={'https': proxy})
# }
# create_task_order_log(json.dumps(log_data))
# ######################################################################################################################
#
# 让一个地址失效
# url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyOneAddress&address_id=2426'
# resp = requests.get(url)
# if resp.json().get('code') == 200:
#     print('已成功让该地址失效！')

# ==================================================================================================================
# def update_page_and_rank(data):
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressUpdatePageAndRank'
#     resp = post(requests.session(), url=url, post_data=data)
#     print(resp.text)
#     if resp.json()['code'] == 200:
#         print('更新商品排名成功!')
#     else:
#         print('更新商品排名失败!')
# data = {
# 		"data": {
# 			"page_num": "10",
# 			"row_num": "10",
# 			"task_id": "1214"
# 		}
# 	}
# update_page_and_rank(json.dumps(data))
# =====================================================================================================================
# 留评
#
# 获取当前ip信息，返回字符串
# from lib.tools import get,get_oxylabs_proxy
#
#
# def get_ip_info(proxies):
#     getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
#     if getIpInfo:
#         ipInfo = json.loads(getIpInfo.text)
#         ip = ipInfo['ip']
#     else:
#         ip = '未获取到ip'
#     return ip
# def update_brushing_status(data):
#     # 测试机
#     # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     # 线上
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     resp = requests.post(url=url, data=data)
#     # print(resp.text)
#     if resp.json()['msg'] == 'ok':
#         print('刷单状态更新成功！')
#     else:
#         print('刷单状态更新失败！')
#
# # 新增刷单操作日志
# def create_task_order_log(data):
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
#     resp = requests.post(url, data)
#     if resp.json()['status'] == 0:
#         print('新增刷单操作日志成功!')
#     else:
#         print('新增刷单操作日志失败!')
#
#
#
# review_data = {
#                     str(51): {
#                         "task_id": 51,
#                         "status": 6,
#                     }
#                 }
# update_brushing_status(json.dumps(review_data))
# # 新增刷单操作日志
# proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
# log_data = {
#     "task_id": 51,
#     "info": "留评成功！",
#     'ip': get_ip_info(proxies={'https':proxy})
# }
# create_task_order_log(json.dumps(log_data))
# #
# # =======================================================================================================================
# 加不了购物车
# import time
# import  requests
# def get_oxylabs_proxy(_country,_city ,_session):
# # def get_oxylabs_proxy(_country,_session):
#     #端口10000随机
#     #端口10001 - 19999 美国端口
#     username = 'rdby111'
#     password = '4G5wTzP5rj'
#     country = _country
#     city = _city
#     session = _session
#     port = 10000
#     if _country == 'gb':
#         port = 20000
#     if _country == 'ca' or _country == 'cn' or _country == 'de':
#         port = 30000
#
#     if city :
#         entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
#                  (username, country,city,session, password,country,port))
#     else:
#         entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
#              (username, country,session, password,country,port))
#     proxies = {
#         'http': entry,
#         'https': entry,
#     }
#     return proxies
#
# def get(session, url, retry=5, *args, **kwargs):
#     re_time = 0
#     res = None
#     if "timeout" not in kwargs:
#         kwargs["timeout"] = 15
#
#     while re_time < retry:
#         re_time += 1
#         try:
#             res = session.get(url, *args, **kwargs)
#             res.raise_for_status()
#             break
#         except:
#             print("网络错误,正在重试 [%s] 次." % re_time)
#             time.sleep(1.5)
#     return res
# def update_brushing_status( data):
#     # 测试机
#     # url = 'http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     # 线上
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyTaskOrderStatus'
#     resp = requests.post(url=url, data=data)
#     # print(resp.text)
#     if resp.json()['msg'] == 'ok':
#         # logger.info('刷单状态更新成功！')
#         print('刷单状态更新成功！')
#     else:
#         # logger.info('刷单状态更新失败！')
#         print('刷单状态更新失败！')
# # #
# #
# # 新增刷单操作日志
# def create_task_order_log(data):
#     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressCreateTaskOrderLog'
#     resp = requests.post(url, data)
#     if resp.json()['status'] == 0:
#         # logger.info('新增刷单操作日志成功!')
#         print('新增刷单操作日志成功!')
#     else:
#         # logger.info('新增刷单操作日志失败!')
#         print('新增刷单操作日志成功!')
# #
# def get_ip_info( proxies):
#     getIpInfo = get(requests.session(), 'https://ipinfo.io', proxies=proxies)
#     if getIpInfo:
#         ipInfo = json.loads(getIpInfo.text)
#         ip = ipInfo['ip']
#     else:
#         ip = '未获取到ip'
#     return ip
# #
# proxy = get_oxylabs_proxy('us',_city=None, _session=random.random())
#
# brushing_data = {
#                     str(2300):{
#                         "task_id":2300,
#                         "status":21,
#                         # "order_no":'100167474425293',
#                         # "payment_date":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                         # "actual_order_amount":float('21.24')
#                     }
#                 }
# update_brushing_status(json.dumps(brushing_data))
# # 新增刷单操作日志
# log_data = {
#     "task_id": 2300,
#     # "info": "商品下架，终止刷单！",
#     "info": "订单被关闭，找不到review按键！",
#     # "info": "支付失败！",
#     # "info": "失败！",
#     'ip': get_ip_info(proxies={'https': proxy})
# }
# create_task_order_log(json.dumps(log_data))
# # #
