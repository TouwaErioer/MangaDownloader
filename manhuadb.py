#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : DHY
# @File    : manhuadb.py

import re
from bs4 import BeautifulSoup
import base64
import json
from utils import image_download, get_html
from common import enter_range, enter_branch
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

headers = {
    'Referer': 'www.manhuadb.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/66.0.3359.139 Safari/537.36',
    'Host': 'www.manhuadb.com',
}

image_headers = {
    'Referer': 'www.manhuadb.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/66.0.3359.139 Safari/537.36',
    'Host': 'i1.manhuadb.com',
}


# 搜索
def search(keywords: str):
    response = get_html('https://www.manhuadb.com/search?q=' + keywords, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    results = soup.select('.comicbook-index')
    result_list = []
    for result in results:
        item = result.select('a')[0]
        author = result.select('.comic-author a')[0].get('title')
        result_list.append(
            {'title': item.get('title'), 'url': 'http://manhuadb.com' + item.get('href'), 'author': author})
    return result_list


# 获取分支
def get_branch(soup):
    tabs = soup.select('#myTab .nav-link')
    tab = {}
    for item in tabs:
        tab[item.get_text()] = item.get('aria-controls')
    return tab


# 获取全部话
def get_episodes(soup, branch, value):
    url_list = []
    sort_div = soup.select('.sort_div')
    for div in sort_div:
        url = div.select('a')[0].get('href')
        if url.find(branch.get(list(branch.keys())[value])) != -1:
            url_list.append(url)
    return url_list


def works(url, title):
    html = get_html(url, headers).text
    result = json.loads(str(base64.b64decode(re.findall("img_data = '(.*?)'", html)[0]).decode('utf-8')))
    jpg_url = re.findall(r'<img class="img-fluid show-pic" src="(.*?)" />', html)[0]
    suffix = jpg_url.split('/')[-1]
    prefix = jpg_url.replace(suffix, '')
    episode = re.findall('<h2 class="h4 text-center">(.*?)</h2>', html)[0]
    pages = int(re.findall(r'共 (\d*) 页', html)[0])
    task = {
        'title': title,
        'episode': episode,
        'jpg_url_list': [],
        'source': '漫画DB',
        'headers': image_headers
    }
    for res in result:
        task['jpg_url_list'].append({'url': prefix + res['img'], 'page': res['p']})
    # 设置Host
    if len(task['jpg_url_list']) != 0:
        task['headers']['Host'] = task['jpg_url_list'][0]['url'].split('/')[2]
    return task


def run(url):
    host = 'http://www.manhuadb.com'
    # url = input('请输入你要批量下载漫画的网址：')[:-1] or 'https://www.manhuadb.com/manhua/1488'
    html = get_html(url, headers)
    soup = BeautifulSoup(html.content, 'lxml')
    title = soup.select('.comic-title')[0].get_text()

    # 分支
    branch = get_branch(soup)

    # 输入分支
    value = enter_branch(branch)

    # 全部的话数
    episodes = get_episodes(soup, branch, value)

    # 输入范围
    enter = enter_range(episodes)

    # 解析图片链接，线程池
    executor = ThreadPoolExecutor(max_workers=20)
    all_task = [executor.submit(works, host + link, title) for link in episodes[enter[0]:enter[1]]]
    wait(all_task, return_when=ALL_COMPLETED)
    failure_list = []
    for work in all_task:
        result = image_download(work.result())
        if result is not None:
            failure_list.append(result)
    return failure_list
