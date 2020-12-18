#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:05
# @Author  : chobits
# @File    : config.py
import configparser

from component.color import parse_color


def read_config(section, item):
    try:
        config = configparser.RawConfigParser()
        config.read('config.ini')
        if item is None:
            sections = config.sections()
            index = sections.index(section)
            return dict(config.items(sections[index]))
        return str(config.get(section, item))
    except Exception as e:
        print(e)


def write_config(section, item, value):
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set(section, item, value)
        with open('config.ini', 'w') as f:
            config.write(f)
    except Exception as e:
        print(e)


def read_test():
    try:
        config = configparser.RawConfigParser()
        config.read('test.ini', encoding='utf-8')
        sections = config.sections()
        tests = []
        for section in sections:
            section = dict(config.items(section))
            for key, value in section.items():
                if key.find('test') != -1:
                    tests.append({'name': section['name'], 'url': value})
        return tests
    except Exception as e:
        print(e)


def get_proxy():
    proxy = read_config('proxy', None)
    if proxy['socks5_host'] == '' or proxy['socks5_port'] == '':
        return None
    else:
        return proxy


def check_test():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    manhuadb_test = config.get('manhuadb', 'test')
    wuqimh_test = config.get('wuqimh', 'test')
    bilibili_test = config.get('bilibili', 'test')
    mangabz_test = config.get('mangabz', 'test')
    if manhuadb_test == '' or wuqimh_test == '' or bilibili_test == '' or mangabz_test == '':
        return False
    else:
        return True


def read_score():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    manhuadb_test = config.get('manhuadb', 'test')
    wuqimh_test = config.get('wuqimh', 'test')
    bilibili_test = config.get('bilibili', 'test')
    mangabz_test = config.get('mangabz', 'test')

    result = {'漫画db': manhuadb_test, '57漫画': wuqimh_test, 'bilibili漫画': bilibili_test, 'MangaBZ': mangabz_test}
    return result


def write_score(result: dict):
    config = configparser.RawConfigParser()
    config.read('config.ini')
    sections = config.sections()
    for key, value in result.items():
        for section in sections:
            item = dict(config.items(section))
            if 'name' in item:
                if item['name'] == key:
                    config.set(section, 'test', value)
    with open('config.ini', 'w') as f:
        config.write(f)


def get_site_name():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    sections = config.sections()
    result = []
    for section in sections:
        section = dict(config.items(section))
        if 'name' in section:
            result.append(parse_color(section['color']) % section['name'])
    return result
