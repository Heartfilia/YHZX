import datetime
import json
import logging
import logging.handlers
import random
import traceback
import urllib.parse
import time
import os
import pickle
import re
import sys
import hashlib
import platform
from base64 import b64encode

import requests
from PIL import Image
from urllib.parse import urlparse

# from mytools.browser_helper import BrowserHelper
from pytesseract import pytesseract
from us import config
import socket

import urllib3.connection
from user_agent import generate_user_agent

helper = None
seq = random.randint(1, 5)
user_agent_list = [
    'Mozilla/5.0 (Linux; U; Android 4.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 5.1; en-us) AppleWebKit/88+ (KHTML, like Gecko) Safari/999.9.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 5.0; en-us) AppleWebKit/88+ (KHTML, like Gecko) Safari/999.9.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 4.3.5; en-us; HTC_IncredibleS_S710e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1.%s+' % seq,
    'Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 4.3.3; zh-cn; T-Mobile Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 4.3.0; zh-cn; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 4.3.1; zh-cn; SonyEricssonX10i Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 5.1; zh-cn; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 5.1; ar-us; SonyEricssonX10i Build/R2BA026) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 2.2.1; de-de; HTC_Wildfire_A3333 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1%s' % seq,
    'Mozilla/5.0 (Linux; U; Android 2.3.3; de-ch; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1%s' % seq,
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0).%s+' % seq,
    'Mozilla/5.0 (compatible; MSIE 9.1; Windows Phone OS 7.5; Trident/5.1; IEMobile/9.1).%s+' % seq,
    'Mozilla/5.0 (compatible; MSIE 9.2; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.2).%s+' % seq,
    'Mozilla/5.0 (Android 2.2.2; Linux; Opera Mobi/ADR-1103311355; U; en; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 11.00.%s+' % seq,
    'Mozilla/4.0 (compatible; MSIE 8.0; S60; SymbOS; Opera Mobi/SYB-1107071606; en) Opera 11.10.%s+' % seq,
    'Mozilla/4.0 (compatible; MSIE 8.0; Linux armv6l; Maemo; Opera Mobi/8; en-GB) Opera 11.00.%s+' % seq,
]

# https://stormproxies.com/ ebaypp@yyw.com/gets.com123
# https://www.duckdns.org/  yyw178001@gmail.com/yyw.com123
storm_proxy_gateways_main = [
    # 6号路由
    "http://108.59.14.208:13040",
    "http://108.59.14.203:13040"
    # 5号路由
    # "http://5.79.73.131:13080"
]

storm_proxy_gateways_3_minutes = [
    # 6号路由
    "http://163.172.48.109:15002",
    "http://163.172.48.117:15002",
    "http://163.172.48.119:15002",
    "http://163.172.48.121:15002"

    # 5号路由
    # "http://142.54.177.226:15003",
    # "http://198.204.228.234:15003",
    # "http://69.30.240.226:15004",
    # "http://69.30.197.122:15004",
    # "http://142.54.177.226:15004",
    # "http://198.204.228.234:15004",
    # "http://195.154.255.118:15003",
    # "http://195.154.222.228:15003",
    # "http://195.154.252.58:15003",
    # "http://195.154.222.26:15003",
    # "http://195.154.255.118:15004",
    # "http://195.154.222.228:15004",
    # "http://195.154.252.58:15004",
    # "http://195.154.222.26:15004"
]

storm_proxy_gateways_15_minutes = [
    #6号路由
    "http://63.141.241.98:16001",
    "http://173.208.209.42:16001",

    #5号路由
    # "http://63.141.241.98:16001",
    # "http://173.208.209.42:16001",
    # "http://69.197.179.122:16001",
    # "http://173.208.199.74:16001",
    # "http://163.172.36.211:16001",
    # "http://163.172.36.213:16001",
    # "http://163.172.214.109:16001",
    # "http://163.172.214.117:16001"

]

#proxyrack代理
# rack_proxy_gateways_main = [
#     'socks5://megaproxy.rotating.proxyrack.net:222'
#     # 'socks5://209.205.212.34:1200'
#     # 'socks5://209.205.212.34:1201'
# ]

#邮件发送模板
sendMessModel = [
    'pls contact me ,i do not get any contact .',
    'where is my order ?',
    'when your will ship my order ?',
    'you are very bad server ,i do not get any reponse .',
    'this items copy ?',
    'Do u authorize sell this items ?',
    'your items is fake .why you sell it ?',
    'can u ship to my home address ?',
    'why you do not reply my email ?',
    'these items are  fake  or real ?',
    'do u get authorize  of this items  ?',
    'This is  authorized  items ?',
    'authorized  items or copy ?',
    'it is more than one moths ,where is orders ？',
    'why not ship my orders ,it is pass 30days',
    'if you do not ship my order at once ,i will report to amazon',
    'this items dagerouse ,it will fire ?',
    'your sent me the  danger items ？',
    'i got very bad quality items ,i will give you bad feedback .',
    'you sell copy items',
    'why you sell fake items ?',
    'it is fake items ?',
    'u get  authoriz for this item ?',
    'you sell wrong items to me ,pls refund .',
    'i spotted the fake from your store  ,you will closed',
    'your sold fake items ,i will report then close your account .',
    'the quality is very bad ,can you upgade it ?',
    'do u  authority to do this items ?',
    'do u have  authority  file of this items  ?',
    'i can not got call with ,i worry you are fraud',
    'your are fraud or you can keep good quality for this itme ?',
    'i do not think your get authority for t his item ,you are bilker ?',
    'I was received the items, it was broken, please refund. ',
    'I found your prrduct is fake. FAKE PRODUCT, I need my money back!!!',
    'FAKE!! TERRIBLE PRODUCT!! IT WAS BROKEN WHEN I GOT IT..',
    'It is really conterfeit product, why amazon let those conterfeit store sell these goods? ',
    'OH MY GOD!!! THE PRODUCT WAS EXPLODED!!!! GET FIRE!! TAKE MY MONEY BACK!!TOO DISGUSTING!!',
    'That is ridiculous! The items without LOGO! IT MUST BE FAKE PRODUCT! I need to return and take my money back!',
    'Why the item looks like fake goods! Without Logo,and it was broken! please send me return label!',
    'I promise never buy products from your store. ALL PRODUCTS ARE CONTERFEIT!!! FAKE! ALL FAKE PRODUCT!!',
    'I would report to Amazon! Why did not refund me? Terrible quality!! Conterfeit fake product!!',
    'GIVE MY MONEY BACK, YOUR FAKE STORE! CONTERFIET PRODUCT! GOD!!'
]

marketplace = {'1': 'https://www.amazon.com/', '2': 'https://www.amazon.ca/', '3': 'https://www.amazon.co.uk/',
               '4': 'https://www.amazon.de/', '5': 'https://www.amazon.es/', '6': 'https://www.amazon.fr/',
               '7': 'https://www.amazon.it/', '8': 'https://www.amazon.co.jp/', '9': 'https://www.amazon.com.mx/',
               '10': 'https://www.amazon.com.au/'}

#退货评论文本域textarea id文本匹配
return_comment = [
    {"reason": "CR-ORDERED_WRONG_ITEM","required": "AC_OPTIONAL"},
    {"reason": "CR-FOUND_BETTER_PRICE","required": "AC_REQUIRED_STORE_A"},
    {"reason": "CR-NO_REASON_GIVEN","required": "AC_OPTIONAL"},
    {"reason": "CR-QUALITY_UNACCEPTABLE","required": "AC_OPTIONAL"},
    {"reason": "CR-NOT_COMPATIBLE","required": "AC_OPTIONAL"},
    {"reason": "CR-DAMAGED_BY_FC","required": "AC_REQUIRED_WHAT_IS_WRONG"},
    {"reason": "CR-MISSED_ESTIMATED_DELIVERY","required": "AC_OPTIONAL"},
    {"reason": "CR-MISSING_PARTS","required": "AC_REQUIRED_WHAT_IS_WRONG"},
    {"reason": "CR-DAMAGED_BY_CARRIER","required": "AC_REQUIRED_WHAT_IS_WRONG"},
    {"reason": "CR-SWITCHEROO","required": "AC_REQUIRED_ITEM_RECEIVED_IN_ERROR"},
    {"reason": "CR-DEFECTIVE","required": "AC_REQUIRED_WHAT_IS_WRONG"},
    {"reason": "CR-EXTRA_ITEM","required": "AC_REQUIRED_ITEM_RECEIVED_IN_ERROR"},
    {"reason": "CR-UNWANTED_ITEM","required": "AC_OPTIONAL"},
    {"reason": "CR-UNAUTHORIZED_PURCHASE","required": "AC_OPTIONAL"},
    {"reason": "AMZ-PG-BAD-DESC","required": "AC_OPTIONAL"},
]

