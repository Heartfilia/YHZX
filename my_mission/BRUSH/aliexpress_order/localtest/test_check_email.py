import re
import requests
from mytools import tools
import json

s = requests.Session()
cvf = tools.get(s,'http://134.175.243.164/mailbox/index.php?m=api&do=getVerifyCode&email='+'Veqwluzk950@beads.wiki'+ '&account=mm123')
if cvf.text:
    cvf = json.loads(cvf.text)
    if 'mail_body' in cvf['message']:
        body = cvf['message']['mail_body']
        form_R = re.compile('(\d{6})')
        list_form = form_R.findall(body)

        # if 'mail_body' in cvf['message']:
    #     body = cvf['message']['mail_body']
    #     cvf_bodyR = re.compile(r'<p class=\\\"otp\\\">([^"]*)<\/p>')
    #     # post_data = {
        #     'code': cvf_bodyR.findall(body)[0],
        #     # 'action': tools.get_input_value("action", r.text),
        #     # 'openid.mode': tools.get_input_value("openid.mode", r.text),
        #     # 'language': tools.get_input_value("language", r.text),
        #     # 'openid.ns': tools.get_input_value("openid.ns", r.text),
        #     # 'verifyToken': tools.get_input_value("verifyToken", r.text),
        #     # 'metadata1': ''
        # }
        print(list_form[0])