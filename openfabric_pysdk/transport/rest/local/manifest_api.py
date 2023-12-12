from typing import Any, Dict

from openfabric_pysdk.loader import *
from openfabric_pysdk.flask.rest import *
from openfabric_pysdk.context import State
from openfabric_pysdk.benchmark import MeasureBlockTime
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
        with MeasureBlockTime("ManifestRestApi::get"):
            return self.__descriptor.app.get_manifest().all()
