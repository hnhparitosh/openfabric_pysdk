import json
from typing import Any

from openfabric_pysdk.flask import *


#######################################################
#  Remote service
#######################################################
class RemoteService:

    # ------------------------------------------------------------------------
    @staticmethod
    def get(url: str, deserializer=None):
        return RemoteService.__unwrap(get(url), deserializer=deserializer)

    # ------------------------------------------------------------------------
    @staticmethod
    def post(url: str, data: Any, deserializer=None):
        return RemoteService.__unwrap(post(url, json=data), deserializer=deserializer)

    # ------------------------------------------------------------------------
    @staticmethod
    def patch(url: str, data: Any, deserializer=None):
        return RemoteService.__unwrap(patch(url, json=data), deserializer=deserializer)

    # ------------------------------------------------------------------------
    @staticmethod
    def delete(url: str, deserializer=None):
        return RemoteService.__unwrap(delete(url), deserializer=deserializer)

    # ------------------------------------------------------------------------
    @staticmethod
    def __unwrap(response: Response, deserializer=None):
        if response.ok is False:
            return None
        json_object = json.loads(response.text)
        return deserializer(json_object)
