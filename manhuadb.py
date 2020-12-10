#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : DHY
# @File    : manhuadb.py
import re
from bs4 import BeautifulSoup
import base64
import json
from config import config
from utils import get_html
from MangaParser import MangaParser


class ManhuaDB(MangaParser):

    def __init__(self, Config):
        self.tor = bool(int(Config.download['tor']))
        self.config = Config.manhuadb
        self.site = self.config['site']
        self.host = self.config['host']
        self.name = self.config['name']
        self.color = '\33[1;33m%s\033[0m'
        self.search_url = self.config['search-url']
        self.headers = {
            'Host': self.host,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:63.0) Gecko/20100101 Firefox/63.0',
        }

    def search(self, keywords: str):
        url = self.search_url % keywords
        response = get_html(url, headers=self.headers, tor=self.tor)
        soup = BeautifulSoup(response.content, 'lxml')
        results = soup.select('.comicbook-index')
        result_list = []
        for result in results:
            item = result.select('a')[0]
            author = result.select('.comic-author a')[0].get('title')
            result_list.append(
                {'title': item.get('title'),
                 'url': self.site + item.get('href'),
                 'author': author,
                 'name': self.name,
                 'color': self.color,
                 'object': self
                 },
            )
        return result_list

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

    def get_jpg_list(self, url):
        response = get_html(url, self.headers)
        html = response.text
        jpg_url = re.findall(r'<img class="img-fluid show-pic" src="(.*?)" />', html)[0]
        suffix = jpg_url.split('/')[-1]
        prefix = jpg_url.replace(suffix, '')
        episode = re.findall('<h2 class="h4 text-center">(.*?)</h2>', html)[0]
        jpg_list = json.loads(str(base64.b64decode(re.findall("img_data = '(.*?)'", html)[0]).decode('utf-8')))
        jpg_list = [prefix + jpg['img'] for jpg in jpg_list]
        return jpg_list, episode

    def works(self, url, title):
        result, episode = self.get_jpg_list(url)
        header = {
            'Host': self.config['image-host'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:63.0) Gecko/20100101 Firefox/63.0',
        }
        task = {
            'title': title,
            'episode': episode,
            'jpg_url_list': [],
            'source': self.name,
            'headers': header
        }
        for index, res in enumerate(result, 1):
            task['jpg_url_list'].append({'url': res, 'page': index})
        # 设置Host
        if len(task['jpg_url_list']) != 0:
            task['headers']['Host'] = task['jpg_url_list'][0]['url'].split('/')[2]
        return task

    def get_episodes_url(self, url):
        return url


if __name__ == '__main__':
    print(ManhuaDB(config()).search('魔王城'))
