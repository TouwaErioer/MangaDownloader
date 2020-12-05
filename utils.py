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
import configparser


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
        print('请求错误，%s', url)


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


def image_download(task: dict, semaphore=5):
    # 参数检查
    if 'title' in task is False and 'episode' in task is False and 'jpg_url_list' in task is False and 'source' in task:
        assert ValueError

    title = task['title']
    episode = task['episode']
    jpg_url_list = task['jpg_url_list']
    source = task['source']
    headers = task['headers']
    folder = read_config('folder', 'path')
    loop = asyncio.get_event_loop()
    all_task = []
    semaphore = asyncio.Semaphore(semaphore)
    for jpg_url in jpg_url_list:
        if not os.path.exists('%s%s/%s/%s' % (folder, source, title, episode)):
            # 递归创建文件夹
            os.makedirs('%s%s/%s/%s' % (folder, source, title, episode))
        path = '%s%s/%s/%s/%s' % (folder, source, title, episode, str(jpg_url['page']) + '.jpg')

        if not os.path.exists(path):
            all_task.append(
                asyncio.ensure_future(work({'url': jpg_url['url'], 'path': path, 'headers': headers}, semaphore)))
    if len(all_task) > 0:
        with tqdm(total=len(all_task), desc='%s' % episode) as bar:
            for t in all_task:
                t.add_done_callback(lambda _: bar.update(1))
            loop.run_until_complete(asyncio.wait(all_task))
    failure_list = [task.result() for task in all_task if task.result() is not None]

    if len(failure_list) != 0:
        return failure_list


def aes_decrypt(key, iv, content):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    content = base64.b64decode(content)
    text = cipher.decrypt(content).decode('utf-8')
    return text.strip()


def repeat(failures, count):
    tasks = []
    if len(failures) != 0 and count != 0:
        print('\n第%d次重试' % (2 - count + 1))
        for failure in failures:
            path = str(failure[0]['path']).replace(str(read_config('folder', 'path')) + '/', '').split('/')
            res = {
                'title': path[1],
                'episode': path[2],
                'jpg_url_list': [],
                'source': path[0],
                'headers': failure[0]['headers']
            }
            for failure_task in failure:
                res['jpg_url_list'].append(
                    {'url': failure_task['url'], 'page': str(failure_task['path']).split('/')[-1].split('.')[0]})
                tasks.append(res)
            for task in tasks:
                failures = image_download(task)
        if failures is not None:
            repeat(failures, count - 1)
    else:
        for failure in failures:
            print('%s下载失败，%s' % (str(failure['path']).split('/')[1], failure['url']))


def read_config(section, item):
    try:
        config = configparser.RawConfigParser()
        config.read('config.ini', encoding='utf-8')
        if item is None:
            sections = config.sections()
            index = sections.index(section)
            return config.items(sections[index])
        return str(config.get(section, item))
    except Exception as e:
        print(e)


def write_config(section, item, value):
    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        config.set(section, item, value)
        config.write(open('config.ini', 'w'))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    search_switch = read_config('search', None)
    search = [option[0] for option in search_switch if bool(int(option[1]))]
    print(search)