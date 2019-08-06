# from linecache import cache
# from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Info
from urllib.request import unquote
# Create your views here.


def error_page(request):
    return render(request, '404.html')


def home(request):
    return HttpResponse('<h1 align="center">当前服务只有后台管理系统以及接口信息</h1>')


def info_api(request, account="1", platform='z'):
    # 返回api信息用来处理提醒
    if account == '1':
        company = '广州市银河在线饰品有限公司'
    elif account == '2':
        company = '广州外宝电子商务有限公司'
    else:
        company = '广州市银河在线饰品有限公司'

    if platform == 'z':
        pf = '智联'
    elif platform == 'q':
        pf = '前程无忧'
    else:
        pf = '智联'

    Ft = Info.objects.all().filter(isRemind=True)
    fulljson = {
        'platform': pf,
        'account': company,
        'numbers': Ft.count(),
        'data': []
    }

    for i in Ft:
        dic = {
            "info": i.info,
            "isRemind": i.isRemind,
            "lateRemind": i.lateRemind
        }
        fulljson['data'].append(dic)
    return JsonResponse(fulljson)


def insert_info(request, account, platform, minf):
    if request.method == 'GET':
        return HttpResponse('非法请求')
    else:
        if account == '1':     # 默认的账户
            company = '广州市银河在线饰品有限公司'
        elif account == '2':
            company = '广州外宝电子商务有限公司'
        else:
            company = '广州市银河在线饰品有限公司'

        if platform == 'z':     # 默认这个
            pf = '智联'
        elif platform == 'q':
            pf = '前程无忧'
        else:
            pf = '智联'

        if Info.objects.get(info=minf):
            pass
        else:
            dic = {
                "info": unquote(minf),
                "account": company,
                "platform": pf
            }
            print(dic)
            # obj = Info(**dic)
            # obj.save()
            return HttpResponse('Insert Done')
