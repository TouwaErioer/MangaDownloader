#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:20
# @Author  : chobits
# @File    : help.py
import os

from component.color import green_text, yellow_text
from utlis.config import get_site_name, get_proxy


def print_help(enter_type):
    if enter_type == 'keywords':
        print(green_text % '- keywords [:author] [:site] ')
    elif enter_type == 'range':
        print(green_text % '- start [:end]')
    elif enter_type == 'cookie':
        print(green_text % '- cookie 请输入cookie')
    elif enter_type == 'help':
        print(yellow_text % '- start  开始')
        print(yellow_text % '- help   显示帮助信息')
        print(yellow_text % '- list   显示支持站点列表')
        print(yellow_text % '- proxy  设置socks5代理')
        print(yellow_text % '- config 显示配置信息')
    elif enter_type == 'list':
        sites = get_site_name()
        for site in sites:
            print('- ' + green_text % site)
    elif enter_type == 'proxy':
        proxy = get_proxy()
        verify = None
        if proxy is not None:
            print('- socks5_host:%s' % (yellow_text % proxy['socks5_host']))
            print('- socks5_port:%s' % (yellow_text % proxy['socks5_port']))
            verify = input(yellow_text % '修改proxy(y/n)? ') or 'y'
        if proxy is None or verify != 'n':
            from component.enter import enter_proxy
            enter_proxy()
    elif enter_type == 'config':
        if os.name == 'nt':
            os.system('notepad config.ini')
        elif os.name == 'posix':
            os.system('vi config.ini')
