#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : DHY
# @File    : manhuadb.py
import re
import requests
from bs4 import BeautifulSoup
import base64
import json

from utils import image_download, get_html
# from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

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

failure_task_list = []


def get_image_url(page: str, index: int, url: str) -> str:
    url = url[0:-5] + '_p' + str(page) + '.html'
    page = requests.request('get', url, headers=headers).content
    soup = BeautifulSoup(page, 'lxml')
    content = soup.select('.img-fluid')
    if len(content) > 0:
        return content[0].get('src')
    else:
        failure_task_list.append({'index': index, 'url': url})
        return None


def main():
    url = input('请输入你要批量下载漫画的网址：')[:-1] or 'https://www.manhuadb.com/manhua/1488'

    html = get_html(url, headers)
    page = html.content
    soup = BeautifulSoup(page, 'lxml')
    title = soup.select('.comic-title')[0].get_text()

    # 所有分支
    tabs = soup.select('#myTab .nav-link')
    tab = {}

    for item in tabs:
        # {'连载' -> 'content-id'}
        tab[item.get_text()] = item.get('aria-controls')

    # 分支大于1，选择分支
    if len(tab) > 1:
        placeholder = '查询到多个分支\n'
        for index, value in enumerate(list(tab.keys()), 1):
            placeholder += str(index) + '、' + value + '\n'
        placeholder += '请输入序号，默认1：'
        value = int(input(placeholder) or 1) - 1
    else:
        value = 0

    # 输入分支检查
    if value > len(list(tab.keys())) or value < 0:
        raise IndexError('超出分支范围')

    # 全部的话数
    url_list = []
    sort_div = soup.select('.sort_div')
    for div in sort_div:
        url = div.select('a')[0].get('href')
        if url.find(tab.get(list(tab.keys())[value])) != -1:
            url_list.append(url)

    index = int(input('请输入截止范围（共%d话，默认下载全部）：' % len(url_list)) or len(url_list))

    # 输入章节检查
    if index > len(url_list) or index < 0:
        raise IndexError('超出章节范围')

    # 每话
    for index, link in enumerate(url_list[:index], 1):

        url = 'http://www.manhuadb.com' + link
        html = get_html(url, headers)
        html = html.text

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
            'pages': pages,
            'headers': image_headers
        }

        for res in result:
            task['jpg_url_list'].append({'url': prefix + res['img'], 'page': res['p']})

        # 设置Host
        if len(task['jpg_url_list']) != 0:
            task['headers']['Host'] = task['jpg_url_list'][0]['url'].split('/')[2]

        image_download(task)

    for failure_task in failure_task_list:
        url = failure_task['url']
        p = int(url.split('/')[-1].split('_')[-1].split('.')[0].replace('p', ''))
        print('第%d话-%dp-解析失败 %s' % (failure_task['index'], p, url))


if __name__ == '__main__':
    main()
