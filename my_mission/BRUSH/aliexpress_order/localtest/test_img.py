import requests
import os

def get_img_abspath(img_url):
    img_dir = os.path.join(os.path.dirname(__file__), 'images')
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    img_name = 'FeedBack' + '.' + img_url.split('.')[-1]
    # img_abspath = os.path.abspath(__file__)+'/'+img_dir + '/' + img_name
    img_abspath = img_dir + '/' + img_name
    r = requests.get(img_url, stream=True)
    # f = open(img_abspath, "wb")
    with open(img_abspath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    # print(img_abspath)
    return img_abspath


if __name__ == '__main__':
    img_url = 'http://dingyue.nosdn.127.net/fGV8patCQ93yO1SfIen76pT8DVNVUoLAJ2wsrCBWvBbX71534229699024compressflag.png'
    print(get_img_abspath(img_url))