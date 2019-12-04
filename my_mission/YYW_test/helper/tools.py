#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 16:17
# @Author  : Lodge
import os
import csv
import sys
# import json
import time
import random
import logging
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from helper import python_config, range_config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save_html(html, name):
    """
    存网页,供分析使用
    :param html:(string) html文件
    :param name:(string) 要存的文件的名字
    """
    with open(os.path.join(BASE_DIR, 'utils', f'{name}.html'), 'w', encoding='utf-8') as html_file:
        html_file.write(html)


def save_csv(name, title=None, *args, **kwargs):
    """
    存入 csv 表格中
    :param name: 表的名字
    :param title: 这个表的表头[列表]
    :param args: 其它数据 [列表]
    :param kwargs: 其他数据
    :return: 不返回,已经存了
    """
    save_csv_dir = os.path.join(BASE_DIR, 'doc')
    save_csv_name = os.path.join(save_csv_dir, f'{name}.csv')
    if not os.path.exists(save_csv_dir):
        os.mkdir(save_csv_dir)
        with open(save_csv_name, 'w', encoding='utf-8') as first_file:
            writer_w = csv.writer(first_file)
            if title:
                writer_w.writerow(title)
    with open(save_csv_name, 'a+', encoding='utf-8') as csv_file:
        writer_a = csv.writer(csv_file)
        for each_row in args:
            writer_a.writerow(each_row)


def send_rtx_info(msg, receivers=python_config.RECEIVERS):
    """
    发送RT消息
    :param receivers:(string) 接收者的名字
    :param msg:(string) 消息
    """
    message = f"* 自动化测试程序 *\n平台:yyw.com\n原因:{msg}"
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": message,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def log(name, std_level=logging.INFO, file_level=logging.INFO):
    file_name_date = time.strftime('%Y%m', time.localtime())
    full_name = f'{name}.log'
    # def logger(name, std_level=logging.INFO, file_level=logging.DEBUG):
    logger = logging.getLogger()
    # log_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    # log_filename = log_dir + '/log/' + name + '.log'
    # if not os.path.isdir(log_dir + "/log"):
    #     os.mkdir(log_dir + "/log")
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log', str(file_name_date))
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filename = os.path.join(log_dir, full_name)
    file_handler = logging.FileHandler(log_filename, mode='a', encoding="utf8")
    # maxBytes=102400000000,
    # backupCount=10

    # fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fmt = logging.Formatter("%(asctime)s=%(levelname)s=%(filename)s[line:%(lineno)d]=>%(message)s")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    stdout_handler.setLevel(std_level)
    logger.addHandler(stdout_handler)
    logger.setLevel(file_level)
    return logger


def chose_driver(driver, LOG, headless=False):
    """
    选择驱动
    :param driver: 驱动名字
    :param LOG: 写日志的日志对象
    :param headless: 无头模式,默认为不启动,要启动传来一个True就好了
    :return: selenium对象
    """
    if driver == 'Chrome':
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument("--no-sandbox")
            options.add_argument('--disable-gpu')
            return webdriver.Chrome(options=options)
        except expected_conditions.WebDriverException:
            LOG.error(f'{driver}:的驱动不匹配或者未安装相关驱动')
            return False
    elif driver == 'Firefox':
        try:
            return webdriver.Firefox(
                executable_path=r'C:\Users\User\AppData\Local\Programs\Python\Python37\Scripts\geckodriver.exe')
        except expected_conditions.WebDriverException:
            LOG.error(f'{driver}:的驱动不匹配或者未安装相关驱动')
            return False
    elif driver == 'IE':
        try:
            return webdriver.Ie()
        except expected_conditions.WebDriverException:
            LOG.error(f'{driver}:的驱动不匹配或者未安装相关驱动')
            return False
    elif driver == 'Edge':
        try:
            return webdriver.Edge()
        except expected_conditions.WebDriverException:
            LOG.error(f'{driver}:的驱动不匹配或者未安装相关驱动')
            return False
    elif driver == 'Phantomjs':
        try:
            return webdriver.PhantomJS()
        except expected_conditions.WebDriverException:
            LOG.error(f'{driver}:的驱动不匹配或者未安装相关驱动')
            return False
    else:
        LOG.info(f'{driver}:启动失败或不存在,现在已经启动默认的Chrome浏览器')
        return webdriver.Chrome()


