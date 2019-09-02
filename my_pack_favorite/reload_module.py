# file A : this file
# file B : other_module.py
import importlib


while True:
	import other_module
	cookie = importlib.reload(other_module).cookie
	print(cookie)
	input('enter to continue>>')




# file B info: name: other_module.py
# remenber press ctrl+s after changed
cookie = "here are cookies info"