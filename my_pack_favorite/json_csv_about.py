# if you want to write json file  you could use indent to pretty format
import json


with open('test.json', 'w') as file:
	file.write(json.dumps(data, indent=2))


# if you want to write csv file  you could use
# writer = csv.writer(csvfile)
# writer.writerow(['id', 'name', 'age'])
# writer.writerow(['10', 'lodge', '21'])
import csv

with open('test.csv', 'w') as file:
	writer = csv.writer(csvfile, delimiter='')
	writer.writerow(['10', 'lodge', 21])

with open('data.csv', 'w') as file:
	fieldnames = ['id', 'name', 'age']
	writer.writeheader()
	writer.writerow({'id': '1001', 'name': 'bob', 'age': 20})

with open('data.csv', 'a') as file:
	fieldnames = ['id', 'name', 'age']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writerow({'id': '1004', 'name': 'Durant', 'age': 22})

# read
with open('data.csv', 'r', encoding='utf-8') as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		print(row)

import pandas as pd


df = pd.read_csv('data.csv')
print(df)

