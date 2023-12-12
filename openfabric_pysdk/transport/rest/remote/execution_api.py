from openfabric_pysdk.flask import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.service import RemoteService
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Execution API
#######################################################
class ExecutionApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Execute execution and get response", tags=["Execution"])
    @use_kwargs(InputSchema, location='json')
    @marshal_with(OutputSchema)
    def post(self, *args) -> OutputClass:
        data = InputSchema().dump(list(args) if InputSchema().many is True else args[0])
        url = f"{self.__descriptor.remote}/{self.__descriptor.endpoint}"
        return RemoteService.post(url, data, OutputSchema().load)
