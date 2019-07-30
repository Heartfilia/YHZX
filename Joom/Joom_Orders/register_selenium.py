import random
import time
import logger
import json
import requests
from multiprocessing import Process
from selenium import webdriver
from name_cfg import names_cfg
from name_cfg.config import Upper_Letter_List, Lower_Letter_List, Digit_List, Email_Domains
from mytools.tools_1 import get_oxylabs_proxy, create_proxyauth_extension, get, post
from user_agent import generate_user_agent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# logger = logger('register_US')
class JoomRegisterSpider():
    def __init__(self, ):  # user_info, register_city):
        # self.user_info = user_info
        # 屏蔽谷歌浏览器弹出的通知
        self.options = webdriver.ChromeOptions()
        self.prefs = {'profile.default_content_setting_values': {'notifications': 2}}
        self.options.add_experimental_option('prefs', self.prefs)

        # 加user-agent 变成手机浏览器
        self.User_Agent = generate_user_agent(device_type="smartphone")
        self.headers = {
            "user-agent": self.User_Agent
        }
        # self.chrome_options = Options()
        self.options.add_argument('user-agent="%s"' % self.User_Agent)
        # 设置静默模式
        # self.options.add_argument("headless")
        # 设置代理
        # 代理需要指定账户密码时，添加代理使用这种方式
        # self.options.add_extension(proxyauth_plugin_path)
        # self.proxy = 'http://10502+US+10502-%s:Y7aVzHabW@us-30m.geosurf.io:8000' % random.randint(600000, 800000)
        self.proxy = get_oxylabs_proxy('ru', _city=None, _session=random.random())['https']
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        # self.options.add_extension(proxyauth_plugin_path)
        # 代理不需要指定账户密码时，添加代理使用这种方式
        # self.options.add_argument('--proxy-server=%s' % self.proxy)

        self.path = "chromedriver.exe"
        self.driver = webdriver.Chrome(self.path, chrome_options=self.options)
        self.index_url = "https://www.joom.com/en"
        self.username = random.choice(names_cfg.names)
        # 密码
        self.password = "lisi123456"
        # 邮箱
        # self.email = self.user_info["data"]["email"]["login_joom_email"]
        self.email = random.choice(Upper_Letter_List) + ''.join(random.sample(Lower_Letter_List, 7)) + ''.join(
            random.sample(Digit_List, 3)) + '@' + random.choice(Email_Domains)
        print(self.email)

        self.wait = random.randint(1, 3)
        self.items = {}

    def witer_table(self):
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, '//form[@class="form___1qcS9"]//div[@class="caption___2klrn"]'))
        # )
        print("正在填写表单~~~")
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[1]/label/input').send_keys(self.username)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[2]/label/input').send_keys(self.username)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[3]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[3]/label/input').send_keys(self.email)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[4]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[4]/label/input').send_keys(self.password)
        time.sleep(self.wait)
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[5]/label/input').clear()
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[5]/label/input').send_keys(self.password)
        time.sleep(self.wait)
        # 提交表单
        self.driver.find_element_by_xpath('//form[@class="form___1qcS9"]/div[6]/button').click()
        print("填表完成~~~正在注册")

    def register(self):  # 1
        self.driver.get(self.index_url)
        self.driver.maximize_window()
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]//a[@class="button___X0gmy"]'))
        )
        if self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 overlapOthers___3P9LN"]') != -1:
            self.driver.find_element_by_xpath('//div[@class="popup___ByDf3 overlapOthers___3P9LN"]//div[@class="close___zSRXA"]').click()

        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="content"]//a[@class="button___X0gmy"]').click()

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="content___ZmMAf"]'))
        )

        if self.driver.find_element_by_xpath('//div[@class="inner___2LYLS"]/div[1]/div/a').text == "Facebook":
            print("选择账号界面")
            time.sleep(5)
            button = self.driver.find_element_by_xpath('//a[text()="Click here"]')
            self.driver.execute_script("arguments[0].click();", button)
            print("进入注册界面")
            time.sleep(2)
            self.witer_table()


        elif self.driver.find_element_by_xpath('//div[@class="caption___3L-qE"]').text == "Sign in":
            print("登录界面")
            time.sleep(5)
            button = self.driver.find_element_by_xpath('//a[text()="Register"]')
            self.driver.execute_script("arguments[0].click();", button)
            print("进入注册界面")
            time.sleep(2)
            self.witer_table()

        else:
            print("注册界面")
            self.witer_table()

        """
             表单填写完成后还需要检测一下有没有漏填的 
             ***重新填写需要清空再写，该判断有bug***
        """
        try:
            print("正在检查表单是否填写完整——————")
            # self.driver.find_element_by_xpath('//div[@class="caption___2klrn"]/span') != -1
            self.driver.find_element('//div[@class="caption___2klrn"]/span')
            time.sleep(5)
            print("填写不完整")
            a = True
        except:
            a = False
            print("填写完整")

        if a == False:
            print("------正在判断账号有没有注册成功------")
            # 判断账号有没有注册成功
            time.sleep(5)
            if self.driver.find_element_by_xpath('//span[@class="text___2-0vG"]').text != "Sign in":
                print("~~~~~~账号注册成功~~~~~~~")
            else:
                print("账号注册失败")
                # self.invalid_ip()
                self.driver.quit()
                return None

            time.sleep(self.wait)

            self.items["email"] = self.email
            self.items["password"] = self.password
            self.items['headers'] = self.headers
            self.items['cookie'] = self.driver.get_cookies()

            # self.get_data_info()

            print("————————>保存数据中————————>")
            self.save_info()
            print("*********数据保存成功********")
            self.driver.quit()
            return

        elif a == True:
            print("第一个名字没有填，重新填写")
            self.witer_table()

    # 登录失败 就把地址改为无效
    def invalid_ip(self):
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomModifyOneAddress&address_id={addressId}"
        res = get(requests.Session(), url=url.format(addressId=self.user_info["data"]["id"]))
        if res:
            if json.dumps(res.text)["code"] == 200:
                print("地址改为无效——操作成功")
            else:
                print("地址改为无效——操作失败")

    # 获取到需要上传的data信息
    def get_data_info(self):
        data = {
            'data': {
                "joom_password": self.password,  # "密码",
                "email_id": self.user_info["data"]["email"]["id"],  # "邮箱ID",
                "credit_id": self.user_info["data"]["credit"]["id"],  # "信用卡ID",
                "address_id": self.user_info["data"]["address"]["id"],  # "地址ID",
                "ip_id": self.user_info["data"]["ip"]["id"],  # "IP的ID",
                "register_city": self.user_info["data"]["address"]["city"],  # "注册城市",
                "header": json.dumps(self.headers),  # "头信息",
                "cookies": json.dumps(self.driver.get_cookies()),  # "cookies信息",
                "status_code": 200,  # "状态码，如200、1、2",
                # "device_type": 1,#"设备类型，如0 pc 1mobile"
            }
        }
        self.save_register_info(json.dumps(data))

    # 把自动注册刷单账号存入数据库,
    def save_register_info(self, data):
        url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomAutoCreateAccountPost"
        response = post(requests.Session(), url, post_data=data)
        print(response.text)
        print(response.status_code)
        if response:
            if response.text.strip() == "success" and response.status_code == 200:
                # print(resp.text)
                print('注册信息已成功入库！')
            else:
                print('注册信息入库失败！')

    # 保存信息到本地文件
    def save_info(self):
        j = json.dumps(self.items)
        with open('joom_userinfo.json', "a")as fp:
            fp.write(j + ",\n")


