#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 14:25
# @Author  : Lodge


JS_DISABLE_WEBDRIVER = '''() =>{
    Object.defineProperties(navigator,{
        webdriver:{
            get: () => false
        }
    })
}'''

JS2 = '''() => {
    window.navigator.chrome = {
        runtime: {},
        // etc.
    };
}'''

JS_SET_LANGUAGE_TO_EN = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
}'''

JS4 = '''() =>{
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5, 6],
    });
}'''

JS_SCROLL = "window.scrollTo(%d, %d);"
JS_LAST_SCROLL = "window.scrollTo(%d, document.body.scrollHeight);"

# 下面的不用处理，调用也可以不调用
JS_ALERT_STATUS = '''() => {
    alert (
        window.navigator.webdriver
    )
}'''

JS_CLICK_AD = '''
document.querySelector("body > div.next-overlay-wrapper.opened > div.next-overlay-inner.next-dialog-container > div > a").click()
'''

JS_CLICK_AD2 = '''
document.querySelector("body > div.ui-window.ui-window-normal.ui-window-transition.ui-newuser-layer-dialog > div > div > a").click()
'''

NEXT_PAGE = '''
document.querySelector("#root > div > div > div.main-content > div.right-menu > div > div.list-pagination > div > div.next-pagination.next-medium.next-normal > div > button.next-btn.next-medium.next-btn-normal.next-pagination-item.next-next").click()
'''
