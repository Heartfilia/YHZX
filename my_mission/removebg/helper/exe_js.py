#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/31 18:15
# @Author  : Lodge
js1 = '''() =>{
    Object.defineProperties(navigator,{
        webdriver:{
            get: () => false
        }
    })
}'''

js2 = '''() => {
    window.navigator.chrome = {
        runtime: {},
        // etc.
    };
}'''

js3 = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
}'''

js4 = '''() =>{
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5,6],
    });
}'''

# 下面的不用处理，调用也可以不调用
js5 = '''() => {
    alert (
        window.navigator.webdriver
    )
}'''
