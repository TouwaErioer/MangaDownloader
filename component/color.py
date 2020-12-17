#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:21
# @Author  : chobits
# @File    : color.py

write_text = '\33[1;30m%s\033[0m'
red_text = '\33[1;31m%s\033[0m'
green_text = '\33[1;32m%s\033[0m'
yellow_text = '\33[1;33m%s\033[0m'
blue_text = '\33[1;34m%s\033[0m'
pink_text = '\33[1;35m%s\033[0m'
cyan_blue_text = '\33[1;36m%s\033[0m'
gray_text = '\33[1;37m%s\033[0m'
light_grey_text = '\33[1;38m%s\033[0m'


def parse_color(color: str):
    if color == 'yellow_text':
        return yellow_text
    elif color == 'green_text':
        return green_text
    elif color == 'blue_text':
        return blue_text
    elif color == 'pink_text':
        return pink_text
    elif color == 'cyan_blue_text':
        return cyan_blue_text
