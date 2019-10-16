import time
import requests


URL = 'https://passport.58.com/58/login/pc/dologin'


session = requests.Session()

headers = {
    'referer': 'https://passport.58.com/login?path=http://vip.58.com/?r=0.7920381730820756',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
}

data = {
    'username': '123456',
    'password': 'xx',
    'token': 'xx',
    'fingerprint': '6USBUyxVpk1DdwG9Z0TkDygQiv2mne6t',

}
