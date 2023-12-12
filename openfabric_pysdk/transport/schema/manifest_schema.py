from openfabric_pysdk.fields import Schema, fields


#######################################################
#  Manifest Schema
#######################################################
class ManifestSchema(Schema):
    name = fields.String(description="App name", allow_none=True)
    version = fields.String(description="App version", allow_none=True)
    description = fields.String(description="APP description", allow_none=True)
    organization = fields.String(description="APP organization", allow_none=True)
    sdk = fields.String(description="APP sdk", allow_none=True)
    overview = fields.String(description="APP overview", allow_none=True)
    input = fields.String(description="APP input", allow_none=True)
    output = fields.String(description="APP output", allow_none=True)

    def __init__(self):
        super().__init__(many=False)
