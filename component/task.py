#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/13 0:25
# @Author  : chobits
# @File    : task.py


class Task:
    def __init__(self, name, title, episode_title, jpg_list, headers):
        self.name = name
        self.title = title
        self.episode_title = episode_title
        self.jpg_list = jpg_list
        self.headers = headers
