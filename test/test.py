#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : website.py
import asyncio

import aiohttp

from utlis.network import get_aiohttp_connector


async def work_speed(url, proxy):
    # v2ray 开启Mux多路复用
    # https://www.v2ray.com/chapter_02/mux.html
    try:
        connector = get_aiohttp_connector(proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=10) as response:
                await response.read()
                return True
    except Exception:
        return False


def test_proxy_concurrency(proxy):
    loop = asyncio.get_event_loop()
    tasks = []
    for n in range(0, 10):
        tasks.append(asyncio.ensure_future(work_speed('https://api.ipify.org/', proxy)))
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        if task.result() is False:
            return False
    return True


def enter_keywords():
    while True:
        keywords = input('请输入关键词> ') or '电锯人'
        if keywords.find(':') != -1:
            array = keywords.split(':')
            keywords = array[0]
            author = array[1]
            if len(array) == 3:
                site = array[2]
                return keywords, author, site
            else:
                return keywords, author, None
        elif keywords == 'help' or keywords == 'h':
            pass
        else:
            return keywords


if __name__ == '__main__':
    print(enter_keywords())
