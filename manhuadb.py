#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : DHY
# @File    : manhuadb.py
import re
from bs4 import BeautifulSoup
import base64
import json
from utils import image_download, get_html, switch_ip
from common import enter_range, enter_branch
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from MangaParser import MangaParser

from fake_useragent import UserAgent


class manhuadb(MangaParser):

    def __init__(self, config):
        self.config = config.manhuadb
        self.site = self.config['site']
        self.host = self.config['host']
        self.name = self.config['name']
        self.color = '\33[1;33m%s\033[0m'
        self.search_url = self.config['search-url']
        self.tor = bool(int(self.config.download['tor']))
        self.headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:63.0) Gecko/20100101 Firefox/63.0',
        }

    # 搜索
    def search(self, keywords: str):
        try:
            url = self.search_url % keywords
            response = get_html(url, headers=self.headers, tor=self.tor)
            soup = BeautifulSoup(response.content, 'lxml')
            results = soup.select('.comicbook-index')
            result_list = []
            for result in results:
                item = result.select('a')[0]
                author = result.select('.comic-author a')[0].get('title')
                result_list.append(
                    {'title': self.color % item.get('title'), 'url': self.site + item.get('href'),
                     'author': self.color % author,
                     'source': self.color % self.name,
                     'path': '%s/%s' % (self.name, item.get('title'))
                     },
                )
            return result_list
        except Exception as e:
            print('请求错误，%s，%s' % (url, e))

    # 获取分支
    def get_branch(self, soup):
        tabs = soup.select('#myTab .nav-link')
        tab = {}
        for item in tabs:
            tab[item.get_text()] = item.get('aria-controls')
        return tab

    # 获取全部话
    def get_episodes(self, soup, branch, value):
        url_list = []
        sort_div = soup.select('.sort_div')
        for div in sort_div:
            url = div.select('a')[0].get('href')
            if url.find(branch.get(list(branch.keys())[value])) != -1:
                url_list.append(url)
        return url_list

    def get_jpg_list(self, html):
        return json.loads(str(base64.b64decode(re.findall("img_data = '(.*?)'", html)[0]).decode('utf-8')))

    def works(self, url, title):
        html = get_html(url, self.headers).text
        result = self.get_jpg_list(html)
        jpg_url = re.findall(r'<img class="img-fluid show-pic" src="(.*?)" />', html)[0]
        suffix = jpg_url.split('/')[-1]
        prefix = jpg_url.replace(suffix, '')
        episode = re.findall('<h2 class="h4 text-center">(.*?)</h2>', html)[0]
        self.headers['Host'] = self.config['image-host']
        task = {
            'title': title,
            'episode': episode,
            'jpg_url_list': [],
            'source': self.name,
            'headers': self.headers
        }
        for res in result:
            task['jpg_url_list'].append({'url': prefix + res['img'], 'page': res['p']})
        # 设置Host
        if len(task['jpg_url_list']) != 0:
            task['headers']['Host'] = task['jpg_url_list'][0]['url'].split('/')[2]
        return task

    def run(self, url):
        # url = input('请输入你要批量下载漫画的网址：')[:-1] or 'https://www.manhuadb.com/manhua/1488'
        html = get_html(url, self.headers)
        soup = BeautifulSoup(html.content, 'lxml')
        title = soup.select('.comic-title')[0].get_text()

        # 分支
        branch = self.get_branch(soup)

        # 输入分支
        value = enter_branch(branch)

        # 全部的话数
        episodes = self.get_episodes(soup, branch, value)

        # 输入范围
        enter = enter_range(episodes)

        # 解析图片链接，线程池
        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(self.works, self.site + link, title) for link in episodes[enter[0]:enter[1]]]
        wait(all_task, return_when=ALL_COMPLETED)
        failure_list = []
        for work in all_task:
            result = image_download(work.result(), semaphore=int(self.config['semaphore']), tor=self.tor)
            if result is not None:
                failure_list.append(result)
        return failure_list
