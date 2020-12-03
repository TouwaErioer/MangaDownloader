#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py

import manhuadb
import manhuadui
from prettytable import PrettyTable
from threading import Thread
import wuqimh


class works(Thread):
    def __init__(self, func, args):
        super(works, self).__init__()
        self.result = func.search(args)

    def get_result(self):
        return self.result


if __name__ == '__main__':
    keywords = input('请输入关键词：') or '辉夜'
    task1 = works(manhuadb, keywords)
    task2 = works(manhuadui, keywords)
    task3 = works(wuqimh, keywords)
    task1.start()
    task2.start()
    task3.start()
    task1.join()
    task2.join()
    task3.join()
    manhuadb_result = task1.get_result()
    manhuadui_result = task2.get_result()
    wuqimh_result = task3.get_result()
    result = []
    result.extend(manhuadb_result)
    result.extend(manhuadui_result)
    result.extend(wuqimh_result)

    # 找出最大标题长度
    max_title = max([len(res['title']) for res in result])

    # 遍历结果对标题加序号，按最长标题填充对齐
    res = [('{0:{1}<' + str(max_title) + '}').format((str(index) + '.' + value['title']), chr(12288)) for index, value
           in enumerate(result, 1)]

    # 对结果分类
    manhuadb_len = len(manhuadb_result)
    manhuadui_len = len(manhuadui_result)
    wuqimh_len = len(wuqimh_result)

    re1 = res[0:manhuadb_len]
    re2 = res[manhuadb_len:manhuadb_len + manhuadui_len]
    re3 = res[manhuadb_len + manhuadui_len:manhuadb_len + manhuadui_len + wuqimh_len]

    # 其他列按最长列补齐行
    height = max(len(re1), len(re2), len(re3))
    for n in range(height - len(re1)):
        re1.append('')
    for n in range(height - len(re2)):
        re2.append('')
    for n in range(height - len(re3)):
        re3.append('')

    # 表格显示出来
    table = PrettyTable()
    # manhuadui
    table.add_column('manhuadb', re1)
    table.add_column('manhuadui', re2)
    table.add_column('wuqimh', re3)
    table.align['manhuadb'] = 'l'
    table.align['manhuadui'] = 'l'
    table.align['wuqimh'] = 'l'
    print(table)

    placeholder = '共找到%d个结果，请输入序号，默认1：' % len(result)
    while True:
        try:
            value = int(input(placeholder) or 1) - 1
            if value < 0 or value > len(result):
                raise IndexError
            break
        except ValueError:
            print('\033[0;31;40m输入不为数字，请重新输入\033[0m')
        except IndexError:
            print('\033[0;31;40m输入超出范围，请重新输入\033[0m')
    url = result[value]['url']

    failure_list = []

    if url.find('manhuadb') != -1:
        failure_list = manhuadb.run(url)
    elif url.find('manhuadai') != -1:
        failure_list = manhuadui.run(url)
    elif url.find('wuqimh') != -1:
        failure_list = wuqimh.run(url)

    if len(failure_list) != 0:
        for failure in failure_list:
            print(failure)
