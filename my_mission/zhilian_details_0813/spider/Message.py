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


# send_rtx_msg('陈毅', 'testinfo')
