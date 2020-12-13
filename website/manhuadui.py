#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 10:05
# @Author  : DHY
# @File    : manhuadui.py
from component.color import blue_text
from component.result import Result
from component.task import Task
from website.manga import MangaParser
from utlis.network import get_html
from utlis.decrypt import aes_decrypt
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class ManhuaDui(MangaParser):

    def __init__(self, Config):
        self.config = Config.manhuadui
        super().__init__(self.config)
        self.test = Config.test[self.name]
        self.color = blue_text
        self.image_site = self.config['image-site']
        self.headers = {
            'User-Agent': UserAgent().random
        }

    # 搜索
    def search(self, keywords: str, enter_author, detail=True):
        enter_author = enter_author if enter_author is not None else ''
        url = self.search_url % keywords
        search_response = get_html(url, headers=self.headers, tor=self.tor)
        search_soup = BeautifulSoup(search_response.content, 'lxml')
        comic_list = search_soup.select('.list-comic')
        results = []
        for comic in comic_list:
            title = a.get('title')
            author = comic.select('.auth')[0].get_text()
            href = a.get('href')
            a = comic.select('a')[1]
            if title.find(keywords) != -1 and author.find(enter_author) != -1:
                results.append(Result(title, href, author, self, self.color, self.name, None, None, None, None))
        results = self.get_detail(results)
        return results

    def get_soup(self, url):
        self.headers['User-Agent'] = UserAgent().random
        html = get_html(url, self.headers)
        return BeautifulSoup(html.content, 'lxml'), html.elapsed.total_seconds()

    @staticmethod
    def get_title(soup):
        return soup.select('h1')[0].get_text()

    def get_branch(self, soup):
        tabs = soup.select('.zj_list .c_3')
        if len(tabs) != 0:
            data_keys = soup.select('.zj_list_head_px')
            branch = {}
            for index, item in enumerate(tabs):
                branch[item.get_text()] = data_keys[index].get('data-key')
            return branch
        else:
            # raise Exception('已下架')
            return None

    def get_episodes(self, soup, branch_id):
        if branch_id is not None:
            data_key = branch_id
            select_page = soup.select('#chapter-list-%s a' % data_key)
            pages = []
            for page in select_page:
                pages.append(self.site + page.get('href'))
            return pages

    def get_jpg_list(self, url):
        response = get_html(url, self.headers)
        soup = BeautifulSoup(response.content, 'lxml')
        episode = soup.select('.head_title h2')[0].get_text()
        code = re.findall("var chapterImages =\\s*\"(.*?)\"", response.text)[0]
        chapter_path = re.findall("var chapterPath = \"(.*?)\"", response.text)[0]

        key = self.config['key'].encode('utf-8')
        iv = self.config['iv'].encode('utf-8')
        page_list = aes_decrypt(key, iv, code)[1:-1].split(',')
        jpg_list = []
        for p in page_list:
            if p.find('ManHuaKu') != -1:
                if p.find(']') != -1:
                    jpg_list.append(p.replace('\\', '').replace('"', '').split(']')[0])
                else:
                    jpg_list.append(p.replace('\\', '').replace('"', ''))
            else:
                if p.find(']') != -1:
                    jpg_list.append(self.image_site + chapter_path + p.replace('"', '').split(']')[0])
                else:
                    jpg_list.append(self.image_site + chapter_path + p.replace('"', ''))
        return jpg_list, episode

    def works(self, url):
        jpg_list, episode_title = self.get_jpg_list(url)
        jpg_list = [{'url': jpg, 'index': index} for index, jpg in enumerate(jpg_list, 1)]
        task = Task(self.name, self.title, episode_title, jpg_list, self.headers)
        return task
