
import os


# confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
# if not os.path.exists(confirm_pay_dir):
#     os.mkdir(confirm_pay_dir)
# confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_'+ str(28) + '.txt'
# f = open(confirm_pay_filename,'w',encoding='utf-8')
# f.close()
# if None:
#     print('支付成功！')
#     os.remove(confirm_pay_filename)
#     print('文件已删除！')
# elif '':
#     print('支付失败')
#     os.remove(confirm_pay_filename)
#     print('文件已删除！')
confirm_pay_dir = os.path.join(os.path.dirname(__file__), 'confirm_pay_files')
confirm_pay_filename = confirm_pay_dir + '/' + 'taskid_' + str(28) + '.txt'
if os.path.exists(confirm_pay_filename):
    print('文件存在')
    os.remove(confirm_pay_filename)