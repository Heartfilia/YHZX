from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome()
options = webdriver.ChromeOptions()

# options.add_experimental_option('prefs', self.prefs)
# options.add_argument('user-agent="%s"' % self.User_Agent)
# driver.add_cookie({'name':'xxxx','value':'xxxxxxxxxxx'})
# driver.refresh()
