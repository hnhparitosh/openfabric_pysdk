from openfabric_pysdk.fields import Schema, fields, post_load

from .message import Message, MessageType


#######################################################
#  Message schema
#######################################################

class MessageSchema(Schema):
    type = fields.Enum(MessageType)
    content = fields.String()
    created_at = fields.DateTime()

    # ------------------------------------------------------------------------
    @post_load
    def create(self, data, **kwargs):
        from openfabric_pysdk.utility import SchemaUtil
        return SchemaUtil.create(Message(), data)
