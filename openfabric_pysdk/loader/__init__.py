from .config import manifest, execution, state_config
from openfabric_pysdk.utility import LoaderUtil

# Output concept
InputClass = LoaderUtil.get_class("input_class")
InputSchema = LoaderUtil.get_class("input_schema")

# Output concept
OutputClass = LoaderUtil.get_class("output_class")
OutputSchema = LoaderUtil.get_class("output_schema")

# Config concept
ConfigClass = LoaderUtil.get_class("config_class")
ConfigSchema = LoaderUtil.get_class("config_schema")
