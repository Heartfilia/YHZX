# coding=utf-8
import json
import time
import random
import requests


class CrawlPage:
    def __init__(self):
        self.url = 'https://rd5.zhaopin.com/api/rd/resume/list?'
        self.localtime = time.localtime(time.time())
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Content-Type': 'application/json',
            'Content-Type': 'text/plain',
            'Referer': 'https://rd5.zhaopin.com/resume/apply',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            "cookie": "x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5; sts_deviceid=16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d; urlfrom2=121126445; adfcid2=none; adfbid2=0; acw_tc=2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6; login_point=67827992; promoteGray=; diagnosis=0; LastCity=%E5%B9%BF%E5%B7%9E; LastCity%5Fid=763; dywez=95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html; __utmz=269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html; NTKF_T2D_CLIENTID=guest848ED7A8-2D6C-CB43-D002-4785D3149DAB; sou_experiment=psapi; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D; c=OYd5f54u-1565146352123-205a31b6147942073825198; _fmdata=RjVcPpTGcffpZk5l0yUErfjZkmBHOjkP6kSghdv6CtDZCGZsOU%2FpDWROFqcil8ZtN7Dj%2B8TdUuQHdk17CMivo0uhUPDkXO%2BWP45A2LG761M%3D; _xid=gfhUYYFKG3ST%2F1QH8tKqAHYh0%2FaBXgOv9PvNYIX3DV86QIuuKiO1uUlpUG%2BShxIUJBmMYroIFkBPaV7u7onPfw%3D%3D; x-zp-dfp=zlzhaopin-1564541208377-824fee2b5b7e3; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1564539142,1565159011; x-zp-device-id=767356337adeccab996d3c784380a003; JSloginnamecookie=onn20v%5Ft1lyuqqav%5Fgmhphzu6uby%40oauth%2Eweixin; JSShowname=""; JSpUserInfo=236a2d6b566a5c6459695b7550725d7340765a69596b526a5f6825693b654f651c71186a076b596a5a641e693675117254731d7613691e6b1b6a1568086903652d6514711b6a016b1b6a026412691c7553721073137613692b6b056a05681c6901651a655d71016a0c6b026a1264016907755e7220733c765769586b586a52685f69426542654a71406a5a6b2b6a1b641969477506720a731c765169386b3e6a596858694e65336527714b6a5e6b466a5f64486950755f725173487651692a6b266a596858694e65276532714b6a236b266a5b645a695c755d72547341765869536b5f6a5f683c6921654f6542714d6a3a6b226a5764586952752; uiioit=3d752c6452695d6a053555645d7550645e695b6a06355f6453752a642b69566a04355c641; zp-route-meta=uid=655193256,orgid=67827992; dywea=95841923.183147172171786560.1564539142.1565602976.1565657914.24; dywec=95841923; __utma=269921210.1113127844.1564539142.1565602976.1565657914.22; __utmc=269921210; __utmt=1; is-oversea-acount=0; at=bd190984fdba44e388fb723965dc71f5; rt=ebe692e9a70e4bd4bfe07597db596886; login-type=b; sts_sg=1; sts_evtseq=1; sts_sid=16c887beb33183-0a0a25481c30be-3c375f0d-2073600-16c887beb34625; sts_chnlsid=Unknown; zp_src_url=https%3A%2F%2Fpassport.zhaopin.com%2Forg%2Flogin%3Fbkurl%3Dhttps%253A%252F%252Frd5.zhaopin.com%252F; dyweb=95841923.2.10.1565657914; __utmb=269921210.2.10.1565657914"
        }
        self.cookies = {
            "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5",
            "sts_deviceid": "16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d",
            "urlfrom2": "121126445",
            "adfcid2": "none",
            "adfbid2": "0",
            "acw_tc": "2760827015645412125101117e0aea7957a2c5bd1a105885e3208f62506ae6",
            "login_point": "67827992",
            "promoteGray": "",
            "diagnosis": "0",
            "LastCity": "%E5%B9%BF%E5%B7%9E",
            "LastCity%5Fid": "763",
            "dywez": "95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html",
            "__utmz": "269921210.1564567034.8.3.utmcsr=ihr.zhaopin.com|utmccn=(referral)|utmcmd=referral|utmcct=/talk/manage.html",
            "NTKF_T2D_CLIENTID": "guest848ED7A8-2D6C-CB43-D002-4785D3149DAB",
            "sou_experiment": "psapi",
            "zp-route-meta": "uid=655193256,orgid=67827992",
            "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D",
            "c": "OYd5f54u-1565146352123-205a31b6147942073825198",
            "_fmdata": "RjVcPpTGcffpZk5l0yUErfjZkmBHOjkP6kSghdv6CtDZCGZsOU%2FpDWROFqcil8ZtN7Dj%2B8TdUuQHdk17CMivo0uhUPDkXO%2BWP45A2LG761M%3D",
            "_xid": "gfhUYYFKG3ST%2F1QH8tKqAHYh0%2FaBXgOv9PvNYIX3DV86QIuuKiO1uUlpUG%2BShxIUJBmMYroIFkBPaV7u7onPfw%3D%3D",
            "x-zp-dfp": "zlzhaopin-1564541208377-824fee2b5b7e3",
            "Hm_lvt_38ba284938d5eddca645bb5e02a02006": "1564539142,1565159011",
            "x-zp-device-id": "767356337adeccab996d3c784380a003",
            "dywec": "95841923",
            "__utmc": "269921210",
            "is-oversea-acount": "0",
            "JsNewlogin": "1837743086",
            "JSloginnamecookie": "onn20v%5Ft1lyuqqav%5Fgmhphzu6uby%40oauth%2Eweixin",
            "JSShowname": '""',
            "at": "bd190984fdba44e388fb723965dc71f5",
            "Token": "bd190984fdba44e388fb723965dc71f5",
            "rt": "ebe692e9a70e4bd4bfe07597db596886",
            "JSpUserInfo": "236a2d6b566a5c6459695b7550725d7340765a69596b526a5f6825693b654f651c71186a076b596a5a641e693675117254731d7613691e6b1b6a1568086903652d6514711b6a016b1b6a026412691c7553721073137613692b6b056a05681c6901651a655d71016a0c6b026a1264016907755e7220733c765769586b586a52685f69426542654a71406a5a6b2b6a1b641969477506720a731c765169386b3e6a596858694e65336527714b6a5e6b466a5f64486950755f725173487651692a6b266a596858694e65276532714b6a236b266a5b645a695c755d72547341765869536b5f6a5f683c6921654f6542714d6a3a6b226a5764586952752",
            "uiioit": "3d752c6452695d6a053555645d7550645e695b6a06355f6453752a642b69566a04355c641",
            "login-type": "b",
            "sts_sg": "1",
            "sts_chnlsid": "Unknown",
            "zp_src_url": "https%3A%2F%2Fpassport.zhaopin.com%2FwxLogin%3Fbkurl%3Dhttps%253A%252F%252Fpassport.zhaopin.com%252Forg%252Flogin%252Fbind%252Faccount%253Fbkurl%253Dhttps%25253A%25252F%25252Frd5.zhaopin.com%2526isValidate%253Dfalse",
            "__utma": "269921210.1113127844.1564539142.1565329072.1565331103.14",
            "dywea": "95841923.183147172171786560.1564539142.1565329072.1565331103.16",
            "sts_sid": "16c75011e5827a-089796397c2574-3c375f0d-2073600-16c75011e5938c",
            "sts_evtseq": "30",
            "dyweb": "95841923.30.10.1565331103",
            "__utmt": "1",
            "__utmb": "269921210.30.10.1565331103"
        }
        self.session = requests.Session()

    @staticmethod
    def handle0(n):
        num = str(n)
        if len(num) == 1:
            nu = '0' + num
        else:
            nu = num
        return nu

    def params_get(self, i):
        t = time.time()
        node = int(t * 1000)
        today = time.localtime(t)
        yesterday = time.localtime(t - 86400)
        lastweek = time.localtime(t - 604800)

        today_year = str(today.tm_year)[-2:]
        today_month = self.handle0(today.tm_mon)
        today_day = self.handle0(today.tm_mday)

        yesterday_year = str(yesterday.tm_year)[-2:]
        yesterday_month = self.handle0(yesterday.tm_mon)
        yesterday_day = self.handle0(yesterday.tm_mday)

        lastweek_year = str(lastweek.tm_year)[-2:]
        lastweek_month = self.handle0(lastweek.tm_mon)
        lastweek_day = self.handle0(lastweek.tm_mday)

        today_info = today_year + today_month + today_day
        yesterday_info = yesterday_year + yesterday_month + yesterday_day
        lastweek_info = lastweek_year + lastweek_month + lastweek_day

        front = [
            '46ba3dcc4781446ab7b77f11468b6c36',
            '15f87159b7c440078fedea3be92d26e7',
            '97ea329932f04166b268e0cb0b2bfd61',
            'bf37a85ca31548808cc4f6222bf07783'
        ]
        max_len = len(front) - 1
        params = {
            "_": f"{node}",
            "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50,1000)}-{random.randint(200000, 800000)}",
            "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5",
            "S_CreateDate": f"{lastweek_info},{today_info}",
            # "S_CreateDate": f"{yesterday_info},{today_info}",
            "S_ResumeState": "1",
            "S_feedback": '""',
            "isNewList": "true",
            "page": i + 1,
            "pageSize": 100,       # 最多只能传100数据
            "searchSource": 1,
            # "sort": "time",
        }
        return params

    def first_time(self):
        params = self.params_get(0)
        resp = self.session.post(self.url, json=params, headers=self.headers, verify=False)
        data = json.loads(resp.text)
        print(data)
        pg = data['data']['total'] // 100 + 1
        time.sleep(15)
        return pg

    def stabilization(self, pg):
        for i in range(pg):
            params = self.params_get(i)
            time.sleep(10)
            information = self.session.post(self.url, json=params, headers=self.headers, verify=False)
            print(json.loads(information.text))

    def run(self):
        pg = self.first_time()    # 3
        # self.stabilization(pg)
        # print(self.params_get(0))


if __name__ == '__main__':
    app = CrawlPage()
    app.run()

    # json_file = information.text
    # with open(f'histroty{i+1}.json', 'w', encoding='utf-8') as f:
    #     f.write(json_file)
