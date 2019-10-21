#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/26 15:20
# @Author  : Lodge
CHROME_PORT = '19191'
RECEIVERS = ''
HANDLERS = '系统机器人'
EN_ACCOUNT = 'vera'
DOWNLOAD_USER = '2228'
ACCOUNT = ''
ACCOUNT_FROM = ''
HR_ID = 176750
HR_MOBILE = ''
SEARCH_KEYS = ['采购', '文员', '质检员']


POST_URL = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'
POST_URL_DOWN = 'http://hr.gets.com:8989/api/autoOwnerResumeDownload.php?'

POST_URL_SEARCH = 'http://hr.gets.com:8989/api/autoInsertResume.php?'
DOWN_RESUME_KEY = 'http://hr.gets.com:8989/api/autoGetKeyword.php?type=download'
JUDGE_SEND_URL = 'http://hr.gets.com:8989/api/autoGetInterview.php?type=getInterview'

CLEAR_URL_HEAD = 'http://hr.gets.com:8989/api/autoGetInterview.php?type=setInterview&resume_id='

SEND_MSG_URL = 'http://hr.91job.com/api/position/resume/interview'

PASSWORD = ''
