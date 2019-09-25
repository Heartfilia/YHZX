import json
import time
import random
import requests


session = requests.Session()


detail_url = "https://rd5.zhaopin.com/api/rd/resume/detail?"


def params_get(resume_no):
    t = int(time.time() * 1000)
    params = {
        '_': f'{t}',
        'resumeNo': f'{resume_no}_1_1',
        'x-zp-page-request-id': f'fed644deeddb46fbb0b4c75ed1c8a1f5-{t- random.randint(50,1000)}-69103',
        'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
    }
    return params


def headers_get(resume_no):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'text/plain',
        'Referer': f'https://rd5.zhaopin.com/resume/detail?resumeNo={resume_no}_1_1&openFrom=5',
        'Sec-Fetch-Mode': 'cors',
        "sec-fetch-site": "same-origin",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        "cookie": "jobRiskWarning=true; at=aa40e8c080b44806bd7bcc1b23023ff3; sajssdk_2015_cross_new_user=1; Token=aa40e8c080b44806bd7bcc1b23023ff3; sts_chnlsid=Unknown; privacyUpdateVersion=1; rd_resume_srccode=402101; zp-route-meta=uid=655193256,orgid=67827992; adfcid2=none; JsNewlogin=1837743086; x-zp-dfp=zlzhaopin-1564541208377-824fee2b5b7e3; adfcid=none; acw_tc=2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6; urlfrom2=121126445; JSloginnamecookie=onn20v%5Ft1lyuqqav%5Fgmhphzu6uby%40oauth%2Eweixin; urlfrom=121126445; JSpUserInfo=24342e6955715d79453201754c6a5371056a5968436b417409333979246b4c34056906710579463203750f6a3471406a58681d6b0074473304791b6b10341c6937710c7919325b75096a03714e6a1c68476b0c7450330c792a6b1e340b691d711f791c321d750e6a0e715d6a1168186b177409333079276b4c3459695a715d7942320475496a5271026a5a68316b087443335b79096b1e3407695371387920320e75486a5071756a3d684c6b4e741f3346794a6b4034596952715e7947320875386a2771096a58684a6b2c7473334879206b3c345b695a715e794c320275496a59710c6a5c684a6b2c74663348795b6b4a34396921715679443208758; zp_src_url=https%3A%2F%2Fpassport.zhaopin.com%2Forg%2Flogin%2Fbind%2Fmobile; __utmt=1; diagnosis=0; rd_resume_actionId=1564551879644655193256; LastCity%5Fid=763; promoteGray=; x-zp-device-id=d249967fbc2a8769053b7d5bfee9690b; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1564539142; adfbid=0; dywec=95841923; LastCity=%E5%B9%BF%E5%B7%9E; sts_deviceid=16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d; JSShowname=""; sts_sg=1; login_point=67827992; login-type=b; x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5; is-oversea-acount=0; loginreleased=1; __utmz=269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html; dywez=95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html; adfbid2=0; uiioit=3d753d6a44640f385a6d5c6203355c6844795a795639006b566e203671645575496a42649; rt=c5bcbdcb3f974eadb9de36ccb4f4b3d6; __utmc=269921210; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1565399655; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D; sts_sid=16c7fc37ae816b-0a7adb49c590df-30760d58-2073600-16c7fc37ae98de; dywea=95841923.183147172171786560.1564539142.1565493091.1565511613.11; __utma=269921210.1113127844.1564539142.1565493091.1565511614.11; sts_evtseq=2; dyweb=95841923.2.10.1565511613; __utmb=269921210.2.10.1565511614"
    }
    return headers


def response_get(resume_no):
    params = params_get(resume_no)
    headers = headers_get(resume_no)
    response = session.get(detail_url, params=params, headers=headers, verify=False)

    return response.text


def get_resume():
    """
    获取每个简历的id
    :return: 每个简历的id
    """
    with open('/utilsinfo081201.json', 'r', encoding='utf-8') as f:
        resume = f.read()

    resume = json.loads(resume)

    lists = resume["data"]["dataList"]

    for i in lists:
        time.sleep(1)
        d = i["id"]
        return d


def run():
    # resume = get_resume()
    # print(resume)
    # response_get(resume)
    send_rtx_msg()


def send_rtx_msg():
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    msg = """
********* HR 数据自动化 *********
状态原因：xxx
处理标准：xxxx
查看链接：xxx
"""
    post_data = {
        "sender": "系统机器人",
        "receivers": '朱建坤',
        "msg": msg,
    }
    requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


if __name__ == '__main__':
    run()


