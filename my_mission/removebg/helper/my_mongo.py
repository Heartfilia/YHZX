import pymongo

MONGODB_HOST = '192.168.4.139'   # mongodb的远程地址
MONGODB_DB = 'lodge'   # mongodb的数据库
DATEBASE = 'removebg'       # mongodb的表


conn = pymongo.MongoClient(host=MONGODB_HOST, port=27017)


def mongo_user_add(user_name):
    """存储用户账号"""
    user = conn[MONGODB_DB][DATEBASE]
    data = {'user_name': user_name, 'token': '', 'count': 0, 'code': 0}
    user.insert(data)


def mongo_token_update(user_name, api):
    """存api秘钥"""
    users = conn[MONGODB_DB][DATEBASE]
    old_users = users.update_one({'user_name': user_name}, {'$set': {'api': api}})
    print('更新成功{}'.format(old_users))


def mongo_user_find():
    """查询用户"""
    users = conn[MONGODB_DB][DATEBASE]
    old_users = users.find({'count': {'$lte': 50}}).__getitem__(0)
    return old_users['user_name']


def mongo_add_user_find():
    """查看是否激活"""
    users = conn[MONGODB_DB][DATEBASE]
    try:
        old_users = users.find({'code': {'$lte': 0}}).__getitem__(0)
    except:
        print('全部已经激活完成')
        return
    return old_users['user_name']


def mongo_add_api(uid):
    users = conn[MONGODB_DB][DATEBASE]
    datas = {}
    old_users = users.find_one({'_id': uid})


def mongo_api_find():
    """返回API秘钥"""
    users = conn[MONGODB_DB][DATEBASE]
    old_users = users.find({'count': {'$lte': 50}}).__getitem__(0)
    print(old_users['api'])
    return old_users['api']


def mongo_api_count(user_name):
    users = conn[MONGODB_DB][DATEBASE]
    user = users.find_one({'user_name': user_name})
    try:
        old_users = users.update_one({'user_name': user_name}, {'$inc': {'count': 1}}, True)
    except:
        old_users = users.update_one({'user_name': user_name}, {'$inc': {'count': 1}}, True)
    return print('已计数')


def mongo_add_user(user_name):
    users = conn[MONGODB_DB][DATEBASE]
    user = users.find_one({'user_name': user_name})
    try:
        old_users = users.update_one({'user_name': user_name}, {'$inc': {'code': 1}}, True)
    except:
        old_users = users.update_one({'user_name': user_name}, {'$inc': {'code': 1}}, True)
    return print('已激活')





