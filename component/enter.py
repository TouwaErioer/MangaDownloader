#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:17
# @Author  : DHY
# @File    : enter.py
import os
import re

from prettytable import PrettyTable
from component.color import red_text, yellow_text
from component.help import print_help
from test.test import test_proxy_concurrency
from utlis.config import write_config, get_proxy
from utlis.network import check_proxy


def enter_range(pages: list):
    # print('格式：【x:y，从x开始y结束；y，从1开始y结束】')
    while True:
        start = 0
        try:
            end = input('请输入下载范围（%d话）> ' % len(pages)) or len(pages)
            if str(end).find(':') != -1:
                input_arr = end.split(':')
                start = int(input_arr[0])
                end = int(input_arr[1])
                if end > len(pages) or end <= 0 and start > len(pages) or end < 0:
                    raise IndexError
                else:
                    return start, end
            elif end == 'help' or end == 'h':
                print_help('range')
            else:
                end = int(end)
                if end > len(pages) or end <= 0:
                    raise IndexError
                return start, end
        except TypeError:
            print('\033[0;31;40m输入不是数字，重新输入\033[0m')
        except ValueError:
            print('\033[0;31;40m输入不是数字，重新输入\033[0m')
        except IndexError:
            print('\033[0;31;40m超出章节范围\033[0m')


def enter_branch(tab: dict):
    if tab is None or len(tab) == 0:
        return 0
    # 分支大于1，选择分支
    elif len(tab) > 1:
        table = PrettyTable(['序号', '分支'])
        for index, value in enumerate(list(tab.keys()), 1):
            table.add_row([index, value])
        table.align['序号'] = 'l'
        table.align['分支'] = 'l'
        print(table)
        while True:
            try:
                placeholder = '查询到多个分支，请输入序号> '
                value = input(placeholder) or 1
                # 输入分支检查
                if value == 'help' or value == 'h':
                    print_help('请输入分支序号，不能输入大于或小于序号的数字')
                elif int(value) > len(tab.keys()) or int(value) <= 0:
                    raise IndexError
                else:
                    return tab.get(list(tab.keys())[int(value) - 1])
            except ValueError:
                print('\033[0;31;40m输入不为数字\033[0m')
            except IndexError:
                print('\033[0;31;40m超出分支范围\033[0m')
    elif len(tab) == 1:
        return tab.get(list(tab.keys())[0])


def enter_command():
    while True:
        try:
            command = input('MangaDownloader> ') or 'start'
            if command != 'start' and command != 'help':
                raise ValueError
            else:
                if command == 'start':
                    break
                elif command == 'help' or 'h':
                    print_help()
        except ValueError:
            print(red_text % '输入命令有误')


def enter_keywords(config):
    while True:
        keywords = input('请输入关键词> ') or '电锯人'
        if keywords.find(':') != -1:
            array = keywords.split(':')
            keywords = array[0]
            author = array[1]
            if len(array) == 3:
                site = array[2]
                sites = config.get_site_name()
                if site not in sites:
                    raise Exception(red_text % ('站点%s未在支持列表中' % site))
                return keywords, author, site
            else:
                return keywords, author, None
        elif keywords == 'help' or keywords == 'h':
            print_help('keywords')
        else:
            return keywords, None, None


def enter_cookie(config):
    cookie = config['cookie']
    if cookie == '':
        while True:
            cookie = input('请输入cookie> ')
            if cookie == '':
                raise Exception('输入为空，请重新输入')
            elif cookie == 'help' or cookie == 'h':
                print_help('cookie')
            write_config('bilibili', 'cookie', cookie)
            break
    return cookie


def enter_index(results):
    placeholder = '请输入序号> '
    while True:
        try:
            value = input(placeholder) or 1
            if value == 'help' or value == 'h':
                print_help('请输入结果序号，不能输入大于或小于序号的数字')
            elif int(value) <= 0 or int(value) > results:
                raise IndexError
                continue
            else:
                return int(value)
        except ValueError:
            print('\033[0;31;40m输入不为数字，请重新输入\033[0m')
        except IndexError:
            print('\033[0;31;40m输入超出范围，请重新输入\033[0m')


def check_speed(speed):
    # 当速度大于1，没有配置代理，系统为Windows提醒设置代理
    if float(speed) > 1 and get_proxy() is None and os.name == 'nt':
        tip = yellow_text % ('%.2f秒/张' % float(speed))
        is_proxy = input('测试速度大约为%s，建议使用代理(y/n)> ' % tip) or 'y'
        if is_proxy != 'n':
            enter_proxy()


def enter_proxy():
    host = enter_host()
    port = enter_port()

    # 代理连通性测试
    proxy = check_proxy(host, port)
    if proxy is False:
        print(red_text % ('%s:%s代理错误，请重新输入' % (host, port)))
        enter_proxy()

    # 代理并发性测试
    test = test_proxy_concurrency({'socks5_host': host, 'socks5_port': port})
    if test is False:
        write_config('proxy', 'socks5_host', '')
        write_config('proxy', 'socks5_port', '')
        tip = '如果使用v2ray，请开启Mux多路复用concurrency设为1024\n详情：https://www.v2ray.com/chapter_02/mux.html'
        raise Exception(red_text % ('并发测试失败，%s' % tip))

    return host, port


def enter_host():
    while True:
        socks5_host = input('请输入%s> ' % (yellow_text % 'Host'))
        regex_host = r'^((2[0-4]\d|25[0-5]|[1]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[1]?\d\d?)$'
        if re.findall(regex_host, socks5_host):
            write_config('proxy', 'socks5_host', socks5_host)
            return socks5_host
        else:
            print(red_text % '输入socks5_host格式错误')


def enter_port():
    while True:
        try:
            socks5_port = int(input('请输入%s> ' % (yellow_text % 'Port')))
            if 1 < socks5_port < 65535:
                write_config('proxy', 'socks5_port', str(socks5_port))
                return socks5_port
            else:
                print(red_text % '输入socks5_port格式错误')
        except ValueError:
            print(red_text % '输入不为数字，请重新输入')
