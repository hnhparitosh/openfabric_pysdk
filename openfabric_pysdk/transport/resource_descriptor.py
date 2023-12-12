from openfabric_pysdk.app import App
from openfabric_pysdk.context import State


#######################################################
#  Resource descriptor
#######################################################
class ResourceDescriptor:
    app: App
    remote: str
    handler: type
    endpoint: str
