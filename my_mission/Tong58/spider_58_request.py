import re
import os
import json
from lxml import etree
from fontTools.ttLib import TTFont
from PIL import Image
import matplotlib.pyplot as plt
# from helper.Baidu_ocr.client import main_ocr
# import pytesseract


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# font = TTFont(BASE_DIR + r'\helper\fonts\b64.woff')
# bestcmap = font['cmap'].getBestCmap()
# print(bestcmap)
# input('>')
# new_map = dict()
#
# for key in bestcmap.keys():
#     value = re.search(r'(\d+)', bestcmap[key])
#     if not value:
#         continue
#     # print(bestcmap[key])
#     value = int(re.search(r'(\d+)', bestcmap[key]).group(1)) - 1
#     key = hex(key)
#     # print(value)
#     new_map[key] = value
#
# print(new_map)

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
# input('>')
# d_text = ""
# for alpha in '':    # 这里就是遍历那些有问题的字
#     hex_alpha = alpha.encode('unicode_escape').decode()[2:]
#     print(hex_alpha)
#     d_text += "&#x" + hex_alpha + ';'
#
# print(d_text)

for v in font_dict:
    value_key = font_dict[v]
    value = json.loads(value_key)
    x = []
    y = []
    # if v == 'e6be':   # 黄
    if v == 'eb4e':   # 0
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
        plt.show()   # 这个和下面那个功能会重置坐标 如果两个都要显示的话 不要放上句前面
        break

# main_ocr()   # 这里在调用百度那边

# image = Image.open(BASE_DIR + r"\helper\fonts\plt.png")
# tessdata_dir_config = '--tessdata-dir "c://Program Files (x86)//Tesseract-OCR//tessdata"'
# cn = pytesseract.image_to_string(image, lang='eng', config=tessdata_dir_config)
# print(cn)   # 这里是识别结果，不知道咋地，没啥精度


class CompareImage(object):
    def calculate(self, image1, image2):
        g = image1.histogram()
        s = image2.histogram()
        assert len(g) == len(s), "error"

        data = []

        for index in range(0, len(g)):
            if g[index] != s[index]:
                data.append(1 - abs(g[index] - s[index]) / max(g[index], s[index]))
            else:
                data.append(1)

        return sum(data) / len(g)

    def split_image(self, image, part_size):
        pw, ph = part_size
        w, h = image.size

        sub_image_list = []

        assert w % pw == h % ph == 0, "error"

        for i in range(0, w, pw):
            for j in range(0, h, ph):
                sub_image = image.crop((i, j, i + pw, j + ph)).copy()
                sub_image_list.append(sub_image)

        return sub_image_list

    def compare_image(self, file_image1, file_image2, size=(256, 256), part_size=(64, 64)):
        '''
        'file_image1'和'file_image2'是传入的文件路径
         可以通过'Image.open(path)'创建'image1' 和 'image2' Image 对象.
         'size' 重新将 image 对象的尺寸进行重置，默认大小为256 * 256 .
         'part_size' 定义了分割图片的大小.默认大小为64*64 .
         返回值是 'image1' 和 'image2'对比后的相似度，相似度越高，图片越接近，达到1.0说明图片完全相同。
        '''

        image1 = Image.open(file_image1)
        image2 = Image.open(file_image2)

        img1 = image1.resize(size).convert("RGB")
        sub_image1 = self.split_image(img1, part_size)

        img2 = image2.resize(size).convert("RGB")
        sub_image2 = self.split_image(img2, part_size)

        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self.calculate(im1, im2)

        x = size[0] / part_size[0]
        y = size[1] / part_size[1]

        pre = round((sub_data / (x * y)), 6)
        # print(str(pre * 100) + '%')
        print(f'Compare the image result is: {pre}')
        return pre


compare_image = CompareImage()
image1 = BASE_DIR + r"\helper\fonts\digit_1.png"
# image2 = BASE_DIR + r"\helper\fonts\digit_9.png"
image2 = BASE_DIR + r"\helper\fonts\plt.png"
# compare_image.compare_image(image1, image2)


from skimage.measure import compare_ssim
import cv2


def compare(image1, image2):

    imageA = cv2.imread(image1)
    imageB = cv2.imread(image2)
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(grayA, grayB, full=True)

    return score


print(compare(image1, image2))
