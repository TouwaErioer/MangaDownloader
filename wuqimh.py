#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 23:06
# @Author  : DHY
# @File    : wuqimh.py
import js2py
import re

from parser import MangaParser
from utils import get_html
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)


class WuQiMh(MangaParser):

    def __init__(self, config):
        self.tor = bool(int(config.download['tor']))
        self.config = config.wuqimh
        self.site = self.config['site']
        self.name = self.config['name']
        self.host = self.config['host']
        self.color = '\33[1;32m%s\033[0m'
        self.image_site = self.config['image-site']
        self.search_url = self.config['search-url']
        self.headers = {
            'Host': self.host,
            'Referer': self.host,
            'User-Agent': UserAgent().random
        }

    def search(self, keywords, is_recursion=False):
        try:
            url = self.search_url % keywords
            html = get_html(url, self.headers, tor=self.tor)
            soup = BeautifulSoup(html.content, 'lxml')
            page_count = len(soup.select('.pager-cont a'))
            books = soup.select('.book-detail')
            result = []
            for book in books:
                a = book.select('dt a')[0]
                author = book.select('.tags')[2].select('a')[0].get_text()
                result.append({
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
                    result.extend(task.result())
            return result
        except Exception as e:
            print('请求错误，%s，%s' % (url, e))

    def get_soup(self, url):
        html = get_html(url, self.headers)
        return BeautifulSoup(html.content, 'lxml')

    @staticmethod
    def get_title(soup):
        return soup.select('h1')[0].get_text()

    def get_branch(self, soup):
        return None

    def get_episodes(self, soup, branch, value):
        pages = soup.select('#chpater-list-1 a')
        episodes = list(reversed([page.get('href') for page in pages]))
        return episodes

    def get_jpg_list(self, js):
        # js2py运行js获取图片列表
        code = js2py.eval_js(js)
        return str(re.findall("'fs':\\s*(\\[.*?\\])", code)[0])[1:-1].replace("'", '').split(',')

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
        headers['Referer'] = 'http://%s' % self.host
        headers.pop('Host')
        task = {'title': title,
                'episode': episode,
                'jpg_url_list': [{'url': self.image_site + jpg, 'page': index} for index, jpg in
                                 enumerate(jpg_list, 1)],
                'source': self.name,
                'headers': headers
                }
        return task

    def get_episodes_url(self, url):
        return self.site + url
