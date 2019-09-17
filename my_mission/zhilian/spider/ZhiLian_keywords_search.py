# -*- coding: utf-8 -*-
# 智联：银河在线：关键字搜索
import datetime
import importlib
import json
import re
import random
import requests
import pymysql
# from urllib.request import quote
from utils.logger import *    # includes logging infos
from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Queue
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# =================================== #

# 这里是本地存的cookies,如果是selenium格式的话就不用这里了，直接用
# 如果是标准的大字典模式，就可以交给self.get_api_cookie()来处理
ip_info = "http://192.168.1.112:8000/api/"
# 其实这个搜索也只需要一个人的账号就好了 不用其它账号了
from spider import python_config
receivers = python_config.receivers
company_name = python_config.company_name
handler = python_config.handler


class ZhiLian(object):
    def __init__(self):
        try:
            with open('cookies.json', 'r') as f:
                self.cookies = json.loads(f.read())['cookies']
        except Exception as e:
            print('error', e)
            self.cookies = []
        self.base_url = 'https://www.zhaopin.com/'
        self.goal_url = 'https://rd5.zhaopin.com/job/manage'
        self.hr_url = 'https://rd5.zhaopin.com/resume/apply'
        self.search_url = 'https://rd5.zhaopin.com/custom/searchv2/result'
        self.session = requests.Session()
        self.base_dir = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))
        self.refresh_queue = Queue()   # 刷新消息的队列
        self.output_queue = Queue()    # 发布时间的队列
        self.province = [['548', '广东'], ['546', '湖北'], ['556', '陕西'], ['552', '四川'], ['535', '辽宁'], ['536', '吉林'],
                         ['539', '江苏'], ['544', '山东'], ['540', '浙江'], ['549', '广西'], ['541', '安徽'], ['532', '河北'],
                         ['533', '山西'], ['534', '内蒙古'], ['537', '黑龙江'], ['542', '福建'], ['543', '江西'], ['545', '河南'],
                         ['547', '湖南'], ['550', '海南'], ['553', '贵州'], ['554', '云南'], ['555', '西藏'], ['557', '甘肃'],
                         ['558', '青海'], ['559', '宁夏'], ['560', '新疆'], ['563', '台湾省']]
        self.city = [['10301', '560', '双河'], ['10302', '560', '铁门关'], ['10303', '550', '三沙'], ['10304', '563', '台北'],
                     ['763', '548', '广州'], ['765', '548', '深圳'], ['736', '546', '武汉'], ['854', '556', '西安'],
                     ['801', '552', '成都'], ['931', '535', '东港'], ['600', '535', '大连'], ['613', '536', '长春'],
                     ['599', '535', '沈阳'], ['635', '539', '南京'], ['702', '544', '济南'], ['703', '544', '青岛'],
                     ['653', '540', '杭州'], ['639', '539', '苏州'], ['636', '539', '无锡'], ['654', '540', '宁波'],
                     ['719', '545', '郑州'], ['749', '547', '长沙'], ['681', '542', '福州'], ['682', '542', '厦门'],
                     ['622', '537', '哈尔滨'], ['565', '532', '石家庄'], ['664', '541', '合肥'], ['773', '548', '惠州'],
                     ['576', '533', '太原'], ['831', '554', '昆明'], ['707', '544', '烟台'], ['768', '548', '佛山'],
                     ['691', '543', '南昌'], ['822', '553', '贵阳'], ['932', '560', '北屯区'], ['933', '556', '西咸新区'],
                     ['587', '534', '呼和浩特'], ['785', '549', '南宁'], ['799', '550', '海口'], ['847', '555', '拉萨'],
                     ['864', '557', '兰州'], ['878', '558', '西宁'], ['886', '559', '银川'], ['890', '560', '乌鲁木齐'],
                     ['566', '532', '唐山'], ['577', '533', '大同'], ['588', '534', '包头'], ['614', '536', '吉林市'],
                     ['623', '537', '齐齐哈尔'], ['665', '541', '芜湖'], ['692', '543', '景德镇'], ['720', '545', '开封'],
                     ['737', '546', '黄石'], ['750', '547', '株洲'], ['764', '548', '韶关'], ['786', '549', '柳州'],
                     ['800', '550', '三亚'], ['802', '552', '自贡'], ['823', '553', '六盘水'], ['832', '554', '曲靖'],
                     ['848', '555', '昌都'], ['855', '556', '铜川'], ['865', '557', '嘉峪关'], ['879', '558', '海东'],
                     ['887', '559', '石嘴山'], ['891', '560', '克拉玛依'], ['567', '532', '秦皇岛'], ['578', '533', '阳泉'],
                     ['589', '534', '乌海'], ['601', '535', '鞍山'], ['615', '536', '四平'], ['624', '537', '鸡西'],
                     ['640', '539', '昆山'], ['655', '540', '温州'], ['666', '541', '蚌埠'], ['683', '542', '莆田'],
                     ['693', '543', '萍乡'], ['704', '544', '淄博'], ['721', '545', '洛阳'], ['738', '546', '十堰'],
                     ['751', '547', '湘潭'], ['787', '549', '桂林'], ['803', '552', '攀枝花'], ['824', '553', '遵义'],
                     ['833', '554', '玉溪'], ['849', '555', '山南'], ['856', '556', '宝鸡'], ['866', '557', '金昌'],
                     ['880', '558', '海北'], ['888', '559', '吴忠'], ['892', '560', '吐鲁番'], ['907', '550', '洋浦市/洋浦经济开发区'],
                     ['568', '532', '邯郸'], ['579', '533', '长治'], ['590', '534', '赤峰'], ['602', '535', '抚顺'],
                     ['616', '536', '辽源'], ['625', '537', '鹤岗'], ['650', '539', '常熟'], ['656', '540', '嘉兴'],
                     ['667', '541', '淮南'], ['684', '542', '三明'], ['694', '543', '九江'], ['705', '544', '枣庄'],
                     ['722', '545', '平顶山'], ['739', '546', '宜昌'], ['752', '547', '衡阳'], ['766', '548', '珠海'],
                     ['788', '549', '梧州'], ['804', '552', '泸州'], ['825', '553', '安顺'], ['834', '554', '保山'],
                     ['850', '555', '日喀则'], ['857', '556', '咸阳'], ['867', '557', '白银'], ['881', '558', '黄南'],
                     ['889', '559', '固原'], ['893', '560', '哈密'], ['906', '559', '中卫'], ['10153', '550', '琼海'],
                     ['569', '532', '邢台'], ['580', '533', '晋城'], ['591', '534', '通辽'], ['603', '535', '本溪'],
                     ['617', '536', '通化'], ['626', '537', '双鸭山'], ['652', '539', '张家港'], ['657', '540', '湖州'],
                     ['668', '541', '马鞍山'], ['685', '542', '泉州'], ['695', '543', '新余'], ['706', '544', '东营'],
                     ['723', '545', '安阳'], ['740', '546', '襄阳'], ['753', '547', '邵阳'], ['767', '548', '汕头'],
                     ['789', '549', '北海'], ['805', '552', '德阳'], ['826', '553', '铜仁'], ['835', '554', '昭通'],
                     ['851', '555', '那曲'], ['858', '556', '渭南'], ['868', '557', '天水'], ['882', '558', '海南州'],
                     ['894', '560', '昌吉'], ['10183', '550', '儋州'], ['570', '532', '保定'], ['581', '533', '朔州'],
                     ['592', '534', '鄂尔多斯'], ['604', '535', '丹东'], ['618', '536', '白山'], ['627', '537', '大庆'],
                     ['658', '540', '绍兴'], ['669', '541', '淮北'], ['696', '543', '鹰潭'], ['724', '545', '鹤壁'],
                     ['741', '546', '鄂州'], ['754', '547', '岳阳'], ['790', '549', '防城港'], ['806', '552', '绵阳'],
                     ['827', '553', '黔西南'], ['836', '554', '楚雄'], ['852', '555', '阿里'], ['859', '556', '延安'],
                     ['869', '557', '武威'], ['883', '558', '果洛'], ['895', '560', '博尔塔拉'], ['10184', '550', '五指山'],
                     ['571', '532', '张家口'], ['582', '533', '晋中'], ['593', '534', '呼伦贝尔'], ['605', '535', '锦州'],
                     ['619', '536', '松原'], ['628', '537', '伊春'], ['659', '540', '金华'], ['670', '541', '铜陵'],
                     ['687', '542', '漳州'], ['697', '543', '赣州'], ['708', '544', '潍坊'], ['725', '545', '新乡'],
                     ['742', '546', '荆门'], ['755', '547', '常德'], ['791', '549', '钦州'], ['807', '552', '广元'],
                     ['828', '553', '毕节'], ['837', '554', '红河'], ['853', '555', '林芝'], ['860', '556', '汉中'],
                     ['870', '557', '张掖'], ['884', '558', '玉树'], ['896', '560', '巴音郭楞'], ['10185', '550', '文昌'],
                     ['572', '532', '承德'], ['583', '533', '运城'], ['594', '534', '兴安盟'], ['606', '535', '营口'],
                     ['620', '536', '白城'], ['629', '537', '佳木斯'], ['637', '539', '徐州'], ['660', '540', '衢州'],
                     ['671', '541', '安庆'], ['688', '542', '南平'], ['698', '543', '吉安'], ['709', '544', '济宁'],
                     ['726', '545', '焦作'], ['743', '546', '孝感'], ['756', '547', '张家界'], ['769', '548', '江门'],
                     ['792', '549', '贵港'], ['808', '552', '遂宁'], ['829', '553', '黔东南'], ['838', '554', '文山'],
                     ['861', '556', '榆林'], ['871', '557', '平凉'], ['885', '558', '海西'], ['897', '560', '阿克苏'],
                     ['10186', '550', '万宁'], ['573', '532', '沧州'], ['584', '533', '忻州'], ['595', '534', '锡林郭勒盟'],
                     ['607', '535', '阜新'], ['621', '536', '延边'], ['630', '537', '七台河'], ['638', '539', '常州'],
                     ['661', '540', '舟山'], ['672', '541', '黄山'], ['689', '542', '龙岩'], ['699', '543', '宜春'],
                     ['710', '544', '泰安'], ['727', '545', '濮阳'], ['744', '546', '荆州'], ['757', '547', '益阳'],
                     ['770', '548', '湛江'], ['793', '549', '玉林'], ['809', '552', '内江'], ['830', '553', '黔南'],
                     ['862', '556', '安康'], ['872', '557', '酒泉'], ['898', '560', '克孜勒苏'], ['10187', '550', '东方'],
                     ['574', '532', '廊坊'], ['585', '533', '临汾'], ['596', '534', '乌兰察布'], ['608', '535', '辽阳'],
                     ['631', '537', '牡丹江'], ['641', '539', '南通'], ['662', '540', '台州'], ['673', '541', '滁州'],
                     ['690', '542', '宁德'], ['700', '543', '抚州'], ['711', '544', '威海'], ['728', '545', '许昌'],
                     ['745', '546', '黄冈'], ['758', '547', '郴州'], ['771', '548', '茂名'], ['794', '549', '百色'],
                     ['810', '552', '乐山'], ['840', '554', '西双版纳'], ['863', '556', '商洛'], ['873', '557', '庆阳'],
                     ['899', '560', '喀什'], ['10188', '550', '定安'], ['575', '532', '衡水'], ['586', '533', '吕梁'],
                     ['597', '534', '巴彦淖尔'], ['609', '535', '盘锦'], ['632', '537', '黑河'], ['642', '539', '连云港'],
                     ['663', '540', '丽水'], ['674', '541', '阜阳'], ['701', '543', '上饶'], ['712', '544', '日照'],
                     ['729', '545', '漯河'], ['746', '546', '咸宁'], ['759', '547', '永州'], ['772', '548', '肇庆'],
                     ['795', '549', '贺州'], ['811', '552', '南充'], ['841', '554', '大理'], ['874', '557', '定西'],
                     ['900', '560', '和田'], ['10058', '556', '兴平'], ['10189', '550', '屯昌'], ['598', '534', '阿拉善盟'],
                     ['610', '535', '铁岭'], ['633', '537', '绥化'], ['643', '539', '淮安'], ['675', '541', '宿州'],
                     ['713', '544', '莱芜'], ['730', '545', '三门峡'], ['747', '546', '随州'], ['760', '547', '怀化'],
                     ['796', '549', '河池'], ['812', '552', '眉山'], ['842', '554', '德宏'], ['875', '557', '陇南'],
                     ['901', '560', '伊犁'], ['910', '533', '永济市'], ['10190', '550', '澄迈'], ['611', '535', '朝阳'],
                     ['634', '537', '大兴安岭'], ['644', '539', '盐城'], ['714', '544', '临沂'], ['731', '545', '南阳'],
                     ['748', '546', '恩施'], ['761', '547', '娄底'], ['774', '548', '梅州'], ['813', '552', '宜宾'],
                     ['843', '554', '丽江'], ['876', '557', '临夏'], ['902', '560', '塔城'], ['10031', '534', '乌审旗'],
                     ['10191', '550', '临高'], ['612', '535', '葫芦岛'], ['645', '539', '扬州'], ['677', '541', '六安'],
                     ['715', '544', '德州'], ['732', '545', '商丘'], ['762', '547', '湘西'], ['775', '548', '汕尾'],
                     ['814', '552', '广安'], ['844', '554', '怒江'], ['877', '557', '甘南'], ['903', '560', '阿勒泰'],
                     ['10023', '535', '兴城'], ['10057', '546', '公安'], ['10061', '560', '石河子'], ['10081', '537', '安达'],
                     ['10122', '536', '公主岭'], ['10192', '550', '琼中'], ['10470', '556', '杨凌'], ['646', '539', '镇江'],
                     ['678', '541', '亳州'], ['716', '544', '聊城'], ['733', '545', '信阳'], ['776', '548', '河源'],
                     ['815', '552', '达州'], ['845', '554', '迪庆'], ['904', '549', '来宾'], ['10143', '532', '遵化'],
                     ['10159', '537', '双城'], ['10193', '550', '保亭'], ['10198', '536', '珲春'], ['647', '539', '泰州'],
                     ['679', '541', '池州'], ['717', '544', '滨州'], ['734', '545', '周口'], ['777', '548', '阳江'],
                     ['816', '552', '雅安'], ['846', '554', '临沧'], ['905', '549', '崇左'], ['10157', '534', '满洲里'],
                     ['10160', '537', '尚志'], ['10163', '554', '普洱'], ['10164', '560', '奎屯市'], ['10194', '550', '白沙'],
                     ['680', '541', '宣城'], ['718', '544', '菏泽'], ['735', '545', '驻马店'], ['778', '548', '清远'],
                     ['817', '552', '巴中'], ['10069', '541', '凤阳'], ['10161', '537', '绥芬河'], ['10195', '550', '昌江'],
                     ['648', '539', '宿迁'], ['779', '548', '东莞'], ['818', '552', '资阳'], ['10166', '560', '乌苏'],
                     ['10196', '550', '乐东'], ['10510', '537', '肇东市'], ['780', '548', '中山'], ['819', '552', '阿坝'],
                     ['911', '539', '太仓市'], ['10070', '535', '海城'], ['10139', '546', '武穴'], ['10176', '560', '阿拉尔'],
                     ['10181', '541', '广德'], ['10197', '550', '陵水'], ['10201', '552', '简阳'], ['781', '548', '潮州'],
                     ['820', '552', '甘孜'], ['10080', '535', '昌图'], ['10140', '546', '天门'], ['10177', '560', '图木舒克'],
                     ['10182', '541', '宿松'], ['782', '548', '揭阳'], ['821', '552', '凉山'], ['10144', '535', '开原'],
                     ['10168', '546', '仙桃'], ['10178', '560', '五家渠'], ['783', '548', '云浮'], ['10169', '546', '潜江'],
                     ['10171', '546', '宜城'], ['10065', '552', '峨眉'], ['10179', '546', '神农架'], ['10104', '552', '西昌'],
                     ['10044', '545', '济源'], ['10059', '545', '西平'], ['10158', '540', '方家山']]
        self.Industry = [['210500', '10100', '互联网/电子商务'], ['160400', '10100', '计算机软件'],
                         ['160000', '10100', 'IT服务(系统/数据/维护)'], ['160500', '10100', '电子技术/半导体/集成电路'],
                         ['160200', '10100', '计算机硬件'], ['300100', '10100', '通信/电信/网络设备'],
                         ['160100', '10100', '通信/电信运营、增值服务'], ['160600', '10100', '网络游戏'],
                         ['180000', '10200', '基金/证券/期货/投资'], ['180100', '10200', '保险'], ['10100', '0', 'IT|通信|电子|互联网'],
                         ['300500', '10200', '银行'], ['10200', '0', '金融业'], ['300900', '10200', '信托/担保/拍卖/典当'],
                         ['10800', '0', '房地产|建筑业'], ['140000', '10800', '房地产/建筑/建材/工程'], ['10900', '0', '商业服务'],
                         ['140100', '10800', '家居/室内设计/装饰装潢'], ['10300', '0', '贸易|批发|零售|租赁业'],
                         ['140200', '10800', '物业管理/商业中心'], ['10400', '0', '文体教育|工艺美术'],
                         ['200300', '10900', '专业服务/咨询(财会/法律/人力资源等)'], ['10500', '0', '生产|加工|制造'],
                         ['200302', '10900', '广告/会展/公关'], ['11500', '0', '交通|运输|物流|仓储'], ['201400', '10900', '中介服务'],
                         ['10000', '0', '服务业'], ['201300', '10900', '检验/检测/认证'], ['11300', '0', '文化|传媒|娱乐|体育'],
                         ['300300', '10900', '外包服务'], ['11600', '0', '能源|矿产|环保'],
                         ['120400', '10300', '快速消费品（食品/饮料/烟酒/日化）'], ['11100', '0', '政府|非盈利机构'],
                         ['120200', '10300', '耐用消费品（服饰/纺织/皮革/家具/家电）'], ['11400', '0', '农|林|牧|渔|其他'],
                         ['170500', '10300', '贸易/进出口'], ['170000', '10300', '零售/批发'], ['300700', '10300', '租赁服务'],
                         ['201100', '10400', '教育/培训/院校'], ['120800', '10400', '礼品/玩具/工艺美术/收藏品/奢侈品'],
                         ['121000', '10500', '汽车/摩托车'], ['129900', '10500', '大型设备/机电设备/重工业'],
                         ['121100', '10500', '加工制造（原料加工/模具）'], ['121200', '10500', '仪器仪表及工业自动化'],
                         ['210600', '10500', '印刷/包装/造纸'], ['120700', '10500', '办公用品及设备'],
                         ['121300', '10500', '医药/生物工程'], ['121500', '10500', '医疗设备/器械'],
                         ['300000', '10500', '航空/航天研究与制造'], ['150000', '11500', '交通/运输'], ['301100', '11500', '物流/仓储'],
                         ['121400', '10000', '医疗/护理/美容/保健/卫生服务'], ['200600', '10000', '酒店/餐饮'],
                         ['200800', '10000', '旅游/度假'], ['210300', '11300', '媒体/出版/影视/文化传播'],
                         ['200700', '11300', '娱乐/体育/休闲'], ['130000', '11600', '能源/矿产/采掘/冶炼'],
                         ['120500', '11600', '石油/石化/化工'], ['130100', '11600', '电气/电力/水利'], ['201200', '11600', '环保'],
                         ['200100', '11100', '政府/公共事业/非盈利机构'], ['120600', '11100', '学术/科研'],
                         ['100000', '11400', '农/林/牧/渔'], ['100100', '11400', '跨领域经营'], ['990000', '11400', '其他']]

        # self.db = pymysql.connect(host=host,
        #                           port=port,
        #                           user=user,
        #                           password=password,
        #                           database=database)
        # self.cursor = self.db.cursor()

        # 开启基本的信息
        # self.path = "chromedriver.exe"
        self.driver = webdriver.Chrome()
        self.options = webdriver.ChromeOptions()
        # self.driver.maximize_window()

    @staticmethod
    def get_api_cookie(cook):
        """
        从接口获取cookie
        :return: selenium 可用的 cookies 格式
        """
        cookie = []
        for key in cook:
            dic = dict()
            dic['domain'] = 'zhaopin.com'
            dic['path'] = '/'
            dic['name'] = key
            dic['value'] = cook[key]
            cookie.append(dic)

        return cookie

    def do_cookies(self, cooki):
        for cook in cooki:  # 这里是cookies的信息
            if len(cook) < 6:
                new = dict(cook, **{
                    "domain": "zhaopin.com",
                    # "expires": "2019-08-07T03:19:00.679Z",
                    "path": "/",
                    # "httpOnly": False,
                })
            else:
                new = cook
            self.driver.add_cookie(new)

    def get_post_page(self):
        # 获取招聘信息页面
        self.driver.get(self.base_url)    # 打开最基本页面注入cookies
        self.driver.delete_all_cookies()

        if type(self.cookies) == dict:
            cooki = self.get_api_cookie(self.cookies)
            self.do_cookies(cooki)
        elif type(self.cookies) == list:
            self.do_cookies(self.cookies)

        time.sleep(3)
        self.driver.refresh()
        # 以下为打开新窗口，加载页面
        # self.driver.execute_script('window.open();')
        # self.driver.switch_to.window(self.driver.window_handles[1])
        # =================================================== #

        self.driver.get(self.search_url)   # 访问目标网站
        time.sleep(2)
        self.driver.refresh()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except Exception as e:
            LOG.error('*=*=*=*=* 没有找到元素可能是页面元素信息变更 *=*=*=*=*')
            LOG.error('*=*=*=* 现在需要管理员重新登录页面来刷新cookie *=*=*=*')
            msg = f"""
********* HR 数据自动化 *********
负责人：{handler}
状态原因：智联{company_name}关键字搜索程序需要手动登陆
处理标准：请24小时内人为到服务器登陆处理等待状态
"""
            self.send_rtx_msg(msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》程序中断，需要维护信息了《《《《《《')

        time.sleep(5)

        coo = self.driver.get_cookies()
        cook = list()
        for i in coo:
            if 'expiry' in i:
                del i['expiry']
            cook.append(i)
        # LOG.info('》》》刷新本地的Cookies，保持高可用《《《')
        self.save_cookies(cook)
        # =========================================================================================== #
        LOG.info('本地的cookies文件已经刷新')

        self.search_page()
        self.scroll_page()

    def scroll_page(self, n=1):
        """
        滑动屏幕用的
        :param n:
        :return:
        """
        for h in range(n):
            self.driver.execute_script(
               "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                   a=70 * h, b=70 * (h + 1)))
            time.sleep(0.2)

    def send_rtx_msg(self, msg):
        """
        rtx 提醒
        :param receivers:
        :param msg:
        :return:
        """
        post_data = {
            "sender": "系统机器人",
            "receivers": receivers,
            "msg": msg,
        }
        requests.Session().post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)

    def search_page(self):
        # self.driver.get(self.search_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="searchv2-intro__show-helper"]/img'))
            )
        except Exception as e:
            msg = f"""
********* HR 数据自动化 *********
负责人：f{handler}
状态原因：智联{company_name}关键字搜索程序因为未知原因程序未能进入准确位置
处理标准：请到服务器端查看问题后重启程序，可以找相关技术人员协助
"""
            # self.send_rtx_msg(msg)
        else:
            time.sleep(1)
            photo = self.driver.find_element_by_xpath('//div[@class="searchv2-intro__show-helper"]/img')
            self.driver.execute_script("arguments[0].click();", photo)

        time.sleep(5)
        self.chose_expect_place()   # 选择广州
        # self.chose_date()           # 选择一个月

        # 从这里可以设置循环，然后循环处理职位和公司信息

        _POS_, _CMP_, k_v = self.get_api_pos()
        time.sleep(1)

        for pos in _POS_:
            self.input_position(pos)       # 选择职位》》》可以传递岗位
            search = self.driver.find_element_by_xpath('//div[@class="pull-right"]/button[3]/i')
            self.driver.execute_script("arguments[0].click();", search)
            time.sleep(5)
            whole_num = self.get_whole_numbers()  # 返回 int 类型 数据 总共符合的数量
            # print('总共的数量:', whole_num)  # 这个大前提下总共的数量

            if whole_num == 0:
                LOG.info('0= 没有符合的简历信息')
                continue
            if whole_num > 60:
                # 翻页
                next_pg = self.driver.find_element_by_xpath('//button[@class="btn-next"]')
                self.driver.execute_script("arguments[0].click();", next_pg)
                time.sleep(3)
                self.driver.execute_script("arguments[0].click();", next_pg)
                time.sleep(3)
            # else:
                v = k_v[pos]
                v_add_user = v[1]
                v_receiver = v[0]
                self.handle_search(pos, v_add_user, v_receiver)  # 这里主要处理有信息的简历
            else:
                v = k_v[pos]
                v_add_user = v[1]
                v_receiver = v[0]
                self.handle_search(pos, v_add_user, v_receiver)  # 这里主要处理有信息的简历

        box1 = self.driver.find_element_by_xpath('//div[@id="form-item--3"]/div[1]/input')
        box1.clear()

        for cmp in _CMP_:
            self.input_working(cmp)  # 选择公司》》》可以传递公司
            time.sleep(1)
            search = self.driver.find_element_by_xpath('//div[@class="pull-right"]/button[3]/i')
            self.driver.execute_script("arguments[0].click();", search)
            time.sleep(5)
            whole_num = self.get_whole_numbers()  # 返回 int 类型 数据 总共符合的数量
            # print('总共的数量:', whole_num)  # 这个大前提下总共的数量
            if whole_num == 0:
                LOG.info('0= 没有符合的简历信息')
                continue
            else:
                v = k_v[cmp]
                v_add_user = v[1]
                v_receiver = v[0]
                self.handle_search(cmp, v_add_user, v_receiver)  # 这里主要处理有信息的简历

        box2 = self.driver.find_element_by_xpath('//div[@id="form-item-9"]/div[1]/input')
        box2.clear()

    def handle_search(self, key_word, v_add_user, v_receiver):
        tr = self.driver.find_elements_by_xpath('//tbody/tr')
        num = len(tr)
        # print('num::', num)   # 每一页的数量
        for td in range(num):
            if td % 2 == 0:
                continue
            else:
                try:
                    name = self.driver.find_element_by_xpath(f'//tbody/tr[{td}]/td[2]/div/a')
                    print('name::', name.text)
                except Exception as e:
                    print('error:', e)
                    continue
                else:
                    if '已查看' in name.text:
                        print('内容已经被查看, 自动跳过需求')
                        self.scroll_page(td)
                        time.sleep(1)
                        continue
                    else:
                        self.driver.execute_script("arguments[0].click();", name)
                        time.sleep(1)
                        try:
                            self.handle_search_detail(key_word, v_add_user, v_receiver)
                        except:
                            print('请先处理验证码，然后再继续(不要关闭当前窗口)')
                            input('>>')
                            break
                        self.scroll_page(td)

    def handle_search_detail(self, key_word, v_add_user, v_receiver):
        time.sleep(1)
        window = self.driver.window_handles
        self.driver.switch_to.window(self.driver.window_handles[len(window)-1])
        time.sleep(1)
        now_page_url = self.driver.current_url

        resumeNo_handle = now_page_url.split('&')[1:][1]
        main_resumeNo = resumeNo_handle.split('%3B')

        resumeNo_key = main_resumeNo[1]    # FB9BCEB64574FD986F14309ACCC91031
        resumeNo_ts = main_resumeNo[2]     # 1565776032783

        ID_info = self.driver.find_element_by_xpath("//div[@class='resume-content__header']/span/span[1]").text[3:]
        # print("ID_info::", ID_info)   # JOOVsp)MbdFln4dJF8d2mA
        params = self.params_get(ID_info, resumeNo_key, resumeNo_ts)
        headers = self.headers_get()
        info = self.do_get_requests_detail(params, headers)
        resume, eid = self.deal_info(info, key_word)
        # print('resume::', resume)
        self.driver.close()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(5)
        if resume:
            self.post_resume(resume, v_add_user, v_receiver, eid)

    def post_resume(self, resume, v_add_user, v_receiver, eid):
        info = {
            'add_user': v_add_user,
            'data': [resume]
        }
        try:
            print("info::", json.dumps(info))
            url = 'http://hr.gets.com:8989/api/autoInsertResume.php?'
            # url = 'http://testhr.gets.com:8989/api/autoInsertResume.php?'
            rq = self.session.post(url, json=info)
        except Exception as e:
            print(e)
            print('字符编码出问题，已经跳过')
        else:
            with open('post_resume.json', 'a') as fl:
                fl.write(json.dumps(info) + ',\n')
            LOG.info(f'数据的插入详情为:{rq.text}, 接收者是{v_receiver}')
            # send_rtx_msg(v_receiver, f'插入的信息的简历id为:{eid}')

    def deal_info(self, info, key_word):
        if not info.get('data'):
            return '', ''
        now_year = datetime.datetime.now().year
        resume = {
            'resume_from': 2,
        }
        data = info['data']
        detail = data.get('detail')          # dict
        if not detail:
            return ''
        candidate = data['candidate']    # dict

        name = candidate['userName']
        mobile_phone = candidate['mobilePhone'] if candidate.get('mobilePhone') else '0'
        resume_key = key_word
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

        politics_status = detail['PoliticsBackGround']
        marital_status = '1' if detail['MaritalStatus'] == '2' else '2'
        address = candidate['address'] if candidate['address'] else ''
        zip_code = detail['PostalCode'] if detail['PostalCode'] else ''
        email = candidate['email'] if candidate['email'] else ''
        home_telephone = candidate['homePhone'] if candidate['homePhone'] else ''
        work_phone = candidate['workPhone'] if candidate['workPhone'] else ''
        personal_home_page = ''
        excecutiveneed = ''
        self_assessment = detail['CommentContent'] if detail.get('CommentContent') else ''
        i_can_start = ''
        employment_type = '1' if detail['DesiredEmploymentType'] == '2' else '2'
        industry_expected = []                                                        # 数字 未处理
        iey = detail['DesiredIndustry']
        if iey:
            for y in self.Industry:
                if iey in y:
                    industry_expected.append(y[2])
                    break

        DesiredPosition = detail['DesiredPosition'][0] if detail['DesiredPosition'] else ''
        working_place_expected = '广州' if '763' in DesiredPosition.get('DesiredCityDistrict') else '其它'
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
                try:
                    if Sly[0] == '0':
                        if Sly[5] == '0':
                            Salary = Sly[1:5] + '~' + Sly[6:]
                        else:
                            Salary = Sly[1:5] + '~' + Sly[5:]
                    else:
                        Salary = Sly[:5] + '~' + Sly[5:]
                except Exception as e:
                    Salary = 'None'
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
        get_type = 2
        external_resume_id = data['resumeNumber'][:-4]
        resume_logo = candidate['photo']

        resume['name'] = name
        resume['mobile_phone'] = mobile_phone
        resume['company_dpt'] = 1                          # 广州 义乌 但是这个表肯能不传这个信息
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
        resume['resume_logo'] = resume_logo

        return resume, external_resume_id

    def handle0(self, n):
        if len(n) == 1:
            num = f'0{n}'
        else:
            num = n
        return num

    def do_get_requests_detail(self, params, headers):
        url = "https://rd5.zhaopin.com/api/rd/resume/detail?"
        try:
            response = self.session.get(url, params=params, headers=headers, verify=False)
        except:
            LOG.error('status_code: <404> NOT FOUND')
        else:
            time.sleep(7)
            info = json.loads(response.text)
            if info.get('code') == 4:
                print('请替换cookie后回车')
                input('>>')
                return None
            return info

    @staticmethod
    def params_get(ID_info, key, ts):
        t = time.time()
        node = int(t * 1000)
        front = [
            '46ba3dcc4781446ab7b77f11468b6c36',
            '15f87159b7c440078fedea3be92d26e7',
            '97ea329932f04166b268e0cb0b2bfd61',
            'bf37a85ca31548808cc4f6222bf07783',
            'ab21f32d3b93418495b69a0b6b3f84dd',
            '914b5ee54b914c71a986c1ca8a163109'
        ]
        max_len = len(front) - 1
        params = {
            "_": f"{node}",
            "x-zp-page-request-id": f"{front[random.randint(0, max_len)]}-{node - random.randint(50, 1000)}-{random.randint(200000, 999999)}",
            'x-zp-client-id': 'e5cc6ae7-13f9-4f11-ac17-f37439ae1de5',
            'resumeNo': f'{ID_info}_1_1;{key};{ts}'
        }
        return params

    @staticmethod
    def headers_get():
        from spider import cookies
        cookie = importlib.reload(cookies).cookie
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'text/plain',
            'Sec-Fetch-Mode': 'cors',
            "sec-fetch-site": "same-origin",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            "cookie": cookie
        }
        return headers

    @staticmethod
    def get_api_pos():
        p = requests.get('http://hr.gets.com:8989/api/autoGetKeyword.php').text
        time.sleep(0.5)
        # p = '[{"id":"124","keywords":"facebook\u5e7f\u544a\u6295\u653e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"123","keywords":"\u7269\u6d41\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"122","keywords":"SEO","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"121","keywords":"\u96f6\u552e\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"120","keywords":"\u51fa\u8d27\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"119","keywords":"SEN","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"118","keywords":"\u7f51\u7edc\u8425\u9500\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"117","keywords":"\u7f8e\u5de5","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"116","keywords":"\u62e3\u8d27\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"115","keywords":"\u6253\u5305\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"114","keywords":"\u8d28\u68c0","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"113","keywords":"\u4ed3\u7ba1\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"112","keywords":"\u5e94\u6536\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"111","keywords":"\u5e94\u4ed8\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"110","keywords":"\u5e94\u4ed8\u4f1a\u8ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"109","keywords":"\u5e94\u6536\u4f1a\u8ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"108","keywords":"\u4f1a\u8ba1\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"107","keywords":"\u8d22\u52a1\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"106","keywords":"\u51fa\u7eb3","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"105","keywords":"\u8d22\u52a1\u6587\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"104","keywords":"\u65e5\u8bed\u4e9a\u9a6c\u900a\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"103","keywords":"\u5c0f\u8bed\u79cd\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"102","keywords":"\u65e5\u8bed\u62c5\u5f53","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"101","keywords":"\u65e5\u8bed\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"100","keywords":"\u4e9a\u9a6c\u900a\u65e5\u8bed\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"99","keywords":"\u65e5\u8bed\u4e9a\u9a6c\u900a\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"98","keywords":"\u4ea7\u54c1\u5f00\u53d1\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"97","keywords":"\u5916\u8d38\u8ddf\u5355","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"96","keywords":"\u4ea7\u54c1\u7f16\u8f91","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"95","keywords":"\u91c7\u8d2d\u52a9\u7406","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"94","keywords":"\u4ea7\u54c1\u6587\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"93","keywords":"\u884c\u653f\u6587\u5458","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"92","keywords":"\u7535\u5546\u5ba2\u670d","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"91","keywords":"\u529e\u516c\u5ba4\u6587\u5458","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"90","keywords":"\u6587\u5458","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"89","keywords":"\u91c7\u8d2d","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"88","keywords":"\u91c7\u8d2d\u4e13\u5458","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"87","keywords":"\u4e9a\u9a6c\u900a\u8fd0\u8425\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"86","keywords":"\u4ea7\u54c1\u5f00\u53d1","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"85","keywords":"\u7bb1\u5305\u4e70\u624b","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"84","keywords":"\u5f00\u53d1\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"83","keywords":"\u978b\u5b50\u4e70\u624b","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"82","keywords":"\u670d\u88c5\u4e70\u624b","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"81","keywords":"\u4eba\u4e8b\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"80","keywords":"\u9ad8\u7ea7\u62db\u8058\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"79","keywords":"\u62db\u8058\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"78","keywords":"\u62db\u8058\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"77","keywords":"joom \u9500\u552e\u4e3b\u7ba1","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"76","keywords":"joom\u9500\u552e\u4e13\u5458","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"75","keywords":"joom\u8fd0\u8425","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"74","keywords":"ebay\u8fd0\u8425\u4e13\u5458","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"73","keywords":"ebay\u9500\u552e\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"72","keywords":"ebay\u8d1f\u8d23\u4eba","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"71","keywords":"ebay\u8fd0\u8425","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"70","keywords":"ebay\u9500\u552e","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"69","keywords":"wish\u8fd0\u8425\u4e3b\u7ba1","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"68","keywords":"\u8de8\u5883\u7535\u5546\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"67","keywords":"wish\u9500\u552e\u4e3b\u7ba1","sort":"-1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"66","keywords":"\u5916\u8d38\u4e1a\u52a1\u5458","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"65","keywords":"wish\u9500\u552e\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"64","keywords":"\u5e73\u53f0\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"63","keywords":"\u5e73\u53f0\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"62","keywords":"wish\u8fd0\u8425\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"61","keywords":"\u72ec\u7acb\u7ad9\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"60","keywords":"\u72ec\u7acb\u7ad9\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"59","keywords":"\u963f\u91cc\u5df4\u5df4\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"58","keywords":"Alibaba","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"57","keywords":"joom","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"56","keywords":"wish","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"55","keywords":"eaby","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"54","keywords":"AliExpress","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"53","keywords":"amazon","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"52","keywords":"\u901f\u5356\u901a\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"51","keywords":"\u901f\u5356\u901a\u7ecf\u7406","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"50","keywords":"\u901f\u5356\u901a\u4e3b\u7ba1","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"49","keywords":"\u901f\u5356\u901a\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"48","keywords":"\u901f\u5356\u901a\u5ba2\u670d","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"47","keywords":"\u901f\u5356\u901a\u52a9\u7406","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"46","keywords":"wish\u8fd0\u8425","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"45","keywords":"\u4e9a\u9a6c\u900a\u7ecf\u7406","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"44","keywords":"\u884c\u653f\u52a9\u7406","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"43","keywords":"\u4e9a\u9a6c\u900a\u4e3b\u7ba1","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"42","keywords":"wish\u9500\u552e","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2244"},{"id":"41","keywords":"\u4eba\u4e8b\u52a9\u7406","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"40","keywords":"\u884c\u653f\u7ecf\u7406","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"39","keywords":"\u884c\u653f\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"38","keywords":"\u7ee9\u6548\u85aa\u916c\u7ecf\u7406","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"37","keywords":"\u7ee9\u6548\u85aa\u916c\u4e3b\u7ba1","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"36","keywords":"\u4e9a\u9a6c\u900a\u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"35","keywords":"\u4e9a\u9a6c\u900a\u52a9\u7406","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"34","keywords":"\u4e9a\u9a6c\u900a\u5ba2\u670d","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"33","keywords":"Python","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"32","keywords":"\u4e9a\u9a6c\u900a\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"31","keywords":"PHP","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"30","keywords":"\u7ee9\u6548\u85aa\u916c\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"29","keywords":"\u884c\u653f\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"28","keywords":"\u884c\u653f\u524d\u53f0","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"27","keywords":"\u4eba\u4e8b\u4e13\u5458","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"26","keywords":"\u62db\u8058\u7ecf\u7406\/\u4e3b\u7ba1","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"25","keywords":"\u62db\u8058\u4e13\u5458\/\u52a9\u7406","sort":"0","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"24","keywords":"HRBP","sort":"1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"23","keywords":"\u8d5b\u7ef4","sort":"1","receiver":"\u5f20\u5b50\u73cf","rtx_new":"1","add_user":"2086"},{"id":"22","keywords":"\u5b9d\u89c6\u4f73","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"21","keywords":"\u73af\u7403\u6613\u8d2d","sort":"1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"20","keywords":"\u51ef\u4e50\u77f3","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"19","keywords":"\u4ef7\u4e4b\u94fe","sort":"1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"18","keywords":"\u667a\u84dd","sort":"1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"17","keywords":"\u901a\u62d3","sort":"1","receiver":"\u6768\u56fd\u73b2","rtx_new":"1","add_user":"2086"},{"id":"16","keywords":"\u8e0f\u6d6a\u8005","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"15","keywords":"\u6709\u68f5\u6811","sort":"1","receiver":"\u5f20\u5b50\u73cf","rtx_new":"1","add_user":"2086"},{"id":"14","keywords":"\u5e7f\u5dde\u5929\u89c5","sort":"1","receiver":"\u5f20\u5b50\u73cf","rtx_new":"1","add_user":"2086"},{"id":"13","keywords":"AliExpress \u901f\u5356\u901a\u9500\u552e \u901f\u5356\u901a\u8fd0\u8425","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2086"},{"id":"12","keywords":"\u8d26\u53f7\u7533\u8bc9\u5458 | \u5e97\u94fa\u98ce\u63a7\u4e13\u5458","sort":"0","receiver":"\u5f20\u5b50\u73cf","rtx_new":"1","add_user":"2215"},{"id":"11","keywords":"\u5e7f\u5dde\u5170\u4ead\u96c6\u52bf\u8d38\u6613(\u6df1\u5733)\u6709\u9650\u516c\u53f8","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"10","keywords":"\u6ee1\u7ffc","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"9","keywords":"\u5e7f\u5dde\u9ad8\u767b\u76ae\u5177","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"8","keywords":"\u7ec6\u523b","sort":"1","receiver":"\u5f20\u5b50\u73cf","rtx_new":"1","add_user":"2215"},{"id":"7","keywords":"\u767e\u4f26\u8d38\u6613","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"6","keywords":"\u5e7f\u5dde\u65f6\u6613\u4e2d\u4fe1\u606f\u79d1\u6280\u6709\u9650\u516c\u53f8","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"5","keywords":"\u5e7f\u5dde\u5e02\u84dd\u6df1\u8d38\u6613\u6709\u9650\u516c\u53f8","sort":"1","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"4","keywords":"\u4e9a\u9a6c\u900a\u8fd0\u8425  \u9500\u552e","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"3","keywords":"\u670d\u88c5\u4e70\u624b\/\u978b\u5b50\u4e70\u624b\/\u7bb1\u5305\u4e70\u624b","sort":"0","receiver":"\u9648\u6dfc\u7075","rtx_new":"1","add_user":"2114"},{"id":"2","keywords":"\u68d2\u8c37","sort":"1","receiver":"\u8042\u6e05\u5a1c","rtx_new":null,"add_user":"2086"},{"id":"1","keywords":"\u4e00\u767e\u79d1\u6280","sort":"1","receiver":"\u8042\u6e05\u5a1c","rtx_new":null,"add_user":"2086"}]'
        data = json.loads(p)
        pos = []
        cmp = []
        k_v = {}
        for key in data:
            kw = key.get('keywords')
            user = key.get('add_user')
            receiver = key.get('receiver')
            if receiver is None:
                receiver = '系统机器人'
            if key.get('sort') == '0':
                pos.append(kw)
            else:
                cmp.append(kw)
            k_v[kw] = (receiver, user)
        return pos, cmp, k_v

    def get_whole_numbers(self):
        try:
            print('do fast change page')
            time.sleep(10)
            page_source = self.driver.page_source
            time.sleep(3)
            reg = re.compile('<span data-bind="text: total" class="has-text-highlight">(\d*?)</span>')
            num = reg.findall(page_source)[0]
        except Exception as e:
            print('error:', e)
            return 0
        else:
            return int(num)

    def input_position(self, pos=None):
        time.sleep(1.5)
        box1 = self.driver.find_element_by_xpath('//div[@id="form-item--3"]/div[1]/input')
        box1.clear()
        box1.send_keys(pos)
        time.sleep(1.5)
        # checkbox = self.driver.find_element_by_xpath('//div[@class="k-form-item__content is-narrow"]//label[@role="checkbox"][1]/span[@class="k-checkbox__input"]/span/i')
        # self.driver.execute_script("arguments[0].click();", checkbox)
        # time.sleep(1.5)

    def input_working(self, tec=None):
        time.sleep(1.5)
        box2 = self.driver.find_element_by_xpath('//div[@id="form-item-9"]/div[1]/input')
        box2.clear()
        box2.send_keys(tec)
        time.sleep(1.5)

    def chose_date(self):
        time.sleep(2)
        optional = self.driver.find_element_by_xpath('//div[@class="k-form-item resume-filter-item resume-filter-item__search-apply-date"]//div[@class="k-select is-block"]//span/i[1]')
        self.driver.execute_script("arguments[0].click();", optional)
        try:
            time.sleep(3)
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="k-select-dropdown k-popper popFadeInUp"]/ul[1]/li[5]'))
            )
        except Exception as e:
            LOG.warning('选择日期失败，默认就是6个月了')
        else:
            time.sleep(1)
            chosen = self.driver.find_element_by_xpath('//div[@class="k-select-dropdown k-popper popFadeInUp"]/ul[1]/li[5]')
            self.driver.execute_script("arguments[0].click();", chosen)

        time.sleep(0.5)

    def chose_expect_place(self):
        optional2 = self.driver.find_element_by_xpath('//div[@id="form-item-35"]/div/div/input')
        self.driver.execute_script("arguments[0].click();", optional2)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@id="filter-item-dialog-select--35"]//div[@class="k-dialog__footer"]/a[2]'))
            )
        except Exception as e:
            LOG.warning('选择期望工作地点失败，默认就是全国')
        else:
            time.sleep(2)
            chosen_GZ = self.driver.find_element_by_xpath(
                '//div[@data-option-id="0-2"]//span[@class="k-checkbox__inner"]/i')
            self.driver.execute_script("arguments[0].click();", chosen_GZ)
            time.sleep(2)
            chosen_place_sure = self.driver.find_element_by_xpath(
                '//div[@id="filter-item-dialog-select--35"]//div[@class="k-dialog__footer"]/a[3]')
            self.driver.execute_script("arguments[0].click();", chosen_place_sure)

        time.sleep(1)

    # 丄============================================ #

    def do_next_pg(self):
        time.sleep(random.randint(3, 5))
        button = self.driver.find_element_by_xpath("//button[@class='btn-next'][1]")
        time.sleep(random.randint(3, 5))
        self.driver.execute_script("arguments[0].click();", button)

    def save_cookies(self, cook):
        dic = {
            'fresh_time': time.ctime(time.time()),
            'cookies': cook
        }
        jsn = json.dumps(dic)
        with open(self.base_dir + '\cookies.json', 'w') as f:
            f.write(jsn)
        time.sleep(1)

    def isLeapYear(self, year):
        """
        判断当前是否为平年，闰年
        :param year:
        :return:
        """
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        else:
            return False

    def dayBetweenDates(self, month1, day1):
        """
        1：为起始日期，2：为终止日期
        判断year1是否为闰年，选择year1当年每月的天数列表
        :param month1: 终止日期的月份
        :param day1: 终止日期的天数
        :return: int类型的天数信息(两个时间节点相减的信息)
        """
        # 先设置了默认为2019年
        year1 = 2019
        year2 = 2019
        # 获取今天的时间的信息
        nowtime = time.localtime(time.time())  # time.struct_time(tm_year=2016, tm_mon=4, tm_mday=7, tm_hour=10,
                                               # tm_min=3, tm_sec=27, tm_wday=3, tm_yday=98,
                                               # tm_isdst=0)
        month2 = nowtime.tm_mon  # 今天的月
        day2 = nowtime.tm_mday   # 今天的日
        # now_hour = nowtime.tm_hour  # 打开检查程序的小时数
        if self.isLeapYear(year1):
            # print(str(year1) + ':闰年')
            dayofmonth1 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  # 列表下标从0开始的 所以后面计算月份天数的时候，传入的月份应该-1
        else:
            # print(str(year1) + ':非闰年')
            dayofmonth1 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        year_temp = year2 - year1
        month_temp = month2 - month1

        if year_temp == 0:
            if month_temp == 0:
                days = day2 - day1
            else:
                # days = dayofmonth1[month1 - 1] - day1 + day2  # '掐头去尾'
                i = 1
                sum = 0
                # 假设计算3月5号到6月4号的天数，先计算3，4，5月的总天数,所以是 [month1 + i - 1-1]，然后减去5，加上4
                while i < month_temp + 1:
                    day = dayofmonth1[month1 + i - 1 - 1]
                    sum += day
                    i += 1
                days = sum - day1 + day2
        else:
            if self.isLeapYear(year2):
                dayofmonth2 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                year_days = 366
            else:
                dayofmonth2 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                year_days = 365
            i = 1
            sum1 = 0
            sum2 = 0
            middle_year_sum_days = 0

            # 获取小年份剩余的天数
            while i < month1:
                day = dayofmonth1[month1 - i - 1]
                sum1 += day
                i += 1
            other_days1 = year_days - sum1 - day1

            # 获取大年份经过的天数
            i = 1
            while i < month2:
                day = dayofmonth2[month2 - i - 1]
                sum2 += day
                i += 1
            other_days2 = sum2 + day2

            # 获取中间年份的天数
            i = 1
            while i < year_temp:
                middle_year = year1 + i
                if self.isLeapYear(middle_year):
                    year_day = 366
                else:
                    year_day = 365
                middle_year_sum_days += year_day
                i += 1
            days = middle_year_sum_days + other_days1 + other_days2

        return days    # 返回天数 int 类型

    @staticmethod
    def get_info_api(company='1'):
        time.sleep(0.5)
        if company == '广州市银河在线饰品有限公司':
            cy = '1'
        elif company == '广州外宝电子商务有限公司':
            cy = '2'
        elif company == '广州时时美电子商务有限公司':
            cy = '3'
        else:
            cy = '1'

        ifo = requests.get(f'{ip_info}get/refresh/{cy}/z').text         # 这里地址也需要修改  《《《《《
        time.sleep(1)
        info = json.loads(ifo)
        # print('info:', type(info), info)   # dict
        return info

    def ipage(self):
        """
        就是判断下页码数量没记错的话
        :return:
        """
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=300 * h, b=300 * (h + 1)))
            time.sleep(0.5)

        page = self.driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    def run(self):
        """
        程序主启动，包含》大 《异常检测
        :return:
        """
        self.get_post_page()
        self.driver.quit()


def send_rtx_msg(msg):
    """
    rtx 提醒
    :param receivers:
    :param msg:
    :return:
    """
    post_data = {
        "sender": "系统机器人",
        "receivers": receivers,
        "msg": msg,
    }
    ZhiLian().session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


def main():
    while True:
        print('回车以重新打开检索窗口')
        input('>>')
        try:
            app1 = ZhiLian()
            app1.run()
        except:
            msg = f"""
********* HR 数据自动化 *********
负责人:{handler}
状态原因：智联{company_name}关键字搜索程序频率过高
处理标准：请到服务器先处理验证码信息,然后关闭检索窗口再在程序窗口回车重启程序
"""
            send_rtx_msg(msg)


if __name__ == '__main__':
    main()

