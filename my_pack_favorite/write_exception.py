# ��������ʹ�ã�д�����⣬ͬʱ��������(Ϊɶ����������Ϊpycharm�쳣��д�����С���ߣ�д��e�ֻ��ӡ���ң��ɴ൥��д����쳣�ļ�����)


def write_exception(e, local_def, local_class):
    # local_def = sys._getframe().f_code.co_name
    # self.local_class = self.__class__.__name__
    # write_exception(e, local_def, self.local_class)
    with open('./utils/error_log.txt', 'a', encoding='utf-8') as fl:
        t_now = time.strftime('%m-%d %H:%M:%S', time.localtime())
        fl.write(f'{t_now}:{local_class}>{local_def}::{str(e)}')