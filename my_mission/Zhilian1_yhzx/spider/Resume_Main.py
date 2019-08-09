# coding=gbk
import re
import time
import json
import random
import requests

node = int(time.time() * 1000)

url = 'https://rd5.zhaopin.com/api/rd/resume/list?'

params = {
    # "_": f"{str(node)}",
    "_": "1565339862077",
    "x-zp-page-request-id": "da28b330326b4ea290bea762380d1b8e-1565339861339-158444",
    "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5"                                    # 此处信息不会变的
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'content-type': 'text/plain',
    'origin': 'https://rd5.zhaopin.com',
    'referer': 'https://rd5.zhaopin.com/resume/apply',
}


cookies = {
    "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5",
    "sts_deviceid": "16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d",
    "urlfrom2": "121126445",
    "adfcid2": "none",
    "adfbid2": "0",
    "acw_tc": "2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6",
    "login_point": "67827992",
    "promoteGray": "",
    "diagnosis": "0",
    "LastCity": "%E5%B9%BF%E5%B7%9E",
    "LastCity%5Fid": "763",
    "dywez": "95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html",
    "__utmz": "269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html",
    "NTKF_T2D_CLIENTID": "guest848ED7A8-2D6C-CB43-D002-4785D3149DAB",
    "sou_experiment": "psapi",
    "zp-route-meta": "uid=655193256,orgid=67827992",
    "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D",
    "c": "OYd5f54u-1565146352123-205a31b6147942073825198",
    "_fmdata": "RjVcPpTGcffpZk5l0yUErfjZkmBHOjkP6kSghdv6CtDZCGZsOU%2FpDWROFqcil8ZtN7Dj%2B8TdUuQHdk17CMivo0uhUPDkXO%2BWP45A2LG761M%3D",
    "_xid": "gfhUYYFKG3ST%2F1QH8tKqAHYh0%2FaBXgOv9PvNYIX3DV86QIuuKiO1uUlpUG%2BShxIUJBmMYroIFkBPaV7u7onPfw%3D%3D",
    "x-zp-dfp": "zlzhaopin-1564541208377-824fee2b5b7e3",
    "Hm_lvt_38ba284938d5eddca645bb5e02a02006": "1564539142,1565159011",
    "x-zp-device-id": "767356337adeccab996d3c784380a003",
    "dywec": "95841923",
    "__utmc": "269921210",
    "is-oversea-acount": "0",
    "JsNewlogin": "1837743086",
    "JSloginnamecookie": "onn20v%5Ft1lyuqqav%5Fgmhphzu6uby%40oauth%2Eweixin",
    "JSShowname": '""',
    "at": "bd190984fdba44e388fb723965dc71f5",
    "Token": "bd190984fdba44e388fb723965dc71f5",
    "rt": "ebe692e9a70e4bd4bfe07597db596886",
    "JSpUserInfo": "236a2d6b566a5c6459695b7550725d7340765a69596b526a5f6825693b654f651c71186a076b596a5a641e693675117254731d7613691e6b1b6a1568086903652d6514711b6a016b1b6a026412691c7553721073137613692b6b056a05681c6901651a655d71016a0c6b026a1264016907755e7220733c765769586b586a52685f69426542654a71406a5a6b2b6a1b641969477506720a731c765169386b3e6a596858694e65336527714b6a5e6b466a5f64486950755f725173487651692a6b266a596858694e65276532714b6a236b266a5b645a695c755d72547341765869536b5f6a5f683c6921654f6542714d6a3a6b226a5764586952752",
    "uiioit": "3d752c6452695d6a053555645d7550645e695b6a06355f6453752a642b69566a04355c641",
    "login-type": "b",
    "sts_sg": "1",
    "sts_chnlsid": "Unknown",
    "zp_src_url": "https%3A%2F%2Fpassport.zhaopin.com%2FwxLogin%3Fbkurl%3Dhttps%253A%252F%252Fpassport.zhaopin.com%252Forg%252Flogin%252Fbind%252Faccount%253Fbkurl%253Dhttps%25253A%25252F%25252Frd5.zhaopin.com%2526isValidate%253Dfalse",
    "__utma": "269921210.1113127844.1564539142.1565329072.1565331103.14",
    "dywea": "95841923.183147172171786560.1564539142.1565329072.1565331103.16",
    "sts_sid": "16c75011e5827a-089796397c2574-3c375f0d-2073600-16c75011e5938c",
    "sts_evtseq": "30",
    "dyweb": "95841923.30.10.1565331103",
    "__utmt": "1",
    "__utmb": "269921210.30.10.1565331103"
}


session = requests.Session()

# information = session.post('https://rd5.zhaopin.com/api/rd/resume/list?_=1565339862077&x-zp-page-request-id=da28b330326b4ea290bea762380d1b8e-1565339861339-158444&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5', cookies=cookies, headers=headers, verify=False).text
information = session.post(url, data=params, cookies=cookies, headers=headers, verify=False).text
# information = requests.post(url, data=params, cookies=cookies, headers=headers, verify=False).text

print(information)
# json_file = json.loads(information)

# print(json_file)



