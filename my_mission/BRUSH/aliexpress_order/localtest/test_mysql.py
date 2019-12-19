from mysql_helper import Mysql_helper

mysql_helper = Mysql_helper()
item = mysql_helper.query4One()
print(type(item))
print(item)