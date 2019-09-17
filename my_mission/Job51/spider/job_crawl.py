from logger import *
import requests
from lxml import etree
from urllib import request


class QianCheng(object):
    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://ehire.51job.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': 'ehire.51job.com',
            'Referer': 'https://ehire.51job.com/MainLogin.aspx',
            'Cookie': 'guid=e81bba60a47ccb706a6a99ab93918824; slife=lowbrowser%3Dnot%26%7C%26; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; 51job=cenglish%3D0%26%7C%26; search=jobarea%7E%60030200%7C%21ord_field%7E%600%7C%21recentSearch0%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAamazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565682815%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch1%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%D1%C7%C2%ED%D1%B7%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565312878%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch2%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA030202%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAAmazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565251247%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch3%7E%601%A1%FB%A1%FA030200%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FAAmazon%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1565251214%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21collapse_expansion%7E%601%7C%21; EhireGuid=e82df8d95f004368aca6757974f4ed5c; LangType=Lang=&Flag=1; ASP.NET_SessionId=dkv0hefzabupmsordjhyzppp; AccessKey=b937612bee4d4a2; RememberLoginInfo=member_name=52A78CEE69489B37649D5489253311B6&user_name=76EFADFBF5B18288; HRUSERINFO=CtmID=3121921&DBID=1&MType=02&HRUID=3744006&UserAUTHORITY=1111111111&IsCtmLevle=1&UserName=ymrj483&IsStandard=0&LoginTime=08%2f13%2f2019+16%3a44%3a14&ExpireTime=08%2f13%2f2019+16%3a54%3a14&CtmAuthen=0000011000000001000110010000000011100001&BIsAgreed=true&IsResetPwd=0&CtmLiscense=6&mb=&AccessKey=c22a1a718d698f81&source=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ehire.51job.com',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_post(self):
        url = self.base_url + 'InboxResume/InboxRecentEngine.aspx'
        resp = requests.get(url, headers=self.headers, verify=False)
        xpo = etree.HTML(resp.text)
        vary_code = xpo.xpath('//div[@class="aspNetHidden"]/input[@name="__VIEWSTATE"]/@value')[0]
        return vary_code

    def parse_main_page(self, vary_code):
        url = self.base_url + 'InboxResume/InboxRecentEngine.aspx'
        params = {
            '__EVENTTARGET': 'btnProcess',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': f'{vary_code}',
            'ctlSearchInboxEngine1_txt_keyword': '',
            'ctlSearchInboxEngine1_txt_area_search': '',
            'ctlSearchInboxEngine1_txt_funtype_search': '',
            'ctlSearchInboxEngine1_txt_sex': '',
            'ctlSearchInboxEngine1_txt_industry_search': '',
            'ctlSearchInboxEngine1_txt_major_search': '',
            'ctlSearchInboxEngine1_txt_hukou_search': '',
            'ctlSearchInboxEngine1_txt_positionapplied': '',
            'ctlSearchInboxEngine1$hid_keywordtype': '15',
            'ctlSearchInboxEngine1$hid_area_search': '',
            'ctlSearchInboxEngine1$hid_expectjobarea_search ': '',
            'ctlSearchInboxEngine1$hid_funtype_search': '',
            'ctlSearchInboxEngine1$hid_degreefrom': '',
            'ctlSearchInboxEngine1$hid_degreeto': '',
            'ctlSearchInboxEngine1$hid_workyearfrom': '',
            'ctlSearchInboxEngine1$hid_workyearto': '',
            'ctlSearchInboxEngine1$hid_sex': '',
            'ctlSearchInboxEngine1$hid_industry_search': '',
            'ctlSearchInboxEngine1$hid_major_search': '',
            'ctlSearchInboxEngine1$hid_expectsalaryfrom': '',
            'ctlSearchInboxEngine1$hid_expectsalaryto': '',
            'ctlSearchInboxEngine1$hid_cursalaryfrom': '',
            'ctlSearchInboxEngine1$hid_cursalaryto': '',
            'ctlSearchInboxEngine1$hid_hukou_search': '',
            'ctlSearchInboxEngine1$hid_ownerhruid': '',
            'ctlSearchInboxEngine1$hid_label': '',
            'ctlSearchInboxEngine1$hid_titlelabel': '',
            'ctlSearchInboxEngine1$hid_company': '',
            'ctlSearchInboxEngine1$hid_division': '',
            'ctlSearchInboxEngine1$hidKeywordCookie': '',
            'ctlSearchInboxEngine1$hid_allTxt ': '0',
            'ctlSearchInboxEngine1$hidShowMore': '0',
            'ctlSearchInboxEngine1$hidmorelistheight': '126',
            'pagerTopNew$ctl06': '50',
            'cbxColumns$1 ': 'AGE',
            'cbxColumns$2 ': 'WORKYEAR',
            'cbxColumns$4 ': 'AREA',
            'cbxColumns$5 ': 'TOPDEGREE',
            'cbxColumns$16': 'SENDDATE',
            'hidShowCode': '0',
            'hidAccessKey ': 'eaa99bf211964b6',
            'hid_isafreshsearch ': '1',
            'hid_process': '2',
            'hid_posttime ': '7',
            'hid_label': '',
            'hid_labelTxt': '',
            'hidSort': 'SENDDATE',
            'hidShowMore': '0',
            'hidDisplayType ': '0',
            'strSelectCols': 'AGE,WORKYEAR,AREA,TOPDEGREE,SENDDATE',
            'hidFolder': 'EMP',
            'hidSeqID': '',
            'hidRefresh ': '0',
            'exportType ': 'Word',
            'downloadType ': '0',
            'screen ': '0',
            'rdbCustomize ': 'on',
            'chk_intvplan ': 'on',
            'txt_intvplan_time': '',
            'txt_intvplan_time': '',
            'intvresult ': '1',
            'chk_offerplan': 'on',
            'offerresult': '1',
        }
        resp = self.session.post(url, data=params, headers=self.headers, verify=False)
        print(resp.text)

    def run(self):
        vary_code = self.get_post()
        # self.parse_main_page(vary_code)


if __name__ == '__main__':
    app = QianCheng()
    app.run()

