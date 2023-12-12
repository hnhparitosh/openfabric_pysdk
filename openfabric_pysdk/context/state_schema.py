from openfabric_pysdk.fields import Schema, fields

from .state import StateStatus


#######################################################
#  State schema
#######################################################
class StateSchema(Schema):
    status = fields.Enum(StateStatus)
    started_at = fields.DateTime()
