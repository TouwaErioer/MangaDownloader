#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : test.py
import re
import requests
import io
import json
import zipfile


def unsuan(s):
    x = s[-1]
    w = "abcdefghijklmnopqrstuvwxyz"
    xi = w.find(x) + 1
    sk = s[len(s) - xi - 12:len(s) - xi - 1]
    s = s[0:len(s) - xi - 12]
    k = sk[0:len(sk) - 1]
    f = sk[(len(k) - 1):]
    for index, value in enumerate(k, 0):
        s = s.replace(k[index:index + 1], str(index))
    ss = re.split(r'[%s%s\s]\s*' % (f[0], f[1]), s)
    s = ''
    for value in ss:
        s += chr(int(value))
    return s


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


def unhashContent(hashKey, indexData):
    for idx in range(len(indexData)):
        indexData[idx] ^= hashKey[idx % 8]
    return bytes(indexData)


if __name__ == '__main__':

    print('{0:{1}^20}'.format('manhuadb',chr(12288)))