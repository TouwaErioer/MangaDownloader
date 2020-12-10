#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 23:06
# @Author  : DHY
# @File    : wuqimh.py
import js2py
import re

from MangaParser import MangaParser
from config import config
from utils import get_html, speed
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)


class WuQiMh(MangaParser):

    def __init__(self, Config):
        self.tor = bool(int(Config.download['tor']))
        self.config = Config.wuqimh
        self.site = self.config['site']
        self.name = self.config['name']
        self.host = self.config['host']
        self.test = Config.test[self.name]
        self.color = '\33[1;32m%s\033[0m'
        self.image_site = self.config['image-site']
        self.search_url = self.config['search-url']
        self.headers = {
            'Host': self.host,
            'Referer': self.host,
            'User-Agent': UserAgent().random
        }

    def search(self, keywords, is_recursion=False, detail=True):
        url = self.search_url % keywords
        html = get_html(url, self.headers, tor=self.tor)
        soup = BeautifulSoup(html.content, 'lxml')
        page_count = len(soup.select('.pager-cont a'))
        books = soup.select('.book-detail')
        result_list = []
        for book in books:
            a = book.select('dt a')[0]
            author = book.select('.tags')[2].select('a')[0].get_text()
            result_list.append({
                'title': a.get('title'),
                'url': 'http://' + self.host + a.get('href'),
                'author': author,
                'name': self.name,
                'color': self.color,
                'object': self
            })
        # 页数大于1，线程池获取第二页以后的数据
        if page_count > 1 and is_recursion is not True:
            executor = ThreadPoolExecutor(max_workers=5)
            all_task = [executor.submit(self.search, keywords + '-p-' + str(page), is_recursion=True) for page in
                        range(2, page_count + 1)]
            wait(all_task, return_when=ALL_COMPLETED)
            for task in all_task:
                result_list.extend(task.result())
        result_list = self.get_detail(result_list)
        return result_list

    def get_soup(self, url):
        html = get_html(url, self.headers)
        return BeautifulSoup(html.content, 'lxml'), html.elapsed.total_seconds()

    @staticmethod
    def get_title(soup):
        return soup.select('h1')[0].get_text()

    def get_branch(self, soup):
        # 模拟有分支
        return {'branch_id': 1}

    def get_episodes(self, soup, branch_id):
        pages = soup.select('#chpater-list-1 a')
        episodes = list(reversed([page.get('href') for page in pages]))
        episodes = [self.site + episode for episode in episodes]
        return episodes

    def get_jpg_list(self, episodes_url):
        html = get_html(episodes_url, self.headers)
        js = re.findall('eval(.*?)\\n', html.text)[0]
        episode = re.findall('<h2>(.*?)</h2>', html.text)[0]
        # js2py运行js获取图片列表
        code = js2py.eval_js(js)
        jpg_list = str(re.findall("'fs':\\s*(\\[.*?\\])", code)[0])[1:-1].replace("'", '').split(',')
        jpg_list = [self.image_site + jpg for jpg in jpg_list]
        return jpg_list, episode

    def works(self, episodes_url):
        jpg_list, episode = self.get_jpg_list(episodes_url)
        header = self.headers
        header.pop('Host')
        task = {'title': self.title,
                'episode': episode,
                'jpg_url_list': [{'url': jpg, 'page': index} for index, jpg in enumerate(jpg_list, 1)],
                'source': self.name,
                'headers': header
                }
        return task
