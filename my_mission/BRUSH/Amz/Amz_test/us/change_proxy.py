#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/8 14:51
# @Author  : Lodge

import io, sys, time, re, os
import json
import winreg
import requests
import us.tools as tools
from user_agent import generate_user_agent

task_url = "http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=getTaskOrdersList2&marketplace_id=1&get_type=1&inner_debug=1"


def compare_task():
    # 匹配任务
    res = tools.get(requests, task_url, 5)
    print('任务信息:', res.text)
    if res:
        resDict = json.loads(res.text)
        if resDict.get("status") == 2001:
            print('没有匹配基本条件的任务')
            time.sleep(120)
            exit()
        elif resDict.get("status") == 2002:
            print('没有匹配下单时间的任务')
            time.sleep(120)
            exit()
        elif resDict.get("status") == 3001:
            print('没有匹配的账户,需要更换IP城市')
            time.sleep(1)
            exit()
        else:
            for i in resDict:
                print(i)
                if int(resDict[i]['progress_status']) < 2 and int(i) > 191:
                    row = resDict[i]
                    print(f'任务详情为：{row}')
                    flag = first_verify(row)
                    if flag:
                        return 'DONTNEXT', row
                    else:
                        return "CANGO", row


def first_verify(row):
        # 获取缓存文件，如果存在直接退出
        data = tools.get_file("%s.txt" % row["task_id"], 'order')
        if data:
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyTaskOrderStatus",
                      "sec": "20171212getscn"}
            tools.post(requests, url, params=params, post_data=data)
            exit()
            return True


def use_fixed_ip(row):
    ip_type = row['account']['ip_type']
    if int(ip_type) == 1:
        print(f'该注册账号的ip类型为:{ip_type},属于固定ip')
    else:
        print(f'该注册账号的ip类型为:{ip_type},属于动态ip，不可用，请切换为固定ip下单')
        os._exit(0)

    proxies = {
        'http': 'http://%s:8800' % (row['account']['register_ip']),
        'https': 'http://%s:8800' % (row['account']['register_ip'])
    }

    print(f'固定ip为：{proxies}')
    getIpInfo = tools.get(requests, 'https://ipinfo.io', proxies=proxies)
    return proxies
    # if getIpInfo:
    #     ipInfo = json.loads(getIpInfo.text)
    #     ip = ipInfo['ip']
    #     registerCity = ipInfo['city']
    #     print(f'ip为{ip}\r\n 城市{registerCity}')
    #     return proxies
    # else:
    #     print('代理不可用 ，请求失败')
    #     os._exit(0)
    #     return None


def add_proxy(proxies, row):
    try:
        # 增加代理ip
        proxy = proxies['http']
        header = json.loads(row['account']["header"])
        header['user-agent'] = generate_user_agent(device_type="desktop")
        print(header['user-agent'])
        no = row['account']["login_amazon_email"].split("@")[0]
        print(proxy)
        print(row['account']["login_amazon_email"])
        sip = row['account']["ip"]
        return proxy, header, no, sip, header
    except Exception as e:
        print('出现异常...')
        exit()
        return 'Except', 'Except', 'Except', 'Except', 'Except'


# ============================================================================= #


xpath = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def set_proxy(enable, proxyIp, IgnoreIp):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("ERROR: " + str(e.args))


def enable_proxy(proxy=None):
    if proxy:
        proxyIP = proxy
        print('now proxy::', proxyIP)
    else:
        proxyIP = "212.115.61.28:8800"
    IgnoreIp = "172.*;119.*;"
    set_proxy(1, proxyIP, IgnoreIp)
    print("Setting success")


def disable_proxy():
    set_proxy(0, "", "")
    print("Empty proxy success")


def reboot():
    place = input("where are you?(home or ls)\n")
    try:
        if place == "home":
            disable_proxy()
        elif place == "ls":
            enable_proxy()
        else:
            print("please input 'home' or 'ls'(longshine)!")
            reboot()
    except Exception as e:
        print("ERROR: " + str(e.args))
    finally:
        pass


def main(proxy):
    enable_proxy(proxy)


if __name__ == "__main__":
    # main(proxy='None')
    # print('本地开启程序...')
    # reboot()
    disable_proxy()