# 以下案例为主页相关的操作
def register(driver, LOG, eva='normal'):
    """
    注册的时候填写的信息
    :param driver: driver
    :param eva: 密码等级
    :return: 所以信息留存
    """
    status = True    # 是否成功的状态
    reg_time_start = time.time()   # 记录开始时间
    random_first_name = random.choice(range_config.NAMES)
    random_last_name = random.choice(range_config.NAMES)
    random_email = range_config.EMAIL
    random_password = range_config.PASSWORD.get(eva)
    random_phone = range_config.PHONE

    try:
        first_name = driver.find_element_by_id('firstname')
        last_name = driver.find_element_by_id('lastname')
        e_mail = driver.find_element_by_id('email_reg')
        password = driver.find_element_by_id('pwd')
        confirm_password = driver.find_element_by_id('confirm')
        country = driver.find_element_by_xpath('//*[@id="country_chzn_o_7"]')  # US
        country_name = country.text
        telephone = driver.find_element_by_id('telephone')
        agree = driver.find_element_by_id('agree')
        register_done = driver.find_element_by_id('subReg')
    except Exception as e:
        LOG.error('在注册的时候遇到了问题,错误信息为')
        print(e)
    else:
        try:
            first_name.send_keys(random_first_name)
            last_name.send_keys(random_last_name)
            e_mail.send_keys(random_email)
            password.send_keys(random_password)
            confirm_password.send_keys(random_password)
            driver.execute_script("arguments[0].click();", country)
            telephone.send_keys(random_phone)
            agree.click()
        except Exception as e:
            print(e)
            email_verify = ''
            password_verify = ''
            LOG.error('页面元素问题出错...')
            driver.quit()
            exit(0)
        else:
            try:
                email_verify = driver.find_element_by_xpath('//*[@id="email_reg_tip"]/font').text
            except Exception as e:
                email_verify = ''
            else:
                if email_verify:
                    status = False
                    LOG.warning(f'邮箱注册的时候发现的问题为:' + email_verify)

            try:
                password_verify = driver.find_element_by_xpath('//*[@id="form2"]/div[5]/p').text
            except Exception as e:
                password_verify = ''
            else:
                if password_verify:
                    status = False
                    LOG.warning(f'密码注册验证的时候发现的问题为:' + password_verify)
            time.sleep(1)
            register_done.click()
        reg_time_end = time.time()   # 记录完毕时间

        reg_info = {
            'register_time': get_now_time(),
            'first_name': random_first_name,
            'last_name': random_last_name,
            'email': random_email,
            'password': random_password,
            'country': country_name if country_name else 'default country',
            'telephone': random_phone,
            'cost_time': f'{reg_time_end - reg_time_start:.2f}',
            'status': status,
            'error_info': {
                'password': password_verify if password_verify else '',
                'email': email_verify if email_verify else ''
            }
        }
        LOG.info(f'注册信息为:{str(reg_info)}')

        return reg_info


def login(driver, LOG, reg_info):
    """
    登录信息呢
    :param driver: 驱动
    :param reg_info: 注册信息
    :return: 暂时返回时间
    """
    email = reg_info.get('email')
    password = reg_info.get('password')

    e_mail = driver.find_element_by_id('txtUserName')
    in_password = driver.find_element_by_id('txtPassword')
    sign_in = driver.find_element_by_id('Login')

    try:
        e_mail.send_keys(email)
        in_password.send_keys(password)
        sign_in.click()
    except Exception as e:
        print(e)
        LOG.error('登录失败...')
        exit(0)


