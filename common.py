#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : common.py
import configparser

from prettytable import PrettyTable

from utils import read_config, write_config

yellow_text = '\33[1;33m%s\033[0m'
blue_text = '\33[1;34m%s\033[0m'
green_text = '\33[1;32m%s\033[0m'
pink_text = '\33[1;35m%s\033[0m'
red_text = '\33[1;31m%s\033[0m'


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


def print_help(enter_type):
    if enter_type == 'keywords':
        print(green_text % '-[keywords] 标题')
        print(green_text % '-[keywords:author] 标题:作者', )
    elif enter_type == 'range':
        print(green_text % '-[x:y] x ~ y')
        print(green_text % '-[y] 1 ~ y')
    elif enter_type == 'cookie':
        print(green_text % '-[cookie] 请输入bilibili漫画cookie')
    else:
        print(green_text % enter_type)


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


def check_config():
    try:
        config = configparser.RawConfigParser()
        config.read('config.ini', encoding='utf-8')
        sections = config.sections()

        folder = sections[sections.index('folder')]
        download = sections[sections.index('download')]
        site = sections[sections.index('site')]
        decrypt = sections[sections.index('decrypt')]
        search = sections[sections.index('search')]
        path = config.get(folder, 'path')
        semaphore = config.get(download, 'semaphore')
        cookie = config.get(download, 'cookie')
        repeat = config.get(download, 'repeat')
        manhuadb = config.get(site, 'manhuadb')
        manhuadui = config.get(site, 'manhuadui')
        wuqimh = config.get(site, 'wuqimh')
        bilibili = config.get(site, 'bilibili')
        key = config.get(decrypt, 'key')
        iv = config.get(decrypt, 'iv')
        search_manhuadb = config.get(search, 'manhuadb')
        search_manhuadui = config.get(search, 'manhuadui')
        search_wuqimh = config.get(search, 'wuqimh')
        search_bilibili = config.get(search, 'bilibili')
        if semaphore and repeat and manhuadb and manhuadui and wuqimh and bilibili and key and iv and search_manhuadb \
                and search_manhuadui and search_wuqimh and search_bilibili:
            pass
        else:
            raise ValueError(red_text % '必填参数不能为空')
    except Exception as e:
        print(red_text % 'config.ini参数错误，%s' % e)


if __name__ == '__main__':
    check_config()
