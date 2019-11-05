import os
import json

import time

from mytools.tools import load_json, save_json

# 先读取缓存文件
while True:
    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    _cache_file = cache_dir + '/' + 'new_cart_tasks.json'
    cache_task_list = load_json(_cache_file, default={"task_list": []})["task_list"]
    task_infos = {
        '1':'xxx',
        '2':'xxx',
        '3':'xxx',
        '4':'xxx',
        '5':'xxx'
    }
    task_id_str_list = []
    for task_id_str in task_infos:
        if task_id_str not in cache_task_list:
            task_id_str_list.append(task_id_str)
    # 当task_id_str_list为空时，休眠2分钟，避免频繁请求任务接口
    if len(task_id_str_list) == 0:
        print('任务列表为空，程序休眠30分钟...')
        time.sleep(30)
    else:
        print('成功获取到%d条待刷单的数据！' % len(task_id_str_list))
        print('将创建%d个线程来分别执行刷单任务!' % len(task_id_str_list))

    cache_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    _cache_file = cache_dir + '/' + 'new_cart_tasks.json'
    task_list = load_json(_cache_file, default={"task_list": []})["task_list"]

    for taskid in task_infos:
        if taskid not in task_list:
            task_list.append(taskid)
            # if not os.path.isfile(_cache_file):
            save_json(_cache_file, {"task_list": task_list})

            print('任务id已写入缓存文件，由另外的下单程序执行，本程序退出！')
        time.sleep(30)
