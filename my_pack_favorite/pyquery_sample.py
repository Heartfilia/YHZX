# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq


doc = pq(url="http://www.baidu.com")  # >same with >>> doc=pq(requests.get('http://www.baidu.com').text)
print(doc('title'))

doc = pq(filename='demohtml')   # local file

doc = pq(html)
print(doc('#container .list li'))

wrap = doc('.wrap')
wrap.find('p').remove()  # remove node p
print(wrap.text()) 

items = doc('.list')
lis = items.find('li')

# more you need to find in network