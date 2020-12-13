#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:05
# @Author  : DHY
# @File    : config.py
import configparser


def read_config(section, item):
    try:
        config = configparser.RawConfigParser()
        config.read('config.ini', encoding='utf-8')
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
        config.read('config.ini', encoding='utf-8')
        config.set(section, item, value)
        config.write(open('../config.ini', 'w'))
    except Exception as e:
        print(e)