#邮箱账号配
mailConf = [

    #测评专用 <2019-8-20>
    #   opq123
    {'account': 'opq123', 'host': 'skdd.fun'},
    {'account': 'opq123', 'host': 'kyff.online'},
    {'account': 'opq123', 'host': 'ggpt.fun'},
    {'account': 'opq123', 'host': 'skdd.online'},
    {'account': 'opq123', 'host': 'skdd.site'},
    {'account': 'opq123', 'host': 'ggpt.online'},
    {'account': 'opq123', 'host': 'ggpt.site'},
    {'account': 'opq123', 'host': 'wayls.online'},
    {'account': 'opq123', 'host': 'motoc.online'},
    {'account': 'opq123', 'host': 'motoc.site'},
    {'account': 'opq123', 'host': 'ytts.site'},
    {'account': 'opq123', 'host': 'ytts.fun'},
    {'account': 'opq123', 'host': 'asbe.site'},
    {'account': 'opq123', 'host': 'ytts.online'},
    {'account': 'opq123', 'host': 'skwe.online'},
    {'account': 'opq123', 'host': 'askt.online'},
    {'account': 'opq123', 'host': 'asbe.online'},
    {'account': 'opq123', 'host': 'lspo.online'},
    {'account': 'opq123', 'host': 'abckk.site'},
    {'account': 'opq123', 'host': 'abckk.online'},
    {'account': 'opq123', 'host': 'ipip.online'},
    {'account': 'opq123', 'host': 'iptop.fun'},
    {'account': 'opq123', 'host': 'lspo.site'},
    {'account': 'opq123', 'host': 'ittop.fun'},
    {'account': 'opq123', 'host': 'ittop.online'},
    {'account': 'opq123', 'host': 'ittop.site'},
    {'account': 'opq123', 'host': 'iptop.online'},
    {'account': 'opq123', 'host': 'iptop.site'},
    {'account': 'opq123', 'host': 'wekk.site'},
    {'account': 'opq123', 'host': 'wekk.online'},
    {'account': 'opq123', 'host': 'fobeads.online'},
    {'account': 'opq123', 'host': 'kyff.xyz'},
    {'account': 'opq123', 'host': 'topmail.fun'},
    {'account': 'opq123', 'host': 'mppt.online'},
    {'account': 'opq123', 'host': 'mppt.site'},
    {'account': 'opq123', 'host': 'mppt.fun'},
    {'account': 'opq123', 'host': 'motoc.xyz'},
    {'account': 'opq123', 'host': 'skdd.xyz'},
    {'account': 'opq123', 'host': 'diylink.fun'},
    {'account': 'opq123', 'host': 'fobeads.online'},
    {'account': 'opq123', 'host': 'diylink.site'},
    {'account': 'opq123', 'host': 'mppt.site'},
    {'account': 'opq123', 'host': 'mppt.fun'},
    {'account': 'opq123', 'host': 'kyff.xyz'},
    {'account': 'opq123', 'host': 'mppt.online'},
    {'account': 'opq123', 'host': 'skdd.xyz'},
    {'account': 'opq123', 'host': 'diytool.fun'},
    {'account': 'opq123', 'host': 'wayls.xyz'},
    {'account': 'opq123', 'host': 'diylink.online'},
    {'account': 'opq123', 'host': 'diylink.site'},
    {'account': 'opq123', 'host': 'motoc.xyz'},
    {'account': 'opq123', 'host': 'diylink.fun'},
    {'account': 'opq123', 'host': 'topmail.fun'},
    {'account': 'opq123', 'host': 'moop.online'},
    {'account': 'opq123', 'host': 'abckk.xyz'},
    {'account': 'opq123', 'host': 'frre.online'},
    {'account': 'opq123', 'host': 'diytool.online'},
    {'account': 'opq123', 'host': 'ytts.xyz'},
    {'account': 'opq123', 'host': 'asbe.xyz'},
    {'account': 'opq123', 'host': 'topo.fun'},
    {'account': 'opq123', 'host': 'lspo.xyz'},
    {'account': 'opq123', 'host': 'mopo.fun'},
    {'account': 'opq123', 'host': 'askt.xyz'},
    {'account': 'opq123', 'host': 'mopo.site'},
    {'account': 'opq123', 'host': 'iptop.xyz'},
    {'account': 'opq123', 'host': 'namebook.fun'},
    {'account': 'opq123', 'host': 'dakiss.online'},
    {'account': 'opq123', 'host': 'diyhr.online'},
    {'account': 'opq123', 'host': 'fobeads.xyz'},
    {'account': 'opq123', 'host': 'ittop.xyz'},
    {'account': 'opq123', 'host': 'fsbook.site'},
    {'account': 'opq123', 'host': 'wpsll.xyz'},
    {'account': 'opq123', 'host': 'mppt.xyz'},
    {'account': 'opq123', 'host': 'absc.site'},
    {'account': 'opq123', 'host': 'toppk.xyz'},
    {'account': 'opq123', 'host': 'fsbook.online'},
    {'account': 'opq123', 'host': 'absc.fun'},
    {'account': 'opq123', 'host': 'fsbook.fun'},
    {'account': 'opq123', 'host': 'namebook.online'},
    {'account': 'opq123', 'host': 'skwe.xyz'},

    # mm123
    {'account':'mm123','host':'ddrk.fun'},
    {'account':'mm123','host':'ddrk.site'},
    {'account':'mm123','host':'ddrk.xyz'},
    {'account':'mm123','host':'mmlove.fun'},
    {'account':'mm123','host':'mmlove.site'},
    {'account':'mm123','host':'sdjks.site'},
    {'account':'mm123','host':'sdjks.xyz'},
    {'account':'mm123','host':'moopp.online'},
    {'account':'mm123','host':'sdjks.online'},
    {'account':'mm123','host':'moopp.xyz'},
    {'account':'mm123','host':'mmlove.online'},
    {'account':'mm123','host':'mrop.xyz'},
    {'account':'mm123','host':'moppt.site'},
    {'account':'mm123','host':'moppt.fun'},
    {'account':'mm123','host':'diykk.xyz'},
    {'account':'mm123','host':'mrop.fun'},
    {'account':'mm123','host':'diycc.xyz'},
    {'account':'mm123','host':'ytkk.site'},
    {'account':'mm123','host':'diykk.site'},
    {'account':'mm123','host':'lpqa.online'},
    {'account':'mm123','host':'moppt.xyz'},
    {'account':'mm123','host':'psdiy.online'},
    {'account':'mm123','host':'diycc.site'},
    {'account':'mm123','host':'demcc.xyz'},
    {'account':'mm123','host':'demcc.online'},
    {'account':'mm123','host':'ytkk.online'},
    {'account':'mm123','host':'psdiy.fun'},
    {'account':'mm123','host':'psdiy.xyz'},
    {'account':'mm123','host':'fome.xyz'},
    {'account':'mm123','host':'demdem.xyz'},
    {'account':'mm123','host':'namediy.xyz'},
    {'account':'mm123','host':'dirr.xyz'},
    {'account':'mm123','host':'namediy.online'},
    {'account':'mm123','host':'diycc.online'},
    {'account':'mm123','host':'motuoche.xyz'},
    {'account':'mm123','host':'namediy.site'},
    {'account':'mm123','host':'motuoche.xyz'},
    {'account':'mm123','host':'gitme.online'},
    {'account':'mm123','host':'gityou.xyz'},
    {'account':'mm123','host':'ytkk.fun'},
    {'account':'mm123','host':'demdem.online'},
    {'account':'mm123','host':'demcc.site'},
    {'account':'mm123','host':'gitme.site'},
    {'account':'mm123','host':'waibao.fun'},
    {'account':'mm123','host':'lscpu.xyz'},
    {'account':'mm123','host':'dogtop.xyz'},
    {'account':'mm123','host':'demdem.site'},
    {'account':'mm123','host':'gityou.online'},
    {'account':'mm123','host':'dirr.site'},
    {'account':'mm123','host':'dirr.site'},
    {'account':'mm123','host':'diss.site'},
    {'account':'mm123','host':'demdem.site'},
    {'account':'mm123','host':'gityou.online'},
    {'account':'mm123','host':'dakiss.xyz'},
    {'account':'mm123','host':'diyhr.xyz'},
    {'account':'mm123','host':'motuoche.online'},
    {'account':'mm123','host':'diylink.xyz'},
    {'account':'mm123','host':'lscpu.online'},
    {'account':'mm123','host':'mopo.xyz'},
    {'account':'mm123','host':'dogtop.online'},
    # testmail
    {'account': 'testmail', 'host': 'diyfor.cn'},
    {'account': 'testmail', 'host': 'ddrk.online'},
    {'account': 'testmail', 'host': 'mastat.xyz'},
    {'account': 'testmail', 'host': 'motoc.club'},
    {'account': 'testmail', 'host': 'ddrt.online'},
    {'account': 'testmail', 'host': 'lspo.club'},
    {'account': 'testmail', 'host': 'askt.club'},
    {'account': 'testmail', 'host': 'wayls.club'},
    {'account': 'testmail', 'host': 'mastat.online'},
    {'account': 'testmail', 'host': 'abckk.club'},
    {'account': 'testmail', 'host': 'fobeads.club'},
    {'account': 'testmail', 'host': 'wekk.club'},
    {'account': 'testmail', 'host': 'wpsll.club'},
    {'account': 'testmail', 'host': 'skwe.club'},
    {'account': 'testmail', 'host': 'lscpu.club'},
    {'account': 'testmail', 'host': 'toppk.club'},
    {'account': 'testmail', 'host': 'lscpu.club'},
    {'account': 'testmail', 'host': 'frre.club'},
    {'account': 'testmail', 'host': 'ittop.club'},
    {'account': 'testmail', 'host': 'pktop.club'},
    {'account': 'testmail', 'host': 'dakiss.club'},
    {'account': 'testmail', 'host': 'absc.club'},
    {'account': 'testmail', 'host': 'namecc.club'},
    {'account': 'testmail', 'host': 'abckk.top'},
    {'account': 'testmail', 'host': 'gityou.club'},
    {'account': 'testmail', 'host': 'fome.club'},
    {'account': 'testmail', 'host': 'gitme.club'},
    {'account': 'testmail', 'host': 'demdem.club'},
    {'account': 'testmail', 'host': 'diyhr.top	'},
    {'account': 'testmail', 'host': 'motoc.top'},
    {'account': 'testmail', 'host': 'fobeads.top'},
    {'account': 'testmail', 'host': 'demcc.club'},
    {'account': 'testmail', 'host': 'frre.top'},
    {'account': 'testmail', 'host': 'diylink.top'},
    {'account': 'testmail', 'host': 'diycc.club'},
    {'account': 'testmail', 'host': 'wpsll.top'},
    {'account': 'testmail', 'host': 'wayls.top'},
    {'account': 'testmail', 'host': 'namebook.top'},
    {'account': 'testmail', 'host': 'dakiss.top'},
    {'account': 'testmail', 'host': 'lpqa.club'},
    {'account': 'testmail', 'host': 'lscpu.top'},
    {'account': 'testmail', 'host': 'mastat.club'},
    {'account': 'testmail', 'host': 'skwe.top'},
    {'account': 'testmail', 'host': 'pktop.top'},
    {'account': 'testmail', 'host': 'sdjks.club'},
    {'account': 'testmail', 'host': 'lspo.top'},
    {'account': 'testmail', 'host': 'namediy.top'},
    {'account': 'testmail', 'host': 'psdiy.club'},
    {'account': 'testmail', 'host': 'diycc.top'},
    {'account': 'testmail', 'host': 'dogtop.top'},
    {'account': 'testmail', 'host': 'namediy.club'},
    {'account': 'testmail', 'host': 'dirr.top'},
    {'account': 'testmail', 'host': 'diykk.top'},
    {'account': 'testmail', 'host': 'gityou.top'},
    {'account': 'testmail', 'host': 'demdem.top'},
    {'account': 'testmail', 'host': 'gitme.top'},
    {'account': 'testmail', 'host': 'diykk.club'},
    {'account': 'testmail', 'host': 'psdiy.top'},
    {'account': 'testmail', 'host': 'kkide.top'},
    {'account': 'testmail', 'host': 'sdjks.top'},
    {'account': 'testmail', 'host': 'mrop.top'},
    {'account': 'testmail', 'host': 'namecc.top'},
    {'account': 'testmail', 'host': 'moopp.club'},
    {'account': 'testmail', 'host': 'moppt.top'},
    {'account': 'testmail', 'host': 'moopp.top'},
    {'account': 'testmail', 'host': 'lpqa.top'},
    {'account': 'testmail', 'host': 'mastat.top'},


]

