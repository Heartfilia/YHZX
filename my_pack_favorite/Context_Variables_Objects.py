# manager modoles
class MyOpen(object):
    def __init__(self,path,mode):
        # 记录要操作的文件路径和模式
        self.__path = path
        self.__mode = mode
 
    def __enter__(self):
        print('代码执行到了__enter__......')
        # 打开文件
        self.__handle = open(self.__path,self.__mode)
        # 返回打开的文件对象引用, 用来给  as 后的变量f赋值
        return self.__handle
 
    # 退出方法中，用来实现善后处理工作
    def __exit__(self, exc_type, exc_val, exc_tb):
        print('代码执行到了__exit__......')      
        self.__handle.close()
 
# a+ 打开一个文件用于读写。如果该文件已存在，文件指针将会放在文件的结尾。文件打开时会是追加模式。如果该文件不存在，创建新文件用于读写。
with MyOpen('test.txt','a+') as f:
    # 创建写入文件
    f.write("Hello Python!!!")
    print("文件写入成功")

# ====================================================== #

# __exit__方法的参数
# __exit__ 方法中有三个参数，用来接收处理异常，如果代码在运行时发生异常，异常会被保存到这里。 
# exc_type : 异常类型
# exc_val : 异常值
# exc_tb : 异常回溯追踪

# ======================================================= #
# decorator module

