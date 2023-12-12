from openfabric_pysdk.fields import Schema, fields


#######################################################
#  Benchmark Schema
#######################################################
class BenchmarkSchema(Schema):
    name = fields.String(allow_none=True)
    avg = fields.String(allow_none=True)
    count = fields.String(allow_none=True)
    stddev = fields.String(allow_none=True)
    min = fields.String(allow_none=True)
    max = fields.String(allow_none=True)

    def __init__(self):
        super().__init__(many=True)
