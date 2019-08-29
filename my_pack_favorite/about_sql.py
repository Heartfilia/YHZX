# mysql ##################################################
import pymysql


db = pymysql.connect(host='localhost', user='root', password='123456', port=3306)
cursor = db.cursor()

cursor.execute('SELECT VERSION()')
data = cursor.fetchone()
print('Database version:', data)
cursor.execute('CREATE DATABASE spiders DEFAULT CHARACTER SET utf8')
cursor.execute('CREATE TABLE IF NOT EXISTS students (id VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL age INT NOT NULL, PRIMARY KEY (id)')

sql = 'INSERT INTO students(id, name, age) values (%s, %s, %s)'
try:
	cursor.execute(sql, (id, user, age))
	db.commit()
except:
	db.rollback()

cursor.close()
db.close()


# mongo #########################################################
import pymongo
client = pymongo.MongoClient(host='localhost', port=27017)
# client = MongoClient('mongodb://localhost:27017/')

db = client.test  # database
# db = client['test']

collection = db.students
# collection = db['students']

student = {
	'id': '201908',
	'name': 'Lodge',
	'age': 21,
	'gender': 'male'
}
result = collection.insert(student)

result = collection.insert([student1, student2])
result = collection.insert_many([student1, student2])

result = collection.find_one({'name': 'Lodge'})

# also could search by ObjectId
from bson.objectid import ObjectId
result = collection.find_one({'_id': ObjectId('5551171sdfdf14df1d')})


results = collection.find({'age': 20})
for result in results:
	print(result.name)

results = collection.find({'name': {'$regex': '^L.*'}})
# $regex  $exists  $type  $mod  $text  $where

results = collection.find({'age': {'$lt': 20}})
# $lt:<  $gt:>  $lte:<=  $gte:>=  $ne:!=  $in:in  $nin:not in 


count = collection.find().count()

results = collection.find().sort('name', pymongo.ASCENDING)

results = collection.find().sort('name', pymongo.ASCENDING).skip(2)

condition = {'name': 'Kevin'}
student = collection.find_one(condition)
student['age'] = 25
result = collection.update(condition, student)

student = collection.find_one(condition)
student['age'] = 26
result = collection.update_one(condition, {'$set': student})
print(result.matchd_count, result.modified_count)

result = collection.remove({'name': 'Kevin'})
result = collection.delete_one({'name': 'Kevin'})   # result.deleted_count
result = collection.delete_many({'age': {'$lt': 25}})


# find_one_and_delete()
# find_one_and_replace()
# find_one_and_update()

# create_index()
# create_indexes()
# drop_index()


# redis ##############################################################
from redis import StrictRedis


redis = StrictRedis(host='localhost', port=6379, db=0, password='test')
redis.set('name', 'Bob')
print(redis.get('name'))    # b'Bob'


from redis import StrictRedis, ConnectionPool


pool = ConnectionPool(host='localhost', port=6379, db=0, password='password')
redis = StrictRedis(connect_pool=pool)
# more information need to search on baidu
