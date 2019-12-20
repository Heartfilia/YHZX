import os
import requests
from lxml import etree
from . import my_mongo   # 采用数据库读取账号


def login_img():
    """登录获取最新的秘钥
    :api 秘钥api
    :user_name 用户账号
    """
    sin_url = 'https://www.remove.bg/users/sign_in'
    headers = {
    'cookie': '__cfduid=dbc3eac8404adfca80076007f6d5427bc1571882795; paddlejs_checkout_variant={"inTest":true,"controlGroup":false,"isForced":false,"variant":"multipage-compact-payment"}; _ga=GA1.2.526629557.1571882801; _gid=GA1.2.663543043.1571882801; _gat=1; _hjid=41c6066d-630c-4172-887d-d87a596d45df; _hjIncludedInSample=1; _remove_bg_session=aPWgqEhDAWuoYvo6sWradzMMnzoeH2RX4E0P6vuvc6Xde5KgFEicQL8PIrXHMuEmM6SxmALeVYCOKPWQsiY6XLT7kc%2FYEq37bRc3O0RMObnc%2F93N%2FT2NZ%2BBxLMcEH5t2zny%2Bc8W%2FE24iyDMk0eb1yGMTwkAoHgw5GoYvQYhClBxcmsseL2ZnNFo2gmpFWyKgyqLnIsUSAvAJF5IBP%2Bo2DIeh0P4OlEbzWQrkfC2Jhg6xt7CzQhIdff8Z8tukPMlxQRfiXco%3D--O1WeWHHm4skMcJi0--9izE33g0U8TX0BEF6SFaog%3D%3D',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    response = requests.get(sin_url, headers=headers)
    print(response.status_code)
    log_data = response.content
    f = etree.HTML(log_data)
    token = f.xpath('/html/head/meta[@name="csrf-token"]/@content')  # 获取到相应的token值
    user_name = my_mongo.mongo_user_find()
    print(user_name)
    data = {
        'utf8': '✓',
        'authenticity_token': token,
        'user[email]': user_name,
        'user[password]': 'getscom123',
        'user[remember_me]': '0',
        'commit': 'Log in'
    }

    f = requests.post(sin_url, headers=headers, data=data)
    api_html = f.content.decode()
    api_data = etree.HTML(api_html)
    api = api_data.xpath('//*[@id="api-key"]/div[2]/p/span/code/text()')   # 获取账号相对于的api秘钥
    my_mongo.mongo_token_update(user_name=user_name, api=api)
    return api, user_name


def get_img(url):
    """
    回调地址
    利用图片url地址进行的请求
    'size': 'auto'设置为获取预览图片。
    """
    KEY_HERE, user_name = login_img()
    if KEY_HERE is None:
        f1 = my_mongo.mongo_api_find()
        KEY_HERE = f1[0]
    print(KEY_HERE)
    old_img_url = url
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        data={
            'image_url': url,
            'size': 'auto'
        },
        headers={'X-Api-Key': KEY_HERE[0]},
    )
    if response.status_code == requests.codes.ok:
        my_mongo.mongo_api_count(user_name)
        with open(old_img_url[:-1] + '.png', 'wb') as out:
            print(response.content)
            out.write(response.content)
            return response.content
    else:
        print("Error:", response.status_code, response.text)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def file(file_name):
    """
    本地上传图片处理
    'size': 'full'设置为获取预览图片。
    """
    KEY_HERE, user_name = login_img()
    fivew = os.path.join(BASE_DIR, 'img', 'new_img', file_name)
    print(fivew)
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(fivew, 'rb')},
        data={'size': 'full'},
        headers={'X-Api-Key': KEY_HERE[0]},
    )
    # full是最高清的图片
    if response.status_code == requests.codes.ok:
        my_mongo.mongo_api_count(user_name)
        # with open(f'{file_name[:-4]}.png', 'wb') as out:
        #     out.write(response.content)
        return response.content
    else:
        print("Error:", response.status_code, response.text)


if __name__ == '__main__':
    pass
