from bs4 import BeautifulSoup

soup = BeautifulSoup(markup, 'html.parser')
soup = BeautifulSoup(markup, 'lxml')
soup = BeautifulSoup(markup, 'xml')
soup = BeautifulSoup(markup, 'html5lib')


# example
soup = BeautifulSoup(html, 'lxml')    # this html is text
print(soup.p)
print(soup.p.string)
print(soup.prettify())
print(soup.title.string)
print(soup.head)

print(soup.p.attrs)            # >> {'class': ['title'], 'name': 'dromouse'}
print(soup.p.attrs['name'])    # >> dromouse
print(soup.p.name)             # >> dromouse
print(soup.p['name'])          # >> dromouse

print(soup.p.contents)    

print(soup.p.children)
for i, child in enumerate(soup.p.children):
	print(i, child)


for ul in soup.find_all(name='li'):
	print(li.string)

print(soup.find_all(attrs={'id': 'list-1'}))
print(soup.find_all(attrs=re.compile('link')))
print(soup.select('ul li'))


for li in soup.select('li'):
	print('Get Text:', li.get_text())   # same with V
	print('String:', li.string)         # same with ^

