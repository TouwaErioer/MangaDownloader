#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 10:05
# @Author  : DHY
# @File    : manhuadui.py
from parser import MangaParser
from utils import get_html, aes_decrypt
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class ManhuaDui(MangaParser):

    def __init__(self, config):
        self.tor = bool(int(config.download['tor']))
        self.config = config.manhuadui
        self.site = self.config['site']
        self.name = self.config['name']
        self.color = '\33[1;34m%s\033[0m'
        self.image_site = self.config['image-site']
        self.search_url = self.config['search-url']
        self.headers = {
            'User-Agent': UserAgent().random
        }

    # 搜索
    def search(self, keywords: str):
        try:
            url = self.search_url % keywords
            search_response = get_html(url, headers=self.headers, tor=self.tor)
            search_soup = BeautifulSoup(search_response.content, 'lxml')
            results = search_soup.select('.list-comic')
            result_list = []
            for result in results:
                author = result.select('.auth')[0].get_text()
                a = result.select('a')[1]
                result_list.append({
                    'title': a.get('title'),
                    'url': a.get('href'),
                    'author': author,
                    'name': self.name,
                    'color': self.color,
                    'object': self
                })
            return result_list
        except Exception as e:
            print('请求错误，%s，%s' % (url, e))

    def get_soup(self, url):
        html = get_html(url, self.headers)
        return BeautifulSoup(html.content, 'lxml')

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
            raise Exception('已下架')

    def get_episodes(self, soup, branch, value):
        data_key = branch.get(list(branch.keys())[value])
        select_page = soup.select('#chapter-list-' + data_key + ' a')
        pages = []
        for page in select_page:
            pages.append(self.site + page.get('href'))
        return pages

    def get_jpg_list(self, code, chapter_path):
        key = self.config['key'].encode('utf-8')
        iv = self.config['iv'].encode('utf-8')
        page_list = aes_decrypt(key, iv, code)[1:-1].split(',')
        jpg_list = []
        for index, p in enumerate(page_list, 1):
            if p.find('ManHuaKu') != -1:
                if p.find(']') != -1:
                    jpg_list.append({'url': p.replace('\\', '').replace('"', '').split(']')[0], 'page': index})
                else:
                    jpg_list.append({'url': p.replace('\\', '').replace('"', ''), 'page': index})
            else:
                if p.find(']') != -1:
                    jpg_list.append({
                        'url': self.image_site + chapter_path + p.replace('"', '').split(']')[0],
                        'page': index
                    })
                else:
                    jpg_list.append({
                        'url': self.image_site + chapter_path + p.replace('"', ''),
                        'page': index
                    })
        return jpg_list

    def works(self, url, title):
        response = get_html(url, self.headers)
        soup = BeautifulSoup(response.content, 'lxml')
        episode = soup.select('.head_title h2')[0].get_text()
        code = re.findall("var chapterImages =\\s*\"(.*?)\"", response.text)[0]
        chapter_path = re.findall("var chapterPath = \"(.*?)\"", response.text)[0]
        jpg_list = self.get_jpg_list(code, chapter_path)
        task = {'title': title, 'episode': episode, 'jpg_url_list': jpg_list, 'source': self.name,
                'headers': self.headers}
        return task
