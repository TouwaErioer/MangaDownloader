#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/5 23:59
# @Author  : DHY
# @File    : config_parser.py
import configparser
import os

from common import red_text


class config:
    def __init__(self):
        try:
            config_parser = configparser.RawConfigParser()
            config_parser.read('config.ini', encoding='utf-8')
            self.folder = dict(config_parser.items('folder'))
            self.download = dict(config_parser.items('download'))
            self.manhuadb = dict(config_parser.items('manhuadb'))
            self.manhuadui = dict(config_parser.items('manhuadui'))
            self.wuqimh = dict(config_parser.items('wuqimh'))
            self.bilibili = dict(config_parser.items('bilibili'))
            self.wuqimh['section'] = 'wuqimh'
            self.manhuadui['section'] = 'manhuadui'
            self.manhuadb['section'] = 'manhuadb'
            self.download['section'] = 'download'
            self.folder['section'] = 'folder'
            self.bilibili['section'] = 'bilibili'
            self.check_dicts([self.folder, self.download, self.manhuadb, self.manhuadui, self.wuqimh, self.bilibili])
        except Exception as e:
            print(red_text % 'config.ini参数错误，%s' % e)

    @staticmethod
    def check_dicts(sections: list):
        for section in sections:
            section_name = section['section']

            # key验证
            if section_name == 'folder':
                if 'path' in section:
                    pass
                else:
                    raise ValueError('%s参数错误' % section_name)
                if os.path.exists(section['path']) is False:
                    # path不存在，创建文件夹
                    os.mkdir(section['path'])
            elif section_name == 'download':
                if 'semaphore' in section and 'repeat' in section and 'tor' in section and 'remote' in section:
                    pass
                else:
                    raise ValueError('%s参数错误' % section_name)
            elif section_name == 'manhuadb' or section_name == 'manhuadui' or section_name == 'wuqimh' \
                    or section_name == 'bilibili':
                if 'search' in section and 'site' in section and 'host' in section and 'name' in section \
                        and 'color' in section:
                    pass
                else:
                    raise ValueError('%s参数错误' % section_name)

                if section_name == 'manhuadb':
                    if 'image-host' in section and 'search-url' in section:
                        pass
                    else:
                        raise ValueError('%s参数错误' % section_name)
                elif section_name == 'manhuadui':
                    if 'key' in section and 'iv' in section and 'search-url' in section and 'image-site' in section:
                        pass
                    else:
                        raise ValueError('%s参数错误' % section_name)
                elif section_name == 'wuqimh':
                    if 'search-url' in section and 'image-site' in section:
                        pass
                    else:
                        raise ValueError('%s参数错误' % section_name)
                elif section_name == 'bilibili':
                    if 'cookie' in section and 'search-api' in section and 'comic-detail-api' in section \
                            and 'index-api' in section and 'image-token-api' in section:
                        pass
                    else:
                        raise ValueError('%s参数错误' % section_name)

            # value验证
            for item in section.items():
                if item[1] or item[0] == 'cookie':
                    pass
                else:
                    raise ValueError('%s-%s参数不能为空' % (section_name, str(item[0])))

    def select_site(self):
        return [site['name'] for site in [self.manhuadb, self.manhuadui, self.wuqimh, self.bilibili] if
                int(site['search'])]


if __name__ == '__main__':
    config()
