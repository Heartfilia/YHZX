import os
import time

print("开始测试")
def cmd():
    os.system("F:")
    os.system(r"cd Joom\Joom_Orders")
    os.system(r"python register_selenium.py")

if __name__ == '__main__':
    while True:
        cmd()
        time.sleep(10)