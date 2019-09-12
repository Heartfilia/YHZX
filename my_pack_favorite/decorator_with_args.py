import time
from functools import wraps

def timer(goaltime):
	def sleeptime(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if goaltime not in ['Sun']:
				print('ok')
				func(goaltime)
				print('ok')
		return wrapper
	return sleeptime

@timer(time.strftime("%a", time.localtime()))
def go(goaltime):
	print('11111')
	print(goaltime)


go(time.strftime("%a", time.localtime()))