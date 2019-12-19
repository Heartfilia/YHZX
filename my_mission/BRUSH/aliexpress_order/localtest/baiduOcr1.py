from aip import AipOcr
# APP_ID = "15239794"
# API_KEY = "HU5RXaK5EgcWKSaZOXixBrR9"
# SECRET_KEY = "UBZEonHx9dscUIxrHV0ulzyl7998gZhT"
APP_ID = "14602873"
API_KEY = "x5D6yZTAfHoLRpGoVHbX2V8p"
SECRET_KEY = "MrlsTXCXS8AouNl4a6v4XwbRV9ucgLW3"
filePath = "captcha.png"

class Captcha:
    def __init__(self):
        # for i in range(len(APP_CLIENTS)):

        self.aipOcr = AipOcr(APP_ID,API_KEY,SECRET_KEY)
        self.options = {
            "detect_direction":"true",
            "language_type":"ENG"
        }
    def get_file_content(self,filePath):
        with open(filePath,"rb") as fp:
            return fp.read()

    def get_captcha(self):
        result = self.aipOcr.basicAccurate(self.get_file_content(filePath),self.options)
        captcha = result['words_result'][0]["words"].strip()
        return captcha