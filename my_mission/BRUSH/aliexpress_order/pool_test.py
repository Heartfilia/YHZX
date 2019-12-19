import random
from multiprocessing import Pool
import time
import sys
from selenium import webdriver

def action(i):
    print('正在启动第%d个浏览器' % i)
    driver = webdriver.Chrome()
    driver.get('http://www.baidu.com')
    time.sleep(random.randint(1, 20))
    print('正在关闭第%d个浏览器' % i)
    driver.quit()
    # sys.exit(0)

if __name__ == '__main__':
    while True:
        pool = Pool(processes=4)
        for i in range(1, 4):
            pool.apply_async(func=action, args=(i, ))
        pool.close()
        pool.join()
        print('任务执行完毕！')
        time.sleep(5)
        print('sleep 5 seconds!')