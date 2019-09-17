import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome()

driver.get('https://www.baidu.com')
# time.sleep(3)
print('title0:', driver.title)
# driver.execute_script('window.open();')
# time.sleep(3)

# window = driver.window_handles
# driver.switch_to.window(driver.window_handles[len(window) - 1])
# driver.get('https://www.meituan.com')
# print('title1:', driver.title)
# time.sleep(3)
# driver.close()
# # print('title2:', driver.title)
# window = driver.window_handles
# driver.switch_to.window(driver.window_handles[len(window) - 1])

# driver.get('https://www.51job.com/')
# time.sleep(1)
# print('title3:', driver.title)

WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="u1"]/a[1]'))
)

print('now')
time.sleep(3)
driver.find_element_by_xpath('//*[@id="u1"]/a[1]').click()
# driver.quit()




