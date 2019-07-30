import os
def fib():
    user_info = {
        "task_id" : "256"
    }
    path = r"F:\Joom\Joom_Orders\cache"
    filername = user_info["task_id"] + ".txt"
    paths = os.path.join(path, filername)
    with open(paths,"w",encoding="utf-8")as fp:
        fp.write("订单号")
    print(paths)
fib()


def detele_cache_filer():
    user_info = {
        "task_id": "256"
    }
    dirPath = r"F:\Joom\Joom_Orders\cache/"
    filername = user_info["task_id"] + ".txt"
    print(filername)
    if (os.path.exists(dirPath + "foo.txt")):
        os.remove(dirPath + "foo.txt")
    haha = dirPath + filername
    print(haha)
    os.remove(haha)
# detele_cache_filer()
# path = r"F:\Joom\Joom_Orders\cache"
# file_list = os.listdir(path)
# print(file_list)
# print("cy.txt" in file_list )

dirPath = r"F:\Joom\Joom_Orders\cache/"
filername = "cy" + ".txt"  # self.user_info["task_id"] + ".txt"
print(filername)
paths = dirPath + filername
file_list = os.listdir(dirPath)
print(file_list)

str = "862923@163.com"
num = str.split("@")[0]
print(num)

false = 1
true = 0
str = '[{"domain": "www.joom.com", "expiry": 1560823252, "httpOnly": false, "name": "human", "path": "/", "secure": false, "value": "1560822652266"}, {"domain": "www.joom.com", "expiry": 1560822835, "httpOnly": false, "name": "seed", "path": "/", "secure": false, "value": "t4g4v"}, {"domain": "www.joom.com", "expiry": 1876182652.398436, "httpOnly": true, "name": "accesstoken", "path": "/", "secure": true, "value": "SEV0001MTU2MDgyMjYxN3xlM0VrSEd4dHlfdkR0Sk51ZDg5YzNjOHk2VDJvcHFTWkVRREpJRUd4aE1Xa3hId1pPZEpPUmdveER0aVQ4X2NkMi00amlPYmphaTd3Z3hod0toRkdMQlU2UllETG9IWnYwbFJUaUtkbWFyNzN2eU91M2xSeVQ2dE9SMURvbGd4X3BFOFU0OFlWNFNyV1JYVmZTa2R2YU1vUHc0UDQtdnhHN01zNWk3LU8tbXhaSlNZPXwNRpvMSCyhHigxHOdb4MFHALdBUZkOFUyD9DDBWHPcjQ%3D%3D"}, {"domain": "www.joom.com", "expiry": 1876182623.089989, "httpOnly": false, "name": "ctx_seed", "path": "/", "secure": true, "value": "1oxym"}, {"domain": "www.joom.com", "expiry": 1592358652.251976, "httpOnly": true, "name": "uping", "path": "/", "secure": true, "value": "1749488751"}, {"domain": "www.joom.com", "expiry": 1560824444.084715, "httpOnly": false, "name": "adjust_session", "path": "/", "secure": true, "value": "app_token%3Drrjrofpr96gw%26adid%3Df99026a807ddedbfdca11f3f97bbab27%26ask_in%3D2000"}, {"domain": "www.joom.com", "expiry": 1560824444.083609, "httpOnly": false, "name": "adjust_jdid", "path": "/", "secure": true, "value": "00000000-5d08-433b-29c9-03330178d7a8"}, {"domain": "www.joom.com", "expiry": 1560909042.574327, "httpOnly": false, "name": "close_splashBanner", "path": "/", "secure": true, "value": "1"}, {"domain": "www.joom.com", "expiry": 1876182652.40646, "httpOnly": false, "name": "ephemeral", "path": "/", "secure": true, "value": "n"}, {"domain": "www.joom.com", "expiry": 1876182654.466342, "httpOnly": false, "name": "authorized", "path": "/", "secure": true, "value": "y"}, {"domain": "www.joom.com", "expiry": 1876182652.398539, "httpOnly": true, "name": "refreshtoken", "path": "/", "secure": true, "value": "SEV0001MTU2MDgyMjYxN3x3bnI3dTVOYmNKTTlDbzZLYlBXOXhyOTNNVDFNdnVNRU9UNVMwZXVjcGRWb3l6bWVSVzYxZTd3N2oyeFJKZ2YyajhwSnk0ZlFub1czbEppcXJtdHF4ajNhSUVtY0hXVHJKWWsxRWR0cGt3YS11R1llYmtEdXJSeElZaUpJOFZ0RzR6OXB4OENVa0hWWmlnMzdGVXhzeHp3RjZteFo2ck56N0VtdDNvbndnZVhjOHdUTUJhNUd2UzJNbU1md0dZU0hLdz09fLUqbMW-MGisxkwOyZ76HPIy7isXiUZ3pdzmNsHqKhaH"}, {"domain": "www.joom.com", "expiry": 1876182623.089914, "httpOnly": true, "name": "deviceid", "path": "/", "secure": true, "value": "5d08433b29c903330178d7a8"}, {"domain": "www.joom.com", "expiry": 1876182652.398647, "httpOnly": false, "name": "pref", "path": "/", "secure": true, "value": "%7B%22v%22%3A4%2C%22currency%22%3A%22RUB%22%2C%22language%22%3A%22en%22%2C%22region%22%3A%22RU%22%7D"}, {"domain": ".joom.com", "expiry": 1568598659, "httpOnly": false, "name": "_fbp", "path": "/", "secure": false, "value": "fb.1.1560822659190.1170234816"}, {"domain": "www.joom.com", "expiry": 1560823242.560118, "httpOnly": false, "name": "session_id", "path": "/", "secure": true, "value": "ae213656f7cc6bb2b5931ae7a5203589"}, {"domain": "www.joom.com", "expiry": 1876182623.089454, "httpOnly": false, "name": "ver", "path": "/", "secure": true, "value": "r%2F2.5.1-6930081"}]'
# print(eval(str))
print(type((str)))
for i in (str):
    print(i)
    print(i["name"])