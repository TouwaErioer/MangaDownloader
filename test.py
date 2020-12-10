#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : test.py
import os
import zipfile
from flask import send_from_directory, Flask, make_response

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
    print(os.name)
