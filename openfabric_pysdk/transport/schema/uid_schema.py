from openfabric_pysdk.fields import Schema, fields, post_load

from openfabric_pysdk.utility import SchemaUtil


#######################################################
#  UID Schema
#######################################################
class UserId(Schema):
    uid: str = None


class UserIdSchema(Schema):
    uid = fields.String(required=True)

    @post_load
    def create(self, data, **kwargs):
        return SchemaUtil.create(UserId(), data)
