import uuid

from openfabric_pysdk.context import RaySchema
from openfabric_pysdk.engine import engine
from openfabric_pysdk.fields import fields
from openfabric_pysdk.flask.rest import *
from openfabric_pysdk.loader import *
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
        return engine.read(qid, 'out', OutputSchema().load)


class QueueDeleteApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Remove the indicated requests and the associated results", tags=["Queue"])
    @use_kwargs({'qid': fields.String(required=True)}, location='query')
    @marshal_with(RaySchema)
    def delete(self, qid: str, *args):
        app = self.__descriptor.app
        return engine.delete(qid, app)


class QueueListApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    @doc(description="Get list of existing requests and their status", tags=["Queue"])
    @marshal_with(RaySchema(many=True))
    def get(self, *args):
        return engine.pending_rays()


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
        sid = uuid.uuid4().hex
        uid = uuid.uuid4().hex
        rid = uuid.uuid4().hex
        app = self.__descriptor.app
        qid = engine.prepare(app, data, sid=sid, uid=uid, rid=rid)
        ray = engine.ray(qid)
        return ray
