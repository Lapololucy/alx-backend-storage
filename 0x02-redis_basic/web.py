#!/usr/bin/env python3
"""Implementing an expiring web cache and tracker"""
import requests
import redis
from functools import wraps
from typing import Callable
import functools


_redis = redis.Redis()


def count_request(method: Callable) -> Callable:
    """Count number of request sent to a URL"""

    @wraps(method)
    def wrapper(*args, **kwargs):
        """Wrapper function for decorator"""
        url = str(*args)
        _redis.incr("count:{}".format(url))
        cache = _redis.get("count:{}".format(url))

        if cache:
            return cache.decode('utf-8')
        else:
            html = method(url)
            _redis.setex("count:".format(url), 10, html)
        return html

    return wrapper


@count_request
def get_page(url: str) -> str:
    """Obtain HTML content through URL"""
    res = requests.get(url)
    return res.text

# Use functools.lru_cache to cache with expiration time of 10 seconds
get_page = functools.lru_cache(maxsize=1, typed=False, timeout=10)(get_page)

url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.example.com"
print(get_page(url))
print(get_page(url))
print(get_page(url))