#邮箱账号配
mailConf_1 = [
{'account': 'opq123', 'host': 'dersses.store'},
]

# 任务盘查 邮箱域名匹配库
mailConf_test = [
    {'account':'mm123','host':'amzkeys.top'},
    {'account':'mm123','host':'amzkeys.ltd'},
    {'account':'mm123','host':'reviewclubs.club'},
    {'account':'mm123','host':'reviewclubs.top'},
    {'account':'mm123','host':'amzkeys.fun'},
    {'account':'mm123','host':'amzkeys.store'},
    {'account':'mm123','host':'amzkeys.site'},
    {'account':'mm123','host':'amzkeys.online'},
    {'account':'mm123','host':'amzkeys.club'},
    {'account':'mm123','host':'amzkeys.xyz'},
    #2019.7.13新增
    {'account':'mm123','host':'amzdb.ltd'},
    {'account':'mm123','host':'aliexpre.online'},
    {'account':'mm123','host':'aliexpre.site'},
    {'account':'mm123','host':'aliexpre.club'},
    {'account':'mm123','host':'aliexpre.store'},
    {'account':'mm123','host':'aliexpre.cn'},
    {'account':'mm123','host':'amzdb.online'},
    {'account':'mm123','host':'amzdb.net'},
    {'account':'mm123','host':'amzdb.site'},
    {'account':'mm123','host':'amzdb.cn'},
    {'account':'mm123','host':'mydb.ltd'},
    {'account':'mm123','host':'mydb.online'}, #似乎有问题
    {'account':'mm123','host':'mydb.store'},  # 同上
    {'account':'mm123','host':'myyun.info'},
    {'account':'mm123','host':'mydb.shop'},
    {'account':'mm123','host':'myyun.ltd'},
    {'account':'mm123','host':'myyun.store'},
    {'account':'mm123','host':'myyun.online'},
    {'account':'mm123','host':'gets.group'},
    {'account':'mm123','host':'amzbuy.xyz'},
    {'account':'mm123','host':'xinhe.store'},


    {'account':'testmail','host':'aliexpre.biz'},
    {'account':'testmail','host':'aliexpre.info'},
    {'account':'testmail','host':'aliexpre.vip'},
    {'account':'testmail','host':'aliexpre.ltd'},
    {'account':'testmail','host':'aliexpre.net'},
    {'account':'testmail','host':'myfeedback.store'},
    {'account':'testmail','host':'myfeedback.site'},
    {'account':'testmail','host':'myfeedback.club'},
    {'account':'testmail','host':'myfeedback.ltd'},
    {'account':'testmail','host':'myfeedback.cn'},
     #2019.7.13新增
    {'account':'testmail','host':'amzsd.site'},
    {'account':'testmail','host':'amzsd.club'},
    {'account':'testmail','host':'amzbuy.fun'},
    {'account':'testmail','host':'amzbuy.top'},
    {'account':'testmail','host':'amzbuy.online'},
    {'account':'testmail','host':'sdcn.pub'},
    {'account':'testmail','host':'sdcn.site'},
    {'account':'testmail','host':'sdcn.live'},
    {'account':'testmail','host':'amzsd.live'},
    {'account':'testmail','host':'amzsd.pub'},
    {'account':'testmail','host':'amzsd.top'},
    {'account':'testmail','host':'amzsd.fun'},
    {'account':'testmail','host':'amzsd.co'},
    {'account':'testmail','host':'amzsd.xyz'},
    {'account':'testmail','host':'amzsd.online'},
    {'account':'testmail','host':'sdcn.online'},
    {'account':'testmail','host':'amazoncn.site'},
    {'account':'testmail','host':'amazoncn.top'},
    {'account':'testmail','host':'sdcn.art'},
    {'account':'testmail','host':'sdcn.fun'},
 

    {'account':'opq123','host':'myreview.site'},
    {'account':'opq123','host':'myreview.online'},
    {'account':'opq123','host':'myreview.ltd'},
    {'account':'opq123','host':'reviewclub.site'},
    {'account':'opq123','host':'reviewclub.online'},
    {'account':'opq123','host':'reviewclub.top'},
    {'account':'opq123','host':'reviewclub.ltd'},
    {'account':'opq123','host':'reviewclub.club'},
    {'account':'opq123','host':'reviewclub.cn'},
    {'account':'opq123','host':'reviewclubs.site'},
    {'account':'opq123','host':'reviewclubs.cn'},
    {'account':'opq123','host':'reviewclubs.online'},
    #2019.7.13新增
    {'account':'opq123','host':'amazoncn.club'},
    {'account':'opq123','host':'amazoncn.fun'},
    {'account':'opq123','host':'amazoncn.co'},
    {'account':'opq123','host':'amazoncn.live'},
    {'account':'opq123','host':'yywexpress.top'},
    {'account':'opq123','host':'ayes.fun'},
    {'account':'opq123','host':'ayes.pub'},
    {'account':'opq123','host':'ayes.online'},
    {'account':'opq123','host':'yywexpress.live'},
    {'account':'opq123','host':'yywexpress.fun'},
    {'account':'opq123','host':'yywexpress.online'},
    {'account':'opq123','host':'yywexpress.co'},
    {'account':'opq123','host':'yywexpress.pub'},
    {'account':'opq123','host':'yywexpress.xyz'},
    {'account':'opq123','host':'yywexpress.club'},
    {'account':'opq123','host':'ayes.xyz'},
    {'account':'opq123','host':'ayes.live'},
    {'account':'opq123','host':'milkywayjewelry.top'},
    {'account':'opq123','host':'milkywayjewelry.xyz'},
    {'account':'opq123','host':'milkywayjewelry.site'},
    {'account':'opq123','host':'milkywayjewelry.pub'},
    {'account':'opq123','host':'milkywayjewelry.live'},
    {'account':'opq123','host':'milkywayjewelry.online'},
    {'account':'opq123','host':'milkywayjewelry.fun'},
    {'account':'opq123','host':'milkywayjewelry.co'},

    # 测评专用 <2019-8-20>
    #   opq123
    {'account': 'opq123', 'host': 'skdd.fun'},
    {'account': 'opq123', 'host': 'kyff.online'},
    {'account': 'opq123', 'host': 'ggpt.fun'},
    {'account': 'opq123', 'host': 'skdd.online'},
    {'account': 'opq123', 'host': 'skdd.site'},
    {'account': 'opq123', 'host': 'ggpt.online'},
    {'account': 'opq123', 'host': 'ggpt.site'},
    {'account': 'opq123', 'host': 'wayls.online'},
    {'account': 'opq123', 'host': 'motoc.online'},
    {'account': 'opq123', 'host': 'motoc.site'},
    {'account': 'opq123', 'host': 'ytts.site'},
    {'account': 'opq123', 'host': 'ytts.fun'},
    {'account': 'opq123', 'host': 'asbe.site'},
    {'account': 'opq123', 'host': 'ytts.online'},
    {'account': 'opq123', 'host': 'skwe.online'},
    {'account': 'opq123', 'host': 'askt.online'},
    {'account': 'opq123', 'host': 'asbe.online'},
    {'account': 'opq123', 'host': 'lspo.online'},
    {'account': 'opq123', 'host': 'abckk.site'},
    {'account': 'opq123', 'host': 'abckk.online'},
    {'account': 'opq123', 'host': 'ipip.online'},
    {'account': 'opq123', 'host': 'iptop.fun'},
    {'account': 'opq123', 'host': 'lspo.site'},
    {'account': 'opq123', 'host': 'ittop.fun'},
    {'account': 'opq123', 'host': 'ittop.online'},
    {'account': 'opq123', 'host': 'ittop.site'},
    {'account': 'opq123', 'host': 'iptop.online'},
    {'account': 'opq123', 'host': 'iptop.site'},
    {'account': 'opq123', 'host': 'wekk.site'},
    {'account': 'opq123', 'host': 'wekk.online'},
    {'account': 'opq123', 'host': 'fobeads.online'},
    {'account': 'opq123', 'host': 'kyff.xyz'},
    {'account': 'opq123', 'host': 'topmail.fun'},
    {'account': 'opq123', 'host': 'mppt.online'},
    {'account': 'opq123', 'host': 'mppt.site'},
    {'account': 'opq123', 'host': 'mppt.fun'},
    {'account': 'opq123', 'host': 'motoc.xyz'},
    {'account': 'opq123', 'host': 'skdd.xyz'},
    {'account': 'opq123', 'host': 'diylink.fun'},
    {'account': 'opq123', 'host': 'fobeads.online'},
    {'account': 'opq123', 'host': 'diylink.site'},
    {'account': 'opq123', 'host': 'mppt.site'},
    {'account': 'opq123', 'host': 'mppt.fun'},
    {'account': 'opq123', 'host': 'kyff.xyz'},
    {'account': 'opq123', 'host': 'mppt.online'},
    {'account': 'opq123', 'host': 'skdd.xyz'},
    {'account': 'opq123', 'host': 'diytool.fun'},
    {'account': 'opq123', 'host': 'wayls.xyz'},
    {'account': 'opq123', 'host': 'diylink.online'},
    {'account': 'opq123', 'host': 'diylink.site'},
    {'account': 'opq123', 'host': 'motoc.xyz'},
    {'account': 'opq123', 'host': 'diylink.fun'},
    {'account': 'opq123', 'host': 'topmail.fun'},
    {'account': 'opq123', 'host': 'moop.online'},
    {'account': 'opq123', 'host': 'abckk.xyz'},
    {'account': 'opq123', 'host': 'frre.online'},
    {'account': 'opq123', 'host': 'diytool.online'},
    {'account': 'opq123', 'host': 'ytts.xyz'},
    {'account': 'opq123', 'host': 'asbe.xyz'},
    {'account': 'opq123', 'host': 'topo.fun'},
    {'account': 'opq123', 'host': 'lspo.xyz'},
    {'account': 'opq123', 'host': 'mopo.fun'},
    {'account': 'opq123', 'host': 'askt.xyz'},
    {'account': 'opq123', 'host': 'mopo.site'},
    {'account': 'opq123', 'host': 'iptop.xyz'},
    {'account': 'opq123', 'host': 'namebook.fun'},
    {'account': 'opq123', 'host': 'dakiss.online'},
    {'account': 'opq123', 'host': 'diyhr.online'},
    {'account': 'opq123', 'host': 'fobeads.xyz'},
    {'account': 'opq123', 'host': 'ittop.xyz'},
    {'account': 'opq123', 'host': 'fsbook.site'},
    {'account': 'opq123', 'host': 'wpsll.xyz'},
    {'account': 'opq123', 'host': 'mppt.xyz'},
    {'account': 'opq123', 'host': 'absc.site'},
    {'account': 'opq123', 'host': 'toppk.xyz'},
    {'account': 'opq123', 'host': 'fsbook.online'},
    {'account': 'opq123', 'host': 'absc.fun'},
    {'account': 'opq123', 'host': 'fsbook.fun'},
    {'account': 'opq123', 'host': 'namebook.online'},
    {'account': 'opq123', 'host': 'skwe.xyz'},

    # mm123
    {'account': 'mm123', 'host': 'ddrk.fun'},
    {'account': 'mm123', 'host': 'ddrk.site'},
    {'account': 'mm123', 'host': 'ddrk.xyz'},
    {'account': 'mm123', 'host': 'mmlove.fun'},
    {'account': 'mm123', 'host': 'mmlove.site'},
    {'account': 'mm123', 'host': 'sdjks.site'},
    {'account': 'mm123', 'host': 'sdjks.xyz'},
    {'account': 'mm123', 'host': 'moopp.online'},
    {'account': 'mm123', 'host': 'sdjks.online'},
    {'account': 'mm123', 'host': 'moopp.xyz'},
    {'account': 'mm123', 'host': 'mmlove.online'},
    {'account': 'mm123', 'host': 'mrop.xyz'},
    {'account': 'mm123', 'host': 'moppt.site'},
    {'account': 'mm123', 'host': 'moppt.fun'},
    {'account': 'mm123', 'host': 'diykk.xyz'},
    {'account': 'mm123', 'host': 'mrop.fun'},
    {'account': 'mm123', 'host': 'diycc.xyz'},
    {'account': 'mm123', 'host': 'ytkk.site'},
    {'account': 'mm123', 'host': 'diykk.site'},
    {'account': 'mm123', 'host': 'lpqa.online'},
    {'account': 'mm123', 'host': 'moppt.xyz'},
    {'account': 'mm123', 'host': 'psdiy.online'},
    {'account': 'mm123', 'host': 'diycc.site'},
    {'account': 'mm123', 'host': 'demcc.xyz'},
    {'account': 'mm123', 'host': 'demcc.online'},
    {'account': 'mm123', 'host': 'ytkk.online'},
    {'account': 'mm123', 'host': 'psdiy.fun'},
    {'account': 'mm123', 'host': 'psdiy.xyz'},
    {'account': 'mm123', 'host': 'fome.xyz'},
    {'account': 'mm123', 'host': 'demdem.xyz'},
    {'account': 'mm123', 'host': 'namediy.xyz'},
    {'account': 'mm123', 'host': 'dirr.xyz'},
    {'account': 'mm123', 'host': 'namediy.online'},
    {'account': 'mm123', 'host': 'diycc.online'},
    {'account': 'mm123', 'host': 'motuoche.xyz'},
    {'account': 'mm123', 'host': 'namediy.site'},
    {'account': 'mm123', 'host': 'motuoche.xyz'},
    {'account': 'mm123', 'host': 'gitme.online'},
    {'account': 'mm123', 'host': 'gityou.xyz'},
    {'account': 'mm123', 'host': 'ytkk.fun'},
    {'account': 'mm123', 'host': 'demdem.online'},
    {'account': 'mm123', 'host': 'demcc.site'},
    {'account': 'mm123', 'host': 'gitme.site'},
    {'account': 'mm123', 'host': 'waibao.fun'},
    {'account': 'mm123', 'host': 'lscpu.xyz'},
    {'account': 'mm123', 'host': 'dogtop.xyz'},
    {'account': 'mm123', 'host': 'demdem.site'},
    {'account': 'mm123', 'host': 'gityou.online'},
    {'account': 'mm123', 'host': 'dirr.site'},
    {'account': 'mm123', 'host': 'dirr.site'},
    {'account': 'mm123', 'host': 'diss.site'},
    {'account': 'mm123', 'host': 'demdem.site'},
    {'account': 'mm123', 'host': 'gityou.online'},
    {'account': 'mm123', 'host': 'dakiss.xyz'},
    {'account': 'mm123', 'host': 'diyhr.xyz'},
    {'account': 'mm123', 'host': 'motuoche.online'},
    {'account': 'mm123', 'host': 'diylink.xyz'},
    {'account': 'mm123', 'host': 'lscpu.online'},
    {'account': 'mm123', 'host': 'mopo.xyz'},
    {'account': 'mm123', 'host': 'dogtop.online'},
    # testmail
    {'account': 'testmail', 'host': 'diyfor.cn'},
    {'account': 'testmail', 'host': 'ddrk.online'},
    {'account': 'testmail', 'host': 'mastat.xyz'},
    {'account': 'testmail', 'host': 'motoc.club'},
    {'account': 'testmail', 'host': 'ddrt.online'},
    {'account': 'testmail', 'host': 'lspo.club'},
    {'account': 'testmail', 'host': 'askt.club'},
    {'account': 'testmail', 'host': 'wayls.club'},
    {'account': 'testmail', 'host': 'mastat.online'},
    {'account': 'testmail', 'host': 'abckk.club'},
    {'account': 'testmail', 'host': 'fobeads.club'},
    {'account': 'testmail', 'host': 'wekk.club'},
    {'account': 'testmail', 'host': 'wpsll.club'},
    {'account': 'testmail', 'host': 'skwe.club'},
    {'account': 'testmail', 'host': 'lscpu.club'},
    {'account': 'testmail', 'host': 'toppk.club'},
    {'account': 'testmail', 'host': 'lscpu.club'},
    {'account': 'testmail', 'host': 'frre.club'},
    {'account': 'testmail', 'host': 'ittop.club'},
    {'account': 'testmail', 'host': 'pktop.club'},
    {'account': 'testmail', 'host': 'dakiss.club'},
    {'account': 'testmail', 'host': 'absc.club'},
    {'account': 'testmail', 'host': 'namecc.club'},
    {'account': 'testmail', 'host': 'abckk.top'},
    {'account': 'testmail', 'host': 'gityou.club'},
    {'account': 'testmail', 'host': 'fome.club'},
    {'account': 'testmail', 'host': 'gitme.club'},
    {'account': 'testmail', 'host': 'demdem.club'},
    {'account': 'testmail', 'host': 'diyhr.top	'},
    {'account': 'testmail', 'host': 'motoc.top'},
    {'account': 'testmail', 'host': 'fobeads.top'},
    {'account': 'testmail', 'host': 'demcc.club'},
    {'account': 'testmail', 'host': 'frre.top'},
    {'account': 'testmail', 'host': 'diylink.top'},
    {'account': 'testmail', 'host': 'diycc.club'},
    {'account': 'testmail', 'host': 'wpsll.top'},
    {'account': 'testmail', 'host': 'wayls.top'},
    {'account': 'testmail', 'host': 'namebook.top'},
    {'account': 'testmail', 'host': 'dakiss.top'},
    {'account': 'testmail', 'host': 'lpqa.club'},
    {'account': 'testmail', 'host': 'lscpu.top'},
    {'account': 'testmail', 'host': 'mastat.club'},
    {'account': 'testmail', 'host': 'skwe.top'},
    {'account': 'testmail', 'host': 'pktop.top'},
    {'account': 'testmail', 'host': 'sdjks.club'},
    {'account': 'testmail', 'host': 'lspo.top'},
    {'account': 'testmail', 'host': 'namediy.top'},
    {'account': 'testmail', 'host': 'psdiy.club'},
    {'account': 'testmail', 'host': 'diycc.top'},
    {'account': 'testmail', 'host': 'dogtop.top'},
    {'account': 'testmail', 'host': 'namediy.club'},
    {'account': 'testmail', 'host': 'dirr.top'},
    {'account': 'testmail', 'host': 'diykk.top'},
    {'account': 'testmail', 'host': 'gityou.top'},
    {'account': 'testmail', 'host': 'demdem.top'},
    {'account': 'testmail', 'host': 'gitme.top'},
    {'account': 'testmail', 'host': 'diykk.club'},
    {'account': 'testmail', 'host': 'psdiy.top'},
    {'account': 'testmail', 'host': 'kkide.top'},
    {'account': 'testmail', 'host': 'sdjks.top'},
    {'account': 'testmail', 'host': 'mrop.top'},
    {'account': 'testmail', 'host': 'namecc.top'},
    {'account': 'testmail', 'host': 'moopp.club'},
    {'account': 'testmail', 'host': 'moppt.top'},
    {'account': 'testmail', 'host': 'moopp.top'},
    {'account': 'testmail', 'host': 'lpqa.top'},
    {'account': 'testmail', 'host': 'mastat.top'},
]

