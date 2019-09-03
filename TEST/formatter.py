# import json

# f = "guid=e81bba60a47ccb706a6a99ab93918824; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; LangType=Lang=&Flag=1; _ujz=MTU3NTgxNzc3MA%3D%3D; search=jobarea%7E%60030200%7C%21ord_field%7E%600%7C%21recentSearch0%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAPython+%B8%DF%BC%B6%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch1%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FApython%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch2%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch3%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAphp%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21recentSearch4%7E%60030200%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA0%A1%FB%A1%FAamazon%A1%FB%A1%FA2%A1%FB%A1%FA1%7C%21collapse_expansion%7E%601%7C%21; 51job=cenglish%3D0%26%7C%26; ASP.NET_SessionId=uwmfa50nyvbs4kclltvoxeuv"

# f1 = f.split("; ")

# cookies = list()
# for i in f1:
#     f2 = {"name": i.split('=', 1)[0], "value": i.split('=', 1)[1], "httponly": "✓", "domain": "ehire.51job.com", "path": "/"}
#     cookies.append(f2)


# print(json.dumps(cookies))

# def decorator(fn):
# 	def test():
# 		for i in range(3):
# 			print('=' * 20)
# 			fn('hello')
# 			print('*' * 20 )
# 			print()

# 	return test


# @decorator
# def a(test):
# 	print('here are my test information')
# 	print(test)


# a()

# import time


# f = '*' * 50

# lon = len(f)

# for x in range(lon):
#     x = x + 1
#     print(f'\r{">" * x}{" " * (50 - x)}|', end='', flush=True)
#     time.sleep(0.5)

# from requests import Session
# session = Session()

# def report_send_rtx_msg():
#     """
#     rtx 提醒
#     :param receivers:
#     :param msg:
#     :return:
#     """
#     post_data = {
#         "sender": "系统机器人",
#         "receivers": '朱建坤',
#         "msg": '测试信息',
#     }
#     session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
# report_send_rtx_msg()

# def fun():
#     for i in range(5):
#         yield i


# for i in fun():
# 	print(i)

f = "pageSize=90&cityId=763&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=python&kt=3&_v=0.20908331&x-zp-page-request-id=b5ff670b48af4518829e4a432cafbad0-1567492285015-790004&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5"
f1 = f.split("&")
f2 = {f3.split("=", 1)[0]: f3.split("=", 1)[1] for f3 in f1}
print(f2)
