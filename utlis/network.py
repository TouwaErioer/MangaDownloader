#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 10:55
# @Author  : DHY
# @File    : network.py

import asyncio
import socket
import time

import aiohttp
import requests
import socks
from fake_useragent import UserAgent
from retrying import retry

from utlis.config import read_test, read_config
from aiohttp_socks import ProxyType, ProxyConnector


# 封装同步get请求
@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_html(url: str, headers: dict, proxy: dict):
    try:
        proxies = get_proxies(proxy)
        response = requests.get(url, headers=headers, timeout=15, proxies=proxies)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response
    except Exception as e:
        print(e, url, headers)


# 封装异步get请求
@retry(stop_max_attempt_number=3, wait_fixed=2000)
async def async_get(url: str, headers: dict, proxy: dict):
    connector = get_aiohttp_connector(proxy)
    async with aiohttp.ClientSession(connector=connector) as session:
        response = await session.get(url, headers=headers, timeout=15)
        content = await response.read()
        return content


# 异步下载图片
@retry(stop_max_attempt_number=5, wait_fixed=2000)  # 报错重试5次，每隔2秒
async def download_image(task: dict, semaphore, proxy=None):
    try:
        async with semaphore:
            # socks5代理
            connector = get_aiohttp_connector(proxy)
            headers = task['headers']
            headers['User-Agent'] = UserAgent().random
            async with aiohttp.ClientSession(connector=connector) as session:
                response = await session.get(task['url'], headers=headers, timeout=5)
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
async def work_speed(task, proxy=None):
    try:
        async with asyncio.Semaphore(500):
            connector = get_aiohttp_connector(proxy)
            async with aiohttp.ClientSession(connector=connector) as session:
                start = time.time()
                response = await session.get(task['url'], timeout=3)
                await response.read()
                response_time = '%.2f' % float(time.time() - start)
                return task['name'], response_time
    except asyncio.exceptions.TimeoutError:
        return task['name'], 3


def speed(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 404:
            return '%.2f' % response.elapsed.total_seconds()
    except Exception:
        pass


def get_test():
    proxies = read_config('proxy', None)
    result = {}
    tests = read_test()
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(work_speed(test, proxies)) for test in tests]
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        name, response_time = task.result()
        if name in result:
            result[name] = float(result[name]) + float(response_time)
        else:
            result[name] = response_time
    for key, value in result.items():
        result[key] = '%.2f' % float(value / 5)
    return result


def check_proxy(host, port):
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket

    try:
        requests.get('https://api.ipify.org/')
        return True
    except requests.exceptions.ConnectionError:
        return False


def get_aiohttp_connector(proxy: dict):
    if proxy is None:
        return None
    else:
        host = proxy['socks5_host']
        port = int(proxy['socks5_port'])
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5,
            host=host,
            port=port
        )
        return connector


def get_proxies(proxy: dict):
    if proxy is None:
        return None
    else:
        host = proxy['socks5_host']
        port = proxy['socks5_port']
        proxy = 'socks5://%s:%s' % (host, port)
        proxies = {
            'http': proxy,
            'https': proxy
        }
        return proxies
