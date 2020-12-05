#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py
import manhuadb
import manhuadui
from prettytable import PrettyTable
from common import yellow_text, blue_text, green_text, pink_text
import wuqimh
import bilibili
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from utils import repeat


def work(func, args):
    return func.search(args), func


if __name__ == '__main__':
    keywords = input('请输入关键词> ') or '辉夜'
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
    table = PrettyTable(['序号', '标题', '漫画源', '作者', '速度'])
    for index, value in enumerate(result, 1):
        index = str(index)
        title = str(value['title'])
        url = str(value['url'])
        source = ''
        author = str(value['author'])
        if url.find('manhuadb') != -1:
            index = yellow_text % index
            source = yellow_text % '漫画DB'
            title = yellow_text % title
            author = yellow_text % author
        elif url.find('manhuadai') != -1:
            index = blue_text % index
            source = blue_text % '漫画堆'
            title = blue_text % title
            author = blue_text % author
        elif url.find('wuqimh') != -1:
            index = green_text % index
            source = green_text % '57漫画'
            title = green_text % title
            author = green_text % author
        else:
            index = pink_text % index
            source = pink_text % 'bilibili漫画'
            title = pink_text % title
            author = pink_text % author
        table.add_row([index, title, source, author, 1])
    table.align['序号'] = 'l'
    table.align['标题'] = 'l'
    table.align['漫画源'] = 'l'
    table.align['作者'] = 'l'
    table.align['话数'] = 'l'
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
        cookie = '_uuid=C6EA66E9-58BE-D6E1-B955-6CAB2C9964AC90814infoc; buvid3=8A04CD2C-A8A8-44E2-9E3C-08EC2C3A291658502infoc; CURRENT_FNVAL=80; blackside_state=1; Hm_lvt_6ab26a3edfb92b96f655b43a89b9ca70=1607009620,1607009620; PVID=1; Hm_lvt_a69e400ba5d439df060bf330cd092c0d=1607009620,1607009620,1607048995; sid=74aczuq6; finger=1571944565; DedeUserID=5994872; DedeUserID__ckMd5=75d8f1c95545e76a; SESSDATA=7ff706e9%2C1622601282%2C8bb69*c1; bili_jct=c72081981ac5a3106fc1e5ac2d7247cf; Hm_lpvt_6ab26a3edfb92b96f655b43a89b9ca70=1607049309; Hm_lpvt_a69e400ba5d439df060bf330cd092c0d=1607049333'

        if cookie is None:
            while True:
                cookie = input('请输入cookie> ')
                if cookie == '':
                    raise Exception('输入为空，请重新输入')
                break
        failure_list = bilibili.run(url, cookie)
    repeat(failure_list, 2)
