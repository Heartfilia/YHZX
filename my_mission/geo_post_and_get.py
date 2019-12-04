import time
import json
import requests
from functools import wraps


def timer(goaltime):
	def sleeptime(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			now_local = time.localtime()
			hour_info = time.strftime('%H', now_local)
			min_info = time.strftime('%M', now_local)
			second_info = time.strftime('%S', now_local)
			if int(second_info) == 0:
				if int(min_info) == 0:
					if hour_info in str(goaltime):
						print('定时器启动')
						func()
					else:
						print('时: 准备休眠的时为:', 1)
						time.sleep(3600)
				else:
					minu = 3600 - int(min_info) * 60
					print('分: 准备休息的分为:', minu // 60)
					time.sleep(minu)
			else:
				sec = 60 - int(second_info)
				print('秒: 准备休息的秒为:', sec)
				time.sleep(sec)
		return wrapper
	return sleeptime


def send_rtx_info(msg, receivers='郭伟冲;陈毅;朱建坤'):
	"""
	发送RT消息
	:param receivers:(string) 接收者的名字
	:param msg:(string) 消息
	"""
	message = f"*** GEO检测程序 ***\n链接: https://client.geosurf.io/dashboard\n{msg}"
	post_data = {
		"sender": "系统机器人",
		"receivers": receivers,
		"msg": message,
	}
	requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


@timer(['10', '16'])
def run():
	s = requests.Session()

	headers1 = {
		# 这里是登录好的 (账号:密码) base64加密后的指令,不变的话可写死
		'Authorization': 'Basic eXl3ZGJ5MTExQGdtYWlsLmNvbTpNaWxreVdheTIwMTg=',
		'Referer': 'https://client.geosurf.io/login',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
	}
	resp = s.post('https://dashboard-api.geosurf.io/accounts/login', headers=headers1, data={})

	author = json.loads(resp.text).get('token')

	headers2 = {
		'Authorization': 'Bearer ' + author,
		'Referer': 'https://client.geosurf.io/dashboard'
	}

	headers = dict(headers1, **headers2)
	response = s.get('https://dashboard-api.geosurf.io/accounts/balance', headers=headers)

	balance = json.loads(response.text).get('balance')

	if balance:
		if balance < 50:
			msg = f'余额: {balance} 美金\n充值提醒: 当前金额小于50美金,需要注意充值'
		else:
			msg = f'余额: {balance} 美金\n正常检测: 属于可控范围'
	else:
		msg = '提醒原因: GEO代理出错,需要检查监控程序'

	send_rtx_info(msg)


if __name__ == '__main__':
	while True:
		run()
