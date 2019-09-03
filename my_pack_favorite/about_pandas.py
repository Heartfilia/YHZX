from pandas import Series, DataFrame
import pandas as pd

print('=' * 40)
s = Series([100, "Python", "Php", "Java"])
# print(s)

# print(s.values)

# print(s.index)
print('=' * 40)

s2 = Series([100, "Python", "Php", "Java"], index=["mark", "title", "university", "name"])
# print(s2)
# print(s2.index)
# print(s2['name'])
print('=' * 40)
sd = {"python": 8000, "c++": 8100, "c#": 4000}
s3 = Series(sd)
# print(s3)
s4 = Series(sd, index=['java', 'python', 'c++', 'c#'])
# print(s4)
print('=' * 40)
ilist = ['java', 'perl']
s5 = Series(sd, index=ilist)
# print(s5)
print('=' * 40 )
# print(pd.isnull(s4))
# print(pd.notnull(s4))
# print(s4.isnull())
# s4.index = ['p1', 'p2', 'p3', 'p4']
# print(s4)
print('=' * 40)
s6 = Series([3, 9, 4, 7], index=['a', 'b', 'c', 'd'])
# print(s6)
# print(s6[s6 > 5])
# print(s6 * 5)
# print(s4 + s4)
data = {'name': ['yahoo', 'google', 'facebook'], "marks": [200, 400, 800], 'price': [9, 3, 7]}
f1 = DataFrame(data)
# print(f1)
f2 = DataFrame(data, columns=['name', 'price', 'marks'])
# print(f2)
f3 = DataFrame(data, columns=['name', 'price', 'marks', 'debt'], index=['a', 'b', 'c'])
# print(f3)

newdata = {'lang': {'firstline': 'python', 'secondline': 'java'}, 'price': {'firstline': 8000}}
f4 = DataFrame(newdata)
print(f4)

