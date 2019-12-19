import pymysql

class Mysql_helper(object):
    def __init__(self):
        dbparams = {
            'host':"127.0.0.1",
            "user":"root",
            "password":'123456',
            "port":3306, #此处不能是字符串，否则报错
            "database":"users",
            "charset":"utf8"
        }
        self.conn = pymysql.connect(**dbparams)
        self.cursor = self.conn.cursor()
        self._sql = None

    def process_item(self, item):
        #execute("sql语句",[参数列表或元组])
        self.cursor.execute(self.sql,(item['email'],item['password'],item['cookies'],item['headers'],item['credit_card']))
        self.conn.commit()
        return item

    def query4One(self):
        sql = "select * from userinfo where id = 26;"
        self.cursor.execute(sql)
        item = self.cursor.fetchone()
        self.cursor.close()
        return item

    @property
    def sql(self):
        if not self._sql:
            self._sql = """
            insert into userinfo(email,password,cookies,headers,credit_card) values(%s,%s,%s,%s,%s)
            """
            return self._sql
        return self._sql
