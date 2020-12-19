# MangaDownload

一款高速、易扩展、多功能的漫画下载器

尊重版权，请支持正版，通过本工具下载或生成的资源**禁止传播分享！禁止利用本项目进行商业活动！**

## 支持漫画源

- 漫画db
- 漫画堆（暂时无法访问）
- 57漫画
- bilibili漫画（仅可下载已付费）
- MangaBZ

## 功能

- 支持多漫画源搜索

- 支持作者、站点筛选

- 自定义下载目录

- tor代理更换ip

- 服务器remote

- 开启展示详情

- 支持socks5代理

- 自定义指定站点下载速度

## 安装

### 源代码启动

环境：python3.8

依赖包：

```
aiohttp (3.7.3)
aiohttp-socks (0.5.5)
beautifulsoup4 (4.9.3)
bs4 (0.0.1)
crypto (1.4.1)
fake-useragent (0.1.11)
Js2Py (0.70)
lxml (4.6.2)
prettytable (2.0.0)
progress (1.5)
pycrypto (2.6.1)
requests (2.25.0)
tqdm (4.54.1)
uvloop (0.14.0)
retrying (1.3.3)
```

### 二进制打包

- Windows

  [点击下载](https://github.com/TouwaErioer/MangaDownloader/releases/download/0.1/mangadownload-win.7z)

- Linux

  [点击下载](https://github.com/TouwaErioer/MangaDownloader/releases/download/0.1/mangadownload-linux.7z)

## 使用
### 命令行

```
- start  开始
- help   显示帮助信息
- list   显示支持站点列表
- proxy  设置socks5代理
- config 显示配置信息
```

### 关键词

```
- keywords [:author] [:site]
```

### 范围

```
- start [:end]
```

### cookie

```
- cookie
```