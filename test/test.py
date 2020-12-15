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


if __name__ == '__main__':
    print(test_proxy({'socks5_host': '127.0.0.1', 'socks5_port': 1090}))
