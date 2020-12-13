#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/2 19:58
# @Author  : DHY
# @File    : website.py
from component.enter import enter_proxy, check_speed

# def get_test():
#     result = {}
#     tests = read_test()
#     loop = asyncio.get_event_loop()
#     tasks = [asyncio.ensure_future(work_speed(test)) for test in tests]
#     loop.run_until_complete(asyncio.wait(tasks))
#     for task in tasks:
#         name, response_time = task.result()
#         if name in result:
#             result[name] = float(result[name]) + float(response_time)
#         else:
#             result[name] = response_time
#     for key, value in result.items():
#         result[key] = '%.2f' % float(value / 5)
#     return result


if __name__ == '__main__':
    check_speed(1.2)
