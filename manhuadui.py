#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 10:05
# @Author  : DHY
# @File    : manhuadui.py

from MangaParser import MangaParser
from utils import get_html, image_download, aes_decrypt
import re
from bs4 import BeautifulSoup
from common import enter_range, enter_branch
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from fake_useragent import UserAgent


class manhuadui(MangaParser):

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
                result_list.append(
                    {'title': self.color % a.get('title'), 'url': a.get('href'), 'author': self.color % author,
                     'source': self.color % self.name, 'path': '%s/%s' % (self.name, a.get('title'))})
            return result_list
        except Exception as e:
            print('请求错误，%s，%s' % (url, e))

    # 获取分支
    def get_branch(self, soup):
        tabs = soup.select('.zj_list .c_3')
        if len(tabs) != 0:
            data_keys = soup.select('.zj_list_head_px')
            branch = {}
            for index, item in enumerate(tabs):
                branch[item.get_text()] = data_keys[index].get('data-key')
            return branch
        else:
            return None

    # 获取全部话
    def get_episodes(self, soup, branch, value):
        data_key = branch.get(list(branch.keys())[value])
        select_page = soup.select('#chapter-list-' + data_key + ' a')
        pages = []
        for page in select_page:
            pages.append(self.site + page.get('href'))
        return pages

    # 获取图片链接列表
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
                    jpg_list.append(
                        {'url': self.image_site + chapter_path +
                                p.replace('"', '').split(']')[0],
                         'page': index})
                else:
                    jpg_list.append(
                        {'url': self.image_site + chapter_path + p.replace('"', ''),
                         'page': index})
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

    def run(self, url):
        html = get_html(url, self.headers)
        soup = BeautifulSoup(html.content, 'lxml')
        title = soup.select('h1')[0].get_text()

        # 分支
        branch = self.get_branch(soup)
        if branch is None:
            raise Exception('已下架')

        # 选择分支
        value = enter_branch(branch)

        # 全部话
        episodes = self.get_episodes(soup, branch, value)

        # 选择话
        enter = enter_range(episodes)

        # 解析图片链接，线程池
        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(self.works, url, title) for url in episodes[enter[0]:enter[1]]]
        wait(all_task, return_when=ALL_COMPLETED)

        failure_list = []
        not_exist_task = []
        for work in all_task:
            result = image_download(work.result(), semaphore=int(self.config['semaphore']), tor=self.tor)
            if type(result) is tuple:
                failure_list.append(result[0])
            elif type(result) is str:
                not_exist_task.append(result)
        return failure_list, not_exist_task
