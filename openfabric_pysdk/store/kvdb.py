import logging
import os
import traceback
from typing import Any, Dict
import pickledb


#######################################################
#  KeyValueDB
#######################################################
class KeyValueDB:
    __name: str = None
    __db_path: str = None
    __autodump: bool = None
    __db: pickledb.PickleDB = None

    # ------------------------------------------------------------------------
    def __init__(self, name: str, path: str = None, autodump: bool = False):

        if path is None:
            path = f"{os.getcwd()}"

        if not os.path.exists(path):
            os.makedirs(path)

        self.__name = name
        self.__autodump = autodump
        self.__db_path = f"{path}/{name}.json"
        try:
            self.__db = pickledb.load(self.__db_path, False, sig=False)
        except:
            logging.error(f"Openfabric - store {self.__db_path} is corrupted, recreate it")
            os.remove(self.__db_path)
            traceback.print_exc()
            self.__db = pickledb.load(self.__db_path, False, sig=False)

    # ------------------------------------------------------------------------
    def reload(self):
        try:
            self.__db = pickledb.load(self.__db_path, False, sig=False)
        except:
            logging.error(f"Openfabric - store {self.__db_path} is corrupted, recreate it")
            os.remove(self.__db_path)
            traceback.print_exc()
            self.__db = pickledb.load(self.__db_path, False, sig=False)

    # ------------------------------------------------------------------------
    def exists(self, key: str):
        return self.__db.exists(key)

    # ---------------------------`---------------------------------------------
    def rem(self, key: str):
        self.__db.rem(key)
        if self.__autodump:
            self.dump()

    # ---------------------------`---------------------------------------------
    def drop(self):
        self.__db.deldb()
        if os.path.isfile(self.__db_path):
            os.remove(self.__db_path)

    # ------------------------------------------------------------------------
    def get(self, key: str):
        return self.__db.get(key)

    # ------------------------------------------------------------------------
    def keys(self):
        return self.__db.getall()

    # ------------------------------------------------------------------------
    def set(self, key: str, val: Any):
        self.__db.set(key, val)
        if self.__autodump:
            self.dump()

    # ------------------------------------------------------------------------
    def dump(self):
        self.__db.dump()

    # ------------------------------------------------------------------------
    def all(self) -> Dict[str, Any]:
        return self.__db.db
