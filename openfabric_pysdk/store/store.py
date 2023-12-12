import logging
from typing import Any, Dict

from .lru import LRU
from .kvdb import KeyValueDB


#######################################################
#  Store
#######################################################
class Store:
    __path: str = None
    __kvdbs: LRU = None
    __autodump: bool = None

    # ------------------------------------------------------------------------
    def __init__(self, path: str = None, autodump: bool = False):
        self.__path = path
        self.__autodump = autodump
        self.__kvdbs = LRU(10, self.dump)

    # ------------------------------------------------------------------------
    def dump(self, kvdb: KeyValueDB):
        logging.debug(f"Openfabric - evicting {kvdb}")
        kvdb.dump()

    # ------------------------------------------------------------------------
    def flush(self, name: str):
        kvdb = self.__instance(name)
        logging.debug(f"Openfabric - flush {kvdb}")
        kvdb.dump()

    # ------------------------------------------------------------------------
    def get(self, name, key, default=None) -> Any:
        kvdb = self.__instance(name)
        value = kvdb.get(key)
        if value:
            return value
        else:
            return default

    # ------------------------------------------------------------------------
    def set(self, name: str, key: str, val: Any):
        kvdb = self.__instance(name)
        kvdb.set(key, val)

    # ------------------------------------------------------------------------
    def rem(self, name: str, key: str):
        kvdb = self.__instance(name)
        kvdb.rem(key)

    # ------------------------------------------------------------------------
    def drop(self, name: str):
        kvdb = self.__instance(name)
        self.__kvdbs.rem(name)
        kvdb.drop()

    # ------------------------------------------------------------------------
    def all(self, name: str) -> Dict[str, Any]:
        kvdb = self.__instance(name)
        return kvdb.all()

    # ------------------------------------------------------------------------
    def __instance(self, name: str) -> KeyValueDB:
        kvdb = self.__kvdbs.get(name, None)
        if kvdb is None:
            kvdb = KeyValueDB(f"{name}", path=self.__path, autodump=self.__autodump)
            self.__kvdbs.put(name, kvdb)
        return kvdb
