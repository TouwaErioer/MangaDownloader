#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : chobits
# @File    : manhuadb.py
import re
from bs4 import BeautifulSoup
import base64
import json

from component.result import Result
from component.task import Task
from config import config
from utlis.network import get_html
from website.manga import MangaParser


class ManhuaDB(MangaParser):

    def __init__(self, Config):
        self.config = Config.manhuadb
        super().__init__(self.config)
        self.headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:63.0) Gecko/20100101 Firefox/63.0',
        }

    def search(self, keywords: str, enter_author, site):
        if site is None or site == self.name:
            enter_author = enter_author if enter_author is not None else ''
            url = self.search_url % keywords
            response = get_html(url, self.headers)
            soup = BeautifulSoup(response.content, 'lxml')
            comic_book = soup.select('.comicbook-index')
            results = []
            for comic in comic_book:
                item = comic.select('a')[0]
                title = item.get('title')
                author = comic.select('.comic-author a')[0].get('title')
                href = self.site + item.get('href')
                if title.find(keywords) != -1 and author.find(enter_author) != -1:
                    results.append(Result(title, href, author, self, self.color, self.name, None, None, None,
                                          response.elapsed.total_seconds()))
            results = super().search(results)
            return results

    def get_soup(self, url):
        html = get_html(url, self.headers)
        return BeautifulSoup(html.content, 'lxml'), html.elapsed.total_seconds()

    @staticmethod
    def get_title(soup):
        return soup.select('.comic-title')[0].get_text()

    def get_branch(self, soup):
        tabs = soup.select('#myTab .nav-link')
        if len(tabs) != 0:
            tab = {}
            for item in tabs:
                tab[item.get_text()] = item.get('aria-controls')
            return tab
        else:
            raise Exception('已下架')

    def get_episodes(self, soup, branch_id):
        url_list = []
        sort_div = soup.select('.sort_div')
        for div in sort_div:
            url = div.select('a')[0].get('href')
            if url.find(branch_id) != -1:
                url_list.append(self.site + url)
        return url_list

    def get_jpg_list(self, episode_url):
        response = get_html(episode_url, self.headers)
        html = response.text
        jpg_url = re.findall(r'<img class="img-fluid show-pic" src="(.*?)" />', html)[0]
        suffix = jpg_url.split('/')[-1]
        prefix = jpg_url.replace(suffix, '')
        episode = re.findall('<h2 class="h4 text-center">(.*?)</h2>', html)[0]
        jpg_list = json.loads(str(base64.b64decode(re.findall("img_data = '(.*?)'", html)[0]).decode('utf-8')))
        jpg_list = [prefix + jpg['img'] for jpg in jpg_list]
        return jpg_list, episode

    def works(self, episode_url):
        jpg_list, episode_title = self.get_jpg_list(episode_url)
        headers = self.headers.copy()
        # 设置Host
        headers['Host'] = jpg_list[0].split('/')[2]
        jpg_list = [{'url': jpg, 'index': index} for index, jpg in enumerate(jpg_list, 1)]
        task = Task(self.name, self.title, episode_title, jpg_list, headers)
        return task


if __name__ == '__main__':
    print(ManhuaDB(config()).search('魔王城'))
