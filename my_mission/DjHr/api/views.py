# from linecache import cache
# from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect
from django.template import loader
from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse
from django.http import HttpResponseRedirect
# Create your views here.


def error_page(request):
    return render(request, '404.html')


def home(request):
    pass