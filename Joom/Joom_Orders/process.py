"""
import  os
import  time
from multiprocessing import Process


# 子进程 执行代码
def run_proc(name):
    print('Run child process %s(%s)' % (name, os.getpid()))

if __name__ == '__main__':
    print('parent process %s ' % os.getpid())
    list = []
    for i in  range(3):
        p = Process(target=run_proc, args=('test', ))
        print('Process will start……')
        p.start()
        list.append(p)
        time.sleep(3)

    for i in range(len(list)):
        p.join()
        print('Process end')
"""


import psutil
# import os, time, random
# from multiprocessing  import Pool
#
# def long_time_task(name):
#     print('Run task %s(%s)' % (name, os.getpid()))
#     start = time.time()
#     time.sleep(random.random() * 3)
#     end = time.time()
#     print('Task %s run %0.2f seconds' % (name, (end - start)))
#
#
# if __name__ == '__main__':
#     print('Parent process %s' % os.getpid())
#     p = Pool()
#     for i in range(5):
#         p.apply_async(long_time_task, args=(i,))
#     print('Witing for all subprocess done……')
#     p.close()
#     p.join()
#     print('All subprocesses done')


"""




from multiprocessing import Process, Queue
import os, time, random

# 写数据进程执行的代码:
def write(q):
    for value in ['A', 'B', 'C']:
        print('Put %s to queue...' % value)
        q.put(value)
        time.sleep(random.random())

# 读数据进程执行的代码:
def read(q):
    while True:
        value = q.get(True)
        print ('Get %s from queue.' % value)

if __name__=='__main__':
    # 父进程创建Queue，并传给各个子进程：
    q = Queue()
    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))
    # 启动子进程pw，写入:
    pw.start()
    # 启动子进程pr，读取:
    pr.start()
    # 等待pw结束:
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止:
    pr.terminate()

"""
import time, threading

def loop():
    print('thread %s is running...' % threading.current_thread().name)
    n = 0
    while n < 5:
        n = n+1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        time.sleep(1)
    print('thread %s is end.' % threading.current_thread().name)

print('thread %s is running...' % threading.current_thread().name)
t = threading.Thread(target=loop, name='LoopThread')
t.start()
t.join()
print('thread %s is end.' % threading.current_thread().name)
