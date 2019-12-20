#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/31 17:30
# @Author  : Lodge
import asyncio
from pyppeteer import launch

from helper.exe_js import js1, js2, js3, js4, js5


async def main():
    browser = await launch({'headless': False, 'args': ['--no-sandbox']})
    page = await browser.newPage()
    await page.setUserAgent('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36')
    await page.goto('https://www.remove.bg/users/sign_up')
    await page.evaluate(js1)
    # await page.evaluate(js2)
    await page.evaluate(js3)
    await page.evaluate(js4)
    await page.evaluate(js5)

    await page.type('#user_email', '1354654684646@qq.com', {'delay': 100})
    await page.type('#user_password', '123123', {'delay': 100})
    await page.type('#user_password_confirmation', '123123', {'delay': 100})
    await page.click('#user_terms_of_service')
    await asyncio.sleep(1000)
    # await browser.close()


asyncio.get_event_loop().run_until_complete(main())

