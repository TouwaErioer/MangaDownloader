#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/3 12:35
# @Author  : DHY
# @File    : manga.py
import asyncio
import time
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from component.enter import enter_branch, enter_range
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

from utlis.config import read_config
from utlis.download import download
from utlis.network import get_detail


class MangaParser(metaclass=ABCMeta):

    def __init__(self, config):
        self.name = config['name']
        self.site = config['site']
        self.host = config['host']
        self.search_url = config['search-url']
        self.tor = bool(int(read_config('download', 'tor')))
        self.url = None
        self.title = None

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
    def get_episodes(self, soup, branch_id):
        pass

    # 获取图片列表
    @abstractmethod
    def get_jpg_list(self, episode_url):
        pass

    # 任务
    @abstractmethod
    def works(self, episode_url):
        pass

    # 获取搜索结果的soups
    def get_search_soups(self, results):
        if len(results) != 0:
            tasks = [{'url': result.href, 'headers': self.headers, 'name': result.name} for result in results]
            # 解决 RuntimeError: Event loop is close
            # https://stackoverflow.com/questions/61543406/asyncio-run-runtimeerror-event-loop-is-closed
            # Linux ProactorEventLoop
            # Windows SelectorEventLoop
            # Python3.8 -
            # if os.name == 'nt':
            #     asyncio.set_event_loop(asyncio.SelectorEventLoop())
            # elif os.name == 'posix':
            #     # Linux使用uvloop
            #     import uvloop
            #     asyncio.set_event_loop(uvloop.new_event_loop())
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            loop = asyncio.get_event_loop()
            results = []
            for task in tasks:
                if task['name'] == 'bilibili漫画':
                    task['api'] = self.ComicDetail_API
                    task['method'] = 'post'
                results.append(asyncio.ensure_future(get_detail(task)))
            loop.run_until_complete(asyncio.wait(results))
            loop.close()
            contents = [res.result() for res in results if res.result() is not None]
            if type(contents[0][0]) is dict:
                details = [
                    {'url': content[1], 'soup': content[0], 'response_time': content[2], 'name': tasks[0]['name']} for
                    content in contents]
            else:
                details = [{'url': content[1], 'soup': BeautifulSoup(content[0], 'lxml'), 'response_time': content[2],
                            'name': tasks[0]['name']}
                           for content in contents]
            return details

    def parser_detail(self, details):
        if details is not None and len(details) != 0:
            results = []
            for detail in details:
                soup = detail['soup']
                score = detail['response_time']
                branch = self.get_branch(soup)
                ban = False if branch is not None else True
                branches = 0 if ban else len(branch)
                branch_id = 0 if ban else branch.get(list(branch.keys())[0])
                episodes = 0 if ban else len(self.get_episodes(soup, branch_id))
                result = {'url': detail['url'], 'ban': ban, 'branches': branches, 'episodes': episodes, 'speed': score}
                if detail['name'] == 'MangaBZ':
                    author = self.get_author(soup)
                    result['author'] = author
                results.append(result)
            return results

    def get_detail(self, results):
        soups = self.get_search_soups(results)
        details = self.parser_detail(soups)
        for result in results:
            for detail in details:
                if result.href == detail['url']:
                    result.update(detail)
        return results

    # 运行
    def run(self, url):

        self.url = url

        # 获取soup
        soup, total_seconds = self.get_soup(url)

        # 获取标题
        self.title = self.get_title(soup)

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
        all_task = [executor.submit(self.works, url) for url in episodes[start:end]]
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