def get_random_agent_list(device_type='smartphone'):
    # return user_agent_list[random.randint(0, len(user_agent_list)-1)]
    return generate_user_agent(device_type=device_type)


def send_rtx_msg(receivers, msg):

    # post_data = "sender=系统机器人&receivers=%s&msg=%s" % (receivers, msg)

    # try:
    #     c = pycurl.Curl()
    #     c.setopt(c.URL, 'http://rtx.fbeads.cn:8012/sendInfo.php')
    #     c.setopt(c.POSTFIELDS, post_data.encode("utf8"))
    #     c.perform()
    # except:
    #     print("rtx 消息发送失败")
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    requests.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def cur_get(url, retry_time=5):
    r = get(requests.session(), url)
    return r.text


def file_get_contents(file, default=None):
    if os.path.isfile(file):
        f = open(file, encoding="utf-8")
        txt = f.read()
        f.close()
    else:
        txt = default
    return txt


def file_put_contents(file, txt):
    f = open(file, mode="wt", encoding="utf-8")
    f.write(str(txt))
    f.close()


def lock_file_by_process(process_id, asin, shop_name):
    lock_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    lock_dir += "/data/lock/"
    if not os.path.isdir(lock_dir):
        os.makedirs(lock_dir)

    lock_file = lock_dir + get_task_key(asin, shop_name) + ".lock"

    if os.path.isfile(lock_file):
        if asin == 'cookies_queue_lock':
            return "0"
        else:
            if file_get_contents(lock_file) == str(process_id):
                return "1"
            else:
                return "0"

        # return "0"
    else:
        file_put_contents(lock_file, process_id)
        return "1"


