import time
from functools import wraps

def timer(goaltime):
	def sleeptime(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			day_info = time.strftime("%a", time.localtime())
			if day_info not in goaltime:
				print('ok')
				func(*args, **kwargs)
				print('ok')
		return wrapper
	return sleeptime

@timer(['Sun'])   # tuple, list and set all are Okay WEEK
def go(other):
	print('11111')
	print(other)


go(time.strftime("%H:%M", time.localtime()))