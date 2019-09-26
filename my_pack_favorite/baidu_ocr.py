from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '你的 App ID'
API_KEY = '你的 Api Key'
SECRET_KEY = '你的 Secret Key'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('example.jpg')

""" 调用通用文字识别, 图片参数为本地图片 """
client.basicGeneral(image);

""" 如果有可选参数 """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"

""" 带参数调用通用文字识别, 图片参数为本地图片 """
client.basicGeneral(image, options)

url = "http//www.x.com/sample.jpg"

""" 调用通用文字识别, 图片参数为远程url图片 """
client.basicGeneralUrl(url);

""" 如果有可选参数 """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"

""" 带参数调用通用文字识别, 图片参数为远程url图片 """
client.basicGeneralUrl(url, options)

# =================== 实例 ======================= #
import re
import ssl
import urllib, sys

from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '17352180'
API_KEY = 'nXwvTLPhZll9jpRRYFf8E2ZM'
SECRET_KEY = '15FkboqNk0Kbrsm8vShCtZbu3V0GiwbG'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('base64.png')

""" 调用通用文字识别, 图片参数为本地图片 """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"


json_key =client.basicGeneral(image)

f_key = ''
for text in json_key.get('words_result'):
    f_key += text.get('words')

last_one = re.findall(r'([a-zA-Z0-9_]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_]+)+', f_key)

print(f_key)
if last_one:
    print(last_one[0])
else:
    print('None')