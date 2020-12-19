#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : chobits
# @File    : website.py
import asyncio

import aiohttp

from utlis.config import check_test, read_test, write_score, read_score, get_proxy, get_site_name
from utlis.network import get_aiohttp_connector, work_speed


async def speed(url, proxy):
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


# 测试代理并发性
def test_proxy_concurrency(proxy):
    loop = asyncio.get_event_loop()
    tasks = []
    for n in range(0, 10):
        tasks.append(asyncio.ensure_future(speed('https://api.ipify.org/', proxy)))
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        if task.result() is False:
            return False
    return True


# 获取test.ini的测试结果
def get_test():
    if check_test() is False:
        proxies = get_proxy()
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
        write_score(result)
        return result
    else:
        return read_score()
