#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 11:03
# @Author  : chobits
# @File    : repeat.py

# 重试，直到没有失败任务
from component.task import Task
from utlis.config import get_proxy
from utlis.download import read_config, download


def repeat(failures, count=1):
    if failures is None or len(failures) == 0:
        print('下载完成')
    else:
        print('\n第%d次重试' % count)
        tasks = []
        for failure in failures:
            config_path = str(read_config('folder', 'path'))
            array = str(failure[0]['path']).replace(config_path, '').split('/')
            title = array[1]
            episode_title = array[2]
            jpg_list = []
            name = array[0]
            headers = failure[0]['headers']
            for failure_task in failure:
                url = failure_task['url']
                path = str(failure_task['path'])
                index = path.split('/')[-1].split('.')[0]
                jpg_list.append({'url': url, 'index': index})
            task = Task(name, title, episode_title, jpg_list, headers)
            tasks.append(task)
        proxy = get_proxy()
        download_results = [download(task, proxy) for task in tasks]
        results = [result for result in download_results if result is not None and type(result) is list]
        if len(results) != 0:
            return repeat(results, count + 1)
