import json,re 
import os,sys
import random
import time
import requests
import threading
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from baiduOcr import BaiduOrc
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mytools import tools
from mytools.tools import logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from config import *
from selenium.webdriver.support.select import Select
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ProxyError


logger = logger('register_de')
class AliexpressRegisterSpider():

    def __init__(self,user_info,proxy,index,register_city):
        # self.proxy = get_oxylabs_proxy('us', _city=None, _session=random.random())['https']
        self.proxy = proxy
        self.index = index
        self.register_city = register_city
        auth = self.proxy.split("@")[0][7:]
        proxyid = self.proxy.split("@")[1]
        proxyauth_plugin_path = tools.create_proxyauth_extension(
            proxy_host=proxyid.split(":")[0],
            proxy_port=int(proxyid.split(":")[1]),
            proxy_username=auth.split(":")[0],
            proxy_password=auth.split(":")[1]
        )
        self.User_Agent = generate_user_agent(device_type="desktop")
        self.chrome_options = Options()
        self.chrome_options.add_extension(proxyauth_plugin_path)
        self.chrome_options.add_argument('user-agent="%s"' % self.User_Agent)
        self.chrome_options.add_argument('--referer=https://www.aliexpress.com')
        #设置无头模式
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument('--disable-gpu')
        # 设置不加载图片
        self.chrome_options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.user_info = user_info
        # print('当前正在注册的用户是',self.user_info['data']['email']["login_aliexpress_email"])
        self.password = "ZhanShen001"
        self.index_url = 'http://www.aliexpress.com/'
        self.headers = {
            "user-agent": self.User_Agent
        }

    def register(self):
        try:
            self.driver.get('https://login.aliexpress.com/join/buyer/expressJoin.htm')
            WebDriverWait(driver=self.driver, timeout=30).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Email address"]'))
            )
            self.driver.find_element_by_xpath('//input[@placeholder="Email address"]').send_keys(self.user_info['data']['email']["login_aliexpress_email"])
            time.sleep(random.uniform(4, 6))
            self.driver.find_element_by_xpath('//input[@placeholder="Password"]').send_keys(self.password)
            time.sleep(random.uniform(4, 6))
            js = 'document.getElementById("ws-xman-register-submit").click();'
            self.driver.execute_script(js)
            time.sleep(10)
            self.driver.get(self.index_url)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'close-layer'))
                )
                self.driver.find_element_by_class_name('close-layer').click()
            except TimeoutException:
                pass
            # time.sleep(5)
            # self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            # time.sleep(3)
            # if  'Hi, US' in self.driver.page_source:
            # time.sleep(10)
            try:
                WebDriverWait(driver=self.driver, timeout=30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="username"]/a[1]'))
                )
                text = self.driver.find_element_by_xpath('//div[@class="username"]/a[1]/span').text.strip()
                if 'DE' in text:
                    self.set_user_info()
                    time.sleep(10)
                    if 'successfully submitted' in self.driver.page_source:
                        logger.info('个人信息设置成功！success!')
                        self.do_after_set_user_info_success()
                        self.driver.quit()
                        sys.exit(0)
                    else:
                        logger.info('个人信息设置失败！failed,Quit!')
                        self.driver.quit()
                        sys.exit(0)
                else:
                    logger.info('注册出错，程序结束！')
                    self.driver.quit()
                    sys.exit(0)
            except TimeoutException:
                pass

            if re.search(r', DE!', self.driver.page_source):
                self.set_user_info()
                time.sleep(10)
                if 'successfully submitted' in self.driver.page_source:
                    logger.info('个人信息设置成功！success!')
                    self.do_after_set_user_info_success()
                    self.driver.quit()
                    sys.exit(0)
                else:
                    logger.info('个人信息设置失败！failed,Quit!')
                    self.driver.quit()
                    sys.exit(0)
            else:
                logger.info('注册出错，程序结束！')
                self.driver.quit()
                sys.exit(0)
        except TimeoutException:
            logger.info('等待超时，程序终止！')
            self.driver.quit()
            sys.exit(0)

    def set_user_info(self):
        logger.info('正在设置用户的基本信息...')
        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="fast-entry"]/ul/li[1]/a'))
        )
        self.driver.find_element_by_xpath('//div[@class="fast-entry"]/ul/li[1]/a').click() #'My Aliexpress/Accout'

        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.element_to_be_clickable((By.ID, 'headMenu_account'))
        )
        self.driver.find_element_by_id('headMenu_account').click() #'Account'

        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="me-menu-body"]/p[@class="me-menu-title"]/a'))
        )
        self.driver.find_element_by_xpath('//div[@class="me-menu-body"]/p[@class="me-menu-title"]/a').click() #'Edit Settings'
        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="settings-panel"]/div[1]/ul/li[2]/a'))
        )
        self.driver.find_element_by_xpath('//div[@id="settings-panel"]/div[1]/ul/li[2]/a').click() #'Edit Member Profile'
        time.sleep(5)
        # 此处切换选项卡
        self.driver.switch_to.window(self.driver.window_handles[1])
        #点击"edit"
        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="dpl-btn to-edit-btn"]'))
        )
        self.driver.find_element_by_xpath('//a[@class="dpl-btn to-edit-btn"]').click()
        #开始编辑
        WebDriverWait(driver=self.driver, timeout=30).until(
            EC.presence_of_element_located((By.XPATH, '//table[@class="tables V"]/tbody/tr[1]/td/div[1]/input'))
        )
        time.sleep(10)
        truename = self.user_info['data']['address']['truename']
        if re.search(r"[^A-Za-z\s]", truename):
            truename = re.sub(r"[^A-Za-z\s]", '', truename)
        print(truename)
        # time.sleep(60)
        if len(truename.split()) == 1:
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[1]/input').clear()
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[1]/input').send_keys(truename.split()[0])
            time.sleep(random.uniform(0.5, 1.0))
            # time.sleep(60)
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[2]/input').clear()
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[2]/input').send_keys(truename.split()[0])
        else:
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[1]/input').clear()
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[1]/input').send_keys(truename.split()[0])
            time.sleep(random.uniform(0.5, 1.0))
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[2]/input').clear()
            self.driver.find_element_by_xpath('//table[@class="tables V"]/tbody/tr[1]/td/div[2]/input').send_keys(truename.split()[1])
        time.sleep(random.uniform(0.5, 1.0))
        # sys.exit(0)
        self.driver.find_element_by_id('mr').click() #性别，选女
        time.sleep(random.uniform(0.5, 1.0))
        street = self.user_info['data']['address']["address_line1"]
        if re.search(r"[^A-Za-z\s]", street):
            street = re.sub(r"[^A-Za-z\s]", '', street)
        self.driver.find_element_by_xpath('//table[@class="contact-address"]/tbody/tr[1]/td/input').send_keys(street)#街道
        time.sleep(random.uniform(0.5, 1.0))
        city = self.user_info['data']['address']["city"]
        if re.search(r"[^A-Za-z\s]", city):
            city = re.sub(r"[^A-Za-z\s]", '', city)
        self.driver.find_element_by_xpath('//table[@class="contact-address"]/tbody/tr[2]/td/input').send_keys(city)#城市
        time.sleep(random.uniform(0.5, 1.0))
        state_region = self.user_info['data']['address']["state_region"]
        if re.search(r"[^A-Za-z\s]", state_region):
            state_region = re.sub(r"[^A-Za-z\s]", '', state_region)
        self.driver.find_element_by_xpath('//input[@id="province"]').send_keys(state_region)  # 省或州，非select
        # state_selectBtn = Select(self.driver.find_element_by_id('usProvinceList'))#州或者省
        # try:
        #     state_selectBtn.select_by_visible_text(self.user_info['data']['address']["state_region"])
        # except Exception:
        #     logger.info('从接口获取的StateOrRegion信息对应不上，默认为下拉列表的第一个州或地区！')
        #     StateOrRegion = self.driver.find_element_by_xpath('//select[@id="usProvinceList"]/option[2]').text
        #     print(StateOrRegion)
        #     state_selectBtn.select_by_visible_text(StateOrRegion)
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_xpath('//table[@class="contact-address"]/tbody/tr[5]/td/input').send_keys(self.user_info['data']['address']["postal_code"])#邮编
        # 电话号码需要处理，若有"+4"前缀，则去掉"+4"前缀
        PhoneNumber = self.user_info['data']['address']["mobile"]
        if re.search(r'\+4|\s|\(|\)|Â|\+', PhoneNumber):
            PhoneNumber = re.sub(r'\+4|\s|\(|\)|Â|\+', '', PhoneNumber)
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_xpath('//*[@id="GroupListForm"]/table/tbody/tr[6]/td/table/tbody/tr/td[3]/input').send_keys(PhoneNumber)
        time.sleep(random.uniform(0.5, 1.0))
        self.driver.find_element_by_id('formSubmit').submit()
        logger.info('点击提交个人信息的设置!')

    def do_after_set_user_info_success(self):
        self.driver.get(self.index_url)
        time.sleep(10)
        logger.info('%s用户注册成功！' % self.user_info['data']['email']["login_aliexpress_email"])
        data = {
            'data': {
                "aliexpress_password": self.password,
                "email_id": self.user_info['data']['email']['id'],
                "credit_id": self.user_info['data']["credit"]['id'],
                "address_id": self.user_info['data']["address"]['id'],
                "ip_id": self.user_info['data']["ip"]['id'],
                "register_city": self.register_city,
                "header": json.dumps(self.headers),
                "cookies": json.dumps(self.driver.get_cookies()),
                "status_code": "200"
            }
        }
        # print(json.dumps(data))
        self.save_success_register_info(json.dumps(data))
        self.driver.quit()
        dir = os.path.join(os.path.dirname(__file__), 'data')
        last_domain_json_file = dir + '/' + 'last_email_domain.json'
        with open(last_domain_json_file, 'w', encoding='utf-8') as f:
            domain_index_data = {
                'last_index': self.index
            }
            f.write(json.dumps(domain_index_data))

    # 将成功注册的用户信息入库
    @staticmethod
    def save_success_register_info(data):
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountPost'
        resp = tools.post(requests.session(), url=url, post_data=data)
        if resp:
            if resp.text.strip() == "success" and resp.status_code == 200:
                # print(resp.text)
                logger.info('注册信息已成功入库！')
            else:
                logger.info('注册信息入库失败！')
            
    # @staticmethod
    # def modify_one_address_invalid(self,address_id):
    #     url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressModifyOneAddress&address_id=%s' % address_id
    #     resp = requests.get(url)
    #     if resp.json().get('code') == 200:
    #         logger.info('成功让地址失效！')
    #     else:
    #         logger.info('未能让地址失效')


