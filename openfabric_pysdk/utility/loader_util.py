import importlib
from pydoc import locate

#######################################################
# Class loader utility class
#######################################################
class LoaderUtil:

    @staticmethod
    def import_class(name):
        return locate(name.__module__ + "." + name.__name__)

    @staticmethod
    def get_class(name):
        from openfabric_pysdk.loader.config import execution
        from openfabric_pysdk.benchmark import MeasureBlockTime
        with MeasureBlockTime("Loader::get_class"):
            class_config = execution.get(name)
            if class_config is None or class_config is False or "class" not in class_config or "package" not in class_config:
                return None
            clazz = class_config['class']
            package = class_config['package']
            if clazz is None or package is None:
                return None
            module = importlib.import_module(package)
            return locate(module.__name__ + "." + clazz)

    @staticmethod
    def get_function(name):
        from openfabric_pysdk.loader.config import execution
        from openfabric_pysdk.benchmark import MeasureBlockTime
        with MeasureBlockTime("Loader::get_function"):
            function_config = execution.get(name)
            # TODO: pickledb returns false when the key does not exist.
            if function_config is None or function_config is False or "function" not in function_config or "package" not in function_config:
                return None
            function = function_config['function']
            package = function_config['package']
            if function is None or package is None:
                return None
            module = importlib.import_module(package)
            # print(module.__name__ + "." + function)
            return locate(module.__name__ + "." + function)
