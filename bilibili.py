#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/4 14:07
# @Author  : DHY
# @File    : bilibili.py
import asyncio
import time
import requests
from fake_useragent import UserAgent
import io
import json
import zipfile
from MangaParser import MangaParser
from common import enter_cookie
from utils import work_speed, speed


class BiliBili(MangaParser):

    def __init__(self, Config):
        self.tor = bool(int(Config.download['tor']))
        self.config = Config.bilibili
        self.color = '\33[1;35m%s\033[0m'
        self.name = self.config['name']
        self.SEARCH_API = self.config['search-api']
        self.ComicDetail_API = self.config['comic-detail-api']
        self.Index_API = self.config['index-api']
        self.ImageToken = self.config['image-token-api']
        self.host = self.config['host']
        self.test = Config.test[self.name]
        self.cookie = enter_cookie(self.config)
        self.headers = {
            'origin': self.host,
            'User-Agent': UserAgent().random
        }

    def search(self, keywords):
        self.headers['referer'] = 'https://manga.bilibili.com/search?from=manga_detail&keyword='
        response = requests.post(self.SEARCH_API, data={'key_word': keywords, 'page_num': 1, 'page_size': 20},
                                 headers=self.headers)
        result = response.json()['data']['list']
        result_list = [{
            'title': str(res['title']).replace('<em class=\"keyword\">', '').replace('</em>', ''),
            'url': str(res['id']),
            'author': res['author_name'][0].replace('<em class=\"keyword\">', '').replace('</em>', ''),
            'name': self.name,
            'color': self.color,
            'object': self,
            'ban': False,
            'branches': 1
        } for res in result]
        result_list = self.get_detail(result_list)
        return result_list

    # 获取第一话图片的速度
    def get_search_data(self, results):
        episodes = self.get_episodes(self.get_soup(results[0]['url']), None, 1)
        result = self.works(self.get_episodes_url(episodes[0]), None)
        jpg_list = result['jpg_url_list']
        start = time.time()
        loop = asyncio.get_event_loop()
        results = [asyncio.ensure_future(work_speed({'url': jpg['url'], 'headers': self.headers})) for jpg in jpg_list]
        loop.run_until_complete(asyncio.wait(results))
        return float(time.time() - start), len(episodes)

    # 获取data
    def get_soup(self, comic_id):
        self.headers['referer'] = 'https://manga.bilibili.com/detail/mc%d?from=manga_search' % int(comic_id)
        response = requests.post(self.ComicDetail_API, data={'comic_id': comic_id}, headers=self.headers)
        result = response.json()
        return result['data'], response.elapsed.total_seconds()

    @staticmethod
    def get_title(data):
        return data['title']

    def get_branch(self, soup):
        return {'branch_id': 1}

    def works(self, episodes_url):
        jpg_list, ep_title = self.get_jpg_list(episodes_url)
        if jpg_list is not None and ep_title is not None:
            task = {
                'title': self.title,
                'episode': ep_title,
                'jpg_url_list': [{'url': res, 'page': index} for index, res in enumerate(jpg_list, 1)],
                'source': self.name,
                'headers': self.headers
            }
            return task

    def get_episodes(self, data, branch_id):
        ep_list = reversed(data['ep_list'])
        ep_list = [{'title': str(ep['short_title']) + '.' + ep['title'], 'id': ep['id']} for ep in ep_list]
        return ep_list

    def get_jpg_list(self, ep):
        comic_id = self.url
        ep_id = ep['id']
        ep_title = ep['title']
        self.headers['cookie'] = self.cookie
        self.headers['referer'] = 'https://manga.bilibili.com/mc%s/%s?from=manga_detail' % (str(comic_id), str(ep_id))
        result = requests.post(self.Index_API, data={'ep_id': ep_id}, headers=self.headers).json()
        if int(result['code']) == 0:
            response = requests.get('https://i0.hdslb.com' + result['data'], headers=self.headers)
            index_data = list(response.content)[9:]
            hash_key = self.generate_hash_key(comic_id, ep_id)
            index_data = self.un_hash_content(hash_key, index_data)

            file = io.BytesIO(index_data)
            obj = zipfile.ZipFile(file)
            data = json.loads(obj.read("index.dat"))

            res = requests.post(self.ImageToken, data={"urls": json.dumps(data["pics"])}, headers=self.headers)
            jpg_list = ["{}?token={}".format(i["url"], i["token"]) for i in res.json()["data"]]

            return jpg_list, ep_title
        else:
            print('%s https://manga.bilibili.com/mc%d/%d307985' % (result['msg'], comic_id, ep_id))
            return None

    @staticmethod
    def generate_hash_key(season_id, episode_id):
        n = [None for i in range(8)]
        e = int(season_id)
        t = int(episode_id)
        n[0] = t
        n[1] = t >> 8
        n[2] = t >> 16
        n[3] = t >> 24
        n[4] = e
        n[5] = e >> 8
        n[6] = e >> 16
        n[7] = e >> 24
        for idx in range(8):
            n[idx] = n[idx] % 256
        return n

    @staticmethod
    def un_hash_content(hash_key, index_data):
        for idx in range(len(index_data)):
            index_data[idx] ^= hash_key[idx % 8]
        return bytes(index_data)
