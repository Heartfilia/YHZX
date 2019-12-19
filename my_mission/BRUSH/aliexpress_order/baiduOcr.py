
from aip import AipOcr
from mytools.tools import *
import os

APP_CLIENTS = [
    ("11780465", "hhkWf3XBHvd4caairOjKFAg8", "FZgkoszbyMcpPjI1hVC26w4NFb5VMHLj"),
    ("11793708", "EVz6YLg33kMwrHZlFKjDYyKO", "Qqy3PSXCfbtzUVDvaMEbfENakXtmaFWt"),
    ("11793734", "0n6rzoNUvreOcSYe3klVNZWr", "1cYpyfG9nTHxLuMfeEs0UGEQBlZTI3Fc"),
    ("11797561", "989rPrNCy22l8X8Nn87sMyzS", "9nFdhCpvx7TF2fnzn2UUsnGBHRjXVbQ5"),
    ("11793766", "6N3C0evtrOC2Ac5ZPaT4G1QL", "msDnA465ANGicm098ShwGVS4zG6qvLBK"),
    ("14303790", "uEt2KFHUF53BTOiueGGhqKA2", "xYEACawg589fOhOZXBCt2Tk8iSMKhPfO"),
    ("14303835", "vj9DLM2cgHXLhvAX4b73kr9S", "hj9BNB7Gkv4jzaRdzGpHvjwC2RpiNd5P"),
    ("14303864", "wcAR9hSMqv1q1vvkP4kCTME4", "DspAHoCBMiHWf5NFGaDNGiS4O2YK9yxU"),
    ("14303903", "PW8wsYdx3vIeo7O07BVaH88p", "R3LIXsy5Wm3AGvNGQhGeGVMAX1GGSldr"),
    ("14303948", "x1ITsgth4PvtPGoDfrTtZQ8l", "yi8zmHGOvHYwmWeSaSPjX6xvFuNw8tgD"),
    ("14550260", "Sz0QRRtzinKoQaZuc3t3SF4x", "VZs71HCuhUMZlO2aA9KFkuiT46xSOEOT"),
    ("14551854", "6SIWr3t67z43qXYNnMuS9BKX", "iEFG2LuA2TV9va72FGXTV4oVEQTfPXNW"),
    ("14551904", "yf5gyGCA43dVjpzD33toFURC", "7w0RqGYTX3jgCz2OSGvmZfZgNWKSlNg7"),
    ("14551960", "itPiX5GxDeTblbeaGb1NGKhv", "ViRcp92GlMCXBThRexr8LrvkcqGQmLYb"),
    ("14552018", "O9hT314n5rvAV9XyOERrxkgI", "46TpmkWauNgHxMIfLK4xCaY9AIlNF1mf"),
    ("14552077", "kjtFKGjad4bdbQfF2mo016im", "QUTZrcKGkY9hrPjc60GYwiitGtyLCirp"),
    ("14552199", "vSPm3ElC8oAUGSFN7DdpXVUk", "sBtUIOExuseejZgfNHepKit2c9BU3a0A"),
    ("14552230", "KFKqOaS2sSH5ruZp9HgNqode", "232NB59MZUZfw0MLZiugwlOLN7Eeuvxl"),
    ("14552275", "ek3cWhFEeev3aEGePrEguoIB", "GcWkYNFYsj34PO4toWdSy5f5kZkd1awA"),
    ("14552327", "ETLW4r0SDCAroVP0lMoqGyLa", "ATErmejN7LdovzGZhWzAg6oGpaF4AqBw"),
    ("14552390", "naqZtOPK2xscOWbRGZ8PNdb1", "7ACNCIIB8bc1Qb6wdg7S9iLGIPkFtZAV"),
    ("14552455", "g2VPyazqGjNKrtGcK8dWy7wl", "kiOkpt8hmxZEcDxOs6ozjKnaEdOgXL93"),
    ("14552508", "zFBD1QvjxA7P6xePamziamH7", "p51f4h6Mkr3cYuOamL1vyiuXBdOTpZxX"),
    ("14552568", "LGA1kqxl2nUoTxxZ4IXMVVE6", "I2VW53ri9LKLc6Knk6keAv9rGL1lRVP9"),
    ("14552703", "GKN3UDc496GrLDTqkQhdlMv9", "yYw9Rp1VTHr8tliUZmuyYwnuwHYLhnI0"),
    ("14552776", "N9nn7QZh01oSKaIu4hFKEf2b", "SpCqTuPr8H588K5xsllEDQYacnrgMy2e"),
    ("14552862", "MGcDNkZgix74AbZCW0YQEhVL", "ZKGC4iGEexjRAmy5zrVdCsNauWY8Us0R"),
    ("14552900", "3bBmBvcVrDDIE8fHXifrqxI8", "656QyylB2Fcs8Dpk0AagRGFzc76plmeG"),
    ("14602357", "LOGICkGqt6LDx8nlqSi0iE2g", "rryWmtjSHTU5ZbUtXUjNkU9MBrgRRBpa"),
    ("14602516", "ZeoyNIBzwG5KKPn9Wxajc52G", "yMq9Gb6pXZ8dw6a7TWT6YOS6dzqNG1Lq"),
    ("14602567", "bbeIf6DX23z68GdnZwYujZm0", "XDPkkEycgmT706IA6ugjkvnCjvimwR9m"),
    ("14602699", "uQgvjmeK50PRwI6wfXPwwmhC", "C1PxAyCUefQGRisMZZ6VPH5GHCCDVUqQ"),
    ("14602763", "We25D7EkU00y797ZSGLHu5RX", "7UojluhboXNj8WipfoUGle3REGeSKwrx"),
    ("14602800", "qMvGQcPNw64RLi2lhAszG04O", "8Z5uhg2xvV5wtK1fL4xQsb0CjENSqHAw"),
    ("14602832", "BTUEohONni1xNx8q1yEQmbB2", "ZOGC1jC5H1AR3NxnCYWKp6By7Hsbo0BR"),
    ("14602873", "x5D6yZTAfHoLRpGoVHbX2V8p", "MrlsTXCXS8AouNl4a6v4XwbRV9ucgLW3"),
]
image_file_path = 'captcha.png'

