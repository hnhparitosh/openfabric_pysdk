from openfabric_pysdk.fields import Schema, fields, post_load

from .bar import Bar


#######################################################
#  Bar schema
#######################################################
class BarSchema(Schema):
    percent = fields.String(allow_none=True)
    remaining = fields.String(allow_none=True)

    @post_load
    def create(self, data, **kwargs):
        from openfabric_pysdk.utility import SchemaUtil
        return SchemaUtil.create(Bar(), data)
