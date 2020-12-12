#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : cli.py
from compoent.common import enter_keywords, enter_index, blue_text, green_text, yellow_text
from config.config import config
from website.manga import MangaParser
from website.mangabz import MangaBZ
from website.manhuadb import ManhuaDB
from website.manhuadui import ManhuaDui
from website.wuqimh import WuQiMh
from website.bilibili import BiliBili
from run.table import show
from compoent.file_tool import get_file_total
from utlis.utils import repeat, make_zip
import shutil
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)


def work(parser, args):
    if isinstance(parser, MangaParser):
        return parser.search(args)
    else:
        raise TypeError('%s不属于%s' % (parser, MangaParser))


def get_manga(option):
    if option == '漫画db':
        return ManhuaDB(config)
    elif option == '漫画堆':
        return ManhuaDui(config)
    elif option == '57漫画':
        return WuQiMh(config)
    elif option == 'bilibili漫画':
        return BiliBili(config)
    elif option == 'MangaBZ':
        return MangaBZ(config)
    else:
        raise ValueError('找不到%s的类' % option)


if __name__ == '__main__':

    # 生成config对象，检查配置文件
    config = config()

    # 已选站点
    options = config.select_site()

    # 输入关键字
    value = enter_keywords()
    keywords = value if type(value) != tuple else value[0]
    author = None if type(value) != tuple else value[1]

    # 线程池获取搜索结果
    executor = ThreadPoolExecutor(max_workers=5)
    all_task = [executor.submit(work, parser, keywords) for parser in [get_manga(option) for option in options]]
    wait(all_task, return_when=ALL_COMPLETED)

    # 合并搜索结果
    results = []
    for task in all_task:
        result = task.result()
        if result is not None:
            results.extend(result)

    # 筛选author
    if author is not None:
        results = [res for res in results if res['author'].find(author) != -1]

    if len(results) != 0:
        # 显示表
        show(results, config)

        # 输入序号
        value = enter_index(len(results))
        print(value)
        selected_result = results[value - 1]
        url = str(selected_result['url'])
        parser = selected_result['object']
        ban = selected_result['ban']
        title = selected_result['title']
        name = selected_result['name']
        path = config.folder['path']
        source_dir = '%s%s/%s' % (path, name, title)
        zip_name = '%s%s/%s.zip' % (path, name, title)

        if ban:
            raise Exception('已下架')

        if isinstance(parser, MangaParser):

            # 运行
            failure_list, not_exist_tasks, time_consuming = parser.run(url)

            # 重试
            repeat(failure_list)

            # todo 使用别的站点下载
            if len(not_exist_tasks) != 0:
                tip = '%s、%s...等文件资源未找到'
                print(tip % (yellow_text % not_exist_tasks[0], yellow_text % not_exist_tasks[1]))

            file_total = get_file_total(source_dir)

            if int(config.download['remote']) and file_total != 0:
                # 压缩
                make_zip(source_dir, zip_name)
                # 删除文件夹
                shutil.rmtree(source_dir)

            file_total = blue_text % str(file_total)
            time_consuming = green_text % str(time_consuming)
            print('共下载文件%s个，耗时%s秒' % (file_total, time_consuming))
        else:
            raise TypeError('%s不属于%s' % (parser, MangaParser))
    else:
        print('没有查询到结果')