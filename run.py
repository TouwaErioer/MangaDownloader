#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py
from prettytable import PrettyTable
from MangaParser import MangaParser
from bilibili import bilibili
from common import red_text, enter_keywords, enter_index
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from config import config
from manhuadb import manhuadb
from manhuadui import manhuadui
from utils import repeat, make_zip
import os
from wuqimh import wuqimh
import shutil


# parser 对象
def work(parser, args):
    if isinstance(parser, MangaParser):
        return parser.search(args), parser
    else:
        raise TypeError


def get_manga(option):
    if option == '漫画db':
        return manhuadb(config)
    elif option == '漫画堆':
        return manhuadui(config)
    elif option == '57漫画':
        return wuqimh(config)
    elif option == 'bilibili漫画':
        return bilibili(config)
    else:
        raise TypeError


if __name__ == '__main__':

    # 生成config对象，检查配置文件
    config = config()

    # 已选站点
    select = config.select_site()
    options = [site for site in select]

    # 输入关键字
    value = enter_keywords()
    keywords = value if type(value) != tuple else value[0]
    search_author = None if type(value) != tuple else value[1]

    # 线程池获取搜索结果
    executor = ThreadPoolExecutor(max_workers=5)
    all_task = [executor.submit(work, parser, keywords) for parser in [get_manga(option) for option in options]]
    wait(all_task, return_when=ALL_COMPLETED)
    results = []
    for task in all_task:
        result = task.result()[0]
        if result is not None:
            for res in result:
                res['obj'] = task.result()[1]
            results.extend(result)

    if search_author is not None:
        results = [res for res in results if res['author'].find(search_author) != -1]

    # 表格显示出来
    if len(results) != 0:
        table = PrettyTable(['序号', '标题', '漫画源', '作者', '状态'])
        for index, value in enumerate(results, 1):
            index = str(index)
            title = str(value['title'])
            url = str(value['url'])
            source = value['source']
            author = str(value['author'])
            folder = config.folder['path']
            path = str(value['path'])
            path = '%s%s' % (folder, path)
            status = red_text % '存在' if os.path.exists(path) else '不存在'
            table.add_row([index, title, source, author, status])
        table.align['序号'] = 'l'
        table.align['标题'] = 'l'
        table.align['漫画源'] = 'l'
        table.align['作者'] = 'l'
        table.align['状态'] = 'l'
        print(table)
        # 输入序号
        value = enter_index(len(results))
        url = str(results[value - 1]['url'])
        obj = results[value - 1]['obj']

        failure_list = []
        if isinstance(obj, MangaParser):
            failure_list = obj.run(url)

        repeat(failure_list, int(config.download['repeat']))
        print('下载完成')
        if int(config.download['remote']):
            source_dir = str(results[value - 1]['path'])
            array = source_dir.split('/')
            title = array[1]
            name = array[0]
            path = config.folder['path']
            source_dir = path + source_dir
            zip_name = '%s[%s]%s.zip' % (path, name, title)
            make_zip(source_dir, zip_name)
            # 删除文件夹
            shutil.rmtree(source_dir)

    else:
        print('没有查询到结果')
