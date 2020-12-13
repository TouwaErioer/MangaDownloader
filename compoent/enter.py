#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:17
# @Author  : DHY
# @File    : enter.py
from prettytable import PrettyTable

from compoent.color import red_text
from compoent.help import print_help
from utlis.config import write_config


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


def enter_keywords():
    while True:
        keywords = input('请输入关键词> ') or '辉夜'
        if keywords.find(':') != -1:
            value = keywords.split(':')
            keywords = value[0]
            author = value[1]
            return keywords, author
        elif keywords == 'help' or keywords == 'h':
            print_help('keywords')
        else:
            return keywords


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
