import re
import os
import json
import base64
from io import BytesIO
from lxml import etree
from fontTools.ttLib import TTFont
from PIL import Image
import matplotlib.pyplot as plt
from helper.Baidu_ocr.client import main_ocr
import pytesseract


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


font = TTFont(BASE_DIR + r'\helper\fonts\b64.woff')
bestcmap = font['cmap'].getBestCmap()
# print(bestcmap)
newmap = dict()

for key in bestcmap.keys():
    value = re.search(r'(\d+)', bestcmap[key])
    if not value:
        continue
    # print(bestcmap[key])
    value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
    key = hex(key)
    # print(value)
    newmap[key] = value

# print(newmap)

xml = etree.parse(BASE_DIR + r'\helper\fonts\b64.xml')
root = xml.getroot()
font_dict = {}
all_data = root.xpath('//glyf/TTGlyph')
for index, data in enumerate(all_data):
    font_key = data.attrib.get('name')[3:].lower()
    contour_list = list()
    if index == 0:
        continue
    for contour in data:
        for pt in contour:
            contour_list.append(dict(pt.attrib))
    font_dict[font_key] = json.dumps(contour_list, sort_keys=True)

# print(font_dict)

# d_text = ""
# for alpha in '':    # 这里就是遍历那些有问题的字
#     hex_alpha = alpha.encode('unicode_escape').decode()[2:]
#     print(hex_alpha)
#     d_text += "&#x" + hex_alpha + ';'
#
# print(d_text)

for v in font_dict:
    value = font_dict[v]
    value = json.loads(value)
    x = []
    y = []
    # if v == 'e6be':   # 黄
    if v == 'eb5d':   # 0
    # if v == 'e031':   # 1
    # if v == 'eae5':   # 2
    # if v == 'eb96':   # 3
    # if v == 'ee2a':   # 4
    # if v == 'f74d':   # 5
    # if v == 'e007':   # 6
    # if v == 'e018':   # 7
    # if v == 'e657':   # 8
    # if v == 'ea06':   # 9
        for al in value:
            x_e = int(al['x'])
            y_e = int(al['y'])
            x.append(x_e)
            y.append(y_e)
        plt.figure(figsize=(1, 1))   # 设置保存图片的大小 (n x 100px)
        plt.fill_between(x, y, facecolor='black')   # 填充图片,使用黑色
        # plt.grid(True)
        plt.plot(x, y)   # 这里可以额外添加很多属性比如线型,线色('-k')这个表示实线黑色  线宽(linewidth)
        plt.axis('off')   # 关闭坐标
        plt.savefig(BASE_DIR + r"\helper\fonts\plt.png")
        # plt.show()   # 这个和下面那个功能会重置坐标 如果两个都要显示的话 不要放上句前面
        break

# main_ocr()   # 这里在调用百度那边了
image = Image.open(BASE_DIR + r"\helper\fonts\plt.png")
tessdata_dir_config = '--tessdata-dir "c://Program Files (x86)//Tesseract-OCR//tessdata"'
cn = pytesseract.image_to_string(image, lang='eng', config=tessdata_dir_config)
print(cn)

