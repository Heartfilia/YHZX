# -*- coding: utf-8 -*-
import json
import random
import requests
import datetime
import urllib3
from urllib.request import unquote
from utils.logger import *
from spider.Message import send_rtx_msg

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 外包电子 cookie
cookie = ""


class Cart(object):
    def __init__(self):
        self.session = requests.Session()
        self.detail_url = "https://rd5.zhaopin.com/resume/detail?"
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
            "cookie": cookie
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
        self.province = [['548', '广东'], ['546', '湖北'], ['556', '陕西'], ['552', '四川'], ['535', '辽宁'], ['536', '吉林'], ['539', '江苏'], ['544', '山东'], ['540', '浙江'], ['549', '广西'], ['541', '安徽'], ['532', '河北'], ['533', '山西'], ['534', '内蒙古'], ['537', '黑龙江'], ['542', '福建'], ['543', '江西'], ['545', '河南'], ['547', '湖南'], ['550', '海南'], ['553', '贵州'], ['554', '云南'], ['555', '西藏'], ['557', '甘肃'], ['558', '青海'], ['559', '宁夏'], ['560', '新疆'], ['563', '台湾省']]
        self.city = [['10301', '560', '双河'], ['10302', '560', '铁门关'], ['10303', '550', '三沙'], ['10304', '563', '台北'], ['763', '548', '广州'], ['765', '548', '深圳'], ['736', '546', '武汉'], ['854', '556', '西安'], ['801', '552', '成都'], ['931', '535', '东港'], ['600', '535', '大连'], ['613', '536', '长春'], ['599', '535', '沈阳'], ['635', '539', '南京'], ['702', '544', '济南'], ['703', '544', '青岛'], ['653', '540', '杭州'], ['639', '539', '苏州'], ['636', '539', '无锡'], ['654', '540', '宁波'], ['719', '545', '郑州'], ['749', '547', '长沙'], ['681', '542', '福州'], ['682', '542', '厦门'], ['622', '537', '哈尔滨'], ['565', '532', '石家庄'], ['664', '541', '合肥'], ['773', '548', '惠州'], ['576', '533', '太原'], ['831', '554', '昆明'], ['707', '544', '烟台'], ['768', '548', '佛山'], ['691', '543', '南昌'], ['822', '553', '贵阳'], ['932', '560', '北屯区'], ['933', '556', '西咸新区'], ['587', '534', '呼和浩特'], ['785', '549', '南宁'], ['799', '550', '海口'], ['847', '555', '拉萨'], ['864', '557', '兰州'], ['878', '558', '西宁'], ['886', '559', '银川'], ['890', '560', '乌鲁木齐'], ['566', '532', '唐山'], ['577', '533', '大同'], ['588', '534', '包头'], ['614', '536', '吉林市'], ['623', '537', '齐齐哈尔'], ['665', '541', '芜湖'], ['692', '543', '景德镇'], ['720', '545', '开封'], ['737', '546', '黄石'], ['750', '547', '株洲'], ['764', '548', '韶关'], ['786', '549', '柳州'], ['800', '550', '三亚'], ['802', '552', '自贡'], ['823', '553', '六盘水'], ['832', '554', '曲靖'], ['848', '555', '昌都'], ['855', '556', '铜川'], ['865', '557', '嘉峪关'], ['879', '558', '海东'], ['887', '559', '石嘴山'], ['891', '560', '克拉玛依'], ['567', '532', '秦皇岛'], ['578', '533', '阳泉'], ['589', '534', '乌海'], ['601', '535', '鞍山'], ['615', '536', '四平'], ['624', '537', '鸡西'], ['640', '539', '昆山'], ['655', '540', '温州'], ['666', '541', '蚌埠'], ['683', '542', '莆田'], ['693', '543', '萍乡'], ['704', '544', '淄博'], ['721', '545', '洛阳'], ['738', '546', '十堰'], ['751', '547', '湘潭'], ['787', '549', '桂林'], ['803', '552', '攀枝花'], ['824', '553', '遵义'], ['833', '554', '玉溪'], ['849', '555', '山南'], ['856', '556', '宝鸡'], ['866', '557', '金昌'], ['880', '558', '海北'], ['888', '559', '吴忠'], ['892', '560', '吐鲁番'], ['907', '550', '洋浦市/洋浦经济开发区'], ['568', '532', '邯郸'], ['579', '533', '长治'], ['590', '534', '赤峰'], ['602', '535', '抚顺'], ['616', '536', '辽源'], ['625', '537', '鹤岗'], ['650', '539', '常熟'], ['656', '540', '嘉兴'], ['667', '541', '淮南'], ['684', '542', '三明'], ['694', '543', '九江'], ['705', '544', '枣庄'], ['722', '545', '平顶山'], ['739', '546', '宜昌'], ['752', '547', '衡阳'], ['766', '548', '珠海'], ['788', '549', '梧州'], ['804', '552', '泸州'], ['825', '553', '安顺'], ['834', '554', '保山'], ['850', '555', '日喀则'], ['857', '556', '咸阳'], ['867', '557', '白银'], ['881', '558', '黄南'], ['889', '559', '固原'], ['893', '560', '哈密'], ['906', '559', '中卫'], ['10153', '550', '琼海'], ['569', '532', '邢台'], ['580', '533', '晋城'], ['591', '534', '通辽'], ['603', '535', '本溪'], ['617', '536', '通化'], ['626', '537', '双鸭山'], ['652', '539', '张家港'], ['657', '540', '湖州'], ['668', '541', '马鞍山'], ['685', '542', '泉州'], ['695', '543', '新余'], ['706', '544', '东营'], ['723', '545', '安阳'], ['740', '546', '襄阳'], ['753', '547', '邵阳'], ['767', '548', '汕头'], ['789', '549', '北海'], ['805', '552', '德阳'], ['826', '553', '铜仁'], ['835', '554', '昭通'], ['851', '555', '那曲'], ['858', '556', '渭南'], ['868', '557', '天水'], ['882', '558', '海南州'], ['894', '560', '昌吉'], ['10183', '550', '儋州'], ['570', '532', '保定'], ['581', '533', '朔州'], ['592', '534', '鄂尔多斯'], ['604', '535', '丹东'], ['618', '536', '白山'], ['627', '537', '大庆'], ['658', '540', '绍兴'], ['669', '541', '淮北'], ['696', '543', '鹰潭'], ['724', '545', '鹤壁'], ['741', '546', '鄂州'], ['754', '547', '岳阳'], ['790', '549', '防城港'], ['806', '552', '绵阳'], ['827', '553', '黔西南'], ['836', '554', '楚雄'], ['852', '555', '阿里'], ['859', '556', '延安'], ['869', '557', '武威'], ['883', '558', '果洛'], ['895', '560', '博尔塔拉'], ['10184', '550', '五指山'], ['571', '532', '张家口'], ['582', '533', '晋中'], ['593', '534', '呼伦贝尔'], ['605', '535', '锦州'], ['619', '536', '松原'], ['628', '537', '伊春'], ['659', '540', '金华'], ['670', '541', '铜陵'], ['687', '542', '漳州'], ['697', '543', '赣州'], ['708', '544', '潍坊'], ['725', '545', '新乡'], ['742', '546', '荆门'], ['755', '547', '常德'], ['791', '549', '钦州'], ['807', '552', '广元'], ['828', '553', '毕节'], ['837', '554', '红河'], ['853', '555', '林芝'], ['860', '556', '汉中'], ['870', '557', '张掖'], ['884', '558', '玉树'], ['896', '560', '巴音郭楞'], ['10185', '550', '文昌'], ['572', '532', '承德'], ['583', '533', '运城'], ['594', '534', '兴安盟'], ['606', '535', '营口'], ['620', '536', '白城'], ['629', '537', '佳木斯'], ['637', '539', '徐州'], ['660', '540', '衢州'], ['671', '541', '安庆'], ['688', '542', '南平'], ['698', '543', '吉安'], ['709', '544', '济宁'], ['726', '545', '焦作'], ['743', '546', '孝感'], ['756', '547', '张家界'], ['769', '548', '江门'], ['792', '549', '贵港'], ['808', '552', '遂宁'], ['829', '553', '黔东南'], ['838', '554', '文山'], ['861', '556', '榆林'], ['871', '557', '平凉'], ['885', '558', '海西'], ['897', '560', '阿克苏'], ['10186', '550', '万宁'], ['573', '532', '沧州'], ['584', '533', '忻州'], ['595', '534', '锡林郭勒盟'], ['607', '535', '阜新'], ['621', '536', '延边'], ['630', '537', '七台河'], ['638', '539', '常州'], ['661', '540', '舟山'], ['672', '541', '黄山'], ['689', '542', '龙岩'], ['699', '543', '宜春'], ['710', '544', '泰安'], ['727', '545', '濮阳'], ['744', '546', '荆州'], ['757', '547', '益阳'], ['770', '548', '湛江'], ['793', '549', '玉林'], ['809', '552', '内江'], ['830', '553', '黔南'], ['862', '556', '安康'], ['872', '557', '酒泉'], ['898', '560', '克孜勒苏'], ['10187', '550', '东方'], ['574', '532', '廊坊'], ['585', '533', '临汾'], ['596', '534', '乌兰察布'], ['608', '535', '辽阳'], ['631', '537', '牡丹江'], ['641', '539', '南通'], ['662', '540', '台州'], ['673', '541', '滁州'], ['690', '542', '宁德'], ['700', '543', '抚州'], ['711', '544', '威海'], ['728', '545', '许昌'], ['745', '546', '黄冈'], ['758', '547', '郴州'], ['771', '548', '茂名'], ['794', '549', '百色'], ['810', '552', '乐山'], ['840', '554', '西双版纳'], ['863', '556', '商洛'], ['873', '557', '庆阳'], ['899', '560', '喀什'], ['10188', '550', '定安'], ['575', '532', '衡水'], ['586', '533', '吕梁'], ['597', '534', '巴彦淖尔'], ['609', '535', '盘锦'], ['632', '537', '黑河'], ['642', '539', '连云港'], ['663', '540', '丽水'], ['674', '541', '阜阳'], ['701', '543', '上饶'], ['712', '544', '日照'], ['729', '545', '漯河'], ['746', '546', '咸宁'], ['759', '547', '永州'], ['772', '548', '肇庆'], ['795', '549', '贺州'], ['811', '552', '南充'], ['841', '554', '大理'], ['874', '557', '定西'], ['900', '560', '和田'], ['10058', '556', '兴平'], ['10189', '550', '屯昌'], ['598', '534', '阿拉善盟'], ['610', '535', '铁岭'], ['633', '537', '绥化'], ['643', '539', '淮安'], ['675', '541', '宿州'], ['713', '544', '莱芜'], ['730', '545', '三门峡'], ['747', '546', '随州'], ['760', '547', '怀化'], ['796', '549', '河池'], ['812', '552', '眉山'], ['842', '554', '德宏'], ['875', '557', '陇南'], ['901', '560', '伊犁'], ['910', '533', '永济市'], ['10190', '550', '澄迈'], ['611', '535', '朝阳'], ['634', '537', '大兴安岭'], ['644', '539', '盐城'], ['714', '544', '临沂'], ['731', '545', '南阳'], ['748', '546', '恩施'], ['761', '547', '娄底'], ['774', '548', '梅州'], ['813', '552', '宜宾'], ['843', '554', '丽江'], ['876', '557', '临夏'], ['902', '560', '塔城'], ['10031', '534', '乌审旗'], ['10191', '550', '临高'], ['612', '535', '葫芦岛'], ['645', '539', '扬州'], ['677', '541', '六安'], ['715', '544', '德州'], ['732', '545', '商丘'], ['762', '547', '湘西'], ['775', '548', '汕尾'], ['814', '552', '广安'], ['844', '554', '怒江'], ['877', '557', '甘南'], ['903', '560', '阿勒泰'], ['10023', '535', '兴城'], ['10057', '546', '公安'], ['10061', '560', '石河子'], ['10081', '537', '安达'], ['10122', '536', '公主岭'], ['10192', '550', '琼中'], ['10470', '556', '杨凌'], ['646', '539', '镇江'], ['678', '541', '亳州'], ['716', '544', '聊城'], ['733', '545', '信阳'], ['776', '548', '河源'], ['815', '552', '达州'], ['845', '554', '迪庆'], ['904', '549', '来宾'], ['10143', '532', '遵化'], ['10159', '537', '双城'], ['10193', '550', '保亭'], ['10198', '536', '珲春'], ['647', '539', '泰州'], ['679', '541', '池州'], ['717', '544', '滨州'], ['734', '545', '周口'], ['777', '548', '阳江'], ['816', '552', '雅安'], ['846', '554', '临沧'], ['905', '549', '崇左'], ['10157', '534', '满洲里'], ['10160', '537', '尚志'], ['10163', '554', '普洱'], ['10164', '560', '奎屯市'], ['10194', '550', '白沙'], ['680', '541', '宣城'], ['718', '544', '菏泽'], ['735', '545', '驻马店'], ['778', '548', '清远'], ['817', '552', '巴中'], ['10069', '541', '凤阳'], ['10161', '537', '绥芬河'], ['10195', '550', '昌江'], ['648', '539', '宿迁'], ['779', '548', '东莞'], ['818', '552', '资阳'], ['10166', '560', '乌苏'], ['10196', '550', '乐东'], ['10510', '537', '肇东市'], ['780', '548', '中山'], ['819', '552', '阿坝'], ['911', '539', '太仓市'], ['10070', '535', '海城'], ['10139', '546', '武穴'], ['10176', '560', '阿拉尔'], ['10181', '541', '广德'], ['10197', '550', '陵水'], ['10201', '552', '简阳'], ['781', '548', '潮州'], ['820', '552', '甘孜'], ['10080', '535', '昌图'], ['10140', '546', '天门'], ['10177', '560', '图木舒克'], ['10182', '541', '宿松'], ['782', '548', '揭阳'], ['821', '552', '凉山'], ['10144', '535', '开原'], ['10168', '546', '仙桃'], ['10178', '560', '五家渠'], ['783', '548', '云浮'], ['10169', '546', '潜江'], ['10171', '546', '宜城'], ['10065', '552', '峨眉'], ['10179', '546', '神农架'], ['10104', '552', '西昌'], ['10044', '545', '济源'], ['10059', '545', '西平'], ['10158', '540', '方家山']]
        self.Industry = [['210500', '10100', '互联网/电子商务'], ['160400', '10100', '计算机软件'], ['160000', '10100', 'IT服务(系统/数据/维护)'], ['160500', '10100', '电子技术/半导体/集成电路'], ['160200', '10100', '计算机硬件'], ['300100', '10100', '通信/电信/网络设备'], ['160100', '10100', '通信/电信运营、增值服务'], ['160600', '10100', '网络游戏'], ['180000', '10200', '基金/证券/期货/投资'], ['180100', '10200', '保险'], ['10100', '0', 'IT|通信|电子|互联网'], ['300500', '10200', '银行'], ['10200', '0', '金融业'], ['300900', '10200', '信托/担保/拍卖/典当'], ['10800', '0', '房地产|建筑业'], ['140000', '10800', '房地产/建筑/建材/工程'], ['10900', '0', '商业服务'], ['140100', '10800', '家居/室内设计/装饰装潢'], ['10300', '0', '贸易|批发|零售|租赁业'], ['140200', '10800', '物业管理/商业中心'], ['10400', '0', '文体教育|工艺美术'], ['200300', '10900', '专业服务/咨询(财会/法律/人力资源等)'], ['10500', '0', '生产|加工|制造'], ['200302', '10900', '广告/会展/公关'], ['11500', '0', '交通|运输|物流|仓储'], ['201400', '10900', '中介服务'], ['10000', '0', '服务业'], ['201300', '10900', '检验/检测/认证'], ['11300', '0', '文化|传媒|娱乐|体育'], ['300300', '10900', '外包服务'], ['11600', '0', '能源|矿产|环保'], ['120400', '10300', '快速消费品（食品/饮料/烟酒/日化）'], ['11100', '0', '政府|非盈利机构'], ['120200', '10300', '耐用消费品（服饰/纺织/皮革/家具/家电）'], ['11400', '0', '农|林|牧|渔|其他'], ['170500', '10300', '贸易/进出口'], ['170000', '10300', '零售/批发'], ['300700', '10300', '租赁服务'], ['201100', '10400', '教育/培训/院校'], ['120800', '10400', '礼品/玩具/工艺美术/收藏品/奢侈品'], ['121000', '10500', '汽车/摩托车'], ['129900', '10500', '大型设备/机电设备/重工业'], ['121100', '10500', '加工制造（原料加工/模具）'], ['121200', '10500', '仪器仪表及工业自动化'], ['210600', '10500', '印刷/包装/造纸'], ['120700', '10500', '办公用品及设备'], ['121300', '10500', '医药/生物工程'], ['121500', '10500', '医疗设备/器械'], ['300000', '10500', '航空/航天研究与制造'], ['150000', '11500', '交通/运输'], ['301100', '11500', '物流/仓储'], ['121400', '10000', '医疗/护理/美容/保健/卫生服务'], ['200600', '10000', '酒店/餐饮'], ['200800', '10000', '旅游/度假'], ['210300', '11300', '媒体/出版/影视/文化传播'], ['200700', '11300', '娱乐/体育/休闲'], ['130000', '11600', '能源/矿产/采掘/冶炼'], ['120500', '11600', '石油/石化/化工'], ['130100', '11600', '电气/电力/水利'], ['201200', '11600', '环保'], ['200100', '11100', '政府/公共事业/非盈利机构'], ['120600', '11100', '学术/科研'], ['100000', '11400', '农/林/牧/渔'], ['100100', '11400', '跨领域经营'], ['990000', '11400', '其他']]

    @staticmethod
    def handle0(n):
        num = str(n)
        if len(num) == 1:
            nu = '0' + num
        else:
            nu = num
        return nu

    # 1
    def params_get(self):
        t = time.time()
        node = int(t * 1000)
        today = time.localtime(t)
        yesterday = time.localtime(t - 86400)
        lastweek = time.localtime(t - 604800)

        today_year = str(today.tm_year)
        today_month = self.handle0(today.tm_mon)
        today_day = self.handle0(today.tm_mday)

        yesterday_year = str(yesterday.tm_year)[-2:]
        yesterday_month = self.handle0(yesterday.tm_mon)
        yesterday_day = self.handle0(yesterday.tm_mday)

        lastweek_year = str(lastweek.tm_year)
        lastweek_month = self.handle0(lastweek.tm_mon)
        lastweek_day = self.handle0(lastweek.tm_mday)

        today_info = today_year + today_month + today_day
        yesterday_info = yesterday_year + yesterday_month + yesterday_day
        lastweek_info = lastweek_year + lastweek_month + lastweek_day
        lastyear_info = str(today.tm_year - 1) + today_month + today_day

        front = [
            '46ba3dcc4781446ab7b77f11468b6c36',
            '15f87159b7c440078fedea3be92d26e7',
            '97ea329932f04166b268e0cb0b2bfd61',
            'bf37a85ca31548808cc4f6222bf07783',
            'c02dc6d312fe483194fece4f996ae8ba'
        ]
        max_len = len(front) - 1
        params = {
            "_": f"{node}",
            "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 800000)}",
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
            "S_CreateDate": f"{lastyear_info},{today_info}",
            "isNewList": "true",
            "sort": "time",
            "time": f"{node - random.randint(6, 15)}",
            "isStash": "true",
            "tagIds": [],
            "page": 1,
            "pageSize": 20,
        }
        return params   #

    # 1
    @staticmethod
    def headers_get():
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'text/plain',
            'Referer': 'https://rd5.zhaopin.com/talent-bank',
            'Sec-Fetch-Mode': 'cors',
            "sec-fetch-site": "same-origin",
            "origin": "https://rd5.zhaopin.com",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            "cookie": cookie
        }
        return headers

    # TODO 1
    def do_get_all(self):
        """
        获取到简历夹里面的简历信息 然后再分析每一个
        :return:
        """
        params = self.params_get()
        headers = self.headers_get()
        info = self.session.post(self.url, json=params, headers=headers, verify=False)
        time.sleep(5)
        # 这里还没有处理详细信息传递 先写着
        try:
            data = json.loads(info.text)['data']
        except KeyError:
            print('键错误，被反爬了，页面不能抓到数据，需要刷新cookie')
            return None
        else:
            total = data['total']
        if total == 0:
            receivers = ''
            msg = '智联:简历收藏夹里面没有简历需要处理'
            send_rtx_msg(receivers, msg)
            return None
        else:
            pass
            receivers = ''
            msg = f'智联:简历收藏夹里面有{total}条简历, 现在准备上传到简历库'
            send_rtx_msg(receivers, msg)
            dataList = data['dataList']
            self.params_get_2(dataList, self.session)

    def params_get_2(self, dataList, session):
        if dataList:
            for data in dataList:
                number = data['number']
                k = data['k']
                t = data['t']

                ts = time.time()
                node = int(ts * 1000)
                front = [
                    '46ba3dcc4781446ab7b77f11468b6c36',
                    '15f87159b7c440078fedea3be92d26e7',
                    '97ea329932f04166b268e0cb0b2bfd61',
                    'bf37a85ca31548808cc4f6222bf07783',
                    'cf560800ad4b40588066133829b3d2f6'
                ]
                max_len = len(front) - 1
                params = {
                    "_": f"{node}",
                    'resumeNo': f'{number}_1_1%3B{k}%3B{t}',
                    "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 800000)}",
                    'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
                    'openFrom': 5
                }
                headers = {
                    "Connection": "Keep-Alive",
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "zh-CN,zh;q=0.9",
                    "cookie": cookie,
                    "referer": f"https://rd5.zhaopin.com/resume/detail?resumeNo={number}_1_1%3B{k}%3B{t}&openFrom=5",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
                    "x-requested-with": "XMLHttpRequest",
                    # "authority": "rd5.zhaopin.com",
                    # "method": "GET",
                    # "path": f"/api/rd/resume/detail?_={t}&resumeNo={number}_1_1%3B{k}%3B1565919566477&x-zp-page-request-id=19687738042c4124bffb9a3ee6475dd6-1565919927778-974149&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5"
                }
                url = "https://rd5.zhaopin.com/api/rd/resume/detail?" + f'_={node}&resumeNo={number}_1_1%3B{k}%3B{t}&x-zp-page-request-id={params["x-zp-page-request-id"]}&x-zp-client-id=e5cc6ae7-13f9-4f11-ac17-f37439ae1de5'
                resp = session.get(url, headers=headers, verify=False)
                time.sleep(10)
                try:
                    info = json.loads(resp.text)
                except Exception as e:
                    LOG.info('error：', e)
                else:
                    resume, account = self.deal_info(info)
                    self.post_resume(resume, account)

    def post_resume(self, jr, account):
        info = {
            'account': account,
            'data': [jr]
        }
        # with open('ttt.txt', 'w', encoding='utf-8') as f:
        #     f.write(str(info))
        print(info)
        url = 'http://testhr.gets.com:8989/api/autoInsertResume.php'
        # url = 'http://hr.gets.com:8989/api/autoOwnerResume.php?'
        try:
            rq = self.session.post(url, json=info)
        except Exception as e:
            LOG.error('目标计算机拒绝链接,错误:', e)
        else:
            LOG.info(f'数据的插入详情为:{unquote(rq.text)}')

    def deal_info(self, info):
        now_year = datetime.datetime.now().year
        resume = {
            'resume_from': 2,
        }
        data = info['data']
        detail = data['detail']          # dict
        jobResume = data['jobResume']    # dict   #null
        candidate = data['candidate']    # dict
        job = data['job']                # dict
        account = "广州外宝电子商务有限公司"       # job['orgName']

        name = candidate['userName']
        mobile_phone = candidate['mobilePhone'] if candidate['mobilePhone'] else '0'
        company_dpt = 1
        resume_key = ''
        gender = detail['Gender']
        date_of_birth = candidate['birthYear'] + self.handle0(candidate['birthMonth']) + self.handle0(candidate['birthDay'])
        current_residency = candidate['address']
        years_of_working = now_year - int(candidate['workYearsRangeId'][:4])
        prove = detail['HuKouProvinceId']
        cit = detail['HuKouCityId']

        Shi = ''
        Sheng = ''
        for num in self.province:
            if num[0] == prove:
                Sheng = num[1]
                break
            else:
                continue

        if Sheng:
            for ofni in self.city:
                if ofni[1] == prove:
                    if ofni[0] == cit:
                        Shi = ofni[2]
                        break
                    else:
                        continue

        hukou = Sheng + ' ' + Shi

        salary_num = detail['CurrentSalary']
        if salary_num:
            sn = str(salary_num)
            if len(sn) == 9:
                if sn[4] == '0':
                    current_salary = sn[:4] + '~' + sn[5:]
                else:
                    current_salary = sn[:4] + '~' + sn[4:]
            elif len(sn) == 10:
                current_salary = sn[:5] + '~' + sn[5:]
            else:
                current_salary = ''
        else:
            current_salary = ''

        politics_status = detail['PoliticsBackGround'] if detail['PoliticsBackGround'] else ''
        marital_status = '1' if detail['MaritalStatus'] == '2' else '2'
        address = candidate['address']
        zip_code = detail['PostalCode'] if detail['PostalCode'] else ''
        email = candidate['email'] if candidate['email'] else ''
        home_telephone = candidate['homePhone'] if candidate['homePhone'] else ''
        work_phone = candidate['workPhone'] if candidate['workPhone'] else ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = detail['CommentContent'] if detail['CommentContent'] else ''
        i_can_start = ''
        employment_type = '1' if detail['DesiredEmploymentType'] == '2' else '2'
        industry_expected = []                                                        # 数字 未处理
        iey = detail['DesiredIndustry']
        if iey:
            for y in self.Industry:
                if iey in y:
                    industry_expected.append(y[2])
                    break

        working_place_expected = '广州' if candidate['cityId'] == '763' else '其它'
        num_expected = detail['DesiredSalaryScope']
        time_now = time.time()
        dateModified = time.strftime('%Y-%m-%d', time.localtime(time_now))
        # print('更新日期:', dateModified)
        if num_expected:
            sn = str(num_expected)
            if len(sn) == 9:
                if sn[4] == '0':
                    salary_expected = sn[:4] + '~' + sn[5:]
                else:
                    salary_expected = sn[:4] + '~' + sn[4:]
            elif len(sn) == 10:
                salary_expected = sn[:5] + '~' + sn[5:]
            else:
                salary_expected = '面议'
        else:
            salary_expected = '面议'

        job_function_expected = ''
        current_situation = ''

        word_experience = []
        info_experience = detail['WorkExperience']
        if info_experience:
            for ifo in info_experience:

                Sly = ifo['Salary']       # 0800110000
                if Sly[0] == '0':
                    if Sly[5] == '0':
                        Salary = Sly[1:5] + '~' + Sly[6:]
                    else:
                        Salary = Sly[1:5] + '~' + Sly[5:]
                else:
                    Salary = Sly[:5] + '~' + Sly[5:]

                dic = {
                    '公司名': ifo['CompanyName'],
                    '开始时间': ifo['DateStart'],
                    '结束时间': ifo['DateEnd'] if ifo['DateEnd'] else '',
                    '工作标题': ifo['JobTitle'],
                    '工作描述': ifo['WorkDescription'],
                    '薪资范围': Salary
                }
                word_experience.append(dic)

        project_experience = []
        pec = detail['ProjectExperience']
        if pec:
            for i in pec:
                dic = {
                    '开始时间': i['DateStart'],
                    '结束时间': i['DateEnd'],
                    '项目名字': i['ProjectName'],
                    '责任描述': i['ProjectResponsibility'],
                    '项目描述': i['ProjectDescription']
                }
                project_experience.append(dic)

        education = []
        edu = detail['EducationExperience']
        if edu:
            for i in edu:
                dic = {
                    '开始时间': i['DateStart'],
                    '结束时间': i['DateEnd'],
                    '学校': i['SchoolName'],
                    '专业': i['MajorName']
                }
                education.append(dic)

        honors_awards = ''
        practical_experience = ''
        training = detail['Training'] if detail['Training'] else ''
        language = str(detail['LanguageSkill']) if detail['LanguageSkill'] else ''
        it_skill = ''

        certifications = []
        cer = detail['AchieveCertificate']
        if cer:
            for i in cer:
                dic = {
                    '获得时间': i['AchieveDate'],
                    '证书名字': i['CertificateName']
                }
                certifications.append(dic)

        is_viewed = 1
        resume_date = dateModified
        get_type = 1
        external_resume_id = data['resumeNumber'][:-4]

        resume['name'] = name
        resume['mobile_phone'] = mobile_phone
        resume['company_dpt'] = company_dpt
        resume['resume_key'] = resume_key
        resume['gender'] = gender
        resume['date_of_birth'] = date_of_birth
        resume['current_residency'] = current_residency
        resume['years_of_working'] = years_of_working
        resume['hukou'] = hukou
        resume['current_salary'] = current_salary
        resume['politics_status'] = politics_status
        resume['marital_status'] = marital_status
        resume['address'] = address
        resume['zip_code'] = zip_code
        resume['email'] = email
        resume['home_telephone'] = home_telephone
        resume['work_phone'] = work_phone
        resume['personal_home_page'] = personal_home_page
        resume['excecutiveneed'] = excecutiveneed
        resume['self_assessment'] = self_assessment
        resume['i_can_start'] = i_can_start
        resume['employment_type'] = employment_type
        resume['industry_expected'] = industry_expected[0] if industry_expected else ''
        resume['working_place_expected'] = working_place_expected
        resume['salary_expected'] = salary_expected
        resume['job_function_expected'] = job_function_expected
        resume['current_situation'] = current_situation
        resume['word_experience'] = word_experience
        resume['project_experience'] = project_experience
        resume['education'] = education
        resume['honors_awards'] = honors_awards
        resume['practical_experience'] = practical_experience
        resume['training'] = training
        resume['language'] = language
        resume['it_skill'] = it_skill
        resume['certifications'] = certifications
        resume['is_viewed'] = is_viewed
        resume['resume_date'] = resume_date
        resume['get_type'] = get_type
        resume['external_resume_id'] = external_resume_id
        resume['labeltype'] = 1    # 1 待处理 2 有意向 3 已发面试 4 不合适

        return resume, account

    def run(self):
        self.do_get_all()


if __name__ == '__main__':
    app = Cart()
    app.run()
