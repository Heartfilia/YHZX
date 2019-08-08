# -*- coding: utf-8 -*-
"""
以下内容为插入数据库的用，仅一次使用，后面就直接通过后台管理直接处理数据了
"""

import time
import pymysql
from helper.Positions import POS
from helper.mysql_config import *

db = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
cursor = db.cursor()


def insert_opt(pos):
    sql = f'insert into keyword (keyword, pageinfo, plateform) values ("{pos.strip()}", "0", "智联")'

    try:
        cursor.execute(sql)
        time.sleep(0.3)
        db.commit()
    except Exception as e:
        print('出现错了 问题不大')


if __name__ == '__main__':
    for p in POS:
        insert_opt(p)

    cursor.close()
    db.close()
