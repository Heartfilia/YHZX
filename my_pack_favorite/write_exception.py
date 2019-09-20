# 这个配合类使用，写在类外，同时管理多个类(为啥这样做：因为pycharm异常不写清除会小黄线，写了e又会打印杂乱，干脆单独写这个异常文件算了)


def write_exception(e, local_def, local_class):
    # local_def = sys._getframe().f_code.co_name
    # self.local_class = self.__class__.__name__
    # write_exception(e, local_def, self.local_class)
    with open('./utils/error_log.txt', 'a', encoding='utf-8') as fl:
        t_now = time.strftime('%m-%d %H:%M:%S', time.localtime())
        fl.write(f'{t_now}:{local_class}>{local_def}::{str(e)}')