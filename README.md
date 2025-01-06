# Python Bing Search API

Unofficial bing Search API for Python.

It uses web scraping in the background and is compatible with both **Python 2 and 3**.

## Source

https://github.com/samsha1971/python-bingsearch

## Why this project?

for everyone who want to use bing search.

## Installation

```sh
pip install python-bingsearch
```

## Using

```sh
from bingsearch.bingsearch import BingSearch

bs = BingSearch()
data = bs.search("python")
print(data)
```

```python
# reuse in a program

## first times
with BingSearch() as bs:
    results = bs.search(
        args.keyword, num_results=args.num_results, debug=args.debug)
    
## second times
bs = BingSearch()
results = bs.search(
    args.keyword, num_results=args.num_results, debug=args.debug)
bs.release_resource() # Need active resource release

## third times
with BingSearch() as bs:
    results = bs.search(
        args.keyword, num_results=args.num_results, debug=args.debug)
```

