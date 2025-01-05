#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Sam on 2025/1/4
# Function:

import argparse
import logging
import sys
import uuid
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ABSTRACT_MAX_LENGTH = 300    # abstract max length

# user_agents = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
#     'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
#     'Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36',
#     'Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 '
#     '(KHTML, like Gecko)  QtWeb Internet Browser/3.7 http://www.QtWeb.net',
#     'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
#     'Chrome/41.0.2228.0 Safari/537.36',
#     'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, '
#     'like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2',
#     'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.4pre) '
#     'Gecko/20070404 K-Ninja/2.1.3',
#     'Mozilla/5.0 (Future Star Technologies Corp.; Star-Blade OS; x86_64; U; '
#     'en-US) iNet Browser 4.7',
#     'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
#     'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) '
#     'Gecko/20080414 Firefox/2.0.0.13 Pogo/2.0.0.13.6866'
# ]

# 请求头信息
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Content-Type": "text/html; charset=utf-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://cn.bing.com/",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


session = requests.Session()
session.headers = HEADERS


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 常量定义
BING_SEARCH_URL = "https://www.bing.com/search?"
BING_HOST_URL = "https://www.bing.com"


def search(keyword, num_results=10, debug=0):
    """
    通过playwright进行多页面检索，因playwright完全模拟浏览器，加载了更多文件，所以速度比较慢。
    :param keyword: 关键字
    :param num_results: 指定返回的结果个数，支持多页检索，返回数量超过10个结果
    :param debug: 是否启用调试模式
    :return: 结果列表
    """
    if not keyword:
        return []

    if num_results <= 0:
        return []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        list_result = []

        while len(list_result) < num_results:
            try:
                # 构建搜索 URL
                params = {
                    "q": keyword,
                    "FPIG": str(uuid.uuid4()).replace('-', ''),
                    "first": len(list_result),
                    "FORM": "PORE"
                }
                next_url = BING_SEARCH_URL + urlencode(params)
                page.goto(url=next_url)

                # 截图保存到唯一文件名
                # screenshot_path = f'example_{uuid.uuid4()}.png'
                # page.screenshot(path=screenshot_path)

                res_text = page.content()
                root = BeautifulSoup(res_text, "lxml")

                ol = root.find(id="b_content").find(
                    "main").find(id="b_results")
                if not ol:
                    logger.warning("No search results found.")
                    break

                for li in ol.contents:
                    classes = li.get("class", [])
                    if "b_pag" in classes:
                        try:
                            page.locator(
                                "#b_results > li.b_pag > nav > ul > li > a.sb_pagN").click()
                        except Exception as e:
                            logger.error(
                                f"Failed to click next page button: {e}")
                            break

                    if "b_algo" not in classes:
                        continue

                    news_title = li.find("h2").find("a").get_text(strip=True)
                    news_url = li.find("div", class_="b_tpcn").find(
                        "a").get("href", "")
                    news_abstract = li.find("div", class_="b_caption").get_text(
                        strip=True)[:ABSTRACT_MAX_LENGTH]
                    list_result.append({
                        "rank": len(list_result) + 1,
                        "title": news_title,
                        "url": news_url,
                        "abstract": news_abstract
                    })

            except Exception as e:
                if debug:
                    logger.error(f"Exception during parsing page HTML: {e}")
                break

        browser.close()
        return list_result[:num_results]


def run():
    """
    主程序入口，支持命令得带参执行或者手动输入关键字
    :return:
    """

    parser = argparse.ArgumentParser(
        description='Bing search engine.')

    # positional argument
    parser.add_argument('keyword', type=str)
    parser.add_argument('-n', '--num_results', type=int,
                        default=10)      # option that takes a value
    parser.add_argument('-d', '--debug',
                        action='store_true')  # on/off flag

    args = parser.parse_args()
  
    results = search(args.keyword, num_results=args.num_results, debug=args.debug)
    
    if isinstance(results, list):
        print("search results：(total[{}]items.)".format(len(results)))
        for res in results:
            print("{}. {}\n   {}\n   {}".format(
                res['rank'], res["title"], res["abstract"], res["url"]))
    else:
        print("start search: [{}] failed.".format(args.keyword))


if __name__ == '__main__':
    run()
