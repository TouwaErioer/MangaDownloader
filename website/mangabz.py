#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/11 15:00
# @Author  : DHY
# @File    : mangabz.py
import asyncio
import re

from bs4 import BeautifulSoup
from zhconv import convert

from config.config import config
from utlis.utils import get_html
from website.manga import MangaParser


class MangaBZ(MangaParser):
    image_url = 'http://image.mangabz.com/1/%s/%s/%s.jpg?cid=%s&key=%s&type=1'
    user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36'

    def __init__(self, Config):
        self.tor = bool(int(Config.download['tor']))
        self.config = Config.mangabz
        self.site = self.config['site']
        self.host = self.config['host']
        self.name = self.config['name']
        self.color = '\33[1;36m%s\033[0m'
        self.search_url = self.config['search-url']
        self.loop = asyncio.new_event_loop()
        self.headers = {
            'Host': self.host,
            'Referer': self.site,
        }

    def search(self, keywords):
        response = get_html(self.search_url % keywords, headers=self.headers)
        soup = BeautifulSoup(response.content, 'lxml')
        results = []
        manga_list = soup.select('.mh-item-detali')
        for manga in manga_list:
            a = manga.select('a')[0]
            title = a.get('title')
            href = self.site + a.get('href')
            # 精确搜索，繁体转简体
            if convert(title, 'zh-cn').find(keywords) != -1:
                result = {
                    'title': title,
                    'url': href,
                    'author': '',
                    'name': self.name,
                    'color': self.color,
                    'object': self
                }
                results.append(result)
        results = self.get_detail(results)
        return results

    def get_soup(self, url):
        response = get_html(url, headers=self.headers)
        return BeautifulSoup(response.content, 'lxml'), response.elapsed.total_seconds()

    def get_title(self, soup):
        detail = soup.select('.detail-info-title')
        return str(detail[0].get_text()).strip()

    @staticmethod
    def get_author(soup):
        return soup.select('.detail-info-tip span')[0].select('a')[0].get_text()

    def get_branch(self, soup):
        return {'1': '1'}

    def get_episodes(self, soup, branch_id):
        hrefs = soup.select('.detail-list-form-item')
        episodes = [self.site + href.get('href') for href in hrefs]
        return list(reversed(episodes))

    def get_jpg_list(self, episode_url):
        # 设置移动端headers
        headers = self.headers.copy()
        headers['Referer'] = episode_url
        headers['User-Agent'] = self.user_agent
        response = get_html(episode_url, headers=headers)
        html = response.text
        title = re.findall('<title>(.*?)</title>', html)[0]
        episode_title = str(title).split('_')[1]
        js = re.findall("eval(.*?)\\n", html)[0]
        code = re.findall(",\\d*\\d*,'(.*?)'.split", js)[0]
        key = re.findall('[0-9a-zA-Z]{32}', code)[0]
        pages = re.findall("\\d*_\\d*", code)
        cid = re.findall("/m(.*?)/", episode_url)[0]
        path = re.findall(self.site + "/(.*?)bz/", self.url)[0]
        results = []
        for page in sorted(pages):
            results.append(self.image_url % (path, cid, page, cid, key))
        return results, episode_title

    def works(self, episode_url):
        jpg_list, episode_title = self.get_jpg_list(episode_url)
        headers = self.headers.copy()
        headers['Host'] = 'image.mangabz.com'
        task = {
            'title': self.title,
            'episode': episode_title,
            'jpg_url_list': [{'url': res, 'page': index} for index, res in enumerate(jpg_list, 1)],
            'source': self.name,
            'headers': headers
        }

        return task


if __name__ == '__main__':
    print(MangaBZ(config()).search('女高中生的虛度日常'))