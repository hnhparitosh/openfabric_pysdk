import collections
from typing import Any, OrderedDict


#######################################################
#  LRU
#######################################################
class LRU:
    __size: int = None
    __evict = None
    __lru_cache: OrderedDict[str, Any] = None

    # ------------------------------------------------------------------------
    def __init__(self, size, evict=None):
        self.__size = size
        self.__lru_cache = collections.OrderedDict()
        self.__evict = evict

    # ------------------------------------------------------------------------
    def get(self, key: str, default=None):
        try:
            value = self.__lru_cache.pop(key)
            self.__lru_cache[key] = value
            return value
        except KeyError:
            return default

    # ------------------------------------------------------------------------
    def put(self, key: str, value: Any):
        try:
            self.__lru_cache.pop(key)
        except KeyError:
            if len(self.__lru_cache) >= self.__size:
                _key, _val = self.__lru_cache.popitem(last=False)
                if self.__evict is not None:
                    self.__evict(_val)
        self.__lru_cache[key] = value

    # ------------------------------------------------------------------------
    def rem(self, key: str):
        if self.__lru_cache[key] is not None:
            del self.__lru_cache[key]
