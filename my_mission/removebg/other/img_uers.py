from selenium import webdriver
import random
from tool import my_mongo
import time
from slemine_img import img_activation


options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")  # 这里的信息是附加信息，可以不设置，但是推荐设置
options.add_argument('--disable-gpu')  # 这里的信息是附加信息，可以不设置，但是推荐设置
options.add_experimental_option("debuggerAddress", "127.0.0.1:9928")  # 设置监控端口
browser = webdriver.Chrome(options=options)


def sign_up():
    """注册账号"""
    list1 = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
             'c', 'v', 'b', 'n', 'm']
    user = random.sample(list1, 7)
    i = ''.join(user)   # 获得随机7位的邮箱名
    user_name = i + '@dersses.store'   # 整个邮箱
    my_mongo.mongo_user_add(user_name=user_name)
    yield user_name


if __name__ == '__main__':
    for i in range(100):
        url = 'https://www.remove.bg/users/sign_up'
        browser.get(url)
        time.sleep(2)
        sign_up()
        time.sleep(30)
        try:
            img_activation.get_user()
        except:
            time.sleep(30)
            img_activation.get_user()