def get_lock(process_id, asin, shop_name):
    # lock_url = "https://www.suitshe.com/api/lock.php?act=lock&id=%s&name=%s%s" % (
    #     process_id, asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')))
    # print(lock_url)
    while lock_file_by_process(process_id, asin, shop_name) != "1":
        time.sleep(0.1)


def get_ip(s=None):
    return "None"
    # return get_ip2()
    retry_time = 0
    ip = None
    while retry_time < 5:
        retry_time += 1
        try:
            if s:
                rep = s.get('http://www.suitshe.com/api/ip.php')
            else:
                rep = requests.get('http://www.suitshe.com/api/ip.php')
            ip = rep.text
            break
        except:
            time.sleep(1)
            pass
    return ip


def get_ip2(s=None):
    retry_time = 0
    ip = None
    while retry_time < 5:
        retry_time += 1
        try:
            if s:
                rep = s.get('https://ip.haschek.at/')
            else:
                rep = requests.get('https://ip.haschek.at/')
            ip = rep.text
            break
        except:
            time.sleep(1)
            pass

    return ip


def get_abuyun_proxy():
    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "HDF062RN4528959D"
    proxyPass = "D584EBAEFA169CA4"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    return proxies


def un_lock(asin, shop_name):
    lock_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    lock_dir += "/data/lock/"
    lock_file = lock_dir + get_task_key(asin, shop_name) + ".lock"
    if os.path.isfile(lock_file):
        os.remove(lock_file)


def task_done(asin, shop_name, marketplace_id=1, auto_status=1, auto_error="",inventory_type=0,had_send_email=2,email_number=0,url=None):
    if url:
        un_lock_url = url % (asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, auto_status, auto_error,inventory_type,had_send_email,email_number)
    else:
        un_lock_url = config.task_done_url % (asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, auto_status, auto_error,inventory_type,had_send_email,email_number)
    # print(un_lock_url)
    cur_get(un_lock_url)


def task_power_status(status):
    un_lock_url = config.power_status_url % (json.dumps(status), )
    print(un_lock_url)
    return cur_get(un_lock_url)


def task_watch_done(asin, shop_name, marketplace_id=1, in_selling=2,url=None):
    """
    in_selling:
    2 :已下架
    1 :销售中
    """
    if url:
        un_lock_url = url % (
            asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, in_selling)
    else:
        un_lock_url = config.task_watch_url % (
            asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, in_selling)
    # print(un_lock_url)
    cur_get(un_lock_url)


def task_watch_log(asin, shop_name, marketplace_id, in_selling,url=None):
    """
    in_selling:
    2 :已下架
    1 :销售中
    """
    if url:
        un_lock_url = url % (
            asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, in_selling)
    else:
        un_lock_url = config.task_watch_log_url % (
            asin, urllib.parse.quote(shop_name.encode('utf-8', 'replace')), marketplace_id, in_selling)
    # print(un_lock_url)
    cur_get(un_lock_url)


def update_task(task_url, data_dir):
    print(task_url)
    res = cur_get(task_url)
    # print(res)
    result = None
    task_cache_file = data_dir + "/data/task_list.json"
    task_cache_file_watch = data_dir + "/data/task_list_watch.json"

    task_dir = os.path.dirname(task_cache_file)
    task_dir_watch = os.path.dirname(task_cache_file_watch)
    if not os.path.isdir(task_dir):
        os.makedirs(task_dir)
    if not os.path.isdir(task_dir_watch):
        os.makedirs(task_dir_watch)

    try:
        result = json.loads(res)
    except:
        pass

    if result:
        #############任务缓存文件累加############
        json_data_task = format_task(result)
        resultTask = []

        if os.path.isfile(task_cache_file):
            with open(task_cache_file, 'r', encoding="utf-8") as f:
                resultTask = json.load(f)

        # 循环原有的数据 对比旧数据来置空

        for val_res in range(len(resultTask)):
            if resultTask[val_res] not in json_data_task:
                resultTask[val_res] = ''
        for val_json in range(len(json_data_task)):
            if json_data_task[val_json] not in resultTask:
                is_set = False
                for val_res in range(len(resultTask)):
                    if resultTask[val_res] == '':
                        resultTask[val_res] = json_data_task[val_json]
                        is_set = True
                        break
                if not is_set:
                    resultTask += [json_data_task[val_json]]
        #############任务缓存文件累加############
        save_json(task_cache_file, resultTask)
        save_json(task_cache_file_watch, format_task_watch(result))

    else:
        if os.path.isfile(task_cache_file):
            os.remove(task_cache_file)


def format_task(task_list):
    new_task_list = []
    for task in task_list:
        if "*" not in task["sku"]:
            task["process_num"] = 1
            new_task_list.append(task)
        else:
            cols = task["sku"].split("*")
            asin = cols[0]
            multi = int(cols[1])
            for i in range(multi):
                new_task = dict(task)
                new_task["sku"] = asin + "_" + str(i)
                new_task["processnum"] = multi
                new_task_list.append(new_task)

    print(new_task_list)
    return new_task_list

def format_task_watch(task_list):
    new_task_list = []
    for task in task_list:
        if "*" not in task["sku"]:
            new_task_list.append(task)
        else:
            cols = task["sku"].split("*")
            asin = cols[0]
            multi = int(cols[1])
            for i in range(multi):
                new_task = dict(task)
                new_task["sku"] = asin + "_" + str(i)
                new_task_list.append(new_task)
                break

    print(new_task_list)
    return new_task_list


def get_task_list(data_dir):
    max_task = 1000
    task_list = load_json(data_dir + "/data/task_list.json")
    if task_list and len(task_list) > max_task:
        task_list = task_list[0:max_task - 1]
    return task_list

def get_task_list_watch(data_dir):
    max_task = 300
    task_list = load_json(data_dir + "/data/task_list_watch.json")
    if task_list and len(task_list) > max_task:
        task_list = task_list[0:max_task - 1]
    return task_list

def get_task_list_watch_off(data_dir):
    max_task = 300
    task_list = load_json(data_dir + "/data/task_list_watch_off.json")
    if task_list and len(task_list) > max_task:
        task_list = task_list[0:max_task - 1]
    return task_list


def get_task_key(asin, shop_name):
    return asin + "_" + re.sub(r"[^\w\d]", "", shop_name)


def save_object(filename, _dict):
    if os.path.isfile(filename):
        os.remove(filename)

    output = open(filename, 'wb')
    pickle.dump(_dict, output)


def load_object(filename, default=None):
    if not os.path.isfile(filename):
        return default
    pkl_file = open(filename, 'rb')
    obj = pickle.load(pkl_file)
    return obj


