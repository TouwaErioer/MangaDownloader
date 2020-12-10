#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : run.py
import asyncio
import time

from prettytable import PrettyTable
from MangaParser import MangaParser
from bilibili import BiliBili
from common import red_text, enter_keywords, enter_index, blue_text, green_text, pink_text
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from config import config
from manhuadb import ManhuaDB
from manhuadui import ManhuaDui

from utils import repeat, make_zip, work_speed
import os
from wuqimh import WuQiMh
import shutil
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)


def work(parser, args):
    if isinstance(parser, MangaParser):
        return parser.search(args)
    else:
        raise TypeError


def get_manga(option):
    if option == '漫画db':
        return ManhuaDB(config)
    elif option == '漫画堆':
        return ManhuaDui(config)
    elif option == '57漫画':
        return WuQiMh(config)
    elif option == 'bilibili漫画':
        return BiliBili(config)
    else:
        raise TypeError


if __name__ == '__main__':

    # 生成config对象，检查配置文件
    config = config()

    # 已选站点
    selected = config.select_site()
    options = [site for site in selected]

    # 输入关键字
    value = enter_keywords()
    keywords = value if type(value) != tuple else value[0]
    author = None if type(value) != tuple else value[1]

    # 线程池获取搜索结果
    executor = ThreadPoolExecutor(max_workers=5)
    all_task = [executor.submit(work, parser, keywords) for parser in [get_manga(option) for option in options]]
    wait(all_task, return_when=ALL_COMPLETED)

    results = []
    for task in all_task:
        result = task.result()
        if result is not None:
            results.extend(task.result())

    executor = ThreadPoolExecutor(max_workers=20)
    search_results = [executor.submit(result['object'].get_detail, result['url']) for result in results]
    wait(search_results, return_when=ALL_COMPLETED)

    for search_result in search_results:
        res = search_result.result()
        for result in results:
            if result['url'] == res['url']:
                result.update(res)
        # if res['image_list'] is not None:
        #     headers = res['headers']
        #     start = time.time()
        #     loop = asyncio.get_event_loop()
        #     results = [asyncio.ensure_future(work_speed({'url': jpg, 'headers': headers})) for jpg in res['image_list']]
        #     loop.run_until_complete(asyncio.wait(results))
        #     time_consuming = float(time.time() - start)
        #     print(time_consuming)

    # 筛选author
    if author is not None:
        results = [res for res in results if res['author'].find(author) != -1]
    if len(results) != 0:
        table = PrettyTable(['序号', '标题', '漫画源', '作者', '分支', '话数', '响应', '存在', '和谐'])
        for index, value in enumerate(results, 1):
            index = str(index)
            color = str(value['color'])
            title = str(value['title'])
            url = str(value['url'])
            name = value['name']
            author = str(value['author'])
            ban = red_text % 'True' if bool(value['ban']) else 'False'
            branches = str(value['branches'])
            episodes = str(value['episodes'])
            if name == 'bilibili漫画':
                total_seconds = green_text % '稳定'
            elif float(value['total_seconds']) != 0:
                total_seconds = str(value['total_seconds'])
            else:
                total_seconds = red_text % '404'
            folder = config.folder['path']
            path = '%s/%s' % (name, title)
            source_path = '%s%s' % (folder, path)
            status = red_text % 'yes' if os.path.exists(source_path) else 'no'
            table.add_row(
                [color % index, color % title, color % name, color % author, color % branches, color % episodes,
                 total_seconds, status, ban])
        # 左对齐
        table.align['序号'] = 'l'
        table.align['标题'] = 'l'
        table.align['漫画源'] = 'l'
        table.align['作者'] = 'l'
        table.align['分支'] = 'l'
        table.align['话数'] = 'l'
        table.align['响应'] = 'l'
        table.align['存在'] = 'l'
        table.align['和谐'] = 'l'
        # 表格显示出来
        print(table)

        # 输入序号
        value = enter_index(len(results))
        selected_result = results[value - 1]
        url = str(selected_result['url'])
        parser = selected_result['object']

        # 失败列表
        failure_list = []
        # 资源不存在列表
        not_exist_tasks = []

        if isinstance(parser, MangaParser):
            # 运行
            failure_list, not_exist_tasks, time_consuming = parser.run(url)
            # 重试
            repeat(failure_list)

            if len(not_exist_tasks) != 0:
                for not_exist_task in not_exist_tasks:
                    print(not_exist_task)

            title = selected_result['title']
            name = selected_result['name']
            path = config.folder['path']
            source_dir = '%s%s/%s' % (path, name, title)
            zip_name = '%s%s/%s.zip' % (path, name, title)

            # 查找目录下全部的文件
            file_total = 0
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_total += 1

            # 压缩
            if int(config.download['remote']) and file_total != 0:
                make_zip(source_dir, zip_name)
                # 删除文件夹
                shutil.rmtree(source_dir)
            file_total = blue_text % str(file_total)
            time_consuming = green_text % str(time_consuming)
            print('共下载文件%s个，耗时%s秒' % (file_total, time_consuming))
    else:
        print('没有查询到结果')
