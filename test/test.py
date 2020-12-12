#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : website.py

import os
import re
import zipfile

from fake_useragent import UserAgent
from flask import send_from_directory, Flask, make_response

from utlis.utils import get_html

app = Flask(__name__)


@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response


def make_zip(source_dir, output_filename):
    file = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dir_name, filenames in os.walk(source_dir):
        for filename in filenames:
            path_file = os.path.join(parent, filename)
            arc_name = path_file[pre_len:].strip(os.path.sep)  # 相对路径
            file.write(path_file, arc_name)
    file.close()


if __name__ == '__main__':
    url = 'http://www.mangabz.com/m47436/'
    site = 'http://www.mangabz.com/752bz/'
    headers = {
        'Host': 'www.mangabz.com',
        'Referer': 'www.mangabz.com/m47431/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36'
    }
    response = get_html(url, headers=headers)
    html = response.text
    title = re.findall('<title>(.*?)</title>', html)[0]
    episode_title = str(title).split('_')[1]
    js = re.findall("eval(.*?)\\n", html)[0]
    code = re.findall(",\\d*\\d*,'(.*?)'.split", js)[0]
    cid = re.findall("/m(.*?)/", url)[0]
    key = re.findall('[0-9a-zA-Z]{32}', code)[0]
    pages = re.findall("\\d*_\\d*", code)
    path = re.findall("http://www.mangabz.com/(.*?)bz/", site)[0]
    pages = sorted(pages)
    results = []
    for page in pages:
        image_url = 'http://image.mangabz.com/1/%s/%s/%s.jpg?cid=%s&key=%s&type=1'
        results.append(image_url % (path, cid, page, cid, key))
    print(results)
