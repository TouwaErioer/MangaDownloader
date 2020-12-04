#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 16:44
# @Author  : DHY
# @File    : utils.py
import aiohttp
import asyncio
import os
import requests
from tqdm import tqdm
from Crypto.Cipher import AES
import base64
from fake_useragent import UserAgent

from retrying import retry


# 请求
@retry(stop_max_attempt_number=2, wait_fixed=1000)
def get_html(url, headers):
    try:
        headers['User-Agent'] = UserAgent().random
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response
    except Exception:
        pass


# 异步下载图片
@retry(stop_max_attempt_number=5, wait_fixed=2000)  # 报错重试5次，每隔2秒
async def work(task: dict, semaphore):
    try:
        async with semaphore:
            headers = task['headers']
            headers['User-Agent'] = UserAgent().random
            async with aiohttp.ClientSession() as session:
                response = await session.get(task['url'], headers=headers, timeout=10)
                content = await response.read()
                with open(task['path'], 'wb') as f:
                    f.write(content)
    except Exception:
        return task


def image_download(task: dict, semaphore=500):
    # 参数检查
    if 'title' in task is False and 'episode' in task is False and 'jpg_url_list' in task is False and 'pages' in task:
        assert ValueError

    title = task['title']
    episode = task['episode']
    jpg_url_list = task['jpg_url_list']
    pages = task['pages']
    headers = task['headers']

    loop = asyncio.get_event_loop()
    all_task = []

    semaphore = asyncio.Semaphore(semaphore)
    for jpg_url in jpg_url_list:
        if not os.path.exists(title + '/' + episode):
            # 递归创建文件夹
            os.makedirs(title + '/' + episode)
        path = '%s/%s/%s' % (title, episode, str(jpg_url['page']) + '.jpg')

        if not os.path.exists(path):
            all_task.append(
                asyncio.ensure_future(work({'url': jpg_url['url'], 'path': path, 'headers': headers}, semaphore)))
    if len(all_task) > 0:
        with tqdm(total=len(all_task), desc='%s' % episode) as bar:
            for t in all_task:
                t.add_done_callback(lambda _: bar.update(1))
            loop.run_until_complete(asyncio.wait(all_task))
    failure_list = [task.result() for task in all_task if task.result() is not None]

    return failure_list


def aes_decrypt(key, iv, content):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    content = base64.b64decode(content)
    text = cipher.decrypt(content).decode('utf-8')
    return text.strip()
