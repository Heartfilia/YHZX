from aip import AipOcr

""" ��� APPID AK SK """
APP_ID = '��� App ID'
API_KEY = '��� Api Key'
SECRET_KEY = '��� Secret Key'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


""" ��ȡͼƬ """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('example.jpg')

""" ����ͨ������ʶ��, ͼƬ����Ϊ����ͼƬ """
client.basicGeneral(image);

""" ����п�ѡ���� """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"

""" ����������ͨ������ʶ��, ͼƬ����Ϊ����ͼƬ """
client.basicGeneral(image, options)

url = "http//www.x.com/sample.jpg"

""" ����ͨ������ʶ��, ͼƬ����ΪԶ��urlͼƬ """
client.basicGeneralUrl(url);

""" ����п�ѡ���� """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"

""" ����������ͨ������ʶ��, ͼƬ����ΪԶ��urlͼƬ """
client.basicGeneralUrl(url, options)

# =================== ʵ�� ======================= #
import re
import ssl
import urllib, sys

from aip import AipOcr

""" ��� APPID AK SK """
APP_ID = '17352180'
API_KEY = 'nXwvTLPhZll9jpRRYFf8E2ZM'
SECRET_KEY = '15FkboqNk0Kbrsm8vShCtZbu3V0GiwbG'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

""" ��ȡͼƬ """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('base64.png')

""" ����ͨ������ʶ��, ͼƬ����Ϊ����ͼƬ """
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