def main():  # user_info, register_city):
    spider = JoomRegisterSpider()  # user_info, register_city)
    spider.register()


if __name__ == '__main__':

    # s = requests.Session()
    # try:
    #     url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomGetOneValidAddress&country_code=RU"
    #     r = get(s, url)
    #     html = json.loads(r.text)
    #     print(html)
    #     if html['code'] == 200:
    #         # 获取代理的ip（目前就测试本地的）
    #         # proxies =
    #         get_ipinfo = get(requests.Session(), 'http://ipinfo.io/')
    #         print(get_ipinfo.text)
    #         if get_ipinfo:
    #             ipinfo = json.loads(get_ipinfo.text)
    #             ip = ipinfo["ip"]
    #             print(ip)
    #             register_city = ipinfo["city"]
    #             print(register_city)
    # except BaseException as e:
    #     print(e)
    #
    # # 邮箱规则
    # num = ""
    # for _ in range(11):
    #     num += str(random.randint(1, 9))
    # email = "cy" + num + "@nineboy.art"
    # print(email)
    # # 获取自动注册账号所需要的 邮箱, 地址, IP, 信用卡
    # url = "http://testthird.gets.com:8383/api/index.php?sec=20171212getscn&act=joomAutoCreateAccountGet&country_code={country_code}&validate_email={validateEmail}&dynamic_ip={dynamicIp}"
    # res = get(s, url.format(country_code="RU", validateEmail=email, dynamicIp=ip))
    # content = json.loads(res.text)
    # print(content['code'])
    # if res:
    #     if content["code"] == 200:
    #         user_info = content
    #         print(user_info)
    process_list = []
    for i in range(1):
        print("主线程开始")
        p = Process(target=main, )  # args=(user_info, register_city ) ) # 还有一个代理参数
        p.start()
        process_list.append(p)
        time.sleep(30)
    for i in range(len(process_list)):
        p.join()
#     else:
#         # print('未获取到待注册账户的数据，程序结束！')
#         # sys.exit(0)
#         print('当前无注册任务，程序[sleep 10m]...')
#         time.sleep(60 * 10)
# else:
#     print('任务系统出错，程序[sleep 10m]...')
#     time.sleep(60 * 10)