def get(session, url, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    while re_time < retry:
        re_time += 1
        try:
            res = session.get(url, *args, **kwargs)
            res.raise_for_status()
            break
        except Exception as e:
            print("网络错误,正在重试 [%s] 次." % re_time)
            time.sleep(1.5)
    return res


def update_proxy_ip(proxy_ip_cache_file):
    res = requests.get("http://vip22.daxiangdaili.com/ip/?tid=555376137403150&num=1&format=json&protocol=https&filter=on&delay=3&show_area=true&show_operator=true&longlife=5&operator=1")
    print(res.text)
    proxy_ip_list = json.loads(res.text)
    save_json(proxy_ip_cache_file, proxy_ip_list)


def post(session, url, post_data, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15
    while re_time < retry:
        re_time += 1
        try:
            res = session.post(url, post_data, *args, **kwargs)
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            # change_local_ip_pool()
            time.sleep(1.5)
    return res


def save_file(name, text, sub_dir=""):
    base_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    _dir = base_dir + '/html/' + sub_dir
    if not os.path.isdir(_dir):
        os.makedirs(_dir)
    with open(_dir + '/' + name, 'wt', encoding="utf-8") as f:
        f.write(text)

def get_file(name, sub_dir=""):
    base_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    _dir = base_dir + '/html/' + sub_dir
    if not os.path.isdir(_dir):
        return None
    if not os.path.isfile(_dir + '/' + name):
        return None
    with open(_dir + '/' + name, 'rt', encoding="utf-8") as f:
        return f.read()


def check_order_history(order_history):
    """
    检查下单历史数据
    :param order_history:历史数据
    :return: 0 正常，1 限购产品， 2 其它情况
    """
    if len(order_history) >= 10 and "-1" not in order_history[-10:]:
        # 取最后10个
        order_history = order_history[-10:]
        if max(order_history) == min(order_history):
            return 1
        else:
            return 2
    else:
        return 0


def save_html_cache_file(name, text, country):
    _dir = os.path.dirname(os.path.dirname(__file__)) + "/" + country + '/data/html_cache/'
    if not os.path.isdir(_dir):
        os.makedirs(_dir)
    with open(_dir + name, 'wt', encoding="utf-8") as f:
        f.write(text)


def read_html_cache_file(name, country, cache_time=60 * 60):
    """默认缓存 1 小时"""
    _dir = os.path.dirname(os.path.dirname(__file__)) + "/" + country + '/data/html_cache/'
    cache_file = _dir + name
    if not os.path.isfile(cache_file):
        return False

    if time.time() - os.path.getctime(cache_file) >= cache_time:
        # print(cache_file, " 缓存文件过期")
        os.remove(cache_file)
        return False

    # print(cache_file, " 读取缓存文件")
    with open(cache_file, 'rt', encoding="utf-8") as f:
        return f.read()


def init_logger(log_name=None, std_level=logging.INFO, file_level=logging.INFO, logger=logging.getLogger()):
    log_dir, name = os.path.split(os.path.abspath(sys.argv[0]))
    if log_name:
        name = log_name

    today = datetime.date.today().strftime('%Y%m%d')
    log_filename = log_dir + '/log/' + today + "/" + name.replace(".py", "") + '.log'

    if not os.path.isdir(os.path.dirname(log_filename)):
        os.makedirs(os.path.dirname(log_filename))

    file_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                        mode='a',
                                                        maxBytes=10240000,
                                                        backupCount=100,
                                                        encoding="utf8"
                                                        )

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    stdout_handler.setLevel(std_level)
    logger.addHandler(stdout_handler)
    logger.setLevel(file_level)
    return logger


def ping(host):
    if os.name == 'posix':
        cmd = "ping -c 1 " + host
    else:
        cmd = "ping -n 1 " + host

    if os.system(cmd) == 0:
        return True
    else:
        return False


def log(url, marketplace_id, name, asin, shop_name, record):
    pass
    # shop_name = urllib.parse.quote(shop_name.encode('utf-8', 'replace'))
    # record = urllib.parse.quote(record.encode('utf-8', 'replace'))
    # log_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # requests.get(url % (marketplace_id, name, asin, shop_name, log_time, record))


def img_to_file(s, url, headers=None, proxies=None):

    response = get(s, url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        name = urlparse(url).path.replace("/", "")
        prefix = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        file_path = os.path.dirname(__file__) + "/img/" + prefix + "_" + name
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.exists(file_path):
            with open(file_path, 'wb')as f:
                f.write(response.content)
            print(file_path + " has saved.")
        else:
            print('Already Downloaded', file_path)

        return file_path
    else:
        return False


def img_to_string(path):

    if not os.path.exists(path):
        return False

    image = Image.open(path)

    image = image.convert('L')
    threshold = 127
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    image = image.point(table, '1')
    # image.show()
    return pytesseract.image_to_string(image)


def print_cookie(cookies):
    for ck in cookies:
        print(ck.name, ":", ck.value)


def cookie2dict(cookies):
    obj = {}
    for ck in cookies:
        obj[ck.name] = ck.value
    return obj


def get_input_value(name, html):
    try:
        input_r = re.compile(r'name="%s" value="([^"]*)"' % name)
        return input_r.findall(html)[0]
    except:
        return ''


def get_input_value2(name, html):
    input_r = re.compile(r'name=\'%s\' value=\'([^"]*)\'' % name)
    return input_r.findall(html)[0]


def get_data_attr_value(name, html):
    input_r = re.compile(r'%s="([^"]*)"' % name)
    return input_r.findall(html)[0]


def save_json(filename, json_data):
    if os.path.isfile(filename):
        os.remove(filename)

    if not os.path.isdir(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    f = open(filename, 'wt', encoding="utf-8")
    json.dump(json_data, f)
    f.close()


def load_json(filename, default=None):
    if not os.path.isfile(filename):
        return default
    try:
        f = open(filename, "rt", encoding="utf-8")
        _dict = json.loads(f.read())
        f.close()
    except:
        return default
    return _dict


def load_json_cache_file(filename, default=None, cache_time=60 * 60):
    """默认缓存 1 小时"""
    if not os.path.isfile(filename):
        return default

    if time.time() - os.path.getctime(filename) >= cache_time:
        # print(cache_file, " 缓存文件过期")
        os.remove(filename)
        return default

    f = open(filename, "rt", encoding="utf-8")
    _dict = json.loads(f.read())
    f.close()
    return _dict



def change_ip():
    global helper
    if not helper:
        helper = BrowserHelper()

    helper.browser.visit("http://192.168.6.2")
    if "login.cgi" in helper.browser.html:
        # 飞鱼星登陆
        helper.browser.find_by_id("username").fill("admin")
        helper.browser.find_by_id("password").fill("admin")
        helper.click_by_id("remembering")
        helper.click_by_id("OKBTN")

    helper.browser.visit("http://192.168.6.2/interface_status.cgi")
    # 断开连接
    time.sleep(2)
    helper.browser.find_by_name("PWAN1D_OKBTN").first.click()
    alert = helper.browser.get_alert()
    print(alert.text)
    alert.accept()
    # 重新连接
    helper.browser.find_by_name("PWAN1L_OKBTN").first.click()
    while True:
        time.sleep(3)
        helper.browser.find_by_name("OKBTN1").first.click()
        if "IP地址" in helper.browser.html:
            print("切换成功.")
            return


# 切换ip函数封装 开始
# _default_create_socket = socket.create_connection
# _urllib3_create_socket = urllib3.connection.connection.create_connection
#
#
# def default_create_connection(*args, **kwargs):
#     global SOURCE_ADDRESS
#     try:
#         del kwargs["socket_options"]
#     except:
#         pass
#     in_args = False
#     if len(args) >= 3:
#         args = list(args)
#         args[2] = SOURCE_ADDRESS
#         args = tuple(args)
#         in_args = True
#     if not in_args:
#         kwargs["source_address"] = SOURCE_ADDRESS
#     return _default_create_socket(*args, **kwargs)
#
#
# def urllib3_create_connection(*args, **kwargs):
#     global SOURCE_ADDRESS
#     in_args = False
#     if len(args) >= 3:
#         args = list(args)
#         args[2] = SOURCE_ADDRESS
#         in_args = True
#         args = tuple(args)
#     if not in_args:
#         kwargs["source_address"] = SOURCE_ADDRESS
#     return _urllib3_create_socket(*args, **kwargs)
#
#
# socket.create_connection = default_create_connection
# urllib3.connection.connection.create_connection = default_create_connection
#
#
# def change_local_ip(ip):
#     global SOURCE_ADDRESS
#     SOURCE_ADDRESS = (ip, 0)
#
#
# # 切换ip函数封装 结束
#
# SOURCE_ADDRESS = (config.ip_place_order, 0)


def init_local_ip_pool():
    """轮流切换ip池中ip"""
    # ip_pool = load_json(os.path.dirname(__file__) + "/ip_pool.json")
    # if not ip_pool:
    #     print("ip_pool is empty .")
    #     exit()
    # global SOURCE_ADDRESS
    # index_cache_file = os.path.dirname(__file__) + "/last_ip_pool_index.txt"
    # last_ip_pool_index = int(file_get_contents(index_cache_file, "-1"))
    # SOURCE_ADDRESS = (ip_pool[last_ip_pool_index], 0)
    # print(SOURCE_ADDRESS)


def change_local_ip_pool():
    """轮流切换ip池中ip"""
    # ip_pool = load_json(os.path.dirname(__file__) + "/ip_pool.json")
    # if not ip_pool:
    #     print("ip_pool is empty .")
    #     exit()
    # global SOURCE_ADDRESS
    # index_cache_file = os.path.dirname(__file__) + "/last_ip_pool_index.txt"
    # last_ip_pool_index = int(file_get_contents(index_cache_file, "-1"))
    #
    # # 最多5秒切换一次
    # if os.path.isfile(index_cache_file) and time.time() - os.path.getmtime(index_cache_file) >= 5:
    #     last_ip_pool_index += 1
    #     last_ip_pool_index = last_ip_pool_index % len(ip_pool)
    #
    # file_put_contents(index_cache_file, str(last_ip_pool_index))
    # SOURCE_ADDRESS = (ip_pool[last_ip_pool_index], 0)


def get_5u_proxy():

    api = "http://api.ip.data5u.com/dynamic/get.html?order=c37271bdcee46abcecda4550c4c7a881&json=1&sep=3"

    # {"data":[{"ip":"222.94.144.15","port":11268,"ttl":10774}],"msg":"ok","success":true}
    r = requests.get(api)
    try:
        proxy = json.loads(r.text)["data"][0]
    except:
        traceback.print_exc()
        return False
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxy["ip"],
        "port": proxy["port"],
    }

    proxies = {
        'http': proxyMeta,
        'https': proxyMeta
    }
    return proxies


def get_proxym_proxy():
    proxyMeta = "http://%(user)s:@%(host)s:%(port)s" % {
        "host": "go.proxym.io",
        "port": 3000,
        "user": 8744117284990962,
    }

    proxies = {
        'http': proxyMeta,
        'https': proxyMeta
    }
    return proxies

def get_rack_proxy():
    proxyMeta = "http://%(user)s:%(passwd)s@%(dns)s" % {
        "user": 'yywproxy',
        "passwd": '3836df-210602-f4c641-f8d5b6-75f794',
        "dns": 'megaproxy.rotating.proxyrack.net:222',
    }
    proxies = {
        'http': proxyMeta,
        'https': proxyMeta
    }
    return proxies

def get_oxylabs_proxy(_country,_city,_session):
# def get_oxylabs_proxy(_country,_session):
    #端口10000随机
    #端口10001 - 19999 美国端口
    username = 'rdby111'
    password = '4G5wTzP5rj'
    # password = 'Gets.com@123'
    country = _country
    session = _session
    port = 10000
    if _country == 'gb' or _country == 'it':
        port = 20000
    if _country == 'de' or _country == 'ca':
        port = 30000
    if _country == 'fr' or _country == 'jp' or country == 'au' or country == 'ru':
        port = 40000
    if _city:
        city = _city.replace(' ', '_')
        entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
                 (username, country,city,session, password,country,port))
    else:
        entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
             (username, country,session, password,country,port))
    proxies = {
        'http': entry,
        'https': entry,
    }
    return proxies

