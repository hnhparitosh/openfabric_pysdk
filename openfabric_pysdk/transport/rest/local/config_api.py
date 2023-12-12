from typing import List, Union

from openfabric_pysdk.benchmark import MeasureBlockTime
from openfabric_pysdk.flask.rest import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.service import ConfigService
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
    def get(self, uid: UserId) -> ConfigClass:
        with MeasureBlockTime("ConfigRestApi::get"):
            app = self.__descriptor.app
            return ConfigService.read(app, uid)

    # ------------------------------------------------------------------------
    @doc(description="Set APP configuration", tags=["Developer"])
    @use_kwargs(UserIdSchema, location='query')
    @use_kwargs(ConfigSchema, location='json')
    @marshal_with(ConfigSchema)
    def post(self, uid: UserId, config: Union[ConfigClass, List[ConfigClass]]) -> ConfigClass:
        with MeasureBlockTime("ConfigRestApi::post"):
            app = self.__descriptor.app
            return ConfigService.write(app, uid, config)
