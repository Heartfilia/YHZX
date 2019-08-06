# -*- coding: gbk -*-

from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler
base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
# print(base_dir)    # C:\Users\User\Desktop\GIT\my_mission\WorkSpider\spider


def tick():
    print('Tick! The time is: %s' % datetime.now())
    command = r'python ' + base_dir + r'\ZhiLian.py'
    os.system(command)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'cron', hour=17, minute=10)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C    '))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
