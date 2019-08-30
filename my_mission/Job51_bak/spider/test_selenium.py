import time

from selenium import webdriver


driver = webdriver.Chrome()

driver.get('https://www.baidu.com')
time.sleep(3)
print('title0:', driver.title)
driver.execute_script('window.open();')
time.sleep(3)

window = driver.window_handles
driver.switch_to.window(driver.window_handles[len(window) - 1])
driver.get('https://www.meituan.com')
print('title1:', driver.title)
time.sleep(3)
driver.close()
# print('title2:', driver.title)
window = driver.window_handles
driver.switch_to.window(driver.window_handles[len(window) - 1])

driver.get('https://www.51job.com/')
time.sleep(1)
print('title3:', driver.title)

driver.quit()




