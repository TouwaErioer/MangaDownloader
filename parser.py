#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/3 12:35
# @Author  : DHY
# @File    : parser.py
import time
from abc import ABCMeta, abstractmethod
from common import enter_branch, enter_range
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

from utils import download


class MangaParser(metaclass=ABCMeta):

    def __init__(self):
        self.url = None

    # 搜索
    @abstractmethod
    def search(self):
        pass

    # 获取soup
    @abstractmethod
    def get_soup(self):
        pass

    # 获取标题
    @abstractmethod
    def get_title(self):
        pass

    # 获取全部分支
    @abstractmethod
    def get_branch(self):
        pass

    # 获取全部话数
    @abstractmethod
    def get_episodes(self):
        pass

    # 获取图片列表
    @abstractmethod
    def get_jpg_list(self):
        pass

    # 任务
    @abstractmethod
    def works(self):
        pass

    # 获取话链接
    def get_episodes_url(self, url):
        return url

    # 运行
    def run(self, url):

        self.url = url

        # 获取soup
        soup = self.get_soup(url)

        # 获取标题
        title = self.get_title(soup)

        # 分支
        branch = self.get_branch(soup)

        # 输入分支
        value = enter_branch(branch)

        # 全部的话数
        episodes = self.get_episodes(soup, branch, value)

        # 输入范围
        enter = enter_range(episodes)
        start = enter[0]
        end = enter[1]

        # 解析图片链接，线程池
        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(self.works, self.get_episodes_url(link), title) for link in episodes[start:end]]
        wait(all_task, return_when=ALL_COMPLETED)

        failure_list = []
        not_exist_task = []
        start = time.time()
        for work in all_task:
            try:
                result = download(work.result(), semaphore=int(self.config['semaphore']), tor=self.tor)
            except Exception as e:
                print(e)
            if type(result) is tuple:
                failure_list.append(result[0])
            elif type(result) is str:
                not_exist_task.append(result)
        time_consuming = float(time.time() - start)
        return failure_list, not_exist_task, time_consuming
