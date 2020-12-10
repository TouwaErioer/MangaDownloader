#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/11/29 16:44
# @Author  : DHY
# @File    : utils.py
import zipfile
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


# 封装get请求
@retry(stop_max_attempt_number=2, wait_fixed=1000)
def get_html(url, headers, tor=False):
    print(url)
    proxies = None
    if tor:
        proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'}
    if str(url).find('manhuadb') != -1:
        pass
    else:
        headers['User-Agent'] = UserAgent().random
    response = requests.get(url, headers=headers, timeout=5, proxies=proxies)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response


# 异步下载图片
@retry(stop_max_attempt_number=5, wait_fixed=2000)  # 报错重试5次，每隔2秒
async def work(task: dict, semaphore, tor=False):
    try:
        async with semaphore:
            proxies = None
            if tor:
                proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'}
            headers = task['headers']
            headers['User-Agent'] = UserAgent().random
            async with aiohttp.ClientSession() as session:
                session.proxies = proxies
                response = await session.get(task['url'], headers=headers, timeout=5)
                if response.status != 404:
                    content = await response.read()
                    with open(task['path'], 'wb') as f:
                        f.write(content)
                else:
                    # 资源不存在
                    episode = str(task['path']).split('/')[-2]
                    return str('\33[1;32m%s\033[0m' % ('%s 资源不存在' % episode))
    except Exception as e:
        print(e)
        # 连接异常，失败任务
        return task


def download(task: dict, semaphore=5, tor=False):
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
        url = str(jpg_url['url'])
        suffix = '.' + url.split('.')[-1]
        # 如果没找到文件夹，递归创建文件夹
        if not os.path.exists('%s%s/%s/%s' % (folder, source, title, episode)):
            os.makedirs('%s%s/%s/%s' % (folder, source, title, episode))

        image_path = '%s%s/%s/%s/%s' % (folder, source, title, episode, str(jpg_url['page']) + '.jpg')

        if not os.path.exists(image_path):
            task = {'url': url, 'path': image_path, 'headers': headers}
            all_task.append(asyncio.ensure_future(work(task, semaphore, tor=tor)))

    if len(all_task) > 0:
        # 进度条
        with tqdm(total=len(all_task), desc='%s' % episode) as bar:
            for task in all_task:
                task.add_done_callback(lambda _: bar.update(1))
            loop.run_until_complete(asyncio.wait(all_task))

    # 失败任务表示连接错误的任务
    # 资源不存在任务代表相应404的任务
    # works返回dict或str，返回dict表示失败任务,返回str代表资源不存在任务

    # 失败任务列表
    failure_list = [task.result() for task in all_task if type(task.result()) is dict]
    not_exist_task = None
    if len(all_task) != 0:
        # 如果第一个任务不存在，判断这话不存在
        not_exist_result = all_task[0].result()
        # 资源不存在列表
        not_exist_task = str(not_exist_result) if type(not_exist_result) is str else None
    if len(failure_list) != 0:
        # 有失败任务，代表没有不存在任务
        return failure_list
    if not_exist_task is not None:
        return not_exist_task


def aes_decrypt(key, iv, content):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    content = base64.b64decode(content)
    text = cipher.decrypt(content).decode('utf-8')
    return text.strip()


# 重试，直到没有失败任务
def repeat(failures, count=1):
    if failures is None or len(failures) == 0:
        print('下载完成')
    else:
        print('\n第%d次重试' % count)
        tasks = []
        for failure in failures:
            config_path = str(read_config('folder', 'path'))
            array = str(failure[0]['path']).replace(config_path, '').split('/')
            res = {
                'title': array[1],
                'episode': array[2],
                'jpg_url_list': [],
                'source': array[0],
                'headers': failure[0]['headers']
            }
            for failure_task in failure:
                url = failure_task['url']
                path = str(failure_task['path'])
                page = path.split('/')[-1].split('.')[0]
                res['jpg_url_list'].append({'url': url, 'page': page})
            tasks.append(res)

        download_results = [download(task) for task in tasks]
        results = [result for result in download_results if result is not None]
        if len(results) != 0:
            return repeat(results, count + 1)


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


def make_zip(source_dir, output_filename):
    file = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dir_name, filenames in os.walk(source_dir):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)  # 相对路径
            file.write(path_file, arc_name)
    file.close()


# 异步get请求
@retry(stop_max_attempt_number=5, wait_fixed=1000)
async def get_detail(task, tor=False):
    async with asyncio.Semaphore(500):
        proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'} if tor else None
        url = task['url']
        headers = task['headers']
        async with aiohttp.ClientSession() as session:
            session.proxies = proxies
            response = await session.get(url, headers=headers, timeout=15)
            assert response.status == 200
            content = await response.read()
            return content


async def work_speed(task, tor=False):
    try:
        async with asyncio.Semaphore(500):
            proxies = {'http': 'http://127.0.0.1:8118', 'https': 'http://127.0.0.1:8118'} if tor else None
            async with aiohttp.ClientSession() as session:
                session.proxies = proxies
                response = await session.get(task['url'], headers=task['headers'], timeout=5)
                await response.read()
    except Exception:
        pass
