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
    while True:
        try:
            # 分支大于1，选择分支
            if len(tab) > 1:
                table = PrettyTable(['序号', '分支'])
                for index, value in enumerate(list(tab.keys()), 1):
                    table.add_row([index, value])
                table.align['序号'] = 'l'
                table.align['分支'] = 'l'
                print(table)
                placeholder = '查询到多个分支，请输入序号> '
                value = int(input(placeholder) or 1)
            else:
                value = 1

            # 输入分支检查
            if value > len(tab.keys()) or value <= 0:
                raise IndexError
            return value - 1
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
                elif command == 'help':
                    print(blue_text % '\n输入关键词格式：')
                    print(green_text % '-[keywords] 查询标题为keywords的漫画')
                    print(green_text % '-[keywords:author] 查询标题为keywords，作者名为的漫画\n', )

                    print(blue_text % '输入范围格式：')
                    print(green_text % '-[x:y] 从x开始y结束')
                    print(green_text % '-[y] 从1开始y结束\n')
        except ValueError:
            print(red_text % '输入命令有误')


def enter_keywords():
    keywords = input('请输入关键词> ') or '辉夜'
    if keywords.find(':') != -1:
        value = keywords.split(':')
        keywords = value[0]
        author = value[1]
        return keywords, author
    else:
        return keywords


def enter_cookie():
    cookie = read_config('download', 'cookie')
    if cookie == '':
        while True:
            cookie = input('请输入cookie> ')
            if cookie == '':
                raise Exception('输入为空，请重新输入')
            write_config('download', 'cookie', cookie)
            break
    return cookie


def enter_index(results):
    placeholder = '请输入序号> '
    while True:
        try:
            value = int(input(placeholder) or 1)
            if value <= 0 or value > results:
                raise IndexError
                continue
            return value
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
