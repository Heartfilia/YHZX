### 交接文档A==其它模块部分

---

---

```
==== Hr 服务器 ====
ip: 192.168.1.112
user: administrator
passwrod: Milky123!@#
```

---



##### 非hr相关模块

以下检测功能已经放服务器执行

```python
ip: 192.168.0.221
usr: root
pwd: gets.com123
dir: /root/lodge/*
```

- 独立站评分检测脚本(自动执行)

- 接口冗余文件清除脚本(手动执行)

- geo检测脚本(定时脚本)

  |脚本名字| 相关功能| 需要注意的点|
  | ------------------- | --------------- | ------------------------------------------------------------ |
  | `start_detect.py`   | 独立站评分检测  | 每周三提醒，两个功能检测，定时器，程序会用到公用的mongo数据库注意数据库崩溃 |
  | `clear_info.py`     | hr邀约  | 已经处理 |
  | `geo_post_and_get.py` | geo用量检测脚本 | 定时采用自己写的定时方法，只能整点触发，其他的信息在代码里面已经注释写好了。 |

##### hr检测后台系统

- 文件路径——文件名

  - `ZhilianDet`   >>>   `DjHr`     (首先定位到这个目录去 会看到 `manage.py`)

- 启动程序

  - `python manage.py runserver 0.0.0.0:8000`

- 注意事项

  - 这个可以直接用win终端跑，不需要开启额外的额`IDE`，减少负担。
  - 这个一定要启动，因为和智联岗位信息的检测相关。

- `django`后台账号密码

  - 主账号: `yhzx`     密码: `yhzxroot`

- 功能细分

  > `api` 接口文件路径中` ~/api/~`
  >
  > > `admin.py` 配置`admin`后台的显示模板
  > >
  > > `models.py`  主要处理数据库相关业务
  > >
  > > > 调整数据库的操作有: `python manage.py makemigrations`
  > > >
  > > > 然后还要迁移: `python manage.py migrate`
  > >
  > > `urls.py`  配置子路由的地方,里面涉及的正则功能会在`views.py`里面处理
  > >
  > > `views.py` 主要处理路由请求内容并返回数据的地方
  > >
  > > > 因为当初只有三个公司账号数据,所以只做了三个公司的数据处理,很多地方不建议修改，要不然爬虫程序那边修改的地方也挺多的。
  >
  > `DjHr` 主要的配置文件在这里面 
  >
  > > `settings.py` 配置数据库和注册应用的地方
  > >
  > > `urls.py` 配置主路由的
  >
  > `static` 静态文件
  >
  > `templates` 模板文件（因为是只用了 `admin` 后台，所以我只放了一个404页面）
  >
  > `manage.py`  项目的启动文件，启动方式如上

##### 测试功能相关

测试功能相关的内容不是那么专业，只做了一般的正常非正常流程及判断，输出为日志。

两个平台十分类似，只是部分地方的位置可能改变。

- `YYW` /`BEADS`

  - mobile

    - `homepage_test.py`：主页上商品操作，包含登录注册，选择商品，购买。
    - `personal_page_and_search.py`：个人中心页和商品搜索判断。

  - PC

    - `homepage_test.py`：主页信息检测，包含登录注册

    - `fast_login_test.py`：主页上面不登录购买商品的时候注册登录
    - `homepage_test.py`：requests包下面的是判断主页所有商品的链接及内容加载判断
    - `main_page_view.py`： 主要主要页面的商品信息是否正确问题
    - `pay_order_test.py`：主要检测下单功能
    - `personal_page.py`：主要检测个人中心的一些功能
    - `search_item_test.py`：主要检测商品搜索功能

- 启动

  - 里面有个定时模块，需要添加进定时任务里面去