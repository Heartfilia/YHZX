import datetime
import os
import platform


os_platfrom = platform.platform()

if os_platfrom.startswith('Darwin'):
    print('this is mac os system')
    os.system('ls')

elif os_platfrom.startswith('Window'):
    print('this is win system')
    os.system('dir')

now = datetime.datetime.now()

# sched_Timer = sched_Timer + datetime.timedelta(days=1)

# if now == sched_Timer:
#     do_task()
