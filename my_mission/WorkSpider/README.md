#### 银河在线自动检测智联平台简历刷新信息
<hr>

##### 改程序每天启动一次，然后会把该有的信息发送给指定的人员
<hr>

'chromedriver.exe' is suitable for the version is '76.0.3809.87'

##### 项目启动

[如果是多账号，建议复制整个大文件夹运行一次程序]

[有一个程序跑检测职位排名靠后就可以啦，注释掉`Zhilian.py`里面的启动里面的那个线程就好了]

[启动定时模块就好了，模块会自动调用其它程序]

```vim
python date_task.py  # 这里面需要设置两个参数 hour和minute 表示这个小时分钟自动运行程序
```

<hr>

#### 项目结构

- helper
  - company.py   
  - cookie1.py========测试数据
  - js_downpage.py====js滚动屏幕操作
  - Our_company.py====我方公司信息(list)
  - Positions.py======我方需要关注的职位信息(list)

- spider
  - chromedriver.exe====chrome自动化驱动
  - cookies.json========本地cookies文件，自动更新，读取
  - date_task.py========定时任务，需要设置指定的时间，也主要运行这个程序
  - information.txt=====爬到的公司信息备份
  - Message.py==========调用系统机器人接口发送信息
  - ZhiLian.py==========主程序

- utils
  - 2019.log============日志信息
  - logger.py==========日志生成信息程序
