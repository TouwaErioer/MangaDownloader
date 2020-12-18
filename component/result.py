#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/12 22:35
# @Author  : chobits
# @File    : result.py


class Result:

    def __init__(self, title, href, author, obj, color, name, ban, branches, episodes, speed):
        self.title = title
        self.href = href
        self.author = author
        self.name = name
        self.color = color
        self.obj = obj
        self.ban = ban
        self.branches = branches
        self.episodes = episodes
        self.speed = speed

    def update(self, data: dict):
        if type(data) is not dict:
            raise Exception('传入类型不对')
        for key, value in data.items():
            if key == 'ban':
                self.ban = value
            elif key == 'branches':
                self.branches = value
            elif key == 'episodes':
                self.episodes = value
            elif key == 'speed':
                self.speed = value
            elif key == 'author' and self.author is None:
                self.author = value

    def update_speed(self, tests: dict):
        for key, value in tests.items():
            if key == self.name:
                self.speed = '%.2f' % float((float(self.speed) + float(value)) / 2)
