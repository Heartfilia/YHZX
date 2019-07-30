import  time
import logging
from logging import handlers
import os
import sys
from filelock import FileLock, Timeout
import json
from functools import wraps

def get_oxylabs_proxy(_country,_city ,_session):
# def get_oxylabs_proxy(_country,_session):
    #端口10000随机
    #端口10001 - 19999 美国端口
    username = 'rdby111'
    password = '4G5wTzP5rj'
    country = _country
    city = _city
    session = _session
    port = 10000
    if _country == 'gb':
        port = 20000
    if _country == 'ca' or _country == 'cn' or _country == 'de':
        port = 30000
    if _country == 'ru':
        port = 40000

    if city :
        entry = ('http://customer-%s-cc-%s-city-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
                 (username, country,city,session, password,country,port))
    else:
        entry = ('http://customer-%s-cc-%s-sessid-%s:%s@%s-pr.oxylabs.io:%s' %
             (username, country,session, password,country,port))
    proxies = {
        'http': entry,
        'https': entry,
    }
    return proxies

def get(session, url, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    while re_time < retry:
        re_time += 1
        try:
            res = session.get(url, *args, **kwargs)
            res.raise_for_status()
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            time.sleep(1.5)
    return res

def post(session, url, post_data, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15
    while re_time < retry:
        re_time += 1
        try:
            res = session.post(url, post_data, *args, **kwargs)
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            # change_local_ip_pool()
            time.sleep(1.5)
    return res

def with_filelock(lock_file, timeout=20):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_dir = os.path.dirname(__file__)
            lock_path = cache_dir + "/" + lock_file
            try:
                lock = FileLock(lock_path, timeout=timeout)
                with lock.acquire(timeout=timeout):
                    result = func(*args, **kwargs)
            except Timeout:
                print("Another instance of this application currently holds the lock.")
                return None
            return result

        return wrapper

    return decorate

def save_json(filename, json_data):
    # if os.path.isfile(filename):
    #     os.remove(filename)
    #
    # if not os.path.isdir(os.path.dirname(filename)):
    #     os.makedirs(os.path.dirname(filename))

    # f = open(filename, 'wt', encoding="utf-8")
    # json.dump(json_data, f)
    # f.close()

    # for i in range(3):
    #     if os.path.exists(filename):
    #         os.remove(filename)
    if not os.path.isdir(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    f = open(filename, 'w', encoding='utf-8')
    f.write(json.dumps(json_data))
    f.close()

def load_json(filename, default=None):
    """当文件不存在或者文件内容为空时，返回default;当文件内容不为空时，返回python数据类型"""
    if not os.path.isfile(filename):
        return default
    f = open(filename, "rt", encoding="utf-8")
    #此处有坑，read()后要进行变量赋值，否则再次调用read()为空。
    data = f.read()
    # print('f.read()', data)
    if data:
        _dict = json.loads(data)
        f.close()
        return _dict
    else:
        f.close()
        return default

def logger(name, std_level=logging.INFO, file_level=logging.INFO):
# def logger(name, std_level=logging.INFO, file_level=logging.DEBUG):
    logger = logging.getLogger()
    # log_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))
    # log_filename = log_dir + '/log/' + name + '.log'
    # if not os.path.isdir(log_dir + "/log"):
    #     os.mkdir(log_dir + "/log")
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filename = log_dir + '/' + name + '.log'
    file_handler = logging.handlers.RotatingFileHandler(log_filename,
                                                        mode='a',
                                                        maxBytes=102400,
                                                        backupCount=10,
                                                        encoding="utf8"
                                                        )

    # fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    stdout_handler.setLevel(std_level)
    logger.addHandler(stdout_handler)
    logger.setLevel(file_level)
    return logger

def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    import string
    import zipfile

    if plugin_path is None:
        plugin_path = os.path.abspath(os.path.dirname(__file__)) + "/vimm_chrome_proxyauth_plugin.zip"

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                  },
                  bypassList: ["foobar.com"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    zipf = zipfile.ZipFile(plugin_path)
    # print(zipf.namelist())
    return plugin_path