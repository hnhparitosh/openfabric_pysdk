import uuid

from openfabric_pysdk.engine import engine
from openfabric_pysdk.flask.rest import *
from openfabric_pysdk.loader import *
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Execution API
#######################################################
class ExecutionApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    # ------------------------------------------------------------------------
    @doc(description="Execute execution and get response", tags=["Execution"])
    @use_kwargs(InputSchema, location='json')
    @marshal_with(OutputSchema)
    def post(self, *args) -> OutputClass:
        sid = uuid.uuid4().hex
        data = InputSchema().dump(list(args) if InputSchema().many is True else args[0])
        app = self.__descriptor.app
        qid = engine.prepare(app, data, sid=sid)
        return engine.process(qid)