def address(driver, LOG):
    driver.get(python_config.ADDRESS_SETTING)
    try:
        driver.find_element_by_xpath('//*[@id="u_205011"]/dl/dt/strong')
    except expected_conditions.NoSuchElementException:
        try:
            gender_btn = driver.find_element_by_xpath('//*[@id="regUl"]/li[1]/input[1]')
            state_btn = driver.find_element_by_xpath('//*[@id="stateSelect_chzn"]/a')
            city_input = driver.find_element_by_xpath('//*[@id="city"]')
            street_input = driver.find_element_by_xpath('//*[@id="street_address"]')
            post_code = driver.find_element_by_xpath('//*[@id="postcode"]')
            submit = driver.find_element_by_xpath('//*[@id="changeaddress"]')
        except expected_conditions.NoSuchElementException:
            LOG.error('地址信息的页面元素未能定位到，请关注...')
            return False
        else:
            try:
                gender_btn.click()
                try:
                    state_btn.click()
                except Exception as e:
                    state_input = driver.find_element_by_xpath('//*[@id="state"]')
                    print(e)
                    state_input.clear()
                    state_input.send_keys(python_config.ADDRESS_INFO.get('street'))
                city_input.clear()
                city_input.send_keys(python_config.ADDRESS_INFO.get('city'))
                street_input.clear()
                street_input.send_keys(python_config.ADDRESS_INFO.get('street'))
                post_code.clear()
                post_code.send_keys(python_config.ADDRESS_INFO.get('post_code'))
            except Exception as e:
                LOG.error('地址信息设置错误,需要看一下那个出了问题, e:' + str(e))
            else:
                submit.click()
                LOG.info('地址信息设置成功')
    else:
        LOG.info('已经设置了收货地址信息,不用再次验证...')


def reset_status(driver, LOG):
    """重置当前浏览器的状态,方便测试其它信息"""
    driver.delete_all_cookies()
    driver.refresh()
    time.sleep(3)
    driver.get(python_config.GOAL_URL)
    LOG.info('浏览器的信息已经恢复为未登录的状态,然后回到了主页,会停留10秒钟.')
    time.sleep(10)


def save_screen_shot(driver, opt='V', name=''):
    """
    存截屏: 操作类型:
    driver: 需要传过来当前的驱动
    V==>view:普通截图，
    O==>Options:关键操作截图
    name:: 截图的额外名字
    """
    opt = opt.upper()
    print(f'准备截图:{name},操作是:{opt}')
    today_tic = time.strftime('%H%M%S', time.localtime())
    today_date = time.strftime('%Y%m%d', time.localtime())
    # view 为普通的状态截图保存
    log_dir = os.path.join(BASE_DIR, 'utils', 'images', str(today_date))

    log_dir_view = os.path.join(log_dir, 'view')
    log_dir_options = os.path.join(log_dir, 'options')
    log_dir_error = os.path.join(log_dir, 'error')

    save_shot_view_dir = os.path.join(log_dir_view, f'{today_tic}_{name}.png')
    # options 为某些关键操作截图
    save_shot_options_dir = os.path.join(log_dir_options, f'{today_tic}_{name}.png')
    # 其他的错误操作 'E'
    save_error_dir = os.path.join(log_dir_error, f'{today_tic}_{name}.png')

    if opt == 'V':
        if not os.path.exists(log_dir_view):
            os.mkdir(log_dir_view)
        driver.save_screenshot(save_shot_view_dir)
    elif opt == 'O':
        if not os.path.exists(log_dir_options):
            os.mkdir(log_dir_options)
        driver.save_screenshot(save_shot_options_dir)
    elif opt == 'E':
        if not os.path.exists(log_dir_error):
            os.mkdir(log_dir_error)
        driver.save_screenshot(save_error_dir)
    else:
        if not os.path.exists(log_dir_view):
            os.mkdir(log_dir_view)
        driver.save_screenshot(save_shot_view_dir)


# logger = log('时间统计日志')   # 弄了这个会双重日志 不太好


def count_time(fn):
    def func(*args, **kwargs):
        t1 = time.time()
        fn(*args, **kwargs)
        t2 = time.time()
        print(f'计时函数:{fn.__name__}:此函数调用时间为:{t2-t1:.2f} s')
    return func


def get_now_time():
    time_tic = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return time_tic


# driver = chose_driver('Chrome', log('test'))
# driver.get('http://www.baidu.com')
# save_screen_shot(driver, 'v', 'test')
# time.sleep(100)
