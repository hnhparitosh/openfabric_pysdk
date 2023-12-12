from openfabric_pysdk.fields import Schema, fields, post_load

from .ray import Ray, RayStatus
from .bar_schema import BarSchema
from .message_schema import MessageSchema


#######################################################
#  Ray schema
#######################################################
class RaySchema(Schema):
    sid = fields.String()
    uid = fields.String(allow_none=True)
    qid = fields.String()
    rid = fields.String(allow_none=True)
    bars = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(BarSchema),
        allow_none=True
    )
    messages = fields.Nested(MessageSchema(many=True))
    status = fields.Enum(RayStatus)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    finished = fields.Boolean()

    @post_load
    def create(self, data, **kwargs):
        from openfabric_pysdk.utility import SchemaUtil
        return SchemaUtil.create(Ray(None), data)
