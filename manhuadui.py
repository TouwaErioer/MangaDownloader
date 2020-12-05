#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 10:05
# @Author  : DHY
# @File    : manhuadui.py
from utils import get_html, image_download, aes_decrypt, read_config
import re
from bs4 import BeautifulSoup
from common import enter_range, enter_branch
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/66.0.3359.139 Safari/537.36',
}
host = 'https://www.manhuadai.com/'


# 搜索
def search(keywords: str):
    search_response = get_html('https://www.manhuadai.com/search/?keywords=' + keywords, headers=headers)
    search_soup = BeautifulSoup(search_response.content, 'lxml')
    results = search_soup.select('.list-comic')
    result_list = []
    for result in results:
        author = result.select('.auth')[0].get_text()
        a = result.select('a')[1]
        result_list.append(
            {'title': a.get('title'), 'url': a.get('href'), 'author': author})
    return result_list


# 获取分支
def get_branch(soup):
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
def get_episodes(soup, branch, value):
    data_key = branch.get(list(branch.keys())[value])
    select_page = soup.select('#chapter-list-' + data_key + ' a')
    pages = []
    for page in select_page:
        pages.append(host + page.get('href'))
    return pages


# 获取图片链接列表
def get_jpg_list(code, chapter_path):
    key = read_config('decrypt', 'key').encode('utf-8')
    iv = read_config('decrypt', 'iv').encode('utf-8')
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
                    {'url': 'https://manga.mipcdn.com/i/s/img01.eshanyao.com/' + chapter_path +
                            p.replace('"', '').split(']')[0],
                     'page': index})
            else:
                jpg_list.append(
                    {'url': 'https://manga.mipcdn.com/i/s/img01.eshanyao.com/' + chapter_path + p.replace('"', ''),
                     'page': index})
    return jpg_list


def works(url, title):
    response = get_html(url, headers)
    soup = BeautifulSoup(response.content, 'lxml')
    episode = soup.select('.head_title h2')[0].get_text()
    code = re.findall("var chapterImages =\\s*\"(.*?)\"", response.text)[0]
    chapter_path = re.findall("var chapterPath = \"(.*?)\"", response.text)[0]
    jpg_list = get_jpg_list(code, chapter_path)
    task = {'title': title, 'episode': episode, 'jpg_url_list': jpg_list, 'source': '漫画堆',
            'headers': headers}
    return task


def run(url):
    html = get_html(url, headers)
    soup = BeautifulSoup(html.content, 'lxml')
    title = soup.select('h1')[0].get_text()

    # 分支
    branch = get_branch(soup)
    if branch is None:
        raise Exception('已下架')

    # 选择分支
    value = enter_branch(branch)

    # 全部话
    episodes = get_episodes(soup, branch, value)

    # 选择话
    enter = enter_range(episodes)

    # 解析图片链接，线程池
    executor = ThreadPoolExecutor(max_workers=20)
    all_task = [executor.submit(works, url, title) for url in episodes[enter[0]:enter[1]]]
    wait(all_task, return_when=ALL_COMPLETED)

    failure_list = []
    for work in all_task:
        result = image_download(work.result(), int(read_config('download', 'semaphore')))
        if result is not None:
            failure_list.append(result)

    return failure_list


if __name__ == '__main__':
    print(search('辉夜'))
