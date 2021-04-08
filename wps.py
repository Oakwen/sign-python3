#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import time
import json
import os

# 解决https访问警告
# from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

# 参加打卡活动，第一次或是中间断了签到后需要重新参加活动，才能打开领取会员
'''
URL: http://zt.wps.cn/2018/clock_in/api/sign_up?member=wps
header:{
    sid:
}
get url 
'''


# wps接受邀请
def wps_invite(sid: list, invite_userid: int) -> None:
    default_sid = [
        "V02StVuaNcoKrZ3BuvJQ1FcFS_xnG2k00af250d4002664c02f",
        "V02SWIvKWYijG6Rggo4m0xvDKj1m7ew00a8e26d3002508b828",
        "V02Sr3nJ9IicoHWfeyQLiXgvrRpje6E00a240b890023270f97",
        "V02SBsNOf4sJZNFo4jOHdgHg7-2Tn1s00a338776000b669579",
        "V02S2oI49T-Jp0_zJKZ5U38dIUSIl8Q00aa679530026780e96",
        "V02ShotJqqiWyubCX0VWTlcbgcHqtSQ00a45564e002678124c",
        "V02SFiqdXRGnH5oAV2FmDDulZyGDL3M00a61660c0026781be1",
        "V02S7tldy5ltYcikCzJ8PJQDSy_ElEs00a327c3c0026782526",
        "V02SPoOluAnWda0dTBYTXpdetS97tyI00a16135e002684bb5c",
        "V02Sb8gxW2inr6IDYrdHK_ywJnayd6s00ab7472b0026849b17",
        "V02SwV15KQ_8n6brU98_2kLnnFUDUOw00adf3fda0026934a7f",
        "V02SC1mOHS0RiUBxeoA8NTliH2h2NGc00a803c35002693584d"
    ]
    sid = default_sid+sid
    invite_url = 'http://zt.wps.cn/2018/clock_in/api/invite'
    s = requests.session()
    for index, i in enumerate(sid):
        headers = {
            'sid': i
        }
        r = s.post(invite_url, headers=headers, data={
                   'invite_userid': invite_userid})
        time.sleep(2)
        print("ID={}, 状态码: {}, 请求信息{}".format(
            str(index+1).zfill(2), r.status_code, r.text))


# wps签到
def wps_clockin(sid: str) -> None:
    getquestion_url = 'http://zt.wps.cn/2018/clock_in/api/get_question?member=wps'
    s = requests.session()
    # 打卡签到需要参加活动
    r = s.get(getquestion_url, headers={'sid': sid})
    '''
    {
        "result": "ok",
        "data": {
            "multi_select": 1,
            "options": [
                "30天文档分享链接有效期",
                "远程下载助手",
                "输出长图片去水印",
                "PDF转图片"
            ],
            "title": "以下哪些特权是WPS会员和超级会员共同拥有的？"
        },
        "msg": ""
    }
    '''
    answer_set = {
        'WPS会员全文检索',
        '100G',
        'WPS会员数据恢复',
        'WPS会员PDF转doc',
        'WPS会员PDF转图片',
        'WPS图片转PDF插件',
        '金山PDF转WORD',
        'WPS会员拍照转文字',
        '使用WPS会员修复',
        'WPS全文检索功能',
        '有，且无限次',
        '文档修复'
    }
    try:
        resp = json.loads(r.text)
    except Exception as e:
        print("签到失败！！！ sid可能需要更新")
        return
    # print(resp['data']['multi_select'])
    # 只做单选题 multi_select==1表示多选题
    while resp['data']['multi_select'] == 1:
        r = s.get(getquestion_url, headers={'sid': sid})
        resp = json.loads(r.text)
        # print(resp['data']['multi_select'])

    answer_id = 3
    for i in range(4):
        opt = resp['data']['options'][i]
        if opt in answer_set:
            answer_id = i+1
            break
    print("选项: {}".format(resp['data']['options']))
    print("选择答案: {}".format(answer_id))

    answer_url = 'http://zt.wps.cn/2018/clock_in/api/answer?member=wps'
    # 提交答案
    r = s.post(answer_url, headers={'sid': sid}, data={'answer': answer_id})
    resp = json.loads(r.text)
    # 答案错误
    if resp['msg'] == 'wrong answer':
        print("答案不对，挨个尝试")
        for i in range(4):
            r = s.post(answer_url, headers={'sid': sid}, data={'answer': i+1})
            resp = json.loads(r.text)
            print(i+1)
            if resp['result'] == 'ok':
                print(r.text)
                break

    # 打卡签到
    clockin_url = 'http://zt.wps.cn/2018/clock_in/api/clock_in?member=wps'
    r = s.get(clockin_url, headers={'sid': sid})
    print("签到信息: {}".format(r.text))
    resp = json.loads(r.text)
    # 重新报名
    if resp['msg'] == '前一天未报名':
        print('    尝试报名')
        signup_url = 'http://zt.wps.cn/2018/clock_in/api/sign_up'
        r = s.get(signup_url, headers={'sid': sid})
        print(r.text)


if __name__ == '__main__':
    sid = os.environ['WPS_SID']
    userid = os.environ['WPS_INVITEID']
    msg_url = os.environ['MSG_URL']
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    print("--------------------------" + now + "----------------------------")
    print("sid=" + sid)
    print("userid=" + userid)
    print("MSG_URL="+msg_url)

    wps_clockin(sid)
    wps_invite([], userid)
