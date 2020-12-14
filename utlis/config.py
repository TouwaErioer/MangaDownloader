#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:05
# @Author  : DHY
# @File    : config.py
import configparser


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
