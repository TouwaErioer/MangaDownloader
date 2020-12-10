#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/3 12:35
# @Author  : DHY
# @File    : MangaParser.py
import asyncio
import time
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from common import enter_branch, enter_range
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from utils import download, get_detail, work_speed


class MangaParser(metaclass=ABCMeta):

    def __init__(self):
        self.url = None

    # 搜索
    @abstractmethod
    def search(self, keywords):
        pass

    # 获取soup
    @abstractmethod
    def get_soup(self, url):
        pass

    # 获取标题
    @abstractmethod
    def get_title(self, soup):
        pass

    # 获取全部分支
    @abstractmethod
    def get_branch(self, soup):
        pass

    # 获取全部话数
    @abstractmethod
    def get_episodes(self, soup, branch, value):
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

    # 获取搜索结果的soups
    def get_search_soups(self, result_list):
        if len(result_list) != 0:
            tasks = [{'url': result['url'], 'headers': self.headers} for result in result_list]
            loop = asyncio.get_event_loop()
            results = [asyncio.ensure_future(get_detail(task)) for task in tasks]
            loop.run_until_complete(asyncio.wait(results))
            contents = [res.result() for res in results if res.result() is not None]
            soups = [BeautifulSoup(content, 'lxml') for content in contents]
            return soups

    def parser_detail(self, soups):
        if soups is not None and len(soups) != 0:
            result = []
            test = None
            for soup in soups:
                title = self.get_title(soup)
                branch = self.get_branch(soup)
                ban = False if branch is not None else True
                branches = None if ban else len(branch)
                episodes = None if ban else self.get_episodes(soup, branch, 0)
                test = episodes[0]
                result.append({'title': title, 'ban': ban, 'branches': branches, 'episodes': len(episodes)})

            # 只测试第一项第一页图片
            jpg_list, episode = self.get_jpg_list(test)

            start = time.time()
            loop = asyncio.get_event_loop()
            results = [asyncio.ensure_future(work_speed({'url': jpg, 'headers': self.headers})) for jpg in jpg_list]
            loop.run_until_complete(asyncio.wait(results))
            time_consuming = float(time.time() - start)

            # 每下载一张图耗时时间
            speed = '%.2f' % float(time_consuming / len(jpg_list))
        for res in result:
            res['speed'] = speed
        return result

    def get_detail(self, url):

        self.url = url

        # 获取soup
        soup, total_seconds = self.get_soup(url)

        # 分支
        branch = self.get_branch(soup)

        branches = 1 if branch is None else len(branch)

        ban = False if branch is not None else True

        # 全部的话数
        episodes = self.get_episodes(soup, branch, 0)

        eps = 0 if branch is None else len(episodes)

        if episodes is not None and type(episodes[0]) is str:
            image_list, episode = self.get_jpg_list(episodes[0])
        else:
            image_list = None

        # image_total_seconds = 0
        # if episodes is not None and type(episodes[0]) is str:
        #     image_list, episode = self.get_jpg_list(episodes[0])
        #     try:
        #         response = requests.get(image_list[0], headers=self.headers, timeout=15)
        #         if response.status_code != 404:
        #             image_total_seconds = response.elapsed.total_seconds()
        #     except Exception:
        #         pass
        # elif episodes is None:
        #     image_total_seconds = 0
        # elif type(episodes[0]) is tuple:  # 排除bilibili
        #     image_total_seconds = 0
        #
        # if image_total_seconds != 0:
        #     total_seconds = image_total_seconds + total_seconds
        # else:  # image_total_seconds为0代表资源不存在
        #     total_seconds = 0
        return {'ban': ban, 'total_seconds': '%.2f' % total_seconds, 'branches': branches, 'episodes': eps, 'url': url,
                'image_list': image_list, 'headers': self.headers}

    # 运行
    def run(self, url):

        self.url = url

        # 获取soup
        soup, total_seconds = self.get_soup(url)

        # 获取标题
        title = self.get_title(soup)

        # 分支
        branch = self.get_branch(soup)

        # 输入分支
        branch_id = enter_branch(branch)

        # 全部的话数
        episodes = self.get_episodes(soup, branch_id)

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
            result = download(work.result(), semaphore=int(self.config['semaphore']), tor=self.tor)
            if type(result) is list:
                failure_list.append(result)
            elif type(result) is str:
                not_exist_task.append(result)
        time_consuming = float(time.time() - start)
        return failure_list, not_exist_task, time_consuming
