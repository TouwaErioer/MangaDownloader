#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 23:06
# @Author  : DHY
# @File    : wuqimh.py
import js2py
import re

from MangaParser import MangaParser
from utils import get_html
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from common import enter_range, green_text
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from utils import image_download


class wuqimh(MangaParser):
    source = '57漫画'

    def __init__(self, config):
        self.host = 'www.wuqimh.com'
        self.color = green_text
        self.config = config

    def search(self, keywords, isRecursion=False):
        headers = {
            'Host': 'www.wuqimh.com',
            'Referer': 'www.wuqimh.com',
            'User-Agent': UserAgent().random
        }
        html = get_html('http://www.wuqimh.com/search/q_' + keywords, headers)
        soup = BeautifulSoup(html.content, 'lxml')
        page_count = len(soup.select('.pager-cont a'))
        books = soup.select('.book-detail')
        result = []
        for book in books:
            a = book.select('dt a')[0]
            author = book.select('.tags')[2].select('a')[0].get_text()
            result.append({
                'title': self.color % a.get('title'),
                'url': 'http://' + self.host + a.get('href'),
                'author': self.color % author,
                'source': self.color % self.source
            })
        # 页数大于1，线程池获取第二页以后的数据
        if page_count > 1 and isRecursion is not True:
            executor = ThreadPoolExecutor(max_workers=5)
            all_task = [executor.submit(self.search, keywords + '-p-' + str(page), isRecursion=True) for page in
                        range(2, page_count + 1)]
            wait(all_task, return_when=ALL_COMPLETED)
            for task in all_task:
                result.extend(task.result())
        return result

    def get_branch(self):
        pass

    # python运行js获取图片列表
    def get_jpg_list(self, js):
        code = js2py.eval_js(js)
        return str(re.findall("'fs':\\s*(\\[.*?\\])", code)[0])[1:-1].replace("'", '').split(',')

    def get_episodes(self, soup):
        pages = soup.select('#chpater-list-1 a')
        episodes = list(reversed([page.get('href') for page in pages]))
        return episodes

    def works(self, link, title):
        headers = {
            'Host': 'www.wuqimh.com',
            'Referer': link,
            'User-Agent': UserAgent().random
        }
        html = get_html(link, headers)
        js = re.findall('eval(.*?)\\n', html.text)[0]
        jpg_list = self.get_jpg_list(js)
        episode = re.findall('<h2>(.*?)</h2>', html.text)[0]
        headers['Referer'] = 'http://www.wuqimh.com/'
        headers.pop('Host')
        task = {'title': title,
                'episode': episode,
                'jpg_url_list': [{'url': 'http://images.720rs.com' + jpg, 'page': index} for index, jpg in
                                 enumerate(jpg_list, 1)],
                'source': '57漫画',
                'headers': headers
                }
        return task

    def run(self, url):
        headers = {
            'User-Agent': UserAgent().random
        }
        host = 'http://www.wuqimh.com'
        html = get_html(url, headers)
        soup = BeautifulSoup(html.content, 'lxml')
        title = soup.select('h1')[0].get_text()

        # 获取全部话数
        episodes = self.get_episodes(soup)

        # 输入范围
        enter = enter_range(episodes)

        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(self.works, host + link, title) for link in episodes[enter[0]:enter[1]]]
        wait(all_task, return_when=ALL_COMPLETED)

        failure_list = []
        for work in all_task:
            result = image_download(work.result(), self.config.semaphore)
            if result is not None:
                failure_list.append(result)

        return failure_list


if __name__ == '__main__':
    print(wuqimh())