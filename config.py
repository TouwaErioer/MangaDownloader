#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/5 23:59
# @Author  : DHY
# @File    : config_parser.py
import configparser
from common import red_text


class config:
    def __init__(self):
        try:
            config_parser = configparser.RawConfigParser()
            config_parser.read('config.ini', encoding='utf-8')
            sections = config_parser.sections()
            folder = sections[sections.index('folder')]
            download = sections[sections.index('download')]
            site = sections[sections.index('site')]
            decrypt = sections[sections.index('decrypt')]
            search = sections[sections.index('search')]
            self.search_item = config_parser.items('search')
            self.path = config_parser.get(folder, 'path')
            self.semaphore = int(config_parser.get(download, 'semaphore'))
            self.cookie = config_parser.get(download, 'cookie')
            self.repeat = int(config_parser.get(download, 'repeat'))
            self.manhuadb = config_parser.get(site, 'manhuadb')
            self.manhuadui = config_parser.get(site, 'manhuadui')
            self.wuqimh = config_parser.get(site, 'wuqimh')
            self.bilibili = config_parser.get(site, 'bilibili')
            self.key = config_parser.get(decrypt, 'key')
            self.iv = config_parser.get(decrypt, 'iv')
            self.search_manhuadb = config_parser.get(search, 'manhuadb')
            self.search_manhuadui = config_parser.get(search, 'manhuadui')
            self.search_wuqimh = config_parser.get(search, 'wuqimh')
            self.search_bilibili = config_parser.get(search, 'bilibili')
            if self.semaphore and self.repeat and self.manhuadb and self.manhuadui and self.wuqimh and self.bilibili\
                    and self.key and self.iv and self.search_manhuadb and self.search_manhuadui\
                    and self.search_wuqimh and self.search_bilibili:
                pass
            else:
                raise ValueError(red_text % '必填参数不能为空')
        except Exception as e:
            print(red_text % 'config.ini参数错误，%s' % e)
