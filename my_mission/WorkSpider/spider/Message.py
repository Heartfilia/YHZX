# 如果获取到信息，就发送到公司接口
from requests import Session


s = Session()


def send_rtx_msg(receivers, msg):
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
    s.post("http://rtx.fbeads.cn:8012/sendInfo.php", data=post_data)


# ip_info = "127.0.0.1:8000"
# send_rtx_msg('朱建坤', f'请点击 \nhttp://{ip_info}/admin \n在后台管理系统中处理')
