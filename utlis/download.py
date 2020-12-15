#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 16:44
# @Author  : DHY
# @File    : download.py
import asyncio
import os
from tqdm import tqdm

from component.task import Task
from utlis.config import read_config
from utlis.network import download_image


def download(task: Task, proxy: dict, semaphore=5):
    title = task.title
    name = task.name
    episode_title = task.episode_title
    jpg_list = task.jpg_list
    headers = task.headers

    folder = read_config('folder', 'path')

    loop = asyncio.get_event_loop()
    all_task = []
    semaphore = asyncio.Semaphore(semaphore)

    for jpg in jpg_list:

        url = jpg['url']
        index = jpg['index']

        # 如果没找到文件夹，递归创建文件夹
        manga_path = '%s%s/%s/%s' % (folder, name, title, episode_title)
        if not os.path.exists(manga_path):
            os.makedirs(manga_path)

        # suffix
        image_path = '%s%s/%s/%s/%s' % (folder, name, title, episode_title, str(index) + '.jpg')
        if not os.path.exists(image_path):
            task = {'url': url, 'path': image_path, 'headers': headers}
            all_task.append(asyncio.ensure_future(download_image(task, semaphore, proxy)))

    if len(all_task) > 0:
        # 进度条
        with tqdm(total=len(all_task), desc='%s' % episode_title) as bar:
            for task in all_task:
                task.add_done_callback(lambda _: bar.update(1))
            loop.run_until_complete(asyncio.wait(all_task))

    # 失败任务表示连接错误的任务
    # 资源不存在任务代表相应404的任务
    # works返回dict或str，返回dict表示失败任务,返回str代表资源不存在任务

    # 失败任务列表
    failure_list = [task.result() for task in all_task if type(task.result()) is dict]
    not_exist_task = None
    if len(all_task) != 0:
        # 如果第一个任务不存在，判断这话不存在
        not_exist_result = all_task[0].result()
        # 资源不存在列表
        not_exist_task = str(not_exist_result) if type(not_exist_result) is str else None
    if len(failure_list) != 0:
        # 有失败任务，代表没有不存在任务
        return failure_list
    if not_exist_task is not None:
        return not_exist_task
