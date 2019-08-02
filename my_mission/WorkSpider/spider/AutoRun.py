# 设置定时任务，自动爬取任务
from datetime import datetime
import time
import os
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler

base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))


def tick():
    print('定时任务开始，现在时间为: %s' % datetime.now())
    for i in range(1):
        t = Thread()
        t.start()

        t.join()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # 间隔5秒钟执行一次 86400 24小时
    scheduler.add_job(tick, 'interval', seconds=600)
    # 这里的调度任务是独立的一个线程
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # 其他任务是独立的线程执行
        while True:
            time.sleep(2)
            # print('sleep!')
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('Exit The Job!')
