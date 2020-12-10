#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/10 20:06
# @Author  : DHY
# @File    : table.py
import os
from pathlib import Path

from prettytable import PrettyTable

from common import red_text, green_text


def show(results, config):
    if len(results) != 0:
        table = PrettyTable(['序号', '标题', '漫画源', '作者', '分支', '话数', '存在', '和谐', '响应'])
        for index, value in enumerate(results, 1):
            index = str(index)
            color = str(value['color'])
            title = str(value['title'])
            if len(title) > 15:
                title = title[0:15] + '...'
            else:
                title = title
            url = str(value['url'])
            name = value['name']
            author = str(value['author'])
            ban = red_text % 'True' if bool(value['ban']) else 'False'
            branches = str(value['branches'])
            episodes = str(value['episodes'])
            speed = value['speed']
            if speed is not None:
                if float(speed) < 1:
                    speed = green_text % speed
                else:
                    speed = red_text % speed
            else:
                speed = red_text % '404'
            folder = config.folder['path']
            path = '%s/%s' % (name, title)
            remote = bool(config.download['remote'])
            source_path = '%s%s%s' % (folder, path, '.zip' if remote else '')
            status = red_text % '存在' if Path(source_path).exists() else '不存在'
            table.add_row(
                [color % index, color % title, color % name, color % author, color % branches, color % episodes, status,
                 ban, speed])
        # 左对齐
        table.align['序号'] = 'l'
        table.align['标题'] = 'l'
        table.align['漫画源'] = 'l'
        table.align['作者'] = 'l'
        table.align['存在'] = 'l'
        table.align['分支'] = 'l'
        table.align['话数'] = 'l'
        table.align['和谐'] = 'l'
        table.align['响应'] = 'l'
        # 表格显示出来
        print(table)
