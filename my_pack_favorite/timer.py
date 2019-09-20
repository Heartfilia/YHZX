def timer(set_time):
    """
    一个简单地定时器装置, 放入的 set_time 必须为集合, 列表, 元组。 里面的元素必须为字符串::方便设置指定的时间比如('18:21')
    被装饰的函数一定要是死循环，要不然不能循环检测了
    :param set_time: 设定的触发时间: 全称: 小时。
    :return:
    """
    
    def work_time(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now_time = time.strftime("%H:%M", time.localtime())
            if now_time in set_time:
                print()
                func(*args, **kwargs)
                print('\r程序开始了,正在休眠中...', end='')
                time.sleep(60)
            else:
                print('\r不是程序运行的时间,继续休眠中...', end='')
                time.sleep(60)

        return wrapper
    return work_time


@timer(['11:35', '11:36'])
def main():
    print('go')


# main(['08:55', '12:11', '19:01'])
while True:
    main()