from typing import Any, Dict, List, Union

from openfabric_pysdk.flask import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.service import RemoteService
from openfabric_pysdk.transport import ResourceDescriptor
from openfabric_pysdk.transport.schema import UserId, UserIdSchema


#######################################################
#  Config API
#######################################################
class ConfigApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    # ------------------------------------------------------------------------
    @doc(description="Get APP configuration", tags=["Developer"])
    @use_kwargs(UserIdSchema, location='query')
    @marshal_with(ConfigSchema)
    def get(self, uidc: UserId) -> ConfigClass:
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}?uid={uidc.uid}"
        return RemoteService.get(url, ConfigSchema().load)

    # ------------------------------------------------------------------------
    @doc(description="Set APP configuration", tags=["Developer"])
    @use_kwargs(UserIdSchema, location='query')
    @use_kwargs(ConfigSchema, location='json')
    @marshal_with(ConfigSchema)
    def post(self, uidc: UserId, config: Union[ConfigClass, List[ConfigClass]]) -> ConfigClass:

        if ConfigSchema().many is True and not isinstance(config, list):
            config = [config]
        else:
            config = config[0] if type(config) == list else config

        data = ConfigSchema().dump(config)
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}?uid={uidc.uid}"
        return RemoteService.post(url, data, ConfigSchema().load)
