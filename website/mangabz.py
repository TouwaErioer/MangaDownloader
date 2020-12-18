#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/11 15:00
# @Author  : chobits
# @File    : mangabz.py
import re

from bs4 import BeautifulSoup

from component.result import Result
from component.task import Task
from config.config import config
from utlis.network import get_html
from website.manga import MangaParser


class MangaBZ(MangaParser):

    image_url = 'http://image.mangabz.com/1/%s/%s/%s.jpg?cid=%s&key=%s&type=1'

    # todo 随机
    user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36'

    def __init__(self, Config):
        self.config = Config.mangabz
        super().__init__(self.config)
        self.headers = {
            'Host': self.host,
            'Referer': self.site,
        }

    def search(self, keywords, enter_author, site):
        if site is None or site == self.name:
            enter_author = enter_author if enter_author is not None else ''
            response = get_html(self.search_url % keywords, self.headers)
            soup = BeautifulSoup(response.content, 'lxml')
            results = []
            manga_list = soup.select('.mh-item-detali')
            for manga in manga_list:
                a = manga.select('a')[0]
                title = a.get('title')
                href = self.site + a.get('href')
                # 精确搜索，繁体转简体
                if convert(title, 'zh-cn').find(keywords) != -1:
                    result = Result(title, href, None, self, self.color, self.name, None, None, None, None)
                    results.append(result)
            results = super().search(results)
            results = [result for result in results if
                       result.author is None or result.author.find(enter_author) != -1]
            return results

    def get_soup(self, url):
        response = get_html(url, self.headers)
        return BeautifulSoup(response.content, 'lxml'), response.elapsed.total_seconds()

    def get_title(self, soup):
        detail = soup.select('.detail-info-title')
        return str(detail[0].get_text()).strip()

    @staticmethod
    def get_author(soup):
        return soup.select('.detail-info-tip span')[0].select('a')[0].get_text()

    def get_branch(self, soup):
        # todo branch缺省
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
        response = get_html(episode_url, headers)
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
        jpg_list = [{'url': jpg, 'index': index} for index, jpg in enumerate(jpg_list, 1)]
        task = Task(self.name, self.title, episode_title, jpg_list, headers)
        return task


if __name__ == '__main__':
    print(MangaBZ(config()).search('女高中生的虛度日常'))
