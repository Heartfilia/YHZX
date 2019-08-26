# -*- coding: utf-8 -*-
# 智联招聘的信息爬取
# 这里面的信息为旧 新信息在服务器里面 不过里面也能做到该有的功能 有的需求是变化的 有的地方有bug 但是服务器那边是修改好了的
import datetime
import json
import re
import random
from threading import Thread
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
from helper.Our_company import o_comp   # 导入我们公司的信息 list
# from helper.Positions import POS        # 导入需要关注排行的位置的信息
from helper.company import competitor   # 导入竞争者的信息
from spider import Message
# =================================== #
from helper.mysql_config import *
import urllib3
from urllib.request import unquote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# =================================== #

# 这里是本地存的cookies,如果是selenium格式的话就不用这里了，直接用
# 如果是标准的大字典模式，就可以交给self.get_api_cookie()来处理
ip_info = "http://192.168.6.112:8000/api/"


class ZhiLian(object):
    def __init__(self):
        with open('cookies.json', 'r') as f:
            self.cookies = json.loads(f.read())['cookies']
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
        # self.driver.switch_to_window(self.driver.window_handles[1])

        # =================================================== #

        self.driver.get(self.search_url)   # 访问目标网站
        # self.driver.get(self.goal_url)   # 访问目标网站
        time.sleep(2)
        self.driver.refresh()
        try:
            # 判断是否登录成功还是在登录页面
            # 1.寻找元素在不在 >>> 2.1.不在的话异常，然后异常里面进行阻塞,处理了后接着运行 2.2.存在表明登录成功
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH,
                     '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except Exception as e:
            LOG.error('*=*=*=* 没有找到元素，可能是页面元素信息变更 *=*=*=*=*')
            LOG.error('*=*=*=* 现在需要管理员重新登录页面来刷新cookie *=*=*=*')
            # from spider import Message
            # receivers = '聂清娜;张子珏'
            receivers = '朱建坤'
            msg = '智联招聘自动追踪程序:广州市银河在线饰品有限公司:24小时内重新登录来继续抓取信息'
            Message.send_rtx_msg(receivers, msg)
            WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="rd55-header__inner"]/ul/li[6]/a[@class="rd55-header__base-button"]'))
            )
        except KeyboardInterrupt:
            LOG.warning('》》》》》》程序中断，需要维护信息了《《《《《《')

        time.sleep(5)

        # 此处是存cookie操作 暂时不管 也没有完成

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

        # time.sleep(3)
        # self.do_task()          # 检测简历信息 超过30天发布 和 指定天数未刷新的
        # self.send_msg()         # 发送发布和刷新信息
        # time.sleep(3)
        # ==========================================以下和简历相关=================================== #
        # from .Resume_Crawl import run       # 遍历每个简历信息

        # run()                                # 开始跑程序

        # self.cursor.close()
        # self.db.close()
        # time.sleep(random.randint(5, 10))
        # self.get_hr_book()           # ====获取hr简历信息====  需  要  打  开  ===================== #
        # time.sleep(30)

    # 丅========================================== #
        self.search_page()
        self.scroll_page()

    def scroll_page(self, n=1):
        for h in range(n):
            self.driver.execute_script(
               "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                   a=200 * h, b=200 * (h + 1)))
            time.sleep(1)

    def search_page(self):
        # self.driver.get(self.search_url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@class="searchv2-intro__show-helper"]/img'))
            )
        except Exception as e:
            receivers = '朱建坤'
            msg = '智联相关的程序需要重新检测！'
            Message.send_rtx_msg(receivers, msg)
        else:
            time.sleep(1)
            photo = self.driver.find_element_by_xpath('//div[@class="searchv2-intro__show-helper"]/img')
            self.driver.execute_script("arguments[0].click();", photo)

        time.sleep(5)
        self.chose_expect_place()   # 选择广州
        self.chose_date()           # 选择一个月

        # 从这里可以设置循环，然后循环处理职位和公司信息

        # _POS_ = self.get_api_pos()
        _POS_ = ['Ali', 'ebay', '速卖通', '文员', 'Amazon', 'php', 'python', ]
        _CMP_ = ['科技', '商务', '外贸']
        time.sleep(1)
        for pos in _POS_:
            self.input_position(pos)       # 选择职位》》》可以传递岗位
            time.sleep(1)
            for cmp in _CMP_:
                self.input_working(cmp)        # 选择公司》》》可以传递公司
                time.sleep(1)

                search = self.driver.find_element_by_xpath('//div[@class="pull-right"]/button[3]/i')
                self.driver.execute_script("arguments[0].click();", search)

                time.sleep(5)

                whole_num = self.get_whole_numbers()   # 返回 int 类型 数据 总共符合的数量

                if whole_num == 0:
                    LOG.info('0= 没有符合的简历信息')
                    continue
                else:
                    self.scroll_page()   # 处理第一页的信息之前 滑动一下屏幕 这里面有延时
                    self.handle_search()  # 这里主要处理有信息的简历

    def handle_search(self):
        tr = self.driver.find_elements_by_xpath('//tbody/tr')
        num = len(tr)
        for td in range(num):
            if td % 2 == 0:
                continue
            else:
                try:
                    name = self.driver.find_element_by_xpath(f'//tbody/tr[{td}]/td[2]/div/a')
                except Exception as e:
                    # 没有详细信息
                    continue
                else:
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", name)
                    time.sleep(5)
                    self.handle_search_detail()
                    self.scroll_page(td)

    def handle_search_detail(self):
        time.sleep(1)
        window = self.driver.window_handles
        self.driver.switch_to_window(self.driver.window_handles[len(window)-1])
        time.sleep(1)
        self.driver.refresh()
        time.sleep(1)
        now_page_url = self.driver.current_url
        # print(now_page_url)   # https://rd5.zhaopin.com/resume/detail?keyword=amazon&z=402101&resumeNo=JOOVsp%29MbdFln4dJF8d2mA_1_1%3BFB9BCEB64574FD986F14309ACCC91031%3B1565776032783&openFrom=1

        resumeNo_handle = now_page_url.split('&')[1:][1]
        main_resumeNo = resumeNo_handle.split('%3B')

        resumeNo_key = main_resumeNo[1]
        resumeNo_ts = main_resumeNo[2]

        ID_info = self.driver.find_element_by_xpath("//div[@class='resume-content__header']/span/span[1]").text[3:]
        # print("ID_info::", ID_info)   # JOOVsp)MbdFln4dJF8d2mA
        params = self.params_get(ID_info, resumeNo_key, resumeNo_ts)
        headers = self.headers_get()
        info = self.do_get_requests_detail(params, headers)
        resume = self.deal_info(info)
        # print('resume::', resume)
        self.driver.close()
        self.driver.switch_to_window(self.driver.window_handles[len(window) - 2])
        time.sleep(1)
        self.driver.refresh()
        time.sleep(3)
        if resume:
            self.post_resume(resume)

    def post_resume(self, resume):
        info = {
            'account': 'account',
            'data': [resume]
        }
        print("info::", info)
        url = 'http://testhr.gets.com:8989/api/autoInsertResume.php?'
        rq = self.session.post(url, json=info)
        LOG.info(f'数据的插入详情为:{unquote(rq.text)}')

    def deal_info(self, info):
        if not info.get('data'):
            return ''
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
        time_now = int(data['dateModified'] / 1000)
        dateModified = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_now))
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
        get_type = 2
        external_resume_id = data['resumeNumber'][:-4]

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

        return resume

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
            time.sleep(3)
            # print(response.text)
            # LOG.info('status_code: <200> OK')
            return json.loads(response.text)

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
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'text/plain',
            'Sec-Fetch-Mode': 'cors',
            "sec-fetch-site": "same-origin",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            "cookie": "rd_resume_srccode=402101; jobRiskWarning=true; rt=e8c06b41952d485a8a1a163e402eb667; __utmc=269921210; dywec=95841923; __utma=269921210.745608370.1565774809.1565774809.1565774809.1; JSlogie=15521262081; login_point=67827992; at=ba965698103246b298864313e3b2cabc; sts_deviceid=16c45ccbf571fb-056500981cae5-3f385c06-2073600-16c45ccbf5840d; login-type=b; uiioit=3b622a6459640e644664456a5d6e5a6e5564543856775c7751682c622a64596408644c646; urlfrom=121126445; urlfrom2=121126445; adfcid=none; __utmz=269921210.1565774809.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); acw_tc=2760824315657748143842495e09da051d49ae4e178c13df2092bc658a154c; adfcid2=none; adfbid=0; __utmt=1; dywez=95841923.1564567034.8.3.dywecsr=ihr.zhaopin.com|dyweccn=(referral)|dywecmd=referral|dywectr=undefined|dywecct=/talk/manage.html; adfbid2=0; diagnosis=0; sts_chnlsid=Unknown; sts_sg=1; dywea=95841923.2660674703251129300.1565774809.1565774809.1565774809.1; rd_resume_actionId=1565774813220655193256; zp-route-meta=uid=655193256,orgid=67827992; x-zp-client-id=da383633-9f36-4c66-a026-46cd3d6e5746; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1565774805; sts_sid=16c8f738caba1b-0e9bbadc75f771-3c375f0d-2073600-16c8f738cac640; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1565851719; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22655193256%22%2C%22%24device_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2216c45ccbfa4528-023d4aa56bf0c6-3f385c06-2073600-16c45ccbfa51a0%22%7D; rd_resume_srccode=402101; zp_src_url=https%3A%2F%2Frd5.zhaopin.com%2Fcustom%2Fsearchv2%2Fresult; c=iacZehsh-1565851764817-234e64e198724-258072056; _fmdata=RjVcPpTGcffpZk5l0yUErfjZkmBHOjkP6kSghdv6CtCOPuhtK9AFNBZkksKynlUPU7gZblkF2fifR7bH5CeKxE2bHxQ0SPUA0HYhj9k0Iro%3D; _xid=wMwX2dUYMRRqmhWzSFQ1byhjLl1FXWHDFzoVDl4fLr%2BU0MFD0UyhC1N1Uma2SJbxu6yyjyvYGVgCloV3FdO%2B6w%3D%3D; x-zp-dfp=zlzhaopin-1565851764147-f6ff5d1673abe; rd_resume_actionId=1565852122973655193256; dyweb=95841923.83.10.1565774809; __utmb=269921210.83.10.1565774809; sts_evtseq=174"
        }
        return headers

    @staticmethod
    def get_api_pos():
        p = requests.get('http://192.168.6.112:8000/api/get/rate/z').text
        time.sleep(0.5)
        data = json.loads(p)
        pos = data['data']
        keywords = []
        for key in pos:
            keywords.append(key)
        return keywords

    def get_whole_numbers(self):
        try:
            time.sleep(3)
            page_source = self.driver.page_source
            time.sleep(3)
            reg = re.compile('<span data-bind="text: total" class="has-text-highlight">(\d*?)</span>', re.S)
            num = reg.findall(page_source)[0]
        except Exception as e:
            print('error:', e)
            return 0
        else:
            return int(num)

    def input_position(self, pos=None):
        time.sleep(0.8)
        box1 = self.driver.find_element_by_xpath('//div[@id="form-item--3"]/div[1]/input')
        box1.clear()
        box1.send_keys(pos)
        time.sleep(0.5)

    def input_working(self, tec=None):
        time.sleep(0.8)
        box2 = self.driver.find_element_by_xpath('//div[@id="form-item-9"]/div[1]/input')
        box2.clear()
        box2.send_keys(tec)
        time.sleep(0.5)

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
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@id="filter-item-dialog-select--35"]//div[@class="k-dialog__footer"]/a[2]'))
            )
        except Exception as e:
            LOG.warning('选择期望工作地点失败，默认就是全国')
        else:
            time.sleep(1)
            chosen_GZ = self.driver.find_element_by_xpath(
                '//div[@data-option-id="0-2"]//span[@class="k-checkbox__inner"]/i')
            self.driver.execute_script("arguments[0].click();", chosen_GZ)
            time.sleep(1)
            chosen_place_sure = self.driver.find_element_by_xpath(
                '//div[@id="filter-item-dialog-select--35"]//div[@class="k-dialog__footer"]/a[3]')
            self.driver.execute_script("arguments[0].click();", chosen_place_sure)

        time.sleep(0.5)

    # 丄============================================ #

    def get_hr_book(self):
        time.sleep(random.randint(3, 5))
        self.driver.get(self.hr_url)
        time.sleep(random.randint(3, 5))
        all_num = self.driver.find_element_by_xpath('//div[@class="k-tabs__nav-wrapper"]/div/div[1]/span[2]').text
        print('所有简历数量为：', all_num)
        all_page = self.driver.find_element_by_xpath('//span[@class="k-pagination__total"]').text
        reg = re.compile('(\d*)')
        page = int([i for i in reg.findall(all_page) if i != ''][0])    # 总共的页数
        print('所有页数为：', page)
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=500 * h, b=500 * (h + 1)))
            time.sleep(1)

        for _ in range(1, page+1):
            try:
                LOG.info(f'当前位置为第{_}页！')
                WebDriverWait(self.driver, 86400, poll_frequency=30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//button[@class="btn-next"]'))
                )
                for h in range(8):
                    self.driver.execute_script(
                        "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                            a=500 * h, b=500 * (h + 1)))
                    time.sleep(1)

            except Exception as e:
                LOG.debug('没有找到下一页')
                break
            else:
                self.parse_page()
                LOG.debug('准备前往下一页')
                if _ > 4:
                    LOG.info('只查询前5页简历信息，现在页码超过5页，退出查询')
                    break
                self.do_next_pg()

    def parse_page(self):
        time.sleep(random.randint(3, 5))
        # from spider import Message
        receivers = '聂清娜;张子珏'                                        # <<<======
        button = self.driver.find_element_by_xpath('//div[@class="resume-header__actions"]//i[@class="fa fa-th-list"]')
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(random.randint(3, 8))
        # print(self.driver.page_source)
        # 人员 ： //div[@class="fixable-list__body"]/div[1]//div[@class="user-name__inner"]/a/span/text()
        # 职位 ： //div[@class="fixable-list__body"]//p[@class="job-title"]/text()
        # 公司 ： //div[@class="fixable-list__body"]/div[2]//div[@class="cell-extend-simple"]//dl[1]/dd//li[1]/span[2]
        main_nodes = self.driver.find_elements_by_xpath('//div[@class="fixable-list__body"]/div[1]//div[@class="user-name__inner"]/a/span')

        time.sleep(random.randint(3, 8))
        for i in range(len(main_nodes)):
            staff = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]/div[1]//div[@class="user-name__inner"]/a/span').get_attribute('title')
            position = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]//p[@class="job-title"]')
            company = self.driver.find_element_by_xpath(f'//div[@class="fixable-list__body"][{i+1}]/div[2]//div[@class="cell-extend-simple"]//dl[1]/dd//li[1]/span[2]')
            time.sleep(1)
            dic = {
                "staff": staff if staff else '',
                "position": position.text if position else '',
                "company": company.text if company else ''
            }
            # jsd = json.dumps(dic)
            with open(self.base_dir + r'\resume.txt', 'a') as f:
                f.write(str(dic) + ',\n')
            # print('*-*-*-*-*-*-*-*-' * 6 + '\n', dic)

            if dic["staff"] in competitor:
                msg = f'应聘{dic["position"]}的{dic["staff"]}曾经在{dic["company"]}工作过'
                Message.send_rtx_msg(receivers, msg)

        LOG.info('抢人程序跑完了》》等待接下来的操作')

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

    def fresh_recruit(self):
        """
        2天前的刷新信息
        :return:
        """
        try:
            WebDriverWait(self.driver, 1800).until(
                EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
            )
        except Exception as e:
            LOG.error('*=*=*=* 没有找到元素，可能是页面元素信息变更 *=*=*=*=*')
            LOG.error('*=*=*=* 现在需要管理员重新登录页面来刷新cookie *=*=*=*')
            receivers = '朱建坤'                                              # <<<======
            msg = '智联相关的程序需要重新检测！'
            Message.send_rtx_msg(receivers, msg)
        else:
            time.sleep(3)
            ind = 0
            num = 0
            # 任务需求：检测到数据是2天没有刷新的就提醒
            # xpath: //tr[@class="k-table__row"]/td[3]/div/p/span
            # WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '')))
            # company = self.driver.find_element_by_xpath('//div[@class="user__basic"]/span[@class="user__name"]/span').text
            company = self.driver.find_element_by_xpath('//td[@class="k-table__column"][5]').get_attribute('title')
            # company = '广州市银河在线饰品有限公司'
            page = self.driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
            # print('fresh_recruit:page:', page)
            main_nodes = self.driver.find_elements_by_xpath('//table/tbody/tr[@class="k-table__row"]/td[3]')

            api_all = self.get_info_api(company)   # 从规定的api里面获取到需要的信息  # dict
            pstn = [i['info'] for i in api_all['data'] if i]

            page_source = self.driver.page_source

            if company.strip() == "广州市银河在线饰品有限公司":
                com = '1'
            elif company.strip() == "广州外宝电子商务有限公司":
                com = '2'
            elif company.strip() == "广州时时美电子商务有限公司":
                com = '3'
            else:
                com = '1'

            reg = re.compile('>刷新时间：(.*?)</span>', re.S)
            time.sleep(5)
            li = reg.findall(page_source)

            time.sleep(1)

            qunty_xp = len(main_nodes)
            qunty_re = len(li)

            if qunty_xp > qunty_re:
                minu = qunty_xp - qunty_re
                for _ in range(minu):
                    li.insert(0, '')

            for node in main_nodes:
                time.sleep(2)
                try:
                    posi = node.find_element_by_xpath('./div').get_attribute('title')   # 判断 如果不在就插入 在就不管
                except Exception as e:
                    LOG.warning('这个节点没有信息')
                    posi = ''

                try:
                    i = li[ind].strip()
                except:
                    i = ''

                if posi not in pstn:
                    if posi:
                        self.insert_mysql_one(com, posi)
                    lateRemind = '2'
                else:
                    y = api_all['data'][pstn.index(posi)]
                    y = y['lateRemind']
                    lateRemind = str(y)   # 获取需要提醒的天数

                ind += 1

                # print('简历时间 i:', i)    07-09 19:59（28天前）
                if i:
                    month = int(i[:2])     # 07
                    day = int(i[3:5])      # 27
                    # hour = int(i[6:8])  # 09
                    nums = self.dayBetweenDates(month, day)
                    self.update_mysql_one(posi, i[:5])
                    if nums > int(lateRemind):
                        num += 1  # 统计有几个信息超过指定天没有刷新，有一个就加1
                else:
                    LOG.warning('没有查找到时间节点')
                    self.update_mysql_one(posi, 'Null')
                    continue

            msg = f'您在{company}账号的第{page}页有{num}条简历信息超过规定天数没有刷新了'
            LOG.info(msg)
            self.refresh_queue.put(msg)
            return int(page)

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

    def update_mysql_one(self, posi, dtm):
        sql = f'update info set lastFresh = "{dtm}" where info = "{posi.strip()}" and account=1'

        try:
            LOG.info('数据库准备修改数据>>>>>>>')
            self.cursor.execute(sql)
            self.db.commit()
            time.sleep(0.3)
        except Exception as e:
            LOG.warning('数据错误已经回滚>>>>>>>')
            self.db.rollback()

    def insert_mysql_one(self, com, posi):
        # 方案一 ======== api插入  服务端会出错
        # time.sleep(0.5)
        # pos = quote(posi)        # 这里需要处理下url
        # post_url = f'http://127.0.0.1:8000/api/post/{com}/z/{pos}'
        # time.sleep(0.5)
        # self.session.post(post_url)
        # 方案二 ======== 直接插入
        sql = f'insert into info(info, isRemind, lateRemind, account, platform) values ("{posi.strip()}", "1" , "2", "{com}", "智联")'

        try:
            LOG.info('数据库准备输入>>>>>>>')
            self.cursor.execute(sql)
            self.db.commit()
            time.sleep(0.3)
        except Exception as e:
            LOG.warning('数据错误已经回滚>>>>>>>')
            self.db.rollback()

    def ipage(self):
        for h in range(8):
            self.driver.execute_script(
                "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                    a=500 * h, b=500 * (h + 1)))
            time.sleep(1)

        page = self.driver.find_elements_by_xpath('//div/ul[@class="k-pager"]/li')
        num = len(page)
        return num

    def release_date(self):
        """
        检测30天信息
        :return:
        """
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]'))
        )
        time.sleep(5)
        num = 0
        # 任务需求： 发布日期大于30天的提醒
        # xpath: //tr[@class="k-table__row"]/td[4]
        company = self.driver.find_element_by_xpath('//div[@class="rd55-header__login-point"]/span').text
        info = self.driver.find_elements_by_xpath('//tr[@class="k-table__row"]/td[4]')
        page = self.driver.find_element_by_xpath('//div/ul[@class="k-pager"]/li[contains(@class, "is-active")]').text
        for i in info:
            # i = " 2019-07-27 "
            i = i.text.strip()
            # print('30 i :', i)
            if i:
                month = int(i[5:7])
                day = int(i[-2:])
                nums = self.dayBetweenDates(month, day)
                if nums > 30:
                    num += 1  # 统计有几个信息超过30天没有 重新发布/上线
            else:
                continue
        msg = f'您在{company}账号的第{page}页有{num}个信息超过30天没有 重新发布/上线'
        LOG.info(msg)
        self.output_queue.put(msg)

    def fresh_cookie(self):
        # 获取cookie 相当于刷新
        rep = requests.get(self.base_url, cookies=self.cookies)
        time.sleep(5)
        coo = rep.cookies
        print(coo)
        cook = requests.utils.dict_from_cookiejar(coo)  # cookies 信息： {'at': 'bc68fccbe0994b6d8f20f10c6bf11e76',...
        print(cook)
        # return cook

    def send_msg(self):
        """
        发送消息的函数
        receivers = 字符串,多个信息用 英文分号 分割
        :return:
        """
        # receivers = '朱建坤'                                              # <<<======
        receivers = '聂清娜;张子珏'
        f_n = 0
        o_n = 0
        fresh_msg = ''
        output_msg = ''
        # 从消息队列中把应该获取的信息拼接，下面那个循环一样的
        for _ in range(self.refresh_queue.qsize()):
            if self.refresh_queue.empty():
                break
            else:
                m = self.refresh_queue.get()
                fresh_msg += m

        for _ in range(self.output_queue.qsize()):
            if self.output_queue.empty():
                break
            else:
                m = self.output_queue.get()
                output_msg += m

        fre_re = re.compile(r'(\d*)条简历信息')
        out_re = re.compile(r'(\d*)个信息')
        cmp_re = re.compile(r'您在(\w+)账号的第')
        nm = fre_re.findall(fresh_msg)
        om = out_re.findall(output_msg)
        comp = cmp_re.findall(fresh_msg)[0]
        com_re = re.compile(r'(\w+?)账号的第')
        company = com_re.findall(comp)[0]
        # print('company:::', company)
        for i in nm:
            f_n += int(i)
        if f_n > 0:
            msg = f'您在智联的<<{company}>>账号的招聘信息总共有{f_n}条超过规定天数没有刷新了请及时处理,修改提醒请点击\n' \
                  f'http://192.168.6.112:8000/admin \n然后在后台管理系统中处理'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送刷新信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
            print('msg:::', msg)
        else:
            LOG.info('>>>>>>>>>没有需要发送的<刷新>信息')

        for i in om:
            o_n += int(i)
        if o_n > 0:
            msg = f'您在智联的{company}账号的招聘信息总共有{o_n}条超过30天没有重新发布/上线'
            post_data = {
                "sender": "系统机器人",
                "receivers": receivers,
                "msg": msg,
            }
            LOG.info('》》》》》系统发送发布信息成功')
            self.session.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)
        else:
            LOG.info('>>>>>>>>>没有需要发送的<发布>信息')

    def do_task(self):
        """
        任务翻页以及处理同样的信息事情
        :return:
        """
        while True:
            # page 为总共有多少页
            page = self.ipage()
            # print(f'总共有:{page}页')
            # 搜索该页面的刷新信息
            nowpage = self.fresh_recruit()    # 返回当前所在的页面
            # 搜索该页面的发布信息
            LOG.info('*' * 50)
            self.release_date()
            # 此页面处理完毕后，判断页面是否有下一页，然后处理是否翻页
            if nowpage < page:
                # 有下一页，点击下一页
                button = self.driver.find_element_by_xpath('//div[@class="k-pagination pagination-jobs"]/button[2]')
                self.driver.execute_script("arguments[0].click();", button)
                LOG.info(f'在第{nowpage}页运行成功')
                time.sleep(5)
            else:
                break

    def test(self):
        """
        开发时候使用的测试函数
        :return:
        """
        # self.dayBetweenDates(1, 25)  # 直接返回天数
        # test01: 测试携带cookie登录
        self.get_post_page()      # 《《《 需要开
        self.driver.quit()

    def run(self):
        """
        程序主启动，包含》大 《异常检测
        :return:
        """
        self.get_post_page()
        self.driver.quit()


