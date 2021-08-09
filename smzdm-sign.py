#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
什么值得买自动签到脚本
__author__ = 'Oakwen'
"""
import os
import time

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'zhiyou.smzdm.com',
    'Referer': 'https://www.smzdm.com/',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4449.0 Safari/537.36 Edg/91.0.838.3',
}

MSG_URL = os.environ["MSG_URL"]


class SMZDM_Bot(object):
    def __init__(self):
        self.session = requests.Session()
        # 添加 headers
        self.session.headers = DEFAULT_HEADERS

    def __json_check(self, msg):
        try:
            result = msg.json()
            print(result)
            return True
        except Exception as e:
            print(f'Error : {e}')
            return False

    def load_cookie_str(self, cookies):
        self.session.headers['Cookie'] = cookies

    def checkin(self):
        url = 'https://zhiyou.smzdm.com/user/checkin/jsonp_checkin'
        msg = self.session.get(url)
        if self.__json_check(msg):
            return msg.json()
        return msg.content


if __name__ == '__main__':
    sb = SMZDM_Bot()
    # sb.load_cookie_str(config.TEST_COOKIE)
    cookies = os.environ["SMZDM_COOKIE"]
    sb.load_cookie_str(cookies)
    res = sb.checkin()
    print(res)
    if int(res['error_code']) == 0:
        soup = BeautifulSoup(res['data']['slogan'], 'html.parser')
        success_msg = ''
        for j in soup.contents[0].contents:
            if j.find('span') != -1:
                success_msg = success_msg + j.text
            else:
                success_msg = success_msg + j
        try:
            msg = {'什么值得买签到(づ ●─● )づ': '\n' + (time.strftime("%Y-%m-%d %H:%M:%S",
                                                             time.localtime())) + '\n签到成功\n' + success_msg + '。'}
            requests.get(MSG_URL, msg)
        except Exception as e:
            print('发送微信消息失败\n' + f"{e}" + '\n')
    else:
        msg = {'什么值得买签到(づ ●─● )づ': '\n' + (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + '\n签到失败\n' + str(res['error_msg']) + '\n'}
        requests.get(MSG_URL, msg)
    print('代码完毕')