class BaiduOrc:

    def __init__(self):
        self.cache_dir = os.path.dirname(__file__)
        _cache_file = self.cache_dir + "/data/last_app_index.json"
        if not os.path.exists(os.path.dirname(_cache_file)):
            os.makedirs(os.path.dirname(_cache_file))

        self.last_app_index = load_json(_cache_file, default={"last_app_index": 0})["last_app_index"]
        if not os.path.isfile(_cache_file):
            save_json(_cache_file, {"last_app_index": 0})
        app_id, api_key, secret_key = APP_CLIENTS[self.last_app_index]
        self.client = AipOcr(app_id, api_key, secret_key)

    @with_filelock("baidu_orc.lock", timeout=15)
    def img_to_str(self, options=None):
        r = self.orc(options)
        if "words_result" in r.keys() and len(r["words_result"]) > 0:
            text = r["words_result"][0]["words"]
        else:
            print(r)
            text = None
        return text

    def orc(self, options=None):
        # 记录调用次数
        _cache_file = self.cache_dir + "/data/api_summery.json"
        api_summery = load_json(_cache_file, default={})
        last_app_index = str(self.last_app_index)
        if last_app_index not in api_summery.keys():
            api_summery[last_app_index] = 0
        api_summery[last_app_index] = api_summery[last_app_index] + 1
        save_json(_cache_file, api_summery)

        # 免费次数用完,切换到下一个app帐号
        if api_summery[last_app_index] > 500:
            self.last_app_index += 1
            _cache_file = self.cache_dir + "/data/last_app_index.json"
            save_json(_cache_file, {"last_app_index": self.last_app_index})

        if options is None:
            # options = {"detect_direction": "false", "detect_language": "false"}
            options = {
                            "detect_direction":"true",
                            "language_type":"ENG"
                        }
        image = self.get_file_content(image_file_path)
        # """ 调用网络图片文字识别, 图片参数为本地图片 """
        # r = self.client.webImage(image, options)

        # """通用文字识别"""
        r = self.client.basicAccurate(image,options)
        return r

    def get_file_content(self, image_file_path):
        with open(image_file_path,"rb") as fp:
            return fp.read()



#=======================================================================
# from aip import AipOcr
# # APP_ID = "15239794"
# # API_KEY = "HU5RXaK5EgcWKSaZOXixBrR9"
# # SECRET_KEY = "UBZEonHx9dscUIxrHV0ulzyl7998gZhT"
# APP_ID = "14602873"
# API_KEY = "x5D6yZTAfHoLRpGoVHbX2V8p"
# SECRET_KEY = "MrlsTXCXS8AouNl4a6v4XwbRV9ucgLW3"
# filePath = "captcha.png"
#
# class Captcha:
#     def __init__(self):
#         # for i in range(len(APP_CLIENTS)):
#
#         self.aipOcr = AipOcr(APP_ID,API_KEY,SECRET_KEY)
#         self.options = {
#             "detect_direction":"true",
#             "language_type":"ENG"
#         }
#     def get_file_content(self,filePath):
#         with open(filePath,"rb") as fp:
#             return fp.read()
#
#     def get_captcha(self):
#         result = self.aipOcr.basicAccurate(self.get_file_content(filePath),self.options)
#         captcha = result['words_result'][0]["words"].strip()
#         return captcha
