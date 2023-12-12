from openfabric_pysdk.utility import LoaderUtil

# Execution callback function
execution_callback_function = LoaderUtil.get_function("main_callback")

# Config callback function
config_callback_function = LoaderUtil.get_function("config_callback")

# Config callback function
suspend_callback_function = LoaderUtil.get_function("suspend_callback")
