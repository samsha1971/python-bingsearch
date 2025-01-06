#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Sam on 2025/1/6
# Function:

import argparse
import logging
import uuid
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ABSTRACT_MAX_LENGTH = 500    # abstract max length

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 常量定义
BING_SEARCH_URL = "https://www.bing.com/search?"
BING_HOST_URL = "https://www.bing.com"


class BingSearch:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch()

    def __enter__(self):
        return self

    def search(self, keyword, num_results=10, debug=0):
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

        list_result = []

        page = self.browser.new_page()

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

        return list_result[:num_results]

    def release_resource(self):
        try:
            self.browser.close()
            self.p.stop()
        except Exception as e:
            # print(f"Exception: {e}")
            pass

    def __del__(self):
        self.release_resource()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_resource()


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

    # with BingSearch() as bs:
    #     results = bs.search(
    #         args.keyword, num_results=args.num_results, debug=args.debug)

    # bs = BingSearch()
    # results = bs.search(
    #     args.keyword, num_results=args.num_results, debug=args.debug)
    # bs.release_resource()

    with BingSearch() as bs:
        results = bs.search(
            args.keyword, num_results=args.num_results, debug=args.debug)

    if isinstance(results, list):
        print("search results：(total[{}]items.)".format(len(results)))
        for res in results:
            print("{}. {}\n   {}\n   {}".format(
                res['rank'], res["title"], res["abstract"], res["url"]))
    else:
        print("start search: [{}] failed.".format(args.keyword))


if __name__ == '__main__':
    run()
