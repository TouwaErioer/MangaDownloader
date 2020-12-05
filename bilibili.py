#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/4 14:07
# @Author  : DHY
# @File    : bilibili.py
import requests
from fake_useragent import UserAgent
import io
import json
import zipfile

from MangaParser import MangaParser
from common import enter_range, pink_text, enter_cookie
from concurrent.futures import (ALL_COMPLETED, ThreadPoolExecutor, wait)
from utils import image_download


class bilibili(MangaParser):
    SEARCH_API = 'https://manga.bilibili.com/twirp/comic.v1.Comic/Search?device=pc&platform=web'
    ComicDetail_API = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device=h5&platform=h5'
    Index_API = 'https://manga.bilibili.com/twirp/comic.v1.Comic/Index?device=h5&platform=h5'
    ImageToken = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=h5&platform=h5'
    Host = 'https://manga.bilibili.com'
    headers = {
        'origin': Host,
        'User-Agent': UserAgent().random
    }
    source = 'bilibili漫画'

    def __init__(self, config):
        self.color = pink_text
        self.source = 'bilibili漫画'
        self.config = config

    def search(self, keywords):
        self.headers['referer'] = 'https://manga.bilibili.com/search?from=manga_detail&keyword='
        response = requests.post(self.SEARCH_API, data={'key_word': keywords, 'page_num': 1, 'page_size': 20},
                                 headers=self.headers)
        result = response.json()['data']['list']
        return [{
            'title': self.color % str(res['title']).replace('<em class=\"keyword\">', '').replace('</em>', ''),
            'url': str(res['id']),
            'author': self.color % res['author_name'][0].replace('<em class=\"keyword\">', '').replace('</em>', ''),
            'source': self.color % self.source
        } for res in result]

    def get_branch(self):
        pass

    def works(self):
        pass

    def get_episodes(self, comic_id):
        self.headers['referer'] = 'https://manga.bilibili.com/detail/mc%d?from=manga_search' % int(comic_id)
        response = requests.post(self.ComicDetail_API, data={'comic_id': comic_id}, headers=self.headers)
        result = response.json()
        data = result['data']
        title = data['title']
        ep_list = reversed(data['ep_list'])
        ep_list = [{'title': str(ep['short_title']) + '.' + ep['title'], 'id': ep['id']} for ep in ep_list]
        return title, ep_list

    def get_jpg_list(self, comic_id, ep, cookie, title):
        ep_id = ep['id']
        ep_title = ep['title']
        if cookie is not None:
            self.headers['cookie'] = cookie
        self.headers['referer'] = 'https://manga.bilibili.com/mc%s/%s?from=manga_detail' % (str(comic_id), str(ep_id))
        result = requests.post(self.Index_API, data={'ep_id': ep_id}, headers=self.headers).json()
        if int(result['code']) == 0:
            response = requests.get('https://i0.hdslb.com' + result['data'], headers=self.headers)
            index_data = list(response.content)[9:]
            hash_key = self.generateHashKey(comic_id, ep_id)
            index_data = self.unhashContent(hash_key, index_data)

            file = io.BytesIO(index_data)
            obj = zipfile.ZipFile(file)
            data = json.loads(obj.read("index.dat"))

            res = requests.post(self.ImageToken, data={"urls": json.dumps(data["pics"])}, headers=self.headers)
            result = ["{}?token={}".format(i["url"], i["token"]) for i in res.json()["data"]]
            task = {
                'title': title,
                'episode': ep_title,
                'jpg_url_list': [{'url': res, 'page': index} for index, res in enumerate(result, 1)],
                'source': self.source,
                'headers': self.headers
            }

            return task
        else:
            print('%s https://manga.bilibili.com/mc%d/%d307985' % (result['msg'], comic_id, ep_id))
            return None

    @staticmethod
    def generateHashKey(seasonId, episodeId):
        n = [None for i in range(8)]
        e = int(seasonId)
        t = int(episodeId)
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
    def unhashContent(hashKey, indexData):
        for idx in range(len(indexData)):
            indexData[idx] ^= hashKey[idx % 8]
        return bytes(indexData)

    def run(self, comic_id):
        cookie = enter_cookie()
        title, ep_list = self.get_episodes(comic_id)
        enter = enter_range(ep_list)
        executor = ThreadPoolExecutor(max_workers=20)
        all_task = [executor.submit(self.get_jpg_list, comic_id, ep, cookie, title) for ep in
                    ep_list[enter[0]:enter[1]]]
        wait(all_task, return_when=ALL_COMPLETED)
        result = [task.result() for task in all_task]
        failure_list = []
        for res in result:
            if res is not None:
                failures = image_download(res)
                if failures is not None:
                    failure_list.append(failures)
        return failure_list


if __name__ == '__main__':
    print(bilibili())