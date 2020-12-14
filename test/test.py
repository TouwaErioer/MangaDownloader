#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : website.py
import asyncio

import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector
from retrying import retry

from utlis.config import read_test


async def work_speed(url):
    # v2ray 开启Mux多路复用
    # https://www.v2ray.com/chapter_02/mux.html
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5,
        host='127.0.0.1',
        port=1090
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, timeout=10) as response:
            print(response.status)


if __name__ == '__main__':
    tests = read_test()
    # asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    tasks = []
    for test in tests:
        tasks.append(asyncio.ensure_future(work_speed(test['url'])))
    loop.run_until_complete(asyncio.wait(tasks))
