from openfabric_pysdk.benchmark import MeasureBlockTime, get_all_timings_json
from openfabric_pysdk.flask import *
from openfabric_pysdk.transport import ResourceDescriptor
from openfabric_pysdk.transport.schema import BenchmarkSchema


#######################################################
#  Benchmark API
#######################################################
class BenchmarkApi(MethodResource, Resource):
    __descriptor: ResourceDescriptor = None

    # ------------------------------------------------------------------------
    def __init__(self, descriptor: ResourceDescriptor = None):
        self.__descriptor = descriptor

    # ------------------------------------------------------------------------
    @doc(description="Get APP benchmarks", tags=["Developer"])
    @marshal_with(BenchmarkSchema)
    def get(self):
        with MeasureBlockTime("BenchmarkRestApi::get"):
            return get_all_timings_json()