#主函数
def main(user_infos, proxy, index, register_city):
    spider = AliexpressRegisterSpider(user_infos,proxy,index,register_city)
    spider.register()

#思路：让主线程循环获取任务，每次获取一个任务，并创建一个子线程去跑注册流程，如果子线程网络出错或者其他原因导致的超时，则直接退出子线程。这样主线程又可以获取任务接着跑了。
if __name__ == '__main__':
    while True:
        s = requests.Session()
        try:
            # 获取地址ip
            # r = tools.get(s, 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetOneValidAddress')
            r = tools.get(s, 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressGetOneValidAddress&country_code=DE')
            html = json.loads(r.text)
            if int(html['code']) == 200:
                # oxy代理
                # proxies = tools.get_oxylabs_proxy('us', None, random.random())
                # 住宅代理
                proxies = {'https': 'http://10502+DE+10502-%s:Y7aVzHabW@de-30m.geosurf.io:8000' % random.randint(300000,400000)}
                getIpInfo = tools.get(requests.session(), 'https://ipinfo.io', proxies=proxies)
                if getIpInfo:
                    ipInfo = json.loads(getIpInfo.text)
                    ip = ipInfo['ip']
                    print(ip)
                    register_city = ipInfo["city"]
                    print(register_city)
        except Exception:
            pass
        #邮箱规则：1位随机大写字母 + 7位随机小写字母 + 3位随机数字 + 邮箱域名[按索引轮询]

        dir = os.path.join(os.path.dirname(__file__), 'data')
        last_domain_json_file = dir + '/' + 'last_email_domain.json'
        if not os.path.exists(last_domain_json_file):
            f = open(last_domain_json_file,'w',encoding='utf-8')
            f.close()

        with open(last_domain_json_file,'r',encoding='utf-8') as f:
            json_data = f.read()
            if json_data:
                index = json.loads(json_data)['last_index'] + 1
                if index == len(Email_Domains):
                    index = 0
            else:
                index = 0
        # Email = random.choice(Upper_Letter_List) + ''.join(random.sample(Lower_Letter_List,7)) + ''.join(random.sample(Digit_List,3)) + '@' + Email_Domains[index]
        Email = random.choice(names) + random.choice(names) + ''.join(random.sample(Digit_List,3)) + '@' + Email_Domains[index]
        print(Email)
        url = 'http://third.gets.com/api/index.php?sec=20171212getscn&act=aliexpressAutoCreateAccountGet&country_code={country_code}&validate_email={validateEmail}&dynamic_ip={dynamicIp}'.format(country_code='DE', validateEmail=Email, dynamicIp=ip)
        resp = tools.get(s, url=url)
        if resp:
            if resp.json().get('code') == 200:
                user_infos = resp.json()
                #由于接口一次只返回一个待注册用户的数据，默认只创建一个子线程去执行注册流程
                for i in range(0,1):
                    t = threading.Thread(target=main,args=(user_infos, proxies['https'], index, register_city))
                    t.start()
                    t.join()
            else:
                # logger.info('未获取到待注册账户的数据，程序结束！')
                # sys.exit(0)
                logger.info('当前无注册任务，程序[sleep 10m]...')
                time.sleep(60 * 10)
        else:
            logger.info('任务系统出错，程序[sleep 10m]...')
            time.sleep(60 * 10)
