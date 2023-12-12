from typing import Any, Dict

from openfabric_pysdk.flask import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.fields import fields
from openfabric_pysdk.context import RaySchema
from openfabric_pysdk.service import RemoteService
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Execution Queue API
#######################################################
class QueueGetApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Get the response for the indicated request", tags=["Queue"])
    @use_kwargs({'qid': fields.String(required=True)}, location='query')
    @marshal_with(OutputSchema)
    def get(self, qid: str, *args) -> OutputClass:
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}?qid={qid}"
        return RemoteService.get(url, deserializer=OutputSchema().load)


class QueueDeleteApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Remove the indicated requests and the associated results", tags=["Queue"])
    @use_kwargs({'qid': fields.String(required=True)}, location='query')
    @marshal_with(RaySchema)
    def delete(self, qid: str, *args):
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}?qid={qid}"
        return RemoteService.delete(url, deserializer=RaySchema().load)


class QueueListApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Get list of existing requests and their status", tags=["Queue"])
    @marshal_with(RaySchema(many=True))
    def get(self, *args):
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}"
        return RemoteService.get(url, deserializer=RaySchema(many=True).load)


class QueuePostApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Queue a new request", tags=["Queue"])
    @use_kwargs(InputSchema, location='json')
    @marshal_with(RaySchema)
    def post(self, *args):
        data = InputSchema().dump(list(args) if InputSchema().many is True else args[0])
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}"
        return RemoteService.post(url, data=data, deserializer=RaySchema().load)
