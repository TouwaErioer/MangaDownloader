#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/10 20:06
# @Author  : chobits
# @File    : table.py
from pathlib import Path

from prettytable import PrettyTable

from component.color import red_text, green_text


def show(results, config):
    table_header = ['序号', '标题', '漫画源', '作者', '分支', '话数', '存在', '和谐', '速度']
    detail = check_detail(results)
    table_header = table_header if detail else ['序号', '标题', '漫画源', '速度']
    if len(results) != 0:
        table = PrettyTable(table_header)
        for index, value in enumerate(results, 1):
            index = str(index)
            color = value.color
            title = show_title(value.title)
            name = value.name
            author = value.author
            ban = show_ban(value.ban)
            branches = value.branches
            episodes = value.episodes
            speed = show_speed(value.speed)
            folder = config.folder['path']
            path = '%s/%s' % (name, title)
            remote = bool(config.download['remote'])
            source_path = '%s%s%s' % (folder, path, '.zip' if remote else '')
            status = red_text % '存在' if Path(source_path).exists() else '不存在'
            row = [color % index, color % title, color % name, color % author, color % branches, color % episodes,
                   status, ban, speed]

            row = row if detail else [color % index, color % title, color % name, speed]
            table.add_row(row)
        # 左对齐
        table.align['序号'] = 'l'
        table.align['标题'] = 'l'
        table.align['漫画源'] = 'l'
        table.align['速度'] = 'l'
        if detail:
            table.align['作者'] = 'l'
            table.align['存在'] = 'l'
            table.align['分支'] = 'l'
            table.align['话数'] = 'l'
            table.align['和谐'] = 'l'
        # 表格显示出来
        print(table)


def show_ban(ban):
    return red_text % 'True' if bool(ban) else 'False'


def show_title(title):
    if len(title) > 15:
        return title[0:15] + '...'
    else:
        return title


def show_speed(speed):
    if float(speed) < 1:
        return green_text % speed
    elif 1 < float(speed) < 2.5:
        return red_text % speed
    elif float(speed) >= 2.5:
        return red_text % '404'


def check_detail(results):
    for result in results:
        if result.author is None or result.branches is None or result.episodes is None or result.ban is None:
            return False
    return True