def qs(url):
    query = urllib.parse.urlparse(url).query
    return dict([(k, v[0]) for k, v in urllib.parse.parse_qs(query).items()])

def send_mail(order_id,seller_id,marketplace_id,s,headers,mail_content):
    isPost = False
    try:
        send_mail_url = marketplace[str(marketplace_id)]+'ss/help/contact/writeMessage?writeButton=%E6%8F%90%E4%BA%A4&subject=27&orderID='+order_id+'&sellerID='+seller_id+'&asin=&marketplaceID=&language=en_US'
        html = get(s, send_mail_url, headers=headers, timeout=5).text
        draftMessageIdR = re.compile(r'<input type="hidden" name="draftMessageId" value="([^"]*)"')
        draftDateR = re.compile(r'<input type="hidden" name="draftDate" value="([^"]*)"')
        subjectR = re.compile(r'<input type="hidden" name="subject" value="([^"]*)"')
        asinR = re.compile(r'<input type="hidden" name="asin" value="([^"]*)"')
        languageR = re.compile(r'<input type="hidden" name="language" value="([^"]*)"')
        # 随机获取发送邮件模板
        md5 = make_file_id(str(time.time()))
        sendContent = random.choice(sendMessModel)+'\r\n'+md5+'\r\n'+mail_content
        data = {
            'comment': sendContent,
            'draftMessageId': draftMessageIdR.findall(html)[0],
            'draftDate': draftDateR.findall(html)[0],
            'subject': subjectR.findall(html)[0],
            'orderId': order_id,
            'asin': '',
            'language': languageR.findall(html)[0]
        }
        postMessUrl = re.findall(r'form id="sendEmailForm" name="sendEmailForm" method="post" action="([^"]*)"', html)[0]
        try:
            req = s.post(marketplace[str(marketplace_id)] + postMessUrl, data=data, headers=headers, timeout=10)
            req.raise_for_status()
            html = req.text
            try:
                html.index('a-alert-success')
                isPost = True
            except:
                pass
        except:
                pass
    except:
        pass
    return isPost

def make_file_id(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf8'))
    return m1.hexdigest()

def get_loc_ip2(ifname):
    import fcntl, struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack(b'256s', ifname[:15]))[20:24])

def get_loc_ip():
    ip_address = "0.0.0.0"
    sysstr = platform.system()
    if sysstr == "Windows":
        ip_address = socket.gethostbyname(socket.gethostname())
    elif sysstr == "Linux":
        ip_address = get_loc_ip2(b'eth1')
    return ip_address

def findSubStr(substr, str, i):
    count = 0
    while i > 0:                   #循环来查找
        index = str.find(substr)
        if index == -1:
            return -1
        else:
            str = str[index+1:]   #第一次出现该字符串后后面的字符
            i -= 1
            count = count + index + 1   #位置数总加起来
    return count - 1

def reconnect():
  name="宽带连接"
  username="zonevps"
  password="zonevps"

  #断开链接
  cmdstr = "rasdial %s /disconnect" % name
  os.system(cmdstr)
  time.sleep(5)

  #重新链接
  cmd_str="rasdial %s %s %s" %(name,username,password)
  res=os.system(cmd_str)
  if res==0:
    print("connect successful")
  else:
    reconnect()
  time.sleep(5)

#_user 邮箱
#_password 邮箱密码
#_url message链接 有时候直接在message上能找到验证码
#helper 浏览器对象
#taskid 任务id
#step 验证在哪个时候 1：购物车
def sign_in_password(_user,_password,_url, helper, taskid=None, step=None):
    # print(helper.browser.find_by_id('ap-account-switcher-container'))
    #如果出现换账号页面 则判断为账号被封 任务取消
    if helper.browser.find_by_id('ap-account-switcher-container'):
        dic = {}
        dic[taskid] = {}
        dic[taskid]["task_id"] = taskid
        dic[taskid]["status"] = 10
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyTaskOrderStatus",
                  "sec": "20171212getscn"}
        print(url)
        print(dic)
        response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
        helper.browser.quit()
        exit()
    #出現忘記密碼則為賬號被封
    if helper.browser.find_by_name('appAction') and helper.browser.find_by_name('appAction')._element.get_attribute('value') and  helper.browser.find_by_name('appAction')._element.get_attribute('value')== 'FORGOTPWD':
        dic = {}
        dic[taskid] = {}
        dic[taskid]["task_id"] = taskid
        dic[taskid]["status"] = 10
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyTaskOrderStatus",
                  "sec": "20171212getscn"}
        response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
        helper.browser.quit()
        exit()
    #如果出现图片验证码 则判断为 登录过多 需要跳过该账号 等待一段时间后在处理该账号所对应的任务
    if helper.browser.find_by_id('auth-captcha-image-container'):
        dic = {}
        dic[taskid] = {}
        dic[taskid]["task_id"] = taskid
        dic[taskid]["status"] = 101
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyTaskOrderStatus",
                  "sec": "20171212getscn"}
        response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
        helper.browser.quit()
        exit()
    sendPasswdTime = 1 #输入密码次数 超过5次则判断账号未被封处理
    while helper.browser.find_by_id("ap_password"):
        if helper.browser.find_by_id('auth-captcha-image-container'):
            dic = {}
            dic[taskid] = {}
            dic[taskid]["task_id"] = taskid
            dic[taskid]["status"] = 101
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyTaskOrderStatus",
                      "sec": "20171212getscn"}
            response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
            helper.browser.quit()
            exit()
        #出現忘記密碼則為賬號被封
        if helper.browser.find_by_name('appAction') and helper.browser.find_by_name('appAction')._element.get_attribute('value') and helper.browser.find_by_name('appAction')._element.get_attribute('value') == 'FORGOTPWD':
            dic = {}
            dic[taskid] = {}
            dic[taskid]["task_id"] = taskid
            dic[taskid]["status"] = 10
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyTaskOrderStatus",
                      "sec": "20171212getscn"}
            response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
            helper.browser.quit()
            exit()

        #处理新出现的填写手机页面 跳过即可
        if helper.browser.find_by_id('auth-account-fixup-phone-form'):
            helper.click_by_id("ap-account-fixup-phone-skip-link")
        # 手机验证弹窗
        if helper.browser.find_by_id('ap-account-fixup-phone-skip-link'):
            helper.browser.find_by_id('ap-account-fixup-phone-skip-link').click()

        if sendPasswdTime >= 5:
            dic = {}
            dic[taskid] = {}
            dic[taskid]["task_id"] = taskid
            dic[taskid]["status"] = 10
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyTaskOrderStatus",
                      "sec": "20171212getscn"}
            response = post(requests.session(), url, params=params, post_data=json.dumps(dic))
            helper.browser.quit()
            exit()
        # 需要邮箱验证
        helper.browser.find_by_id("ap_password").fill(_password)
        if helper.browser.find_by_name("rememberMe"):
            helper.browser.find_by_name("rememberMe").click()
        helper.click_by_id("signInSubmit")
        time.sleep(3)
        # 获取邮箱ont-time password
        # 邮箱处理
        if helper.browser.find_by_id("ap_password"):
            cvf = ''
            if 'outlook.com' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://third.gets.com/api/index.php?act=getVerifyCode&sec=20171212getscn&email=%s&account=sd@3288tongxing.com' % _user)
            elif 'diyfor.cn' in _user or 'namefor.cn' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://third.gets.com/api/index.php?act=getVerifyCode&sec=20171212getscn&email=%s&account=testmail' % _user)
            elif '3288tongxing.com' in _user or 'beads.xin' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://134.175.243.164/mailbox/index.php?m=api&do=getVerifyCode&email=%s&account=opq123' % _user)
            else:
                cvf = requests.get('http://134.175.243.164/mailbox/index.php?m=api&do=getVerifyCode&email=%s&account=opq123' % _user)

            if cvf:
                if cvf.text:
                    cvf = json.loads(cvf.text)
                    if 'mail_body' in cvf['message']:
                        body = cvf['message']['mail_body']
                        form_R = re.compile('(\d{6})')
                        list_form = form_R.findall(body)
                        helper.browser.find_by_id("ap_password").fill(list_form[0])
                        helper.click_by_id("signInSubmit")
            else:
                js = 'window.open("'+_url+'");'
                helper.browser.execute_script(js)
                helper.browser.driver.switch_to.window(helper.browser.driver.window_handles[-1])
                # helper.browser.visit('https://www.amazon.com/gp/message')
                helper.browser.find_by_id('message-center-nav-inbox').click()
                helper.browser.find_by_css('.message-table-row-content').click()
                time.sleep(3)
                message_content = helper.browser.find_by_id('hidden-message-content').text
                form_R = re.compile('(\d{6})')
                list_form = form_R.findall(message_content)
                helper.browser.driver.close()
                helper.browser.driver.switch_to.window(helper.browser.driver.window_handles[0])
                helper.browser.find_by_id("ap_password").fill(list_form[0])
                helper.click_by_id("signInSubmit")
                time.sleep(1)
        #strp=1 为下单时候需要输入密码出现异常的兼容处理
        if step == 1 and helper.browser.find_by_text("Oops! We're sorry"):
            helper.click_by_id("nav-cart")
        if step == 1 and helper.browser.find_by_id('sc-buy-box-ptc-button'):
            helper.click_by_id("sc-buy-box-ptc-button")
        sendPasswdTime += 1



    return helper


