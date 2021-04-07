#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
__author__ = 'Oakwen'
"""
import os
import re
import time

import requests
from requests.adapters import HTTPAdapter
from retry import retry

COOKIE = os.environ["V2EX_COOKIE"]

DAILY_URL = 'https://www.v2ex.com/mission/daily'
BALANCE_URL = 'https://www.v2ex.com/balance'
MSG_URL = os.environ["MSG_URL"]


@retry()
def daily():
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        _headers = {'Referer': 'https://www.v2ex.com/mission', 'Host': 'www.v2ex.com',
                    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/87.0.4255.0 Safari/537.36 Edg/87.0.634.0',
                    'Cookie': COOKIE}
        res_daily = s.get(DAILY_URL, headers=_headers, timeout=15)
        once = re.search(r'/redeem\?once=(\d+)', res_daily.text)
        if once is None:
            res_balance = s.get(BALANCE_URL, headers=_headers, timeout=15)
            if res_balance.status_code == 200:
                # print(resb.text)
                balance = re.search(
                    r'\d+?\s的每日登录奖励\s\d+\s铜币', res_balance.text)
                if balance is not None:
                    # print(balance.group(0))
                    msg = {'v2ex签到(づ ●─● )づ': '\n' + (time.strftime("%Y-%m-%d %H:%M:%S",
                                                                    time.localtime())) + '\n今天已经签到过啦\n' + balance.group(
                        0)}
                    requests.get(MSG_URL, msg)
                return True
        else:
            res = s.get(DAILY_URL + once.group(0),
                        headers=_headers, timeout=15)
            if res.text.find('签到成功'):
                res_balance = s.get(BALANCE_URL, headers=_headers, timeout=15)
                if res_balance.status_code == 200:
                    balance = re.search(
                        r'\d+?\s的每日登录奖励\s\d+\s铜币', res_balance.text)
                    # print(balance)
                    msg = {'v2ex签到(づ ●─● )づ': '\n' + (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '\n签到成功\n' + balance.group(
                        0)}
                    requests.get(MSG_URL, msg)
                    return True
                else:
                    # print('balance失败')
                    msg = {'v2ex签到(づ ●─● )づ': '\n' + (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '\n签到成功，获取金币数失败\n'}
                    requests.get(MSG_URL, msg)
                    return True
            else:
                # print('签到失败')
                msg = {'v2ex签到(づ ●─● )づ': '\n' + (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '\n签到失败\n'}
                requests.get(MSG_URL, msg)
                return False
    except Exception as e:
        # print(f"{e}")
        msg = {'v2ex签到(づ ●─● )づ': '\n' + (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '\n' + f"{e}" + '\n'}
        requests.get(MSG_URL, msg)
        return False


if __name__ == '__main__':
    daily()
