#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/1 12:54
# @Author  : DHY
# @File    : common.py


yellow_text = '\33[1;33m%s\033[0m'
blue_text = '\33[1;34m%s\033[0m'
green_text = '\33[1;32m%s\033[0m'
pink_text = '\33[1;35m%s\033[0m'


def enter_range(pages: list):
    # print('格式：【x:y，从x开始y结束；y，从1开始y结束】')
    while True:
        start = 0
        try:
            end = input('请输入下载范围（%d话）> ' % len(pages)) or len(pages)
            if str(end).find(':') != -1:
                input_arr = end.split(':')
                start = int(input_arr[0])
                end = int(input_arr[1])
                if end > len(pages) or end <= 0 and start > len(pages) or end < 0:
                    raise IndexError
            else:
                end = int(end)
                if end > len(pages) or end <= 0:
                    raise IndexError
            return start, end
        except TypeError:
            print('\033[0;31;40m输入不是数字，重新输入\033[0m')
        except ValueError:
            print('\033[0;31;40m输入不是数字，重新输入\033[0m')
        except IndexError:
            print('\033[0;31;40m超出章节范围\033[0m')


def enter_branch(tab: dict):
    while True:
        try:
            # 分支大于1，选择分支
            if len(tab) > 1:
                placeholder = '查询到多个分支\n'
                for index, value in enumerate(list(tab.keys()), 1):
                    placeholder += str(index) + '、' + value + '\n'
                placeholder += '请输入序号> '
                value = int(input(placeholder) or 1) - 1
            else:
                value = 0

            # 输入分支检查
            if value > len(list(tab.keys())) or value < 0:
                raise IndexError
            return value
        except ValueError:

            print('\033[0;31;40m输入不为数字\033[0m')
        except IndexError:
            print('\033[0;31;40m超出分支范围\033[0m')


if __name__ == '__main__':
    print(enter_range([1, 1]))
