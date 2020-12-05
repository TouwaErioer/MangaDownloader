#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py
import manhuadb
import manhuadui
from prettytable import PrettyTable
from common import yellow_text, blue_text, green_text, pink_text, red_text, enter_keywords
import wuqimh
import bilibili
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from utils import repeat

import os


def work(func, args):
    return func.search(args), func


if __name__ == '__main__':
    value = enter_keywords()
    keywords = value if type(value) != tuple else value[0]
    search_author = None if type(value) != tuple else value[1]
    executor = ThreadPoolExecutor(max_workers=5)
    all_task = [executor.submit(work, func, keywords) for func in [manhuadb, manhuadui, wuqimh, bilibili]]
    wait(all_task, return_when=ALL_COMPLETED)
    for task in all_task:
        result = task.result()
        if result[1] == manhuadb:
            manhuadb_result = result[0]
        if result[1] == manhuadui:
            manhuadui_result = result[0]
        if result[1] == wuqimh:
            wuqimh_result = result[0]
        if result[1] == bilibili:
            bilibili_result = result[0]
    result = []
    result.extend(manhuadb_result)
    result.extend(manhuadui_result)
    result.extend(wuqimh_result)
    result.extend(bilibili_result)

    # 表格显示出来
    if len(result) != 0:
        show = False
        table = PrettyTable(['序号', '标题', '漫画源', '作者', '状态'])
        for index, value in enumerate(result, 1):
            index = str(index)
            title = str(value['title'])
            url = str(value['url'])
            source = ''
            author = str(value['author'])
            status = '存在'
            if search_author is None or author.find(search_author) != -1:
                show = True
                if url.find('manhuadb') != -1:
                    index = yellow_text % index
                    source = yellow_text % '漫画DB'
                    path = '%s/%s' % ('漫画DB', title)
                    title = yellow_text % title
                    author = yellow_text % author
                    status = red_text % '存在' if os.path.exists(path) else '不存在'
                elif url.find('manhuadai') != -1:
                    index = blue_text % index
                    source = blue_text % '漫画堆'
                    path = '%s/%s' % ('漫画堆', title)
                    title = blue_text % title
                    author = blue_text % author
                    status = red_text % '存在' if os.path.exists(path) else '不存在'
                elif url.find('wuqimh') != -1:
                    index = green_text % index
                    source = green_text % '57漫画'
                    path = '%s/%s' % ('57漫画', title)
                    title = green_text % title
                    author = green_text % author
                    status = red_text % '存在' if os.path.exists(path) else '不存在'
                else:
                    index = pink_text % index
                    source = pink_text % 'bilibili漫画'
                    path = '%s/%s' % ('bilibili漫画', title)
                    title = pink_text % title
                    author = pink_text % author
                    status = red_text % '存在' if os.path.exists(path) else '不存在'
                table.add_row([index, title, source, author, status])
        table.align['序号'] = 'l'
        table.align['标题'] = 'l'
        table.align['漫画源'] = 'l'
        table.align['作者'] = 'l'
        table.align['状态'] = 'l'
        if show:
            print(table)

            placeholder = '请输入序号> '
            while True:
                try:
                    value = int(input(placeholder) or 1)
                    if value <= 0 or value > len(result):
                        raise IndexError
                        continue
                    break
                except ValueError:
                    print('\033[0;31;40m输入不为数字，请重新输入\033[0m')
                except IndexError:
                    print('\033[0;31;40m输入超出范围，请重新输入\033[0m')
            url = str(result[value - 1]['url'])

            failure_list = []

            if url.find('manhuadb') != -1:
                failure_list = manhuadb.run(url)
            elif url.find('manhuadai') != -1:
                failure_list = manhuadui.run(url)
            elif url.find('wuqimh') != -1:
                failure_list = wuqimh.run(url)
            else:
                cookie = None
                if cookie is None:
                    while True:
                        cookie = input('请输入cookie> ')
                        if cookie == '':
                            raise Exception('输入为空，请重新输入')
                        break
                failure_list = bilibili.run(url, cookie)
            repeat(failure_list, 2)
        else:
            print('没有查询到结果')
    else:
        print('没有查询到结果')
