#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:06
# @Author  : DHY
# @File    : file.py
import os
import zipfile


def make_zip(source_dir, output_filename):
    file = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dir_name, filenames in os.walk(source_dir):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)  # 相对路径
            file.write(path_file, arc_name)
    file.close()


# 统计文件夹下的文件个数
def get_file_total(source_dir):
    file_total = 0
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_total += 1
    return file_total
