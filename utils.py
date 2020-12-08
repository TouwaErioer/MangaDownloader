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
    except Exception:
        # 连接异常，失败任务
        return task


# 图片异步下载
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
        # 如果没找到文件夹，递归创建文件夹
        if not os.path.exists('%s%s/%s/%s' % (folder, source, title, episode)):
            os.makedirs('%s%s/%s/%s' % (folder, source, title, episode))

        image_path = '%s%s/%s/%s/%s' % (folder, source, title, episode, str(jpg_url['page']) + '.jpg')

        if not os.path.exists(image_path):
            task = {'url': jpg_url['url'], 'path': image_path, 'headers': headers}
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
    failure_list = [task.result() for task in all_task if task.result() is dict]

    # 如果第一个任务不存在，判断这话不存在
    not_exist_result = all_task[0].result()

    # 资源不存在列表
    not_exist_task = str(not_exist_result) if not_exist_result is not None else None

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


def repeat(failures, count):
    tasks = []
    if len(failures) != 0 and count != 0:
        print('\n第%d次重试' % (2 - count + 1))
        for failure in failures:
            path = str(failure[0]['path']).replace(str(read_config('folder', 'path')), '').split('/')
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
                failures = download(task)
        if failures is not None:
            repeat(failures, count - 1)
    else:
        print('下载完成')
        if len(failures) != 0:
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


def make_zip(source_dir, output_filename):
    file = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dir_name, filenames in os.walk(source_dir):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)  # 相对路径
            file.write(path_file, arc_name)
    file.close()
