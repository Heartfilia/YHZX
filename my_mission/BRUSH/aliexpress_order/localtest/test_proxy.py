#大象代理

# import requests
# import json
# res = requests.get(
#         # "http://vip22.daxiangdaili.com/ip/?tid=559795625132464&num=100&format=json&protocol=https&filter=on&show_area=true&show_operator=true&longlife=2")
#         "http://vip22.daxiangdaili.com/ip/?tid=559795625132464&num=100&format=json&protocol=https&filter=on&show_area=true&show_operator=true&longlife=2")
# proxy_ip_list = json.loads(res.text)
# print(proxy_ip_list)
# print(len(proxy_ip_list))
# print(res.text)

#osy代理
from mytools.tools import get_oxylabs_proxy
import random


# def create_proxyauth_extension(self, proxy_host, proxy_port,
#                                proxy_username, proxy_password,
#                                scheme='http', plugin_path=None):
#         import string
#         import zipfile
#
#         if plugin_path is None:
#                 plugin_path = os.path.abspath(os.path.dirname(__file__)) + "/vimm_chrome_proxyauth_plugin.zip"
#
#         manifest_json = """
#     {
#         "version": "1.0.0",
#         "manifest_version": 2,
#         "name": "Chrome Proxy",
#         "permissions": [
#             "proxy",
#             "tabs",
#             "unlimitedStorage",
#             "storage",
#             "<all_urls>",
#             "webRequest",
#             "webRequestBlocking"
#         ],
#         "background": {
#             "scripts": ["background.js"]
#         },
#         "minimum_chrome_version":"22.0.0"
#     }
#     """
#
#         background_js = string.Template(
#                 """
#                 var config = {
#                         mode: "fixed_servers",
#                         rules: {
#                           singleProxy: {
#                             scheme: "${scheme}",
#                             host: "${host}",
#                             port: parseInt(${port})
#                           },
#                           bypassList: ["foobar.com"]
#                         }
#                       };
#
#                 chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
#
#                 function callbackFn(details) {
#                     return {
#                         authCredentials: {
#                             username: "${username}",
#                             password: "${password}"
#                         }
#                     };
#                 }
#
#                 chrome.webRequest.onAuthRequired.addListener(
#                             callbackFn,
#                             {urls: ["<all_urls>"]},
#                             ['blocking']
#                 );
#                 """
#         ).substitute(
#                 host=proxy_host,
#                 port=proxy_port,
#                 username=proxy_username,
#                 password=proxy_password,
#                 scheme=scheme,
#         )
#         with zipfile.ZipFile(plugin_path, 'w') as zp:
#                 zp.writestr("manifest.json", manifest_json)
#                 zp.writestr("background.js", background_js)
#
#         zipf = zipfile.ZipFile(plugin_path)
#         # print(zipf.namelist())
#         return plugin_path

proxy = get_oxylabs_proxy('us',_city=None,_session=random.random())['https']
auth = proxy.split("@")[0][7:]
proxyid = proxy.split("@")[1]
# proxyauth_plugin_path =create_proxyauth_extension(
#     proxy_host=proxyid.split(":")[0],
#     proxy_port=int(proxyid.split(":")[1]),
#     proxy_username=auth.split(":")[0],
#     proxy_password=auth.split(":")[1]
# )
proxy_host=proxyid.split(":")[0]
proxy_port=int(proxyid.split(":")[1])
proxy_username=auth.split(":")[0]
proxy_password=auth.split(":")[1]



