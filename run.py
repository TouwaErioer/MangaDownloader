#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py
import manhuadb
import manhuadui
from prettytable import PrettyTable

if __name__ == '__main__':
    keywords = input('请输入关键词：') or '辉夜'
    manhuadb_result = manhuadb.search(keywords)
    manhuadui_result = manhuadui.search(keywords)

    result = []
    result.extend(manhuadb_result)
    result.extend(manhuadui_result)

    manhuadb_len = len(manhuadb_result)
    manhuadui_len = len(manhuadui_result)
    res = []
    for index, value in enumerate(result, 1):
        option = str(index) + '.' + value['title']
        res.append('{0:{1}<25}'.format(option, chr(12288)))

    re1 = res[0:manhuadb_len]
    re2 = res[manhuadb_len:manhuadb_len + manhuadui_len]
    height = max(len(re1), len(re2))
    for n in range(height - len(re1)):
        re1.append('')
    for n in range(height - len(re2)):
        re2.append('')
    table = PrettyTable()
    # manhuadui
    table.add_column('manhuadb', re1)
    table.add_column('manhuadui', re2)
    table.align['manhuadb'] = 'l'
    table.align['manhuadui'] = 'l'
    print(table)
    placeholder = '请输入序号，默认1：'
    value = int(input(placeholder) or 1) - 1
    url = result[value]['url']

    if url.find('manhuadb') != -1:
        manhuadb.run(url)
    elif url.find('manhuadai') != -1:
        manhuadui.run(url)
