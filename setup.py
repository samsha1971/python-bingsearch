#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-04-29
# Function:

import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    install_requires=["requests>=2.18.4", "beautifulsoup4>=4.6.0",
                      "lxml>=4.1.0", "playwright>=1.36.0"],
    name="bingsearch",
    version="1.0.0",
    author="Sam Sha",
    maintainer='Sam Sha',
    author_email="sam_sha@163.com",
    description="bing Search unofficial API for Python with no external dependencies",
    keywords="search-api bing python",
    url="https://github.com/sam_sha/python-bingsearch",
    packages=find_packages(),
    platforms=["all"],
    exclude_package_data={
        '': ['config.json', '__pycache__/*']
    },
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ],
    include_package_data=True,  # needed for MANIFEST

    entry_points={
        'console_scripts': [
            'bingsearch = bingsearch.bingsearch:run'
        ],
    }
)
