from typing import Any, Dict

from openfabric_pysdk.flask import *
from openfabric_pysdk.service import RemoteService
from openfabric_pysdk.transport import ResourceDescriptor
from openfabric_pysdk.transport.schema import ManifestSchema


#######################################################
#  Manifest API
#######################################################
class ManifestApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    # ------------------------------------------------------------------------
    @doc(description="Get APP manifest", tags=["Developer"])
    @marshal_with(ManifestSchema)
    def get(self):
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}"
        return RemoteService.get(url, ManifestSchema().load)
