import requests
import re
import json
from helper import my_mongo


def mailbox(email):
    """
    获取对应邮箱注册地址
    :param email: 邮箱的账号
    :return: 邮箱激活链接
    """
    try:
        cvf = requests.get('http://120.196.73.90:8081/mailbox/index.php?m=api&do=getVerifyCode&email=' + email + '&account=opq123')
        print(cvf)
        if cvf.text:
            cvf = json.loads(cvf.text)
            print(cvf)
            if 'mail_body' in cvf['message']:
                body = cvf['message']['mail_body']
                f = re.search(r'.*btn-primary.*(http://r.remove.bg/lnk/.*) style=', body, re.X)
                print(f.group(1)[:-3])
                return f.group(1)[:-3]
            else:
                return None
    except:
        return None


def get_user():
    """
    激活邮箱的操作
    :return:
    """
    email = my_mongo.mongo_add_user_find()
    print(email)
    url = mailbox(email)
    if url is None:
        return
    requests.get(url)
    my_mongo.mongo_add_user(email)


if __name__ == '__main__':
    get_user()
