#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/3 12:35
# @Author  : DHY
# @File    : MangaParser.py
from abc import ABCMeta, abstractmethod


class MangaParser(metaclass=ABCMeta):

    @abstractmethod
    def search(self, keywords):
        pass

    @abstractmethod
    def get_branch(self, soup):
        pass

    @abstractmethod
    def get_episodes(self, soup, branch, value):
        pass

    @abstractmethod
    def works(self, url, title):
        pass

    @abstractmethod
    def get_jpg_list(self, code):
        pass

    @abstractmethod
    def run(self, url):
        pass
