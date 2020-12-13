#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 10:55
# @Author  : DHY
# @File    : network.py
import asyncio
import time

import aiohttp
import requests
from fake_useragent import UserAgent
from retrying import retry


# 封装get请求
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_html(url, headers, tor=False):
    try:
        print(url)
        proxies = None
        if tor:
            proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'}
        response = requests.get(url, headers=headers, timeout=15, proxies=proxies)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response
    except Exception as e:
        print(e, url, headers)


# 异步下载图片
@retry(stop_max_attempt_number=5, wait_fixed=2000)  # 报错重试5次，每隔2秒
async def download_image(task: dict, semaphore, tor=False):
    try:
        async with semaphore:
            proxies = None
            if tor:
                proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'}
            # connector = None
            # request_class = None
            # elif socks5:
            #     connector = ProxyConnector()
            #     proxies = 'socks5://127.0.0.1:1090'
            #     request_class = ProxyClientRequest
            headers = task['headers']
            headers['User-Agent'] = UserAgent().random
            async with aiohttp.ClientSession() as session:
                session.proxies = proxies
                response = await session.get(task['url'], headers=headers, timeout=5, proxy=proxies)
                if response.status != 404:
                    content = await response.read()
                    with open(task['path'], 'wb') as f:
                        f.write(content)
                else:
                    # 资源不存在
                    episode = str(task['path']).split('/')[-2]
                    print(task['url'])
                    return '%s' % episode
    except Exception:
        # 连接异常，失败任务
        return task


# 获取detail
@retry(stop_max_attempt_number=5, wait_fixed=1000)
async def get_detail(task, tor=False):
    async with asyncio.Semaphore(500):
        proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'} if tor else None
        url = task['url']
        headers = task['headers']
        method = task['method'] if 'method' in task else None
        api = task['api'] if 'api' in task else None
        async with aiohttp.ClientSession() as session:
            session.proxies = proxies
            if method == 'post':
                data = {'comic_id': url}
                start = time.time()
                response = await session.post(api, headers=headers, data=data, timeout=15)
                assert response.status == 200
                content = await response.json()
                response_time = '%.2f' % float(time.time() - start)
                return content['data'], url, response_time
            elif method is None:
                start = time.time()
                response = await session.get(url, headers=headers, timeout=15)
                assert response.status == 200
                content = await response.read()
                response_time = '%.2f' % float(time.time() - start)
                return content, url, response_time


# 测速
async def work_speed(task, tor=False):
    async with asyncio.Semaphore(500):
        proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'} if tor else None
        async with aiohttp.ClientSession() as session:
            session.proxies = proxies
            response = await session.get(task['url'], headers=task['headers'], timeout=5)
            await response.read()


def speed(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 404:
            return '%.2f' % response.elapsed.total_seconds()
    except Exception:
        pass
