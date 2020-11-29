#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 11:20
# @Author  : DHY
# @File    : manhuadb.py
import re
import requests
from bs4 import BeautifulSoup
import socket
import socks
from utils import image_download
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)

headers = {
    'Referer': 'www.manhuadb.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/66.0.3359.139 Safari/537.36',
    'Host': 'www.manhuadb.com',
}


def get_html(url):
    try:
        response = requests.request('get', url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response
    except Exception as e:
        print(e)
        return None


def get_image_url(page: str, index: int, url: str) -> str:
    url = url[0:-5] + '_p' + str(page) + '.html'
    page = requests.request('get', url, headers=headers).content
    soup = BeautifulSoup(page, 'lxml')
    content = soup.select('.img-fluid')
    if len(content) > 0:
        return content[0].get('src')
    else:
        print('第%d话-%dp-解析失败 %s' % (index, int(url.split('/')[-1].split('_')[-1].split('.')[0].replace('p', '')), url))
        return None


def main():
    url = input('请输入你要批量下载漫画的网址：')[:-1] or 'https://www.manhuadb.com/manhua/1488'

    socks.set_default_proxy(socks.SOCKS5, "localhost", 1090)
    socket.socket = socks.socksocket

    html = get_html(url)
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

    # 全部的话数
    url_list = []
    page_links = soup.select('.fixed-a-es')

    for links in page_links:
        url = links.get('href')
        if url.find(tab.get(list(tab.keys())[value])) != -1:
            url_list.append(url)

    # 每话
    for index, link in enumerate(url_list[:3], 1):
        url = 'http://www.manhuadb.com' + link
        html = get_html(url)
        html = html.text
        episode = re.findall('<h2 class="h4 text-center">(.*?)</h2>', html)[0]
        pages = int(re.findall(r'共 (\d*) 页', html)[0])

        task = {
            'title': title,
            'episode': episode,
            'jpg_url_list': [],
            'pages': pages
        }

        # 第一话 解析图片地址
        jpg_url = re.findall(r'<img class="img-fluid show-pic" src="(.*?)" />', get_html(url).text)[0]
        task['jpg_url_list'].append({'url': jpg_url, 'page': 1})

        # 其余话 解析图片地址 线程池
        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(get_image_url, page, index, url) for page in range(2, pages + 1)]
        wait(all_task, return_when=ALL_COMPLETED)

        for executor in all_task:
            url = executor.result()
            if url is not None:
                task['jpg_url_list'].append({'url': url, 'page': url.split('/')[6].split('_')[0]})

        image_download(task)


if __name__ == '__main__':
    main()
