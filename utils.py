#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 16:44
# @Author  : DHY
# @File    : utils.py


import requests
import os
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

img_headers = {
    'Referer': 'https://www.manhuadb.com/manhua/1466',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/66.0.3359.139 Safari/537.36',
    'Host': 'i1.manhuadb.com',
}


def work(task: dict):
    try:
        data = requests.get(task['url'], headers=img_headers)
        with open(task['path'], 'wb') as f:
            f.write(data.content)
    except Exception as e:
        print(e)


def image_download(task: dict):
    # 参数检查
    if 'title' in task is False and 'episode' in task is False and 'jpg_url_list' in task is False and 'pages' in task:
        assert ValueError

    title = task['title']
    episode = task['episode']
    jpg_url_list = task['jpg_url_list']
    pages = task['pages']

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=30)
    all_task = []
    for jpg_url in jpg_url_list:
        if not os.path.exists(title + '/' + episode):
            # 递归创建文件夹
            os.makedirs(title + '/' + episode)
        path = '%s/%s/%s' % (title, episode, str(jpg_url['page']) + '.jpg')

        if not os.path.exists(path):
            all_task.append(executor.submit(work, {'url': jpg_url['url'], 'path': path}))
        else:
            print('文件已存在')

    wait(all_task, return_when=ALL_COMPLETED)
    print('%s-下载完成，共%d话，已下载%d话' % (episode, pages, len(jpg_url_list)))