class Rate(object):
    """
    智能检测排名靠后问题程序
    """
    def __init__(self):
        self.base_url = 'https://sou.zhaopin.com/'
        self.js_url = 'https://fe-api.zhaopin.com/c/i/sou?'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
            'referer': 'https://www.zhaopin.com/',
        }
        self.pos_que = Queue()      # 职位准备存入队列
        self.db = pymysql.connect(host=host,
                                  port=port,
                                  user=user,
                                  password=password,
                                  database=database)
        self.cursor = self.db.cursor()

    def next_page(self):
        """
        处理下一页 以及 判断总共页数
        :return:
        """
        try:
            # self.browser.find_element_by_class_name('btn soupager__btn soupager__btn--disable')  # 没有下一页的标志
            self.browser.find_element_by_class_name('btn soupager__btn')                           # 能翻页
        except Exception as e:
            # 最后一页
            status = False
        else:
            # 有下一页
            status = True
        finally:
            print(status)
            return status

    def case_rate(self):   # selenium
        # https://sou.zhaopin.com/?jl=763&sf=0&st=0&kw=python&kt=3&p=3
        # 以下内容为初版内容, 后续没有用到的，也不需要用到这里
        self.browser.get(self.base_url)
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="a-modal__content"]/div/button'))
        )
        self.browser.find_element_by_xpath('//div[@class="a-modal__content"]/div/button').click()
        time.sleep(2)
        LOG.info('二 》》》排名靠后检测问题程序打开')
        for position in ['']:
            input_box = self.browser.find_element_by_class_name('search-box__common__input')
            time.sleep(1)
            input_box.clear()
            time.sleep(1)
            input_box.send_keys(position)
            print('能走到这里')
            time.sleep(1)
            for _ in range(1, 6):
                # self.browser.execute_script(jd)
                for h in range(20):
                    self.browser.execute_script(
                        "window.scrollTo({a}, {b}); var lenOfPage=document.body.scrollHeight; return lenOfPage;".format(
                            a=500 * h, b=500 * (h + 1)))
                    time.sleep(1)

                time.sleep(10)
                if self.next_page():   # 判断是否有下一页，有的话就翻页，没有就break
                    # 翻页
                    print('有下一页')
                    pass
                else:
                    LOG.info(f'《{position}》这个职位没有下一页了当前为第{_}页')
                    break
                time.sleep(10)

    def update_mysql_one(self, pg, kew, cnt):
        sql = f'update keyword set pageinfo = {pg}, posi_nums = {cnt} where keyword = "{kew.strip()}"'

        try:
            LOG.info('数据库准备修改数据>>>>>>>')
            self.cursor.execute(sql)
            self.db.commit()
            time.sleep(0.3)
        except Exception as e:
            LOG.warning('数据错误已经回滚>>>>>>>')
            self.db.rollback()

    def session_get(self):
        while True:
            if self.pos_que.empty():
                break
            else:
                position = self.pos_que.get()
                time.sleep(5)
                for page in range(6):
                    start = page * 90
                    now_page = page + 1       # 现在页数
                    params = {
                        "start": str(start),
                        "pageSize": "90",  # 每页数据
                        "cityId": "763",  # 广州
                        "workExperience": "-1",
                        "education": "-1",
                        "companyType": "-1",
                        "employmentType": "-1",
                        "jobWelfareTag": "-1",
                        "kw": position,
                        "kt": "3",      # 这个参数很重要，没有就服务器错误
                        # "_v": "0.33455201",  # <<<<<<<<<<<
                        # "x-zp-page-request-id": f"475845d52fa846b9b68d41ef6fce3fca-{int(time.time() * 1000)}-972139",  # <<<<<<
                        # "x-zp-client-id": "e5cc6ae7-13f9-4f11-ac17-f37439ae1de5",
                        # 上面三个数据都不重要，可以不传输的
                    }
                    time.sleep(10)
                    try:
                        requests.packages.urllib3.disable_warnings()
                        resp = requests.get(self.js_url, params=params, headers=self.headers, verify=False)
                    except Exception as e:
                        LOG.error(f'{position}职位的第{now_page}页内容已经写入失败》[可能：请求信息过期或者没有后续页面了]》')
                        break
                    else:
                        dic = json.loads(resp.text, encoding='utf-8')
                        count = dic['data']['count']
                        LOG.info(f'{position}这个岗位总共有{count}个发布信息')
                        if int(count) > 90:
                            last_page = int(count) // 90      # 获取最后一页页码
                        else:
                            last_page = 1
                        data = dic['data']['results']    # list
                        now_info = [f'{position}:{now_page}:::']
                        for com in data:
                            co = com['company']['name']    # goal
                            now_info.append(co)
                        time.sleep(1)
                        with open('information.txt', 'a', encoding='gb18030') as f:
                            f.write(str(now_info) + '\r\n')
                        LOG.info(f'{position}职位的第{now_page}页内容已经写入成功》》》》》》')
                        now_page_info = set(now_info)
                        if now_page_info & o_comp:
                            self.update_mysql_one(now_page, position, count)
                            LOG.info(f'##### 在第{now_page}页的<<{position}>>职位查到公司信息')
                            break    # 只要在规定页码内查到公司信息就可以退出了

                        self.update_mysql_one(0, position, count)

                        if count <= start:
                            LOG.info(f"<<<{position}>>>职位只有{now_page}页数据，已经停止搜索")
                            break

                        if now_page == last_page:
                        #     print('now_page::', now_page)
                        #     print('last_page::', last_page)
                        #     if True:   # False
                        #         self.update_mysql_one(0, position, count)
                        #         LOG.warning(f'智联)))){position}>>职位没有在规定页码内，需要处理')
                        #         # from spider import Message
                        #         # receivers = '聂清娜;朱建坤'                                              # <<<======
                        #         receivers = '朱建坤'
                        #         msg = f'<<{position}>>职位没有在规定页码内，需要处理'
                        #         Message.send_rtx_msg(receivers, msg)
                            break

    def save_pos(self):
        p = requests.get('http://192.168.6.112:8000/api/get/rate/z').text
        time.sleep(0.5)
        data = json.loads(p)
        pos = data['data']
        for p in pos:
            info = p['keyword']
            LOG.info(f'！！！>>> {info} 职位已经放入队列 >>>>>')
            self.pos_que.put(info)

    @staticmethod
    def requests_info():
        page = requests.get('http://192.168.6.112:8000/api/get/rate/z').text
        time.sleep(0.5)
        data = json.loads(page)
        pos = data['data']
        main_info = []
        for p in pos:
            kw = p['keyword']
            pi = p['pageinfo']
            test = (kw, pi)
            if pi == 0:
                main_info.append(test)

        return main_info

    def requests_json(self):
        with open('information.txt', 'a') as f:
            f.write(time.ctime(time.time()) + '::开始记录公司信息\n')
            f.write('=' * 50 + '\n')    #
        # self.re_get()
        q1 = []
        for i in range(1):
            t1 = Thread(target=self.save_pos)
            t1.start()
            LOG.info(f'#####存职位》》的线程{i}已经启动#####')
            q1.append(t1)

        time.sleep(random.randint(3, 7))

        q2 = []
        for i in range(2):
            t2 = Thread(target=self.session_get)
            LOG.info(f'#####搜信息》》的线程{i}已经启动#####')
            t2.start()
            q2.append(t2)

        time.sleep(random.randint(2, 5))
        for i in q1:
            i.join()
        LOG.info(f'#####存职位》》的线程已经回收#####')
        for i in q2:
            i.join()
        LOG.info(f'#####搜信息》》的线程已经回收#####')

    def run(self):
        try:
            # self.case_rate()  # 《《《 需要开
            self.requests_json()   # https://fe-api.zhaopin.com/c/i/sou?
        except Exception as e:
            # 程序出错，可能需要处理
            LOG.warning('》》》》》》程序异常，出了问题需要跟进处理《《《《《')
            receivers = '朱建坤'
            # receivers = '聂清娜;张子珏;杨国玲;陈淼灵'                        # <<<======
            msg = '自动排查排名靠后程序yhzx出错'
            Message.send_rtx_msg(receivers, msg)
        else:
            out_page = self.requests_info()
            if len(out_page) > 0:
                receivers = '聂清娜;张子珏;杨国玲;陈淼灵'
                msg = '智联岗位页面排行信息已经筛选出来，有关键字信息不在规定信息内可以在后台管理《排名信息》里面查看\n' \
                      '快速链接:http://192.168.6.112:8000/admin \n' \
                      '也可以在后台添加需要关注的关键字信息进行关注__系统会第二天自动搜索查询(如果都在指定页数则不提醒，仍然可以通过后台查询管理)'
                Message.send_rtx_msg(receivers, msg)


def main():
    app1 = ZhiLian()
    app1.run()
    # try:
    #     app1.run()
    #     LOG.info('招聘信息》》》抓取进程开启成功')
    # except Exception as e:
    #     receivers = '朱建坤'
    #     msg = '2基本信息筛选1 出现问题，需要调试'
    #     Message.send_rtx_msg(receivers, msg)

    # time.sleep(random.randint(30, 60))   # 因为没有用代理，所以这两个页面其实是同源的，防止ip被封，休息一段时间，反正也不急嘛
    #
    # app2 = Rate()
    # try:
    #     app2.run()
    #     LOG.info('页面信息》》》抓取进程开启成功')
    # except Exception as e:
    #     receivers = '朱建坤'
    #     msg = '排行程序出现问题需要调试'
    #     Message.send_rtx_msg(receivers, msg)


if __name__ == '__main__':
    main()
