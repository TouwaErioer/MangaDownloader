#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:50
# @Author  : chobits
# @File    : cli.py
import time

import requests
from progress.spinner import Spinner

from component.color import blue_text, green_text, yellow_text
from component.enter import enter_keywords, enter_index, check_speed, enter_command
from config.config import config
from test.test import get_test
from website.manga import MangaParser
from website.mangabz import MangaBZ
from website.manhuadb import ManhuaDB
from website.manhuadui import ManhuaDui
from website.wuqimh import WuQiMh
from website.bilibili import BiliBili
from component.table import show
from utlis.repeat import repeat
from utlis.file import make_zip, get_file_total
import shutil
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)


def work(parser):
    if isinstance(parser, MangaParser):
        return parser.search(keywords, author, site)
    else:
        raise TypeError('%s不属于%s' % (parser, MangaParser))


def get_parser(option):
    for parser in parsers:
        if parser.name == option:
            return parser
    raise ValueError('找不到%s的类' % option)


if __name__ == '__main__':
    try:
        enter_command()

        # 生成config对象，检查配置文件
        config = config()

        # 初始化所有解析器
        parsers = MangaParser.__subclasses__()
        parsers = [parser(config) for parser in parsers]

        # 已选站点
        options = config.select_site()

        # 输入关键字
        keywords, author, site = enter_keywords(config)

        start = time.time()
        # 线程池获取搜索结果
        executor = ThreadPoolExecutor(max_workers=5)
        all_task = [executor.submit(work, parser) for parser in [get_parser(option) for option in options]]
        spinner = Spinner('Loading ')
        for task in all_task:
            while task.done() is False:
                spinner.next()
                time.sleep(0.1)
        print('')
        wait(all_task, return_when=ALL_COMPLETED)
        print('用时%f秒' % float(time.time() - start))  # 2s

        # 合并搜索结果
        results = []
        for task in all_task:
            result = task.result()
            if result is not None:
                results.extend(result)

        # 获取测试结果
        tests = get_test()

        for result in results:
            result.update_speed(tests)

        if len(results) != 0:

            # 显示表
            show(results, config)

            # 输入序号
            value = enter_index(len(results)) - 1

            selected = results[value]
            url = selected.href
            parser = selected.obj
            ban = selected.ban
            title = selected.title
            name = selected.name
            speed = selected.speed
            check_speed(speed)
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
            print('%s没有查询到结果' % (yellow_text % keywords))
    except requests.exceptions.ReadTimeout:
        print('连接失败，请重试')
    except Exception as e:
        print(e)