#_user 邮箱
#_password 邮箱密码
#_url message链接 有时候直接在message上能找到验证码
# helper 浏览器对象
# account_id 账号id
# email_id 邮箱id
def sign_in_password_prime(_user,_password,_url,helper,account_id):
    # print(helper.browser.find_by_id('ap-account-switcher-container'))
    # 如果出现换账号页面 则判断为账号被封 任务取消
    if helper.browser.find_by_id('ap-account-switcher-container'):
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyAcountStatus",
                  "account_id": account_id,
                  "sec": "20171212getscn"}
        response = get(requests.session(), url, params=params)
        print(url)
        print(response.text)
        helper.browser.quit()
        exit()
    # 出現忘記密碼則為賬號被封
    if helper.browser.find_by_name('appAction') and helper.browser.find_by_name('appAction')._element.get_attribute('value') and  helper.browser.find_by_name('appAction')._element.get_attribute('value')== 'FORGOTPWD':
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyAcountStatus",
                  "account_id": account_id,
                  "sec": "20171212getscn"}
        get(requests.session(), url, params=params)
        helper.browser.quit()
        exit()
    # 如果出现图片验证码 则判断为 登录过多 需要跳过该账号 等待一段时间后在处理该账号所对应的任务
    if helper.browser.find_by_id('auth-captcha-image-container'):
        url = "http://third.gets.com/api/index.php"
        params = {"act": "modifyAcountStatus",
                  "account_id": account_id,
                  "sec": "20171212getscn"}
        # get(requests.session(), url, params=params)
        helper.browser.quit()
        exit()
    sendPasswdTime = 1 #输入密码次数 超过5次则判断账号未被封处理
    while helper.browser.find_by_id("ap_password"):
        if helper.browser.find_by_id('auth-captcha-image-container'):
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyAcountStatus",
                      "account_id": account_id,
                      "sec": "20171212getscn"}
            # get(requests.session(), url, params=params)
            helper.browser.quit()
            exit()
        # 出現忘記密碼則為賬號被封
        if helper.browser.find_by_name('appAction') and helper.browser.find_by_name('appAction')._element.get_attribute('value') and helper.browser.find_by_name('appAction')._element.get_attribute('value') == 'FORGOTPWD':
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyAcountStatus",
                      "account_id": account_id}
            get(requests.session(), url, params=params)
            helper.browser.quit()
            exit()
        if sendPasswdTime >= 5:
            url = "http://third.gets.com/api/index.php"
            params = {"act": "modifyAcountStatus",
                      "account_id": account_id,
                      "sec": "20171212getscn"}
            get(requests.session(), url, params=params)
            helper.browser.quit()
            exit()
        # 需要邮箱验证
        helper.browser.find_by_id("ap_password").fill(_password)
        if helper.browser.find_by_name("rememberMe"):
            helper.browser.find_by_name("rememberMe").click()
        helper.click_by_id("signInSubmit")
        time.sleep(3)

        # 获取邮箱ont-time password
        # 邮箱处理
        if helper.browser.find_by_id("ap_password"):
            cvf = ''
            if 'outlook.com' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://third.gets.com/api/index.php?act=getVerifyCode&sec=20171212getscn&email=%s&account=sd@3288tongxing.com' % _user)
            elif 'diyfor.cn' in _user or 'namefor.cn' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://third.gets.com/api/index.php?act=getVerifyCode&sec=20171212getscn&email=%s&account=testmail' % _user)
            elif '3288tongxing.com' in _user or 'beads.xin' in _user:
                # 通过邮箱验证
                # 先点击账号
                cvf = requests.get('http://134.175.243.164/mailbox/index.php?m=api&do=getVerifyCode&email=%s&account=opq123' % _user)
            else:
                #通过域名获取域名对应账号
                host_s = _user.split('@')[1]
                account_s = 'opq123'
                for val in mailConf:
                    if host_s in val.values():
                        account_s = val['account']
                cvf = requests.get('http://134.175.243.164/mailbox/index.php?m=api&do=getVerifyCode&email=%s&account=%s' % (_user,account_s))

            if cvf:
                if cvf.text:
                    cvf = json.loads(cvf.text)
                    if 'mail_body' in cvf['message']:
                        body = cvf['message']['mail_body']
                        form_R = re.compile('(\d{6})')
                        list_form = form_R.findall(body)
                        helper.browser.find_by_id("ap_password").fill(list_form[0])
                        helper.click_by_id("signInSubmit")
            else:
                js = 'window.open("'+_url+'");'
                helper.browser.execute_script(js)
                helper.browser.driver.switch_to.window(helper.browser.driver.window_handles[-1])
                # helper.browser.visit('https://www.amazon.com/gp/message')
                helper.browser.find_by_id('message-center-nav-inbox').click()
                helper.browser.find_by_css('.message-table-row-content').click()
                time.sleep(3)
                message_content = helper.browser.find_by_id('hidden-message-content').text
                form_R = re.compile('(\d{6})')
                list_form = form_R.findall(message_content)
                helper.browser.driver.close()
                helper.browser.driver.switch_to.window(helper.browser.driver.window_handles[0])
                helper.browser.find_by_id("ap_password").fill(list_form[0])
                helper.click_by_id("signInSubmit")
                time.sleep(1)
        sendPasswdTime += 1
    # elif helper.browser.find_by_css(".cvf-text-truncate") and '3288tongxing' in _user:
    #     # 通过邮箱验证
    #     # 先点击账号
    #     helper.click_by_css('.cvf-text-truncate')
    #     if helper.browser.find_by_id("ap_password"):
    #         # 需要邮箱验证
    #         helper.browser.find_by_id("ap_password").fill(_password)
    #         helper.click_by_id("signInSubmit")
    #         if helper.browser.find_by_id('continue'):
    #             helper.click_by_id('continue')
    #             cvf = requests.get('http://third.gets.com/api/index.php?act=getVerifyCode&sec=20171212getscn&email=%s' % _user)
    #             if cvf.text:
    #                 cvf = json.loads(cvf.text)
    #                 if 'mail_body' in cvf['message']:
    #                     body = cvf['message']['mail_body']
    #                     cvf_bodyR = re.compile(r'<p class=\\\"otp\\\">([^"]*)<\/p>')
    #                     code = cvf_bodyR.findall(body)[0]
    #                     helper.browser.find_by_name('code').fill(code)
    #                     helper.browser.find_by_id('a-autoid-0').click()
    #                     if

    return helper


# 信用卡汇率转化
def rate_change(query,end):
    """
    信用卡汇率转化
    :param query:  美元金额
    :param end:   转化国家货币的缩写
    :return:      转化后的金额
    """
    data_time = time.time()
    url = f'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query={query}美元等于多少{end}&co=&resource_id=6017&t={data_time}&cardId=6017&ie=utf8&oe=gbk&cb=op_aladdin_callback&format=json&tn=baidu&cb=jQuery110205576346160044889_1565851483354&_={data_time}'
    header = {'user-agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 5.1; Win64; x64; Trident/5.0)'}

    r = requests.get(url=url, headers= header)
    r = r.text.replace('/**/jQuery110205576346160044889_1565851483354(','').replace(');','')
    content = json.loads(r)
    return  content['data'][0]['number2']

# 做一检察代理ip和城市是否发生的操作
def proxy_check(proxies,proxy_city,proxy_ip,task_id):
    """
    做一检察代理ip和城市是否发生的操作
    :param proxies:     ip代理
    :param proxy_city: 代理 城市
    :param proxy_ip:   代理IP
    :param task_id:    任务id
    :return:
    """
    print('=' * 20)
    print(proxy_city)
    print(proxy_ip)
    url = 'http://ipinfo.io/'
    res = requests.get( url=url, proxies=proxies)
    if res:
        ip_info = json.loads(res.text)
        # 代理IP必须为日本的，且城市不为空
        print(ip_info["city"])
        # helper.logger.info(type(ip_info["city"]))
        print(ip_info['ip'])
        # helper.logger.info(type(ip_info["ip"]))
        print('-' * 20)
        print(ip_info['ip'] in proxy_ip and ip_info["city"] in proxy_city)
        print('='*20)

        if ip_info['ip'] in proxy_ip and ip_info["city"] in proxy_city:
            print('代理环境正确')

        else:
            print('代理环境错误，退出程序')
            url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
            res = requests.get( url=url.format(TASK_ID=task_id))
            print(res.text)
            if 'ok' in res.text:
                print('任务账号解绑成功')
            time.sleep(3)

            exit()
    else:
        print('代理环境错误，退出程序')
        url = 'http://third.gets.com:8080/api/index.php?sec=20171212getscn&act=taskUnbindAccount&task_id={TASK_ID}&inner_debug=1'
        res = requests.get( url=url.format(TASK_ID=task_id))
        print(res.text)
        if 'ok' in res.text:
            print('任务账号解绑成功')
        time.sleep(3)

        exit()