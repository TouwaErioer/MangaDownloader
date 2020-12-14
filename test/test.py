#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : website.py
import asyncio

import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector
from retrying import retry

from utlis.config import read_test, write_score


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
    result = {'漫画db': '1.96', '57漫画': '1.68', 'bilibili漫画': '0.10', 'MangaBZ': '1.06'}
    write_score(result)
