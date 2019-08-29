from lxml import etree


html = etree.parse('./test.html', etree.HTMLParser())  # open local file
result = html.xpath('//li/a/@href')

# ################# or ####################

parser = etree.HTML(html)   # this html is html text  not file
result = parser.xpath('//li/a/text()')


# contains()
result = parser.xpath('//li[contains(@class, "test")]/a/@value')

result = parser.xpath('//li[contains(@class, "li") and @name="item"]/a/text()')

# position
result = parser.xpath('//li[1]/a/text()')
result = parser.xpath('//li[last()]/a/text()')
result = parser.xpath('//li[last()-2]/a/text()')      # The third from last
result = parser.xpath('//li[position()<3]/a/text()')

# family  i do't know
result = parser.xpath('//li[1]/ancestor::*')
result = parser.xpath('//li[1]/ancestor::div')
result = parser.xpath('//li[1]/attribute::*')
result = parser.xpath('//li[1]/child::a[@href="link1.html"]')
result = parser.xpath('//li[1]/descendant::span')
result = parser.xpath('//li[1]/following::*[2]')
result = parser.xpath('//li[1]/following-sibling::*')