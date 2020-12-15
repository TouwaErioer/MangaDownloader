#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:20
# @Author  : DHY
# @File    : help.py
from component.color import green_text


def print_help(enter_type):
    if enter_type == 'keywords':
        print(green_text % '-[keywords] 标题')
        print(green_text % '-[keywords:author] 标题:作者')
        print(green_text % '-[keywords:author:site] 标题:作者:站点')
    elif enter_type == 'range':
        print(green_text % '-[x:y] x ~ y')
        print(green_text % '-[y] 1 ~ y')
    elif enter_type == 'cookie':
        print(green_text % '-[cookie] 请输入bilibili漫画cookie')
    else:
        print(green_text % enter_type)
