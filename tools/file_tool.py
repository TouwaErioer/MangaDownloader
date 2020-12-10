#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/10 20:28
# @Author  : DHY
# @File    : file_tool.py
import os


# 统计文件夹下的文件个数
def get_file_total(source_dir):
    file_total = 0
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_total += 1
    return file_